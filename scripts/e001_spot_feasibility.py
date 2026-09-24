"""BTC-only spot timing feasibility probe; output is never a model result."""

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from mfsm_e001.events import detect_events
from mfsm_e001.labels import label_event
from mfsm_e001.tardis_spot import build_tardis_spot_composite


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2025-03-01")
    args = parser.parse_args()
    day = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if day.day != 1:
        parser.error("Tardis public sample date must be the first day of a month")
    folder = ROOT / "data" / "raw" / "tardis" / args.date
    manifest = json.loads((folder / "manifest.json").read_text())
    names = {
        "binance": f"binance_trades_{args.date}_BTCUSDT.csv.gz",
        "bybit": f"bybit-spot_trades_{args.date}_BTCUSDT.csv.gz",
    }
    if any(name not in manifest for name in names.values()):
        raise ValueError("both BTCUSDT spot sources must be in the Tardis manifest")
    start = int(day.timestamp())
    end = start + 86_399
    points = build_tardis_spot_composite(folder / names["binance"], folder / names["bybit"],
                                         start_s=start, end_s=end)
    valid = sum(point.price is not None for point in points)
    longest = run = 0
    for point in points:
        run = run + 1 if point.price is not None else 0
        longest = max(longest, run)
    events = detect_events(points)
    labels = []
    reasons = Counter()
    for event in events:
        if not event.accepted:
            continue
        if event.decision_s + 1800 > end:
            labels.append({"trigger_s": event.trigger_s, "valid": False,
                           "reason": "full_primary_window_outside_sample"})
            reasons["full_primary_window_outside_sample"] += 1
            continue
        label = label_event(points, event, horizon_s=1800)
        labels.append({"trigger_s": event.trigger_s, **asdict(label)})
        reasons["valid" if label.valid else label.reason] += 1
    report = {
        "provenance": "btc_spot_timing_feasibility_non_scoring",
        "date": args.date,
        "raw_schema": "E001-raw-candidate-1",
        "spot_source_sha256": {venue: manifest[name]["sha256"] for venue, name in names.items()},
        "seconds": len(points),
        "valid_two_source_seconds": valid,
        "longest_consecutive_valid_seconds": longest,
        "crossings": len(events),
        "accepted_events": sum(event.accepted for event in events),
        "lockout_crossings": sum(not event.accepted for event in events),
        "primary_label_counts": dict(reasons),
        "event_ledger": [asdict(event) for event in events],
        "primary_label_ledger": labels,
        "warning": "One public sample day; no feature panel, model fit, predictive score or ETH access.",
    }
    output = ROOT / "data" / "derived" / f"e001_spot_feasibility_{args.date}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
