#!/usr/bin/env python3
"""Outcome-blind response-feature availability on existing BTC development days."""

from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from itertools import groupby
import json
from pathlib import Path
from statistics import median
import argparse

from mfsm_e001.capacity_audit import read_capacity_trades, reconstruct_book_inputs
from mfsm_e001.response_features import response_feature_event


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/mfsm_btc_response_001_protocol.json"
FEASIBILITY_RECEIPT = ROOT / "artifacts/mfsm_btc_response_feasibility_result.json"
FEATURE_CODE = ROOT / "src/mfsm_e001/response_features.py"
REPLAY_CODE = ROOT / "src/mfsm_e001/capacity_audit.py"
PERSISTENCE_CODE = ROOT / "src/mfsm_e001/liquidity_state.py"
AUDIT_CODE = ROOT / "scripts/audit_mfsm_btc_response_feasibility.py"


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _field_audit(protocol_path):
    spec = spec_from_file_location("audit_mfsm_btc_response_feasibility", AUDIT_CODE)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_result(protocol_path)


def _relative(path):
    return str(path.relative_to(ROOT))


def _accepted_events(discovery_path, complete_dates):
    discovery = _load(discovery_path)
    if discovery.get("spot_labels_computed") is not False:
        raise ValueError("spot discovery ledger may contain labels")
    if discovery.get("l2_or_trade_outcomes_read") is not False:
        raise ValueError("spot discovery ledger is not price-only")
    events = []
    for day in discovery["days"]:
        date = day["date"]
        if date not in complete_dates:
            continue
        for event in day.get("event_ledger", []):
            if event.get("accepted") is not True:
                continue
            trigger_s = event["trigger_s"]
            if type(trigger_s) is not int:
                raise ValueError("invalid accepted trigger time")
            observed_date = datetime.fromtimestamp(trigger_s, tz=timezone.utc).date().isoformat()
            if observed_date != date:
                raise ValueError("accepted trigger has wrong UTC date")
            events.append({"date": date, "trigger_s": trigger_s})
    events.sort(key=lambda item: item["trigger_s"])
    if len({event["trigger_s"] for event in events}) != len(events):
        raise ValueError("duplicate accepted trigger")
    return events


def _checked_sources(date, protocol, cache):
    if date in cache:
        return cache[date]
    root = ROOT / protocol["feasibility"]["tardis_root"] / date
    manifest_path = root / "manifest.json"
    manifest = _load(manifest_path)
    source = {}
    for role in ("bybit_linear_l2", "bybit_linear_trades"):
        name = protocol["feasibility"]["required_local_files"][role]["filename"].format(date=date)
        path = root / name
        expected = manifest.get(name, {}).get("sha256")
        if not expected or not path.is_file():
            raise ValueError(f"missing pinned {role} file or checksum for {date}")
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"pinned {role} SHA-256 mismatch for {date}")
        source[role] = {"path": _relative(path), "sha256": actual}
    source["manifest"] = {"path": _relative(manifest_path),
                          "sha256": _sha256(manifest_path)}
    cache[date] = source
    return source


def _distribution(rows, feature_name):
    values = sorted(Decimal(row[feature_name]["value"]) for row in rows
                    if row.get(feature_name, {}).get("available"))
    if not values:
        return {"count": 0, "minimum": None, "median": None, "maximum": None}
    return {"count": len(values), "minimum": str(values[0]),
            "median": str(median(values)), "maximum": str(values[-1])}


def _summary(rows):
    impact_name = "pretrigger_sell_impact_beta_5s"
    replenish_name = "pretrigger_bid_replenishment_beta_5s"
    processed = [row for row in rows if row["status"] == "FEATURES_COMPUTED_DIAGNOSTIC"]
    exclusions = Counter(row["status"] for row in rows
                         if row["status"] != "FEATURES_COMPUTED_DIAGNOSTIC")
    impact_reasons = Counter()
    replenish_reasons = Counter()
    for row in processed:
        impact_reasons.update(row[impact_name]["exclusion_counts"])
        replenish_reasons.update(row[replenish_name]["exclusion_counts"])
    return {
        "accepted_candidate_events": len(rows),
        "events_with_computed_bins": len(processed),
        "events_with_impact_feature": sum(row[impact_name]["available"] for row in processed),
        "events_with_replenishment_feature": sum(row[replenish_name]["available"] for row in processed),
        "events_with_both_features": sum(
            row[impact_name]["available"] and row[replenish_name]["available"]
            for row in processed),
        "event_exclusions": dict(sorted(exclusions.items())),
        "impact_bin_exclusions": dict(sorted(impact_reasons.items())),
        "replenishment_bin_exclusions": dict(sorted(replenish_reasons.items())),
        "impact_beta_distribution": _distribution(processed, impact_name),
        "replenishment_beta_distribution": _distribution(processed, replenish_name),
    }


