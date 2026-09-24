"""Explicit fixture runner; real confirmatory builds remain gated."""

import argparse
from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys

from .data import BookUpdate
from .events import SpotTick, build_composite, detect_events
from .features import capacity_features, split_feature_sets
from .labels import label_event
from .public_archive import audit_tardis_csv_gzip, read_binance_spot_zip, read_bybit_spot_gzip


def _archive_summary(path: Path, reader) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    count = 0
    first = None
    last = None
    for row in reader(path):
        count += 1
        first = row.event_ms if first is None else min(first, row.event_ms)
        last = row.event_ms if last is None else max(last, row.event_ms)
    return {"path": str(path), "sha256": digest.hexdigest(), "records": count,
            "first_event_ms": first, "last_event_ms": last, "has_receipt_times": False}


def _fixture() -> dict:
    ticks = []
    for second in range(0, 2130):
        price = Decimal("100")
        if second == 301:
            price = Decimal("99")
        if second == 320:
            price = Decimal("98")
        for venue in ("bybit", "binance"):
            ticks.append(SpotTick(venue, second * 1000, second * 1000, price))
    composite = build_composite(ticks, start_s=0, end_s=2129)
    events = detect_events(composite)
    primary = label_event(composite, events[0], horizon_s=1800)
    books = [
        BookUpdate("bybit", "linear", "BTCUSDT", 301000, 301000, "snapshot", 1, 1,
                   ((Decimal("99"), Decimal("1")),),
                   ((Decimal("99.1"), Decimal("1")),), False, {}),
        BookUpdate("bybit", "linear", "BTCUSDT", 303000, 303000, "delta", 2, 2,
                   ((Decimal("99"), Decimal("2")),), (), False, {}),
    ]
    shared = capacity_features(books, decision_ms=316000, pre_depth_median=Decimal("990"),
                               aggressive_sell_notional=Decimal("50"),
                               liquidation_sell_notional=None)
    b4, mfsm = split_feature_sets(shared)
    return {"provenance": "synthetic_fixture", "events": [asdict(e) for e in events],
            "primary_label": asdict(primary), "b4_features": b4, "mfsm_features": mfsm}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Experiment 001 BTC fixture pipeline")
    parser.add_argument("command", choices=("fixture", "build-real", "audit-public", "audit-tardis"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--binance")
    parser.add_argument("--bybit")
    parser.add_argument("--file")
    parser.add_argument("--data-type")
    parser.add_argument("--exchange")
    parser.add_argument("--symbol", default="BTCUSDT")
    args = parser.parse_args(argv)
    if args.command == "build-real":
        parser.error("real-data build requires audited historical feeds and frozen schema")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.command == "audit-public":
        if not args.binance or not args.bybit:
            parser.error("audit-public requires --binance and --bybit BTC spot archives")
        result = {
            "provenance": "archive_event_time_only",
            "binance": _archive_summary(Path(args.binance), read_binance_spot_zip),
            "bybit": _archive_summary(Path(args.bybit), read_bybit_spot_gzip),
        }
    elif args.command == "audit-tardis":
        if not args.file or not args.data_type or not args.exchange:
            parser.error("audit-tardis requires --file, --data-type and --exchange")
        result = {
            "provenance": "tardis_normalized_csv_audit",
            "sample": audit_tardis_csv_gzip(
                Path(args.file),
                data_type=args.data_type,
                expected_exchange=args.exchange,
                expected_symbol=args.symbol,
            ),
        }
    else:
        result = _fixture()
    output.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
