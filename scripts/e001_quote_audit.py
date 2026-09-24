"""Fixed BTC quote-quality audit and provisional five-second episode ledger."""

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path

from mfsm_e001.events import detect_events
from mfsm_e001.labels import label_event
from mfsm_e001.spot_quotes import iter_quote_grid, quote_composite, quote_invalid_reason


ROOT = Path(__file__).resolve().parents[1]
LIMITS = (1, 2, 5, 10)


def percentiles(values):
    if not values:
        return None
    ordered = sorted(values)
    return {name: ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]
            for name, fraction in (("p50", .5), ("p95", .95), ("p99", .99), ("max", 1))}


def file_sha256(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            sha.update(block)
    return sha.hexdigest()


def audit_day(date, *, include_labels=True):
    day = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    folder = ROOT / "data" / "raw" / "tardis" / date
    manifest = json.loads((folder / "manifest.json").read_text())
    paths = {venue: folder / f"{exchange}_quotes_{date}_BTCUSDT.csv.gz"
             for venue, exchange in (("binance", "binance"), ("bybit", "bybit-spot"))}
    hashes = {}
    for venue, path in paths.items():
        hashes[venue] = file_sha256(path)
        if manifest[path.name]["sha256"] != hashes[venue]:
            raise ValueError(f"manifest hash mismatch: {path}")
    start = int(day.timestamp())
    end = start + 86399
    stats = {limit: {"valid_seconds": 0, "longest_valid_seconds": 0,
                     "longest_invalid_seconds": 0, "complete_30m_windows": 0,
                     "valid_run": 0, "invalid_run": 0} for limit in LIMITS}
    age = {"binance": [], "bybit": []}
    spread = {"binance": [], "bybit": []}
    disagreements = []
    invalid = Counter()
    points = []
    grid_path = ROOT / "data" / "derived" / f"e001_quote_grid_{date}.jsonl.gz"
    grid_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(grid_path, "wt") as output:
        for row in iter_quote_grid(paths["binance"], paths["bybit"], start_s=start, end_s=end):
            output.write(json.dumps(asdict(row), default=str, separators=(",", ":")) + "\n")
            for limit, s in stats.items():
                valid = all(quote_invalid_reason(q, second=row.second, max_age_s=limit) is None
                            for q in (row.binance, row.bybit))
                if valid:
                    s["valid_seconds"] += 1
                    s["valid_run"] += 1
                    s["invalid_run"] = 0
                    s["longest_valid_seconds"] = max(s["longest_valid_seconds"], s["valid_run"])
                    s["complete_30m_windows"] += s["valid_run"] >= 1801
                else:
                    s["invalid_run"] += 1
                    s["valid_run"] = 0
                    s["longest_invalid_seconds"] = max(s["longest_invalid_seconds"], s["invalid_run"])
            point = quote_composite(row, max_age_s=5)
            points.append(point)
            for venue in ("binance", "bybit"):
                q = getattr(row, venue)
                reason = quote_invalid_reason(q, second=row.second, max_age_s=5)
                if reason:
                    invalid[f"{venue}:{reason}"] += 1
                elif point.price is not None:
                    age[venue].append((row.second * 1_000_000 - q.event_us) / 1_000_000)
                    spread[venue].append(float(q.spread_bps))
            if point.price is not None:
                disagreements.append(float(abs(row.binance.midpoint - row.bybit.midpoint) / point.price * 10000))
    for s in stats.values():
        del s["valid_run"], s["invalid_run"]
        s["valid_percent"] = s["valid_seconds"] / 86400 * 100
    events = detect_events(points)
    labels = []
    counts = Counter()
    for event in events if include_labels else ():
        if not event.accepted:
            continue
        if event.decision_s + 1800 > end:
            result = {"valid": False, "reason": "full_primary_window_outside_sample"}
        else:
            result = asdict(label_event(points, event, horizon_s=1800))
        labels.append({"trigger_s": event.trigger_s, **result})
        counts[result["state"] if result["valid"] else result["reason"]] += 1
    return {
        "date": date, "spot_source_sha256": hashes,
        "grid_file": str(grid_path.relative_to(ROOT)),
        "sensitivity": stats, "primary_invalid_venue_seconds": dict(invalid),
        "primary_valid_grid_quote_age_seconds": {v: percentiles(x) for v, x in age.items()},
        "primary_valid_grid_spread_bps": {v: percentiles(x) for v, x in spread.items()},
        "primary_valid_grid_midpoint_disagreement_bps": percentiles(disagreements),
        "crossings": len(events), "accepted_events": sum(e.accepted for e in events),
        "event_ledger": [asdict(e) for e in events], "primary_labels": labels,
        "primary_label_counts": dict(counts),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dates", nargs="+", default=["2025-03-01", "2025-04-01", "2025-05-01"])
    args = parser.parse_args()
    report = {"provenance": "btc_quote_quality_and_episode_feasibility_no_model_scoring",
              "experiment_candidate": "e001-v1.2", "raw_schema": "E001-raw-candidate-2",
              "label_schema": "E001-label-v3", "primary_max_quote_age_seconds": 5,
              "feed_liveness_verified": False, "days": []}
    for date in args.dates:
        result = audit_day(date)
        report["days"].append(result)
        print(f"{date}: {result['sensitivity'][5]['valid_seconds']}/86400 valid seconds; "
              f"{result['accepted_events']} accepted events; {result['primary_label_counts']}", flush=True)
    output = ROOT / "data" / "derived" / "e001_quote_audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
