"""BTC-only, receipt-aware streaming spot composite from Tardis trade CSVs."""

import csv
from contextlib import closing
from decimal import Decimal, InvalidOperation
import gzip
from pathlib import Path

from .data import DataError
from .events import CompositePoint, SpotTick


def read_tardis_spot_trades(path: str | Path, *, exchange: str):
    """Yield source trades in collector arrival order, retaining causal availability."""
    path = Path(path)
    if "eth" in str(path).lower():
        raise DataError("ETH holdout is sealed")
    if exchange not in {"binance", "bybit-spot"} or "BTCUSDT" not in path.name:
        raise DataError("explicit BTCUSDT spot archive and approved exchange required")
    if not path.is_file():
        raise DataError("BTCUSDT spot archive does not exist")
    previous_local_us = -1
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        rows = csv.DictReader(stream)
        required = {"exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"}
        if not required.issubset(rows.fieldnames or []):
            raise DataError("invalid Tardis spot trade columns")
        for row in rows:
            if row["exchange"] != exchange or row["symbol"] != "BTCUSDT":
                raise DataError("out-of-scope spot trade row")
            event_us, local_us = int(row["timestamp"]), int(row["local_timestamp"])
            if event_us < 0 or local_us < event_us or local_us < previous_local_us:
                raise DataError("invalid or nonmonotonic spot timestamps")
            previous_local_us = local_us
            try:
                price = Decimal(row["price"])
            except InvalidOperation as exc:
                raise DataError("invalid spot trade price") from exc
            if not price.is_finite() or price <= 0:
                raise DataError("invalid spot trade price")
            yield SpotTick("bybit" if exchange == "bybit-spot" else "binance",
                           event_us // 1000, (local_us + 999) // 1000, price)


def build_tardis_spot_composite(binance: str | Path, bybit: str | Path,
                                *, start_s: int, end_s: int) -> list[CompositePoint]:
    """Retain the legacy one-second trade reference for the original feasibility audit."""
    if end_s < start_s:
        raise ValueError("empty composite interval")
    source = {
        "binance": read_tardis_spot_trades(binance, exchange="binance"),
        "bybit": read_tardis_spot_trades(bybit, exchange="bybit-spot"),
    }
    with closing(source["binance"]), closing(source["bybit"]):
        pending = {name: next(reader, None) for name, reader in source.items()}
        latest: dict[str, SpotTick | None] = {"binance": None, "bybit": None}
        points = []
        for second in range(start_s, end_s + 1):
            boundary_ms = second * 1000
            selected = []
            for name in ("bybit", "binance"):
                while pending[name] is not None and pending[name].received_ms <= boundary_ms:
                    tick = pending[name]
                    if latest[name] is None or (tick.event_ms, tick.received_ms) > (
                            latest[name].event_ms, latest[name].received_ms):
                        latest[name] = tick
                    pending[name] = next(source[name], None)
                tick = latest[name]
                if tick is not None and tick.event_ms <= boundary_ms and boundary_ms - tick.event_ms <= 1000:
                    selected.append(tick)
            if len(selected) == 2:
                points.append(CompositePoint(second, (selected[0].price + selected[1].price) / 2,
                                             max(x.received_ms for x in selected)))
            else:
                points.append(CompositePoint(second, None, None))
        return points
