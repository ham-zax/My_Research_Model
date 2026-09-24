import json
from decimal import Decimal

import pytest

from mfsm_e001.data import DataError, load_btc_fixture, normalize_bybit_message


def test_bybit_liquidation_buy_means_sell_pressure_without_executed_notional():
    message = {
        "topic": "allLiquidation.BTCUSDT", "type": "snapshot", "ts": 1005,
        "data": [{"T": 1000, "s": "BTCUSDT", "S": "Buy", "v": "0.2", "p": "90000"}],
    }
    row = normalize_bybit_message(message, received_ms=1010, market="linear")[0]
    assert row.position_side == "Buy"
    assert row.pressure_side == "Sell"
    assert row.base_size == Decimal("0.2")
    assert row.bankruptcy_price == Decimal("90000")
    assert row.executed_notional is None


def test_bybit_trade_uses_taker_side_and_linear_base_units():
    message = {
        "topic": "publicTrade.BTCUSDT", "type": "snapshot", "ts": 1010,
        "data": [{"T": 1000, "s": "BTCUSDT", "S": "Sell", "v": "0.2", "p": "90000", "i": "trade-1"}],
    }
    row = normalize_bybit_message(message, received_ms=1012, market="linear")[0]
    assert row.taker_side == "Sell"
    assert row.base_size == Decimal("0.2")
    assert row.notional_quote == Decimal("18000")
    assert row.received_ms == 1012


def test_real_or_eth_path_rejected_before_file_read(tmp_path):
    eth = tmp_path / "eth_history.jsonl"
    eth.write_text("not valid json\n")
    with pytest.raises(DataError, match="sealed"):
        load_btc_fixture(eth)
    with pytest.raises(DataError, match="real-data"):
        load_btc_fixture(tmp_path / "btc_missing.jsonl", mode="real")


def test_duplicate_trade_is_deduplicated_but_conflict_is_rejected(tmp_path):
    path = tmp_path / "btc_trades.jsonl"
    header = {"kind": "fixture_manifest", "asset": "BTC", "synthetic": True}
    trade = {"topic": "publicTrade.BTCUSDT", "type": "snapshot", "ts": 1010,
             "received_ms": 1011,
             "data": [{"T": 1000, "s": "BTCUSDT", "S": "Sell", "v": "0.2", "p": "90000", "i": "one"}]}
    path.write_text("\n".join(map(json.dumps, [header, trade, trade])) + "\n")
    assert len(load_btc_fixture(path)) == 1
    altered = {**trade, "data": [{**trade["data"][0], "p": "91000"}]}
    path.write_text("\n".join(map(json.dumps, [header, trade, altered])) + "\n")
    with pytest.raises(DataError, match="conflicting duplicate"):
        load_btc_fixture(path)


def test_book_reset_and_explicit_gap_are_preserved(tmp_path):
    path = tmp_path / "btc_books.jsonl"
    header = {"kind": "fixture_manifest", "asset": "BTC", "synthetic": True}
    snap = {"topic": "orderbook.50.BTCUSDT", "type": "snapshot", "ts": 1000,
            "received_ms": 1001,
            "data": {"s": "BTCUSDT", "u": 10, "seq": 10, "b": [["100", "1"]], "a": [["101", "1"]]}}
    delta = {"topic": "orderbook.50.BTCUSDT", "type": "delta", "ts": 1100,
             "received_ms": 1101, "source_gap": True,
             "data": {"s": "BTCUSDT", "u": 11, "seq": 11, "b": [["100", "2"]], "a": []}}
    path.write_text("\n".join(map(json.dumps, [header, snap, delta])) + "\n")
    rows = load_btc_fixture(path)
    assert rows[0].kind == "snapshot"
    assert rows[1].source_gap is True
    assert rows[1].kind == "delta"


def test_messages_received_after_event_are_retained_with_availability_time():
    msg = {"topic": "publicTrade.BTCUSDT", "type": "snapshot", "ts": 1000,
           "data": [{"T": 999, "s": "BTCUSDT", "S": "Buy", "v": "1", "p": "100", "i": "late"}]}
    row = normalize_bybit_message(msg, received_ms=2000, market="spot")[0]
    assert row.event_ms == 999
    assert row.received_ms == 2000


def test_fixture_market_metadata_preserves_linear_trade_contract(tmp_path):
    path = tmp_path / "btc_linear.jsonl"
    header = {"kind": "fixture_manifest", "asset": "BTC", "synthetic": True}
    trade = {"topic": "publicTrade.BTCUSDT", "market": "linear", "type": "snapshot",
             "ts": 1010, "received_ms": 1011,
             "data": [{"T": 1000, "s": "BTCUSDT", "S": "Sell", "v": "0.2",
                       "p": "90000", "i": "linear-one"}]}
    path.write_text("\n".join(map(json.dumps, [header, trade])) + "\n")
    assert load_btc_fixture(path)[0].market == "linear"
