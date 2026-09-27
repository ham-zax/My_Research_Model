"""Outcome-blind pre-trigger BTC response summaries for MFSM-BTC-RESPONSE-1.

This module consumes receipt-time top-50 book states and anonymous trade flow.
It does not read spot labels, liquidation prints, or any post-trigger message.
"""

from bisect import bisect_right
from collections import Counter
from decimal import Decimal

from .liquidity_state import persistent_top_bid_add_rate


ZERO = Decimal(0)
BP = Decimal(10_000)
US = 1_000_000
NS = 1_000_000_000


def _feature(eligible, numerator, denominator, exclusions, minimum):
    available = eligible >= minimum and denominator > 0
    value = numerator / denominator if available else None
    if value is not None and value.is_zero():
        value = ZERO
    return {
        "available": available,
        "eligible_bins": eligible,
        "minimum_eligible_bins": minimum,
        "value": str(value) if value is not None else None,
        "exclusion_counts": dict(sorted(exclusions.items())),
    }


def response_feature_event(states, observations, trades, *, trigger_s, protocol):
    """Calculate two descriptive coefficients using only data before ``trigger_s``.

    Book states are valued at five-second receipt cutoffs. The pressure-bin
    interval is (start, end], and the replenishment interval is (end, end+5s].
    The two coefficients may have different eligible-bin counts because
    replenishment requires additional book continuity.
    """
    history = protocol["response_history"]
    width = history["bin_seconds"]
    if (width != 5 or history["window_start_seconds_relative_to_trigger"] != -1800
            or history["window_end_seconds_relative_to_trigger"] != -5
            or history["last_eligible_pressure_bin_end_seconds_relative_to_trigger"] != -10
            or history["replenishment_end_strictly_before_trigger"] is not True):
        raise ValueError("unexpected frozen response-history boundary")
    start = trigger_s - 1800
    last_pressure_end = trigger_s - 10
    last_replenishment_end = last_pressure_end + width
    if last_replenishment_end >= trigger_s:
        raise ValueError("replenishment endpoint reaches trigger")

    # The caller may hold later rows for another event. Discard them here before
    # any matching or response calculation; never let them repair an earlier bin.
    observations = [row for row in observations
                    if row["available_ns"] <= last_replenishment_end * NS
                    and row["event_ns"] <= last_replenishment_end * NS]
    trades = [row for row in trades if row["received_us"] <= last_pressure_end * US]
    book_times = [row["event_ns"] for row in observations]
    trade_times = [row["received_us"] for row in trades]
    if book_times != sorted(book_times) or trade_times != sorted(trade_times):
        raise ValueError("response inputs are not receipt ordered")

    impact_eligible = replenishment_eligible = 0
    impact_numerator = impact_denominator = ZERO
    replenishment_numerator = replenishment_denominator = ZERO
    impact_exclusions = Counter()
    replenishment_exclusions = Counter()
    candidate_bins = 0

    for end_s in range(start + width, last_pressure_end + 1, width):
        candidate_bins += 1
        start_s = end_s - width
        replenishment_end_s = end_s + width
        if replenishment_end_s >= trigger_s:
            raise ValueError("included a trigger-time replenishment window")
        start_book, end_book = states.get(start_s), states.get(end_s)
        reason = None
        if start_book is None or end_book is None:
            reason = "book_boundary_missing"
        elif not start_book.get("top_level_valid") or not end_book.get("top_level_valid"):
            reason = "top50_book_unavailable_or_stale"
        elif start_book["book_epoch"] != end_book["book_epoch"]:
            reason = "book_epoch_changed_in_pressure_bin"
        else:
            reset_left = bisect_right(book_times, start_s * NS)
            reset_right = bisect_right(book_times, end_s * NS)
            if any(row["reset"] for row in observations[reset_left:reset_right]):
                reason = "book_reset_in_pressure_bin"
        if reason is not None:
            impact_exclusions[reason] += 1
            replenishment_exclusions[reason] += 1
            continue

        bid_depth = start_book["top_bid_notional"]
        total_depth = bid_depth + start_book["top_ask_notional"]
        start_mid, end_mid = start_book["midpoint"], end_book["midpoint"]
        if min(bid_depth, total_depth, start_mid, end_mid) <= 0:
            impact_exclusions["nonpositive_book_value"] += 1
            replenishment_exclusions["nonpositive_book_value"] += 1
            continue

        first_trade = bisect_right(trade_times, start_s * US)
        after_trade = bisect_right(trade_times, end_s * US)
        buy = sell = ZERO
        for trade in trades[first_trade:after_trade]:
            if trade["side"] == "sell":
                sell += trade["notional"]
            elif trade["side"] == "buy":
                buy += trade["notional"]
            else:
                raise ValueError("unknown aggressor side")
        q = (sell - buy) / total_depth
        if q <= 0:
            impact_exclusions["nonpositive_net_sell_pressure"] += 1
            replenishment_exclusions["nonpositive_net_sell_pressure"] += 1
            continue

        response_bps = -BP * (end_mid / start_mid).ln()
        impact_numerator += q * response_bps
        impact_denominator += q * q
        impact_eligible += 1

        replenishment_book = states.get(replenishment_end_s)
        if (replenishment_book is None
                or not replenishment_book.get("top_level_valid")):
            replenishment_exclusions["replenishment_book_unavailable_or_stale"] += 1
            continue
        if replenishment_book["book_epoch"] != start_book["book_epoch"]:
            replenishment_exclusions["book_epoch_changed_in_replenishment"] += 1
            continue
        left = bisect_right(book_times, end_s * NS) - 1
        right = bisect_right(book_times, replenishment_end_s * NS)
        window = observations[left:right] if left >= 0 else []
        addition = persistent_top_bid_add_rate(
            window, boundary_ns=replenishment_end_s * NS,
            window_seconds=width)
        if not addition["valid"]:
            replenishment_exclusions[addition["reason"]] += 1
            continue
        addition_relative = addition["persistent_bid_add_rate"] * width / bid_depth
        replenishment_numerator += q * addition_relative
        replenishment_denominator += q * q
        replenishment_eligible += 1

    impact_minimum = protocol["response_measurements"]["pretrigger_sell_impact_beta_5s"]["minimum_eligible_bins"]
    replenish_minimum = protocol["response_measurements"]["pretrigger_bid_replenishment_beta_5s"]["minimum_eligible_bins"]
    return {
        "trigger_s": trigger_s,
        "candidate_bins": candidate_bins,
        "last_pressure_bin_end_s": last_pressure_end,
        "last_replenishment_end_s": last_replenishment_end,
        "pretrigger_sell_impact_beta_5s": _feature(
            impact_eligible, impact_numerator, impact_denominator,
            impact_exclusions, impact_minimum),
        "pretrigger_bid_replenishment_beta_5s": _feature(
            replenishment_eligible, replenishment_numerator,
            replenishment_denominator, replenishment_exclusions,
            replenish_minimum),
        "trade_sequence_certified": False,
        "model_ready": False,
    }
