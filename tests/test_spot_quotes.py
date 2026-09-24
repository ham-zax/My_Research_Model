import csv
from decimal import Decimal
import gzip
import pytest

from mfsm_e001.spot_quotes import iter_quote_grid, quote_composite


def quote_file(tmp_path, exchange, rows):
    path = tmp_path / f"{exchange}_quotes_BTCUSDT.csv.gz"
    with gzip.open(path, "wt", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["exchange", "symbol", "timestamp", "local_timestamp",
                         "bid_price", "ask_price", "bid_amount", "ask_amount"])
        for row in rows:
            writer.writerow([exchange, "BTCUSDT", *row])
    return path


def test_quote_receipt_microseconds_and_five_second_expiry(tmp_path):
    a = quote_file(tmp_path, "binance", [(1_000_000, 2_000_001, 99, 101, 1, 1)])
    b = quote_file(tmp_path, "bybit-spot", [(1_000_000, 1_100_000, 101, 103, 1, 1)])
    points = [quote_composite(row) for row in iter_quote_grid(a, b, start_s=2, end_s=7)]
    assert points[0].price is None  # arrives one microsecond after the grid boundary
    assert points[1].price == Decimal("101")
    assert points[4].price == Decimal("101")  # exactly five seconds old
    assert points[5].price is None


def test_invalid_new_quote_does_not_resurrect_previous_good_quote(tmp_path):
    a = quote_file(tmp_path, "binance", [(1_000_000, 1_000_000, 99, 101, 1, 1),
                                          (2_000_000, 2_000_000, 102, 101, 1, 1)])
    b = quote_file(tmp_path, "bybit-spot", [(1_000_000, 1_000_000, 101, 103, 1, 1)])
    grid = list(iter_quote_grid(a, b, start_s=1, end_s=2))
    assert quote_composite(grid[0]).price == Decimal("101")
    assert quote_composite(grid[1]).price is None
    assert grid[1].binance.invalid_reason == "crossed_or_locked_quote"


def test_quote_capture_order_wins_over_exchange_timestamp_order(tmp_path):
    a = quote_file(tmp_path, "binance", [(1_500_000, 1_600_000, 99, 101, 1, 1),
                                          (1_400_000, 1_700_000, 109, 111, 1, 1)])
    b = quote_file(tmp_path, "bybit-spot", [(1_000_000, 1_000_000, 99, 101, 1, 1)])
    row = next(iter_quote_grid(a, b, start_s=2, end_s=2))
    assert quote_composite(row).price == Decimal("105")


@pytest.mark.parametrize("bid,ask,bid_size", [(99, 101, 0), ("", 101, 1), ("NaN", 101, 1)])
def test_missing_or_zero_size_side_is_not_a_valid_midpoint(tmp_path, bid, ask, bid_size):
    a = quote_file(tmp_path, "binance", [(1_000_000, 1_000_000, bid, ask, bid_size, 1)])
    b = quote_file(tmp_path, "bybit-spot", [(1_000_000, 1_000_000, 99, 101, 1, 1)])
    row = next(iter_quote_grid(a, b, start_s=1, end_s=1))
    assert quote_composite(row).price is None


def test_appending_unavailable_quote_cannot_change_earlier_composite(tmp_path):
    a = quote_file(tmp_path, "binance", [(1_000_000, 1_000_000, 99, 101, 1, 1)])
    b = quote_file(tmp_path, "bybit-spot", [(1_000_000, 1_000_000, 99, 101, 1, 1)])
    before = quote_composite(next(iter_quote_grid(a, b, start_s=2, end_s=2)))
    a = quote_file(tmp_path, "binance", [(1_000_000, 1_000_000, 99, 101, 1, 1),
                                          (1_900_000, 2_000_001, 49, 51, 1, 1)])
    after = quote_composite(next(iter_quote_grid(a, b, start_s=2, end_s=2)))
    assert before == after
