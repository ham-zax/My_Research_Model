"""Narrow BTCUSDT fixture adapter; source payloads remain alongside outputs."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from typing import Any


class DataError(ValueError):
    """An input cannot be interpreted under the declared feed contract."""


@dataclass(frozen=True)
class Trade:
    venue: str
    market: str
    symbol: str
    event_ms: int
    received_ms: int
    trade_id: str
    taker_side: str
    base_size: Decimal
    price: Decimal
    notional_quote: Decimal
    raw: dict[str, Any]


@dataclass(frozen=True)
class Liquidation:
    venue: str
    market: str
    symbol: str
    event_ms: int
    received_ms: int
    position_side: str
    pressure_side: str
    base_size: Decimal
    bankruptcy_price: Decimal
    executed_notional: None
    raw: dict[str, Any]


@dataclass(frozen=True)
class BookUpdate:
    venue: str
    market: str
    symbol: str
    event_ms: int
    received_ms: int
    kind: str
    update_id: int
    sequence: int
    bids: tuple[tuple[Decimal, Decimal], ...]
    asks: tuple[tuple[Decimal, Decimal], ...]
    source_gap: bool
    raw: dict[str, Any]


def _positive(value: Any, name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise DataError(f"invalid {name}") from exc
    if not result.is_finite() or result <= 0:
        raise DataError(f"invalid {name}")
    return result


def _levels(values: Any) -> tuple[tuple[Decimal, Decimal], ...]:
    output = []
    for price, size in values:
        p = _positive(price, "level price")
        try:
            q = Decimal(str(size))
        except (InvalidOperation, TypeError) as exc:
            raise DataError("invalid level size") from exc
        if not q.is_finite() or q < 0:
            raise DataError("invalid level size")
        output.append((p, q))
    return tuple(output)


def normalize_bybit_message(message: dict[str, Any], *, received_ms: int, market: str,
                             require_source_before_receipt: bool = True):
    """Normalize documented Bybit V5 BTCUSDT fields without inferring missing economics."""
    if market not in {"spot", "linear"}:
        raise DataError("unsupported contract market")
    topic = message.get("topic", "")
    if "ETH" in topic.upper() or any(
        isinstance(row, dict) and "ETH" in str(row.get("s", "")).upper()
        for row in (message.get("data") if isinstance(message.get("data"), list) else [message.get("data")])
    ):
        raise DataError("ETH holdout is sealed")
    if not topic.endswith(".BTCUSDT"):
        raise DataError("only BTCUSDT is supported")
    if not isinstance(received_ms, int) or received_ms < 0:
        raise DataError("invalid receipt timestamp")
    generated_ms = int(message["ts"])
    raw = dict(message)
    if topic.startswith("publicTrade."):
        rows = []
        for item in message["data"]:
            if item["s"] != "BTCUSDT" or item["S"] not in {"Buy", "Sell"}:
                raise DataError("unsupported trade symbol or side")
            event_ms = int(item["T"])
            if require_source_before_receipt and (event_ms > received_ms or generated_ms > received_ms):
                raise DataError("receipt precedes trade")
            size, price = _positive(item["v"], "trade size"), _positive(item["p"], "trade price")
            rows.append(Trade("bybit", market, "BTCUSDT", event_ms, received_ms,
                              str(item["i"]), item["S"], size, price, size * price, raw))
        return rows
    if topic.startswith("allLiquidation."):
        if market != "linear":
            raise DataError("liquidation requires linear contract")
        rows = []
        for item in message["data"]:
            if item["s"] != "BTCUSDT" or item["S"] not in {"Buy", "Sell"}:
                raise DataError("unsupported liquidation symbol or side")
            event_ms = int(item["T"])
            if require_source_before_receipt and (event_ms > received_ms or generated_ms > received_ms):
                raise DataError("receipt precedes liquidation")
            rows.append(Liquidation("bybit", market, "BTCUSDT", event_ms, received_ms,
                                    item["S"], "Sell" if item["S"] == "Buy" else "Buy",
                                    _positive(item["v"], "liquidation size"),
                                    _positive(item["p"], "bankruptcy price"), None, raw))
        return rows
    if topic.startswith("orderbook.50."):
        item = message["data"]
        if item["s"] != "BTCUSDT" or message["type"] not in {"snapshot", "delta"}:
            raise DataError("invalid orderbook message")
        if require_source_before_receipt and generated_ms > received_ms:
            raise DataError("receipt precedes orderbook event")
        return [BookUpdate("bybit", market, "BTCUSDT", generated_ms, received_ms,
                           message["type"], int(item["u"]), int(item["seq"]),
                           _levels(item["b"]), _levels(item["a"]),
                           bool(message.get("source_gap", False)), raw)]
    raise DataError("unsupported Bybit topic")


def load_btc_fixture(path: str | Path, *, mode: str = "fixture"):
    """Open only an explicitly named synthetic BTC fixture; real archives need audit."""
    if mode != "fixture":
        raise DataError("real-data mode requires audited archive and schema")
    path = Path(path)
    if "eth" in str(path).lower() or path.suffix != ".jsonl" or not path.name.startswith("btc_"):
        raise DataError("ETH holdout is sealed or path is not an explicit BTC fixture")
    with path.open(encoding="utf-8") as stream:
        header = json.loads(stream.readline())
        if header != {"kind": "fixture_manifest", "asset": "BTC", "synthetic": True}:
            raise DataError("invalid BTC fixture manifest")
        rows = []
        seen_trades: dict[tuple[str, str, str], Trade] = {}
        last_book: dict[tuple[str, str], BookUpdate] = {}
        for line in stream:
            message = json.loads(line)
            market = message.get("market", "spot" if message["topic"].startswith("publicTrade.")
                                 else "linear")
            for row in normalize_bybit_message(message, received_ms=message["received_ms"], market=market):
                if isinstance(row, Trade):
                    key = (row.venue, row.market, row.trade_id)
                    prior = seen_trades.get(key)
                    if prior:
                        if (prior.event_ms, prior.taker_side, prior.base_size, prior.price) != (
                                row.event_ms, row.taker_side, row.base_size, row.price):
                            raise DataError("conflicting duplicate trade")
                        continue
                    seen_trades[key] = row
                if isinstance(row, BookUpdate):
                    key = (row.venue, row.market)
                    prior = last_book.get(key)
                    if prior and row.kind == "delta" and (
                            row.sequence <= prior.sequence or row.update_id <= prior.update_id):
                        raise DataError("nonmonotonic book update")
                    if prior and row.kind == "snapshot" and row.sequence == prior.sequence and row.update_id == prior.update_id:
                        if (row.bids, row.asks) != (prior.bids, prior.asks):
                            raise DataError("conflicting duplicate book snapshot")
                        continue
                    last_book[key] = row
                rows.append(row)
        return rows
