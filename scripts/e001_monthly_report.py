"""Publish the fixed sample scan with conservative episode-history eligibility."""

from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import gzip
import json

from e001_monthly_scan import DATES, ROOT, pipeline_digest, valid_checkpoint
from e001_quote_audit import file_sha256
from mfsm_e001.sampling import audit_episode_history
from mfsm_e001.spot_quotes import Quote, QuoteGrid, quote_composite


def utc(second):
    return datetime.fromtimestamp(second, timezone.utc).isoformat()


def load_points(path):
    def quote(row):
        if row is None:
            return None
        return Quote(row["event_us"], row["received_us"],
                     Decimal(row["midpoint"]) if row["midpoint"] is not None else None,
                     Decimal(row["spread_bps"]) if row["spread_bps"] is not None else None,
                     row["invalid_reason"])

    with gzip.open(path, "rt") as stream:
        return [quote_composite(QuoteGrid(row["second"], quote(row["binance"]), quote(row["bybit"])))
                for row in map(json.loads, stream)]


def main():
    source = ROOT / "data/derived/e001_monthly_scan/audit.json"
    report = json.loads(source.read_text())
    digest = pipeline_digest()
    if report["pipeline_sha256"] != digest:
        raise ValueError("audit code changed; rerun the monthly scan")
    if report["dates_requested"] != DATES:
        raise ValueError("unexpected sample calendar")
    if (report["status"] != "complete" or report["failures"] or
            [day["date"] for day in report["days"]] != DATES):
        raise ValueError("scan incomplete; inspect audit.json failures before publishing the final report")
    report["audit_sha256"] = file_sha256(source)
    report["history_code_sha256"] = file_sha256(ROOT / "src/mfsm_e001/sampling.py")
    report["report_code_sha256"] = file_sha256(ROOT / "scripts/e001_monthly_report.py")
    nominal_counts, qualified_counts, exclusions, histories = Counter(), Counter(), Counter(), Counter()
    for day in report["days"]:
        date = day["date"]
        checkpoint = source.parent / f"{date}.json"
        if valid_checkpoint(checkpoint, date, digest) != day:
            raise ValueError(f"stale or mismatched checkpoint: {date}")
        grid = ROOT / day["grid_file"]
        points = load_points(grid)
        start = int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
        if [p.second for p in points] != list(range(start, start + 86400)):
            raise ValueError(f"incomplete grid: {date}")
        if sum(p.price is not None for p in points) != day["sensitivity"]["5"]["valid_seconds"]:
            raise ValueError(f"grid/audit coverage mismatch: {date}")
        history = audit_episode_history(points)
        by_trigger = {row["trigger_s"]: row for row in history["crossings"]}
        if list(by_trigger) != [e["trigger_s"] for e in day["event_ledger"]]:
            raise ValueError(f"history/audit crossing mismatch: {date}")
        day["grid_sha256"] = file_sha256(grid)
        day["episode_history"] = history
        day_counts = Counter()
        for event in day["event_ledger"]:
            event["trigger_utc"] = utc(event["trigger_s"])
            event["history_status"] = by_trigger[event["trigger_s"]]["status"]
            histories[event["history_status"]] += 1
        for label in day["primary_labels"]:
            label["history_status"] = by_trigger[label["trigger_s"]]["status"]
            label["history_qualified"] = label["history_status"] == "accepted_with_observed_lockout"
            if label["valid"]:
                nominal_counts[label["state"]] += 1
                if label["history_qualified"]:
                    qualified_counts[label["state"]] += 1
                    day_counts[label["state"]] += 1
            else:
                exclusions[label["reason"]] += 1
        day["history_qualified_label_counts"] = dict(day_counts)
        print(f"{date}: {dict(day_counts)} history-qualified labels", flush=True)

    days = report["days"]
    seconds = len(days) * 86400
    valid = sum(d["sensitivity"]["5"]["valid_seconds"] for d in days)
    summary = {
        "completed_days": len(days), "requested_days": len(DATES),
        "grid_seconds": seconds, "valid_seconds": valid,
        "valid_percent": valid / seconds * 100 if seconds else None,
        "crossings": sum(d["crossings"] for d in days),
        "nominal_episodes": sum(d["accepted_events"] for d in days),
        "nominal_lockout_exclusions": sum(d["crossings"] - d["accepted_events"] for d in days),
        "nominal_label_counts": dict(nominal_counts), "label_exclusions": dict(exclusions),
        "crossing_history_status_counts": dict(histories),
        "history_qualified_label_counts": dict(qualified_counts),
        "nominal_labels_excluded_by_history": sum(
            not label["history_qualified"] for day in days for label in day["primary_labels"]),
        "days_with_nominal_episodes": sum(bool(d["accepted_events"]) for d in days),
        "model_fitted": False,
    }
    report["summary"] = summary
    target = ROOT / "artifacts/e001_monthly_sample_results.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    lines = [
        "# BTC monthly sample feasibility result", "",
        "Fixed scan: **2025-03-01 through 2026-09-01**, first day of each month only. "
        "These are 19 isolated days, not continuous monthly coverage. "
        "The calendar and unchanged event rule are recorded in "
        "[the scan protocol](../experiments/e001_monthly_scan_protocol.md).", "",
        "## Result", "",
        f"Completed **{len(days)}/{len(DATES)} days**; acquisition/audit failures: **{len(report['failures'])}**. "
        f"Found **{summary['crossings']} observable threshold crossings**, "
        f"of which **{summary['nominal_lockout_exclusions']}** were suppressed by the nominal two-hour lockout, "
        f"leaving **{summary['nominal_episodes']} nominal episodes** on "
        f"**{summary['days_with_nominal_episodes']} days**.", "",
        f"Nominal valid label counts: `{dict(nominal_counts)}`. "
        f"Missing-path or sample-boundary label exclusions: **{sum(exclusions.values())}**. "
        f"Additional nominal labels excluded by uncertain episode history: "
        f"**{summary['nominal_labels_excluded_by_history']}**. "
        f"Valid labels whose lockout eligibility is supported by observed history: `{dict(qualified_counts)}`.", "",
        f"The approved five-second midpoint rule gives **{valid:,}/{seconds:,} valid seconds "
        f"({summary['valid_percent']:.5f}%)** across completed days. "
        "This measures quote availability and freshness; it does not verify feed connectivity.", "",
        f"**No model was fitted.** This scan has {summary['nominal_episodes']} nominal episodes, "
        f"{nominal_counts['downside-first']} nominal downside-positive labels and "
        f"{qualified_counts['downside-first']} history-qualified downside-positive labels. "
        "It cannot support the prescribed chronological training, calibration and held-out comparison. "
        "The spot scan also does not "
        "supply the complete perpetual feature panel. It establishes data-pipeline feasibility, "
        "not predictive skill or realistic trading performance.", "",
        "## Every sampled day", "",
        "Complete 30-minute windows require 1,801 consecutive valid one-second grid points. "
        "They overlap and are not independent training observations.", "",
        "| Date | Valid seconds / 86,400 | Valid % | Complete 30m windows | Crossings | Nominal episodes | History-qualified valid labels |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for d in days:
        s = d["sensitivity"]["5"]
        lines.append(f"| {d['date']} | {s['valid_seconds']:,} | {s['valid_percent']:.5f} | "
                     f"{s['complete_30m_windows']:,} | {d['crossings']} | {d['accepted_events']} | "
                     f"{sum(d['history_qualified_label_counts'].values())} |")
    lines += ["", "## Nominal episode ledger", "",
              "| Trigger (UTC) | Outcome | History status |",
              "|---|---|---|"]
    for d in days:
        for label in d["primary_labels"]:
            outcome = label["state"] if label["valid"] else label["reason"]
            lines.append(f"| {utc(label['trigger_s'])} | {outcome} | {label['history_status']} |")
    lines += ["", "## Missing history and remaining limitations", "",
              "Each sample begins without the preceding day's episode state. The history audit "
              "tracks all possible prior lockout states and treats unavailable trigger comparisons "
              "as potential unseen crossings. A nominal event is history-qualified only when every "
              "retained state permits it. Ambiguity is conservative; it is not evidence that a hidden "
              "event actually happened. An arbitrary two-hour burn-in alone is insufficient because "
              "an early ambiguous event can shift later lockouts.", "",
              "Missing price comparisons can hide crossings, so the observed crossing count is not "
              "an estimate of all real episodes. Valid labels use the first observed barrier hit or "
              "the full 30-minute horizon; any missing price before resolution invalidates a label. "
              "The full primary horizon must fit inside the sampled day even for an early hit.", "",
              "These first-of-month days omit most calendar time and cannot represent continuous "
              "market regimes. Quote age does not establish sequence continuity, disconnect status "
              "or usable book depth. No execution costs, fills or predictive performance were measured.", "",
              "## Next implementation handoff", "",
              "1. Keep this sample set as an ingestion and label regression fixture. Do not relax "
              "the event threshold or tune quote age to manufacture more labels.",
              "2. Implement a BTC-only continuous collector for the two spot references plus Bybit "
              "perpetual trades, book, liquidation and derivative-state feeds. Persist raw messages, "
              "local receipt timestamps, connection/reset/sequence evidence and source versions. "
              "Use bounded storage and restartable checkpoints; define the forward observation "
              "period before inspecting its outcomes. A longer existing archive is an alternative "
              "only if its provenance and missingness can be established.",
              "3. Verify synchronized book reconstruction and full 25-bps depth support, resolve "
              "liquidation notional semantics, then implement the remaining neutral/B4/MFSM "
              "feature windows. Do not substitute bankruptcy prices for execution prices.",
              "4. Reassess independent episode counts, both classes and chronological blocks on "
              "that continuous period before constructing training/calibration/test splits. "
              "Keep model fitting disabled until the data and common-feature gates are met. "
              "ETH remains sealed and the freeze manifest remains pending.", "",
              "## Reproduce and provenance", "",
              "```bash", "uv sync --locked --extra test",
              "uv run --locked python scripts/e001_monthly_scan.py --download --workers 2",
              "uv run --locked python scripts/e001_monthly_report.py",
              "uv run --locked pytest -q", "```", "",
              "[Machine-readable results](e001_monthly_sample_results.json) retain all source hashes, "
              "per-day coverage and age/spread/disagreement diagnostics, all crossings and labels, "
              "history classifications, pipeline hashes and grid hashes. Source URLs and download "
              "receipts are retained locally in `data/raw/tardis/DATE/manifest.json`; raw data and "
              "derived grids are ignored by Git. The earlier three-day audit remains unchanged. "
              "A failed date is retained as a failure in the scan, never silently recorded as zero events.", ""]
    (ROOT / "artifacts/e001_monthly_sample_report.md").write_text("\n".join(lines))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
