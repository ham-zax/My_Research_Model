"""Read verified public spot archives for coverage inspection, not live backtests."""

import csv
from dataclasses import dataclass
from decimal import Decimal
import gzip
import hashlib
from pathlib import Path
import zipfile

from .data import DataError


@dataclass(frozen=True)
class ArchiveTrade:
    venue: str
    event_ms: int
    price: Decimal
    base_size: Decimal
    trade_id: str
    raw_side: str | None
    received_ms: None = None


def _check_btc(path: Path):
    if "eth" in str(path).lower():
        raise DataError("ETH holdout is sealed")
    if "btc" not in path.name.lower():
        raise DataError("explicit BTC archive filename required")
    if not path.is_file():
        raise DataError("explicit BTC archive file required")


def read_binance_spot_zip(path: str | Path):
    """Binance official daily spot trades CSV; 2025+ microsecond timestamps normalized."""
    path = Path(path)
    _check_btc(path)
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".csv")]
        if len(names) != 1 or "BTCUSDT" not in names[0]:
            raise DataError("expected one BTCUSDT spot trade CSV")
        with archive.open(names[0]) as stream:
            for raw_line in stream:
                row = next(csv.reader([raw_line.decode("utf-8")]))
                if len(row) < 7:
                    raise DataError("invalid Binance trade row")
                raw_ms = int(row[4])
                event_ms = raw_ms // 1000 if raw_ms >= 100_000_000_000_000 else raw_ms
                yield ArchiveTrade("binance", event_ms, Decimal(row[1]), Decimal(row[2]),
                                   row[0], row[5])


def read_bybit_spot_gzip(path: str | Path):
    """Bybit public daily spot CSV; retain side as unverified archive metadata."""
    path = Path(path)
    _check_btc(path)
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"id", "timestamp", "price", "volume", "side"}.issubset(reader.fieldnames or []):
            raise DataError("invalid Bybit spot trade columns")
        for row in reader:
            yield ArchiveTrade("bybit", int(row["timestamp"]), Decimal(row["price"]),
                               Decimal(row["volume"]), row["id"], row["side"])


_TARDIS_REQUIRED_COLUMNS = {
    "trades": {"exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"},
    "incremental_book_L2": {"exchange", "symbol", "timestamp", "local_timestamp", "is_snapshot", "side", "price", "amount"},
    "derivative_ticker": {
        "exchange", "symbol", "timestamp", "local_timestamp", "funding_timestamp",
        "funding_rate", "predicted_funding_rate", "open_interest", "last_price",
        "index_price", "mark_price",
    },
    "liquidations": {"exchange", "symbol", "timestamp", "local_timestamp", "id", "side", "price", "amount"},
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_tardis_csv_gzip(
    path: str | Path,
    *,
    data_type: str,
    expected_exchange: str,
    expected_symbol: str = "BTCUSDT",
) -> dict:
    """Summarize a Tardis normalized CSV file while preserving local receipt time."""
    path = Path(path)
    _check_btc(path)
    required = _TARDIS_REQUIRED_COLUMNS.get(data_type)
    if required is None:
        raise DataError("unsupported Tardis data type")
    if expected_symbol != "BTCUSDT" or "eth" in expected_exchange.lower():
        raise DataError("ETH holdout is sealed")
    if path.suffix != ".gz":
        raise DataError("Tardis CSV input must be gzip compressed")

    records = 0
    first_event_us = None
    last_event_us = None
    first_local_us = None
    last_local_us = None
    sides: set[str] = set()

    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = set(reader.fieldnames or [])
        if not required.issubset(fieldnames):
            raise DataError("invalid Tardis CSV columns")
        for row in reader:
            exchange = row["exchange"]
            symbol = row["symbol"]
            if "ETH" in symbol.upper():
                raise DataError("ETH holdout is sealed")
            if exchange != expected_exchange or symbol != expected_symbol:
                raise DataError("unexpected Tardis exchange or symbol")
            event_us = int(row["timestamp"])
            local_us = int(row["local_timestamp"])
            if event_us < 0 or local_us < 0:
                raise DataError("invalid Tardis timestamp")
            if event_us > local_us:
                raise DataError("local timestamp precedes exchange timestamp")
            records += 1
            first_event_us = event_us if first_event_us is None else min(first_event_us, event_us)
            last_event_us = event_us if last_event_us is None else max(last_event_us, event_us)
            first_local_us = local_us if first_local_us is None else min(first_local_us, local_us)
            last_local_us = local_us if last_local_us is None else max(last_local_us, local_us)
            if "side" in row and row["side"]:
                sides.add(row["side"])

    return {
        "path": str(path),
        "sha256": _sha256(path),
        "provider": "tardis",
        "exchange": expected_exchange,
        "symbol": expected_symbol,
        "data_type": data_type,
        "records": records,
        "columns": sorted(required),
        "timestamp_unit": "microseconds",
        "has_receipt_times": True,
        "receipt_field": "local_timestamp",
        "first_event_us": first_event_us,
        "last_event_us": last_event_us,
        "first_local_us": first_local_us,
        "last_local_us": last_local_us,
        "sides": sorted(sides),
    }
