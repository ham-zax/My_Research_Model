#!/usr/bin/env python3
"""Read-only field/calendar feasibility audit for MFSM-BTC-RESPONSE-1."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = REPO_ROOT / "experiments/mfsm_btc_response_001_protocol.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _header(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        row = next(csv.reader(stream), None)
    if row is None:
        raise ValueError(f"empty gzip CSV: {_relative(path)}")
    return row


def _date_rows(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    root = REPO_ROOT / protocol["feasibility"]["tardis_root"]
    required = protocol["feasibility"]["required_local_files"]
    rows: list[dict[str, Any]] = []

    if not root.is_dir():
        return rows

    for date_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        try:
            datetime.strptime(date_dir.name, "%Y-%m-%d")
        except ValueError:
            continue

        sources: dict[str, Any] = {}
        complete = True
        for role, spec in required.items():
            path = date_dir / spec["filename"].format(date=date_dir.name)
            record: dict[str, Any] = {
                "path": _relative(path),
                "exists": path.is_file(),
                "header_valid": False,
                "missing_columns": list(spec["required_columns"]),
            }
            if path.is_file():
                columns = _header(path)
                missing = sorted(set(spec["required_columns"]) - set(columns))
                record["header_valid"] = not missing
                record["missing_columns"] = missing
                record["columns"] = columns
            if not record["exists"] or not record["header_valid"]:
                complete = False
            sources[role] = record

        rows.append({
            "date": date_dir.name,
            "complete_required_inputs": complete,
            "sources": sources,
        })
    return rows


def _spot_candidates(
    protocol: dict[str, Any],
    complete_dates: set[str],
) -> dict[str, Any]:
    path = REPO_ROOT / protocol["feasibility"]["existing_spot_discovery"]
    if not path.is_file():
        return {
            "source": _relative(path),
            "available": False,
            "crossings_on_complete_dates": None,
            "accepted_candidate_events_on_complete_dates": None,
            "independent_utc_weeks_on_complete_dates": None,
            "dates_with_accepted_candidate_events": [],
        }

    discovery = _load_json(path)
    crossings = 0
    accepted = 0
    weeks: set[str] = set()
    dates_with_events: list[str] = []

    for day in discovery.get("days", []):
        date = day.get("date")
        if date not in complete_dates:
            continue
        crossings += int(day.get("crossings", 0))
        day_accepted = int(day.get("accepted_events", 0))
        accepted += day_accepted
        if day_accepted:
            dates_with_events.append(date)
        for event in day.get("event_ledger", []):
            if not event.get("accepted"):
                continue
            trigger_s = event.get("trigger_s")
            if not isinstance(trigger_s, int):
                continue
            stamp = datetime.fromtimestamp(trigger_s, tz=timezone.utc)
            iso = stamp.isocalendar()
            weeks.add(f"{iso.year}-W{iso.week:02d}")

    return {
        "source": _relative(path),
        "available": True,
        "source_sha256": _sha256(path),
        "crossings_on_complete_dates": crossings,
        "accepted_candidate_events_on_complete_dates": accepted,
        "independent_utc_weeks_on_complete_dates": len(weeks),
        "utc_weeks": sorted(weeks),
        "dates_with_accepted_candidate_events": dates_with_events,
        "warning": (
            "These are price-defined development candidates only. This audit does "
            "not replay L2, compute response measurements, inspect labels, or score models."
        ),
    }


def build_result(protocol_path: Path) -> dict[str, Any]:
    protocol = _load_json(protocol_path)
    if protocol.get("experiment_version") != "MFSM-BTC-RESPONSE-1":
        raise ValueError("unexpected protocol version")

    rows = _date_rows(protocol)
    complete_dates = {
        row["date"] for row in rows if row["complete_required_inputs"]
    }
    candidates = _spot_candidates(protocol, complete_dates)

    header_failures = []
    for row in rows:
        for role, source in row["sources"].items():
            if source["exists"] and not source["header_valid"]:
                header_failures.append({
                    "date": row["date"],
                    "role": role,
                    "path": source["path"],
                    "missing_columns": source["missing_columns"],
                })

    accepted = candidates["accepted_candidate_events_on_complete_dates"]
    gate_failures = []
    if not complete_dates:
        gate_failures.append(
            "No local sample date has all four required files with valid headers."
        )
    if not candidates["available"]:
        gate_failures.append(
            "The existing spot-only discovery ledger is unavailable, so accepted "
            "candidate-event overlap cannot be established."
        )
    elif not isinstance(accepted, int) or accepted <= 0:
        gate_failures.append(
            "No accepted price-defined BTC candidate event overlaps a complete-input date."
        )
    passed = not gate_failures
    status = (
        "DEVELOPMENT_FEASIBLE_NOT_VALIDATION_READY"
        if passed
        else "INSUFFICIENT_LOCAL_FIELD_OR_EVENT_FEASIBILITY"
    )

    return {
        "schema": "MFSM-BTC-RESPONSE-1-feasibility-result-1",
        "experiment_version": "MFSM-BTC-RESPONSE-1",
        "status": status,
        "gate_failures": gate_failures,
        "audit_scope": "headers_calendar_and_price_defined_candidate_counts_only",
        "protocol": _relative(protocol_path),
        "protocol_sha256": _sha256(protocol_path),
        "runner": _relative(Path(__file__).resolve()),
        "runner_sha256": _sha256(Path(__file__).resolve()),
        "local_tardis": {
            "sample_date_directories": len(rows),
            "complete_required_input_dates": len(complete_dates),
            "complete_dates": sorted(complete_dates),
            "header_failures": header_failures,
            "date_inventory": rows,
        },
        "spot_candidate_reuse": candidates,
        "measurement_field_feasibility": {
            "spot_trigger": {
                "required_roles": ["binance_spot_quotes", "bybit_spot_quotes"],
                "field_available_on_complete_dates": bool(complete_dates),
            },
            "pretrigger_sell_impact_beta_5s": {
                "required_roles": ["bybit_linear_l2", "bybit_linear_trades"],
                "field_available_on_complete_dates": bool(complete_dates),
                "value_computed": False,
            },
            "pretrigger_bid_replenishment_beta_5s": {
                "required_roles": ["bybit_linear_l2", "bybit_linear_trades"],
                "field_available_on_complete_dates": bool(complete_dates),
                "value_computed": False,
            },
        },
        "fresh_validation_ready": False,
        "fresh_validation_reason": (
            "The local Tardis first-of-month sample is non-continuous and has been "
            "used in prior development studies. A fresh predeclared continuous period "
            "or untouched archive is still required."
        ),
        "historical_full_period_ready": False,
        "historical_full_period_reason": (
            "The local sample does not provide continuous L2 coverage across the "
            "historical spot event calendar."
        ),
        "model_fit_performed": False,
        "labels_read": False,
        "l2_outcomes_replayed": False,
        "pnl_computed": False,
        "paid_data_used": False,
        "eth_accessed": False,
        "next_gate": (
            "Implement outcome-blind response-feature extraction on development-only "
            "complete dates; inspect only feature availability/distributions; then freeze "
            "neutral comparator summaries and a fresh evaluation calendar before scoring."
            if passed else
            "Resolve the listed missing field or candidate-event evidence and rerun "
            "the field/calendar feasibility audit before response-feature extraction. "
            "Model scoring remains disabled."
        ),
    }


def _render_report(result: dict[str, Any]) -> str:
    local = result["local_tardis"]
    candidates = result["spot_candidate_reuse"]
    complete = local["complete_required_input_dates"]
    total = local["sample_date_directories"]
    accepted = candidates["accepted_candidate_events_on_complete_dates"]
    crossings = candidates["crossings_on_complete_dates"]
    weeks = candidates["independent_utc_weeks_on_complete_dates"]
    passed = result["status"] == "DEVELOPMENT_FEASIBLE_NOT_VALIDATION_READY"

    lines = [
        "# MFSM BTC response-state feasibility result",
        "",
        "Version: MFSM-BTC-RESPONSE-1-feasibility-result-1  ",
        f"Status: **{result['status']}**",
        "",
        "## What this audit checked",
        "",
        "This is a read-only feasibility audit. It inspected local Tardis file presence and CSV headers, then reused the existing spot-only event-discovery ledger only to count price-defined candidate events on dates where all required response inputs are present.",
        "",
        "It did **not** replay L2 outcomes, compute the new response coefficients, read event labels, fit a model, score predictions, compute P&L, use paid data, or access ETH.",
        "",
        "## Local field coverage",
        "",
        f"- Tardis sample date directories: **{total}**.",
        f"- Dates with Binance spot quotes + Bybit spot quotes + Bybit perpetual L2 + Bybit perpetual trades and valid required headers: **{complete}**.",
    ]
    if complete:
        lines.append(
            f"- Complete-input span: **{local['complete_dates'][0]}** through **{local['complete_dates'][-1]}** on non-continuous first-of-month samples."
        )
    lines.extend([
        f"- Header failures among present required files: **{len(local['header_failures'])}**.",
        "",
    ])
    if passed:
        lines.append(
            "The required fields are present locally on complete-input dates for development-time construction of both proposed response summaries: pre-trigger sell-impact beta and pre-trigger bid-replenishment beta. The candidate-event overlap gate also passed."
        )
    elif complete:
        lines.append(
            "The required fields are present on complete-input dates, but the development feasibility gate has **not passed** because candidate-event overlap is missing or unverified."
        )
    else:
        lines.append(
            "No complete-input date verifies all required fields; the development feasibility gate has **not passed**."
        )
    lines.extend(["", "## Price-defined candidate overlap", ""])
    if candidates["available"]:
        lines.extend([
            f"- Crossings on complete-input dates: **{crossings}**.",
            f"- Two-hour-lockout accepted candidate events on complete-input dates: **{accepted}**.",
            f"- Distinct UTC calendar weeks containing those accepted candidates: **{weeks}**.",
            "",
            "These counts establish only that candidate event timestamps overlap the required files. They are **not** response-feature-eligible counts because this milestone deliberately does not replay the L2 histories.",
        ])
    else:
        lines.append("- Existing spot-only discovery ledger was not available, so candidate-event overlap was not established.")

    lines.extend([
        "",
        "## What remains blocked",
        "",
        "- The local Tardis archive is a non-continuous first-of-month development sample and has prior outcome exposure. It cannot serve as fresh confirmation.",
        "- Continuous historical L2 coverage across the full 2023-07 to 2026-08 spot-event calendar is not locally available.",
        "- Binance historical futures L2 is an access-gated alternative and was not used by this audit.",
        "- CryptoStruct remains a paid route and was not used.",
        "- A new prospective public capture needs a newly fixed acquisition period before launch; the prior capture window has expired.",
        "",
        "## Decision",
        "",
    ])
    if passed:
        lines.append(
            "The response-law idea is **field-feasible for development** with data already present in the repository. The next implementation step can therefore be outcome-blind response-feature extraction on these development-only dates. Model scoring should remain disabled until the neutral comparator summaries and a genuinely fresh evaluation calendar are frozen."
        )
    else:
        lines.append("The development field/event feasibility gate has **not passed**. Missing evidence:")
        lines.extend(f"- {failure}" for failure in result["gate_failures"])
        lines.extend(["", result["next_gate"]])
    lines.extend([
        "",
        "## Integrity",
        "",
        f"- Protocol SHA-256: {result['protocol_sha256']}",
        f"- Audit runner SHA-256: {result['runner_sha256']}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol_path = args.protocol.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output directory: {output}")
    output.mkdir(parents=False)

    result = build_result(protocol_path)
    result_path = output / "result.json"
    report_path = output / "report.md"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_report(result), encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "complete_required_input_dates": result["local_tardis"]["complete_required_input_dates"],
        "accepted_candidate_events_on_complete_dates": result["spot_candidate_reuse"]["accepted_candidate_events_on_complete_dates"],
        "independent_utc_weeks_on_complete_dates": result["spot_candidate_reuse"]["independent_utc_weeks_on_complete_dates"],
        "output": _relative(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
