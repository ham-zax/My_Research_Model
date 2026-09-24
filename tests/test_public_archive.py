import gzip
import io
import zipfile
from decimal import Decimal

import pytest

from mfsm_e001.data import DataError
from mfsm_e001.public_archive import (
    audit_tardis_csv_gzip,
    read_binance_spot_zip,
    read_bybit_spot_gzip,
)


def test_binance_trade_archive_preserves_event_time_without_inventing_receipt(tmp_path):
    target = tmp_path / "btc_binance.zip"
    with zipfile.ZipFile(target, "w") as z:
        z.writestr("BTCUSDT-trades-2023-10-01.csv",
                   "3224361464,26962.57,0.00361,97.3348777,1696118400000,False,True\n")
    rows = list(read_binance_spot_zip(target))
    assert len(rows) == 1
    assert (rows[0].venue, rows[0].event_ms, rows[0].price, rows[0].received_ms) == (
        "binance", 1696118400000, Decimal("26962.57"), None)


def test_bybit_trade_archive_parses_header_and_retains_unknown_receipt(tmp_path):
    target = tmp_path / "btc_bybit.csv.gz"
    with gzip.open(target, "wt") as stream:
        stream.write("id,timestamp,price,volume,side\n")
        stream.write("1,1696118403019,26965.24,0.000055,buy\n")
    rows = list(read_bybit_spot_gzip(target))
    assert len(rows) == 1
    assert (rows[0].venue, rows[0].event_ms, rows[0].price, rows[0].received_ms) == (
        "bybit", 1696118403019, Decimal("26965.24"), None)


def test_unmarked_archive_path_is_rejected_before_open(tmp_path):
    path = tmp_path / "unmarked.csv.gz"
    path.write_bytes(b"not a gzip archive")
    with pytest.raises(DataError, match="BTC"):
        list(read_bybit_spot_gzip(path))


def test_tardis_trade_audit_preserves_local_timestamp_receipt(tmp_path):
    target = tmp_path / "btc_tardis_bybit_spot_trades.csv.gz"
    with gzip.open(target, "wt") as stream:
        stream.write("exchange,symbol,timestamp,local_timestamp,id,side,price,amount\n")
        stream.write("bybit-spot,BTCUSDT,1677628800000000,1677628800004201,abc,buy,23100.5,0.01\n")
        stream.write("bybit-spot,BTCUSDT,1677628801000000,1677628801003100,def,sell,23101,0.02\n")

    summary = audit_tardis_csv_gzip(
        target,
        data_type="trades",
        expected_exchange="bybit-spot",
        expected_symbol="BTCUSDT",
    )

    assert summary["records"] == 2
    assert summary["has_receipt_times"] is True
    assert summary["timestamp_unit"] == "microseconds"
    assert summary["first_event_us"] == 1677628800000000
    assert summary["first_local_us"] == 1677628800004201
    assert summary["last_local_us"] == 1677628801003100


def test_tardis_audit_rejects_non_btc_rows(tmp_path):
    target = tmp_path / "btc_tardis_mixed.csv.gz"
    with gzip.open(target, "wt") as stream:
        stream.write("exchange,symbol,timestamp,local_timestamp,id,side,price,amount\n")
        stream.write("bybit-spot,ETHUSDT,1677628800000000,1677628800004201,abc,buy,1600,0.1\n")

    with pytest.raises(DataError, match="ETH holdout"):
        audit_tardis_csv_gzip(
            target,
            data_type="trades",
            expected_exchange="bybit-spot",
            expected_symbol="BTCUSDT",
        )