def build_result(*, progress=None):
    protocol = _load(PROTOCOL)
    if (protocol.get("experiment_version") != "MFSM-BTC-RESPONSE-1"
            or protocol.get("protocol_revision") != "1.1"):
        raise ValueError("unexpected BTC response protocol")
    feasibility_receipt = _load(FEASIBILITY_RECEIPT)
    if feasibility_receipt["protocol_sha256"] != _sha256(PROTOCOL):
        raise ValueError("feasibility receipt does not pin this protocol")
    feasibility = _field_audit(PROTOCOL)
    if feasibility["status"] != "DEVELOPMENT_FEASIBLE_NOT_VALIDATION_READY":
        raise ValueError("local field/event feasibility gate has not passed")
    complete_dates = set(feasibility["local_tardis"]["complete_dates"])
    discovery_path = ROOT / protocol["feasibility"]["existing_spot_discovery"]
    events = _accepted_events(discovery_path, complete_dates)
    if len(events) != feasibility_receipt["measured"]["accepted_candidate_events_on_complete_input_dates"]:
        raise ValueError("accepted event count differs from the frozen feasibility receipt")

    rows = []
    sources = {}
    index = 0
    for date, grouped in groupby(events, key=lambda event: event["date"]):
        day_events = list(grouped)
        day_start_s = int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp())
        replay_events = [event for event in day_events
                         if event["trigger_s"] - 1800 >= day_start_s]
        replay_error = None
        if replay_events:
            try:
                source = _checked_sources(date, protocol, sources)
                target_seconds = sorted({second for event in replay_events
                    for second in range(event["trigger_s"] - 1800,
                                        event["trigger_s"] - 4, 5)})
                observation_ranges = [
                    (event["trigger_s"] - 1800, event["trigger_s"] - 5)
                    for event in replay_events]
                states, observations, book_diagnostics = reconstruct_book_inputs(
                    ROOT / source["bybit_linear_l2"]["path"],
                    target_seconds=target_seconds,
                    observation_ranges=observation_ranges, top_levels=50)
                trades, trade_diagnostics = read_capacity_trades(
                    ROOT / source["bybit_linear_trades"]["path"],
                    windows=[(event["trigger_s"] - 1800,
                              event["trigger_s"] - 10)
                             for event in replay_events])
            except (OSError, ValueError, KeyError, ArithmeticError) as exc:
                replay_error = str(exc)
        for event in day_events:
            trigger_s = event["trigger_s"]
            row = {"date": date, "trigger_s": trigger_s}
            if trigger_s - 1800 < day_start_s:
                row.update(status="PREHISTORY_CROSSES_UNAVAILABLE_PRIOR_UTC_DAY",
                           reason="the required 30-minute history begins before this isolated sample day")
            elif replay_error is not None:
                row.update(status="SOURCE_OR_REPLAY_ERROR", reason=replay_error)
            else:
                try:
                    features = response_feature_event(
                        states, observations, trades, trigger_s=trigger_s,
                        protocol=protocol)
                    row.update(features)
                    row.update(status="FEATURES_COMPUTED_DIAGNOSTIC",
                               shared_day_book_replay=book_diagnostics,
                               shared_day_trade_read=trade_diagnostics,
                               observed_book_cohorts=sum(
                                   (trigger_s - 1800)*1_000_000_000 <= item["event_ns"]
                                   <= (trigger_s - 5)*1_000_000_000
                                   for item in observations))
                except (ValueError, KeyError, ArithmeticError) as exc:
                    row.update(status="SOURCE_OR_REPLAY_ERROR", reason=str(exc))
            rows.append(row)
            index += 1
            if progress is not None:
                progress(index, len(events), row)

    return {
        "schema": "MFSM-BTC-RESPONSE-1-feature-availability-result-1",
        "status": "DEVELOPMENT_FEATURE_DIAGNOSTIC_ONLY",
        "experiment_version": "MFSM-BTC-RESPONSE-1",
        "protocol_revision": protocol["protocol_revision"],
        "protocol_sha256": _sha256(PROTOCOL),
        "feasibility_receipt_sha256": _sha256(FEASIBILITY_RECEIPT),
        "spot_discovery_sha256": _sha256(discovery_path),
        "runner_sha256": _sha256(Path(__file__)),
        "feature_code_sha256": _sha256(FEATURE_CODE),
        "book_trade_replay_sha256": _sha256(REPLAY_CODE),
        "persistent_addition_code_sha256": _sha256(PERSISTENCE_CODE),
        "field_audit_code_sha256": _sha256(AUDIT_CODE),
        "source_files": sources,
        "events": rows,
        "summary": _summary(rows),
        "measurement_limits": [
            "Tardis normalized trade IDs do not provide a per-trade sequence chain; trade feed completeness is not independently certified.",
            "The book-change guard rejects unseen additions that enter the credited top 50, including those beyond 25 bps; the separate 25-bps coverage view is not interpreted as market capacity.",
            "A successful value is a pre-trigger development diagnostic, not a validated forecast or a causal response coefficient.",
            "The first-of-month sample has prior development exposure and is not fresh confirmation data.",
        ],
        "labels_read": False,
        "model_fitted": False,
        "predictions_scored": False,
        "pnl_computed": False,
        "paid_data_used": False,
        "eth_accessed": False,
        "model_ready": False,
    }


