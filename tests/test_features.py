from decimal import Decimal

from mfsm_e001.data import BookUpdate, Liquidation, Trade
from mfsm_e001.features import (capacity_features, neutral_trade_windows,
                                 persistent_bid_additions, pre_event_depth_median,
                                 split_feature_sets)


def book(ms, kind, bids, asks=((Decimal("100.1"), Decimal("1")),), gap=False, update_id=None):
    return BookUpdate("bybit", "linear", "BTCUSDT", ms, ms, kind,
                      update_id if update_id is not None else ms, ms,
                      tuple((Decimal(str(p)), Decimal(str(q))) for p, q in bids),
                      tuple((Decimal(str(p)), Decimal(str(q))) for p, q in asks), gap, {})


def test_persistent_addition_uses_full_fifteen_second_denominator():
    updates = [book(0, "snapshot", [(100, 0)]),
               book(2000, "delta", [(100, 2)]),
               book(4000, "delta", [], update_id=4000)]
    assert persistent_bid_additions(updates, decision_ms=15000) == Decimal("200") / 15


def test_reduction_during_dwell_offsets_added_cohort():
    updates = [book(0, "snapshot", [(100, 0)]),
               book(2000, "delta", [(100, 2)]),
               book(2500, "delta", [(100, 1)])]
    assert persistent_bid_additions(updates, decision_ms=15000) == Decimal("100") / 15


def test_late_addition_cannot_mature():
    updates = [book(0, "snapshot", [(100, 0)]), book(14500, "delta", [(100, 2)])]
    assert persistent_bid_additions(updates, decision_ms=15000) == 0


def test_disappearing_level_counts_as_reduction_and_gap_marks_missing():
    normal = [book(0, "snapshot", [(100, 0)]), book(2000, "delta", [(100, 2)]),
              book(2500, "delta", [(100, 0)])]
    assert persistent_bid_additions(normal, decision_ms=15000) == 0
    gapped = [normal[0], normal[1], book(2500, "delta", [(100, 0)], gap=True)]
    assert persistent_bid_additions(gapped, decision_ms=15000) is None


def test_explicit_book_gap_invalidates_current_depth_until_snapshot():
    updates = [book(0, "snapshot", [(100, 1)]),
               book(2000, "delta", [(100, 2)], gap=True)]
    result = capacity_features(updates, decision_ms=15000,
                               pre_depth_median=Decimal("100"),
                               aggressive_sell_notional=Decimal("50"),
                               liquidation_sell_notional=None)
    assert result["visible_bid_depth"] is None
    assert result["capacity_proxy"] is None


def test_snapshot_reset_during_dwell_marks_missing():
    updates = [book(0, "snapshot", [(100, 0)]), book(2000, "delta", [(100, 2)]),
               book(2500, "snapshot", [(100, 2)])]
    assert persistent_bid_additions(updates, decision_ms=15000) is None


def test_future_update_cannot_change_decision_features():
    updates = [book(0, "snapshot", [(100, 1)]), book(2000, "delta", [(100, 2)])]
    future = book(16000, "delta", [(100, 0)])
    assert persistent_bid_additions(updates, decision_ms=15000) == persistent_bid_additions(
        updates + [future], decision_ms=15000)


def test_capacity_floor_and_same_information_base():
    updates = [book(0, "snapshot", [(100, 1)]), book(2000, "delta", [(100, 2)])]
    base = capacity_features(updates, decision_ms=15000,
                             pre_depth_median=Decimal("10000"),
                             aggressive_sell_notional=Decimal("50"),
                             liquidation_sell_notional=None)
    assert base["visible_bid_depth"] == Decimal("200")
    assert base["replenishment_rate"] == Decimal("100") / 15
    assert base["capacity_floor"] == Decimal("100")
    assert base["liquidation_notional"] is None
    b4, mfsm = split_feature_sets(base)
    assert all(b4[key] == mfsm[key] for key in b4)
    assert mfsm["sell_pressure_ratio"] == Decimal("50") / base["capacity_proxy"]
    assert mfsm["liquidation_pressure_ratio"] is None


def test_zero_pre_event_depth_keeps_ratios_unavailable():
    base = capacity_features([book(0, "snapshot", [(100, 1)])], decision_ms=15000,
                             pre_depth_median=Decimal("0"),
                             aggressive_sell_notional=Decimal("50"),
                             liquidation_sell_notional=None)
    assert base["capacity_proxy"] is None
    assert split_feature_sets(base)[1]["sell_pressure_ratio"] is None


def test_repeated_quotes_can_overstate_future_capacity_without_actual_future_flow():
    updates = [book(0, "snapshot", [(99, 1)])]
    for ms in (1000, 4000, 7000, 10000):
        updates.extend([book(ms, "delta", [(100, 1)]), book(ms + 1500, "delta", [(100, 0)])])
    result = capacity_features(updates, decision_ms=15000, pre_depth_median=Decimal("100"),
                               aggressive_sell_notional=Decimal("0"),
                               liquidation_sell_notional=None)
    assert result["visible_bid_depth"] == 0
    assert result["replenishment_rate"] == Decimal("400") / 15
    assert result["capacity_proxy"] > 0


def test_pretrigger_median_uses_exact_thirty_minute_grid():
    updates = [book(0, "snapshot", [(100, 1)]),
               book(900000, "delta", [(100, 2)])]
    assert pre_event_depth_median(updates, trigger_ms=1800000) == Decimal("150")


def test_pretrigger_median_rejects_gap_even_after_book_recovery():
    updates = [book(0, "snapshot", [(100, 1)]),
               book(10000, "delta", [(100, 2)], gap=True),
               book(11000, "snapshot", [(100, 1)])]
    assert pre_event_depth_median(updates, trigger_ms=1800000) is None


def test_pretrigger_median_accepts_recovered_gap_before_window():
    updates = [book(-20000, "snapshot", [(100, 1)]),
               book(-10000, "delta", [(100, 2)], gap=True),
               book(-9000, "snapshot", [(100, 1)]),
               book(900000, "delta", [(100, 2)])]
    assert pre_event_depth_median(updates, trigger_ms=1800000) == Decimal("150")


def test_neutral_trade_windows_respect_arrival_and_left_open_interval():
    def trade(event, received, ident):
        return Trade("bybit", "linear", "BTCUSDT", event, received, ident, "Sell",
                     Decimal("1"), Decimal("100"), Decimal("100"), {})

    rows = [trade(0, 0, "left"), trade(1, 1, "valid"),
            trade(29000, 31000, "late"), trade(30000, 30000, "edge"),
            trade(30001, 30001, "future")]
    liq = Liquidation("bybit", "linear", "BTCUSDT", 29000, 29000, "Buy", "Sell",
                      Decimal("2"), Decimal("90"), None, {})
    result = neutral_trade_windows(rows, [liq], decision_ms=30000)
    assert result["aggressive_sell_notional_30s"] == Decimal("200")
    assert result["aggressive_sell_notional_1s"] == Decimal("100")
    assert result["liquidation_sell_size_base_30s"] == Decimal("2")
    assert result["liquidation_sell_notional_30s"] is None
    assert result["aggressive_sell_may_include_liquidations"] is True
