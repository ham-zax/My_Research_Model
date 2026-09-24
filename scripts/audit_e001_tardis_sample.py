"""Stream a fixed BTCUSDT Tardis sample and record coverage without building events."""

import argparse
import csv
from datetime import datetime
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "trades": {"exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"},
    "quotes": {"exchange", "symbol", "timestamp", "local_timestamp", "ask_amount", "ask_price",
               "bid_price", "bid_amount"},
    "incremental_book_L2": {"exchange", "symbol", "timestamp", "local_timestamp", "is_snapshot", "side", "price", "amount"},
    "liquidations": {"exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"},
    "derivative_ticker": {"exchange", "symbol", "timestamp", "local_timestamp", "funding_timestamp",
                          "funding_rate", "open_interest", "index_price", "mark_price"},
}


def audit_file(path: Path, exchange: str, kind: str) -> dict:
    count = 0
    min_event = min_local = 10**30
    max_event = max_local = -1
    negative_latency = 0
    missing_local = 0
    snapshot_rows = 0
    nonempty_open_interest = 0
    by_hour: dict[int, int] = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        rows = csv.DictReader(stream)
        if not EXPECTED[kind].issubset(rows.fieldnames or []):
            raise ValueError(f"wrong columns in {path}")
        for row in rows:
            if row["exchange"] != exchange or row["symbol"] != "BTCUSDT":
                raise ValueError(f"out-of-scope row in {path}")
            count += 1
            event = int(row["timestamp"])
            min_event, max_event = min(min_event, event), max(max_event, event)
            if row["local_timestamp"]:
                local = int(row["local_timestamp"])
                min_local, max_local = min(min_local, local), max(max_local, local)
                negative_latency += local < event
                hour = (local // 1_000_000 // 3600) % 24
                by_hour[hour] = by_hour.get(hour, 0) + 1
            else:
                missing_local += 1
            if kind == "incremental_book_L2" and row["is_snapshot"] == "true":
                snapshot_rows += 1
            if kind == "derivative_ticker" and row["open_interest"]:
                nonempty_open_interest += 1
    return {
        "rows": count,
        "event_us_min": min_event if count else None,
        "event_us_max": max_event if count else None,
        "local_us_min": min_local if count > missing_local else None,
        "local_us_max": max_local if count > missing_local else None,
        "missing_local_timestamp_rows": missing_local,
        "local_before_event_rows": negative_latency,
        "hours_with_receipt_rows": sorted(by_hour),
        "snapshot_rows": snapshot_rows if kind == "incremental_book_L2" else None,
        "nonempty_open_interest_rows": nonempty_open_interest if kind == "derivative_ticker" else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2025-03-01")
    args = parser.parse_args()
    datetime.strptime(args.date, "%Y-%m-%d")
    target = ROOT / "data" / "raw" / "tardis" / args.date
    manifest = json.loads((target / "manifest.json").read_text())
    report = {"date": args.date, "provenance": "tardis_normalized_csv_btc_only",
              "source_manifest": str(target / "manifest.json"), "files": {}}
    for name, item in manifest.items():
        if item["symbol"] != "BTCUSDT" or "ETH" in name.upper():
            raise ValueError("manifest contains out-of-scope instrument")
        prefix = name.removesuffix(f"_{args.date}_BTCUSDT.csv.gz")
        exchange, kind = prefix.split("_", 1)
        if exchange not in {"bybit", "bybit-spot", "binance"} or kind not in EXPECTED:
            raise ValueError("manifest contains unapproved feed")
        report["files"][name] = audit_file(target / name, exchange, kind)
        item["has_local_timestamp_column"] = True
        print(f"audited {name}: {report['files'][name]['rows']} rows", flush=True)
    output = ROOT / "data" / "derived" / f"e001_tardis_audit_{args.date}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