def _render_report(result):
    summary = result["summary"]
    lines = [
        "# MFSM BTC response-feature availability on development dates", "",
        f"Status: **{result['status']}**", "",
        "The audit used only accepted price-defined BTC trigger times and earlier Bybit perpetual L2/trades. It did not read labels, fit a model, score predictions, or calculate P&L.", "",
        "| Quantity | Count |", "|---|---:|",
        f"| Accepted candidate events | {summary['accepted_candidate_events']} |",
        f"| Events with computed bins | {summary['events_with_computed_bins']} |",
        f"| Impact coefficient available (at least 30 bins) | {summary['events_with_impact_feature']} |",
        f"| Replenishment coefficient available (at least 30 bins) | {summary['events_with_replenishment_feature']} |",
        f"| Both available | {summary['events_with_both_features']} |", "",
        "## Event exclusions", "",
    ]
    if summary["event_exclusions"]:
        lines.extend(f"- {reason}: {count}" for reason, count in summary["event_exclusions"].items())
    else:
        lines.append("- None at the event level.")
    lines.extend(["", "## Bin exclusions", "",
                  "Counts cover all processed development events and the two summaries have different eligibility requirements.", ""])
    for label, key in (("Sell-impact", "impact_bin_exclusions"),
                       ("Bid-replenishment", "replenishment_bin_exclusions")):
        lines.append(f"- {label}: " + ", ".join(
            f"{reason} {count}" for reason, count in summary[key].items()))
    lines.extend(["", "## Feature distributions among available development diagnostics", ""])
    for label, key in (("Sell-impact beta", "impact_beta_distribution"),
                       ("Bid-replenishment beta", "replenishment_beta_distribution")):
        item = summary[key]
        lines.append(
            f"- {label}: count {item['count']}; minimum {item['minimum']}; median {item['median']}; maximum {item['maximum']}."
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {limit}" for limit in result["measurement_limits"])
    lines.extend(["", "No model-ready or trading-edge result follows from these values.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing output directory: {destination}")

    def progress(index, total, row):
        print(json.dumps({"processed": index, "total": total,
                          "date": row["date"], "trigger_s": row["trigger_s"],
                          "status": row["status"]}), flush=True)

    result = build_result(progress=progress)
    destination.mkdir(parents=False)
    (destination / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8")
    (destination / "report.md").write_text(_render_report(result), encoding="utf-8")
    print(json.dumps({"output": str(destination), "summary": result["summary"]},
                     sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
