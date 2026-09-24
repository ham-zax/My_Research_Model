import csv
from decimal import Decimal
import gzip

import pytest

from mfsm_e001.events import CompositePoint
from mfsm_e001.tardis_spot import build_tardis_spot_composite, read_tardis_spot_trades


def write_trades(path, exchange, rows):
    with gzip.open(path, "wt", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["exchange", "symbol", "timestamp", "local_timestamp", "id",
                         "side", "price", "amount"])
        for index, (event_us, local_us, price) in enumerate(rows):
            writer.writerow([exchange, "BTCUSDT", event_us, local_us, index,
                             "buy", price, "0.1"])


def test_spot_reader_ceil_receipt_time_to_prevent_submillisecond_lookahead(tmp_path):
    path = tmp_path / "binance_trades_2025-03-01_BTCUSDT.csv.gz"
    write_trades(path, "binance", [(1_000_001, 2_000_001, "100")])
    tick = next(read_tardis_spot_trades(path, exchange="binance"))
    assert tick.event_ms == 1000
    assert tick.received_ms == 2001
    assert tick.price == Decimal("100")


def test_two_source_composite_uses_only_arrived_fresh_trades(tmp_path):
    binance = tmp_path / "binance_trades_2025-03-01_BTCUSDT.csv.gz"
    bybit = tmp_path / "bybit-spot_trades_2025-03-01_BTCUSDT.csv.gz"
    write_trades(binance, "binance", [(1_000_000, 1_010_000, "100"),
                                      (2_000_000, 2_000_001, "90")])
    write_trades(bybit, "bybit-spot", [(1_000_000, 1_020_000, "104")])
    points = build_tardis_spot_composite(binance, bybit, start_s=1, end_s=3)
    assert points == [CompositePoint(1, None, None),
                      CompositePoint(2, Decimal("102"), 1020),
                      CompositePoint(3, None, None)]


def test_reader_rejects_eth_path_before_open(tmp_path):
    path = tmp_path / "ETH_data.csv.gz"
    path.write_bytes(b"not gzip")
    with pytest.raises(ValueError, match="ETH"):
        list(read_tardis_spot_trades(path, exchange="binance"))
