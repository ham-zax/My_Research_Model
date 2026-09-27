"""Causal boundaries and availability for the two BTC response summaries."""

from decimal import Decimal
import json
from pathlib import Path

from mfsm_e001.response_features import response_feature_event


D = Decimal
US = 1_000_000
NS = 1_000_000_000
PROTOCOL = json.loads(
    (Path(__file__).resolve().parents[1]
     / "experiments/mfsm_btc_response_001_protocol.json").read_text()
)


def inputs(trigger=2000):
    first, last = trigger - 1800, trigger - 5
    states = {
        second: {
            "top_level_valid": True, "book_epoch": 1,
            "top_bid_notional": D("1000"),
            "top_ask_notional": D("1000"), "midpoint": D("100"),
        }
        for second in range(first, last + 1, 5)
    }
    observations = [
        {
            "event_ns": second * NS, "available_ns": second * NS,
            "book_epoch": 1, "reset": False, "top_level_valid": True,
            "bid_changes_known": True, "changes": [],
            "top_bid_prices": (D("100"),),
        }
        for second in range(first, last + 1)
    ]
    trades = [
        {"received_us": (first + (index + 1) * 5) * US,
         "side": "sell", "notional": D("100")}
        for index in range(35)
    ]
    return states, observations, trades


def calculate(states, observations, trades, *, trigger=2000):
    return response_feature_event(
        states, observations, trades, trigger_s=trigger, protocol=PROTOCOL)


def test_thirty_five_sell_bins_make_both_zero_response_summaries_available():
    result = calculate(*inputs())
    impact = result["pretrigger_sell_impact_beta_5s"]
    replenish = result["pretrigger_bid_replenishment_beta_5s"]
    assert result["candidate_bins"] == 358
    assert result["last_pressure_bin_end_s"] == 1990
    assert result["last_replenishment_end_s"] == 1995
    assert impact["eligible_bins"] == replenish["eligible_bins"] == 35
    assert impact["available"] and replenish["available"]
    assert impact["value"] == replenish["value"] == "0"
    assert result["model_ready"] is False
    assert result["trade_sequence_certified"] is False


def test_final_pressure_bin_and_trigger_time_rows_do_not_enter_features():
    states, observations, trades = inputs()
    original = calculate(states, observations, trades)
    trades.extend([
        {"received_us": 1995 * US, "side": "sell", "notional": D("1000000")},
        {"received_us": 2000 * US, "side": "sell", "notional": D("1000000")},
    ])
    observations.append({
        "event_ns": 2000 * NS, "available_ns": 2000 * NS,
        "book_epoch": 2, "reset": True, "top_level_valid": True,
        "bid_changes_known": True, "changes": [("bid", D("100"), D("100"))],
        "top_bid_prices": (D("100"),),
    })
    states[2000] = {**states[1995], "midpoint": D("50"), "book_epoch": 2}
    assert calculate(states, observations, trades) == original


def test_persistent_addition_uses_next_five_seconds_and_requires_dwell():
    states, observations, trades = inputs()
    first_pressure_end = 205
    for row in observations:
        if row["event_ns"] == (first_pressure_end + 1) * NS:
            row["changes"] = [("bid", D("100"), D("0.5"))]
    result = calculate(states, observations, trades)
    replenish = result["pretrigger_bid_replenishment_beta_5s"]
    assert replenish["available"]
    assert D(replenish["value"]) == D("0.05") / (35 * D("0.05"))


def test_pressure_bin_reset_excludes_that_bin_without_future_repair():
    states, observations, trades = inputs()
    for second, state in states.items():
        if second >= 205:
            state["book_epoch"] = 2
    for row in observations:
        if row["event_ns"] >= 205 * NS:
            row["book_epoch"] = 2
            row["reset"] = row["event_ns"] == 205 * NS
    result = calculate(states, observations, trades)
    assert result["pretrigger_sell_impact_beta_5s"]["eligible_bins"] == 34
    assert result["pretrigger_sell_impact_beta_5s"]["exclusion_counts"][
        "book_epoch_changed_in_pressure_bin"] == 1
