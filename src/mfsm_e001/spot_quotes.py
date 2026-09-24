"""Receipt-aware spot quote states; quote age does not prove feed connectivity."""

from contextlib import closing
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import gzip
from pathlib import Path

from .data import DataError
from .events import CompositePoint


@dataclass(frozen=True)
class Quote:
    event_us: int
    received_us: int
    midpoint: Decimal | None
    spread_bps: Decimal | None
    invalid_reason: str | None


@dataclass(frozen=True)
class QuoteGrid:
    second: int
    binance: Quote | None
    bybit: Quote | None


def read_spot_quotes(path: str | Path, *, exchange: str):
    path = Path(path)
    if "eth" in str(path).lower() or "eth" in str(path.resolve()).lower():
        raise DataError("ETH holdout is sealed")
    if exchange not in {"binance", "bybit-spot"} or "BTCUSDT" not in path.name:
        raise DataError("explicit BTCUSDT spot quote file required")
    previous_local = -1
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"exchange", "symbol", "timestamp", "local_timestamp", "bid_price",
                    "ask_price", "bid_amount", "ask_amount"}
        if not required.issubset(reader.fieldnames or []):
            raise DataError("invalid Tardis quote schema")
        for row in reader:
            if row["symbol"] != "BTCUSDT" or row["exchange"] != exchange:
                raise DataError("out-of-scope quote row")
            event, local = int(row["timestamp"]), int(row["local_timestamp"])
            if min(event, local) < 0 or local < previous_local:
                raise DataError("invalid or nonmonotonic receipt timestamp")
            previous_local = local
            reason = "receipt_precedes_event" if event > local else None
            try:
                bid, ask, bid_size, ask_size = (
                    Decimal(row[key]) for key in ("bid_price", "ask_price", "bid_amount", "ask_amount"))
                if not all(value.is_finite() and value > 0 for value in (bid, ask, bid_size, ask_size)):
                    reason = reason or "invalid_price_or_size"
                elif bid >= ask:
                    reason = reason or "crossed_or_locked_quote"
            except (InvalidOperation, ValueError):
                reason = reason or "missing_or_invalid_quote"
            if reason:
                yield Quote(event, local, None, None, reason)
            else:
                mid = (bid + ask) / 2
                yield Quote(event, local, mid, (ask - bid) / mid * 10000, None)


def iter_quote_grid(binance: str | Path, bybit: str | Path, *, start_s: int, end_s: int):
    """Use the newest received state, with capture row order breaking timestamp ties."""
    if end_s < start_s:
        raise ValueError("empty quote interval")
    readers = {"binance": read_spot_quotes(binance, exchange="binance"),
               "bybit": read_spot_quotes(bybit, exchange="bybit-spot")}
    with closing(readers["binance"]), closing(readers["bybit"]):
        pending = {key: next(reader, None) for key, reader in readers.items()}
        latest = {"binance": None, "bybit": None}
        for second in range(start_s, end_s + 1):
            for key, reader in readers.items():
                while pending[key] is not None and pending[key].received_us <= second * 1_000_000:
                    latest[key] = pending[key]
                    pending[key] = next(reader, None)
            yield QuoteGrid(second, latest["binance"], latest["bybit"])


def quote_invalid_reason(quote: Quote | None, *, second: int, max_age_s: int) -> str | None:
    if quote is None:
        return "no_received_quote"
    if quote.invalid_reason:
        return quote.invalid_reason
    boundary = second * 1_000_000
    if quote.received_us > boundary or quote.event_us > boundary:
        return "quote_not_yet_available"
    if boundary - quote.event_us > max_age_s * 1_000_000:
        return "quote_too_old"
    return None


def quote_composite(grid: QuoteGrid, *, max_age_s: int = 5) -> CompositePoint:
    if max_age_s < 0:
        raise ValueError("negative quote age limit")
    quotes = (grid.binance, grid.bybit)
    if any(quote_invalid_reason(q, second=grid.second, max_age_s=max_age_s) for q in quotes):
        return CompositePoint(grid.second, None, None)
    return CompositePoint(grid.second, (grid.binance.midpoint + grid.bybit.midpoint) / 2,
                          (max(grid.binance.received_us, grid.bybit.received_us) + 999) // 1000)
