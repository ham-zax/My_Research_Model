from decimal import Decimal

from mfsm_e001.events import CompositePoint, Event
from mfsm_e001.labels import label_event


def path(after=None, gap=None):
    rows = [CompositePoint(s, Decimal("100"), s * 1000) for s in range(0, 1817)]
    if after:
        for second, price in after.items():
            rows[second] = CompositePoint(second, Decimal(str(price)), second * 1000)
    if gap:
        rows[gap] = CompositePoint(gap, None, gap * 1000)
    return rows


def event():
    return Event(1, 16, True, "accepted")


def test_downside_hit_before_recovery_is_one():
    result = label_event(path({17: "98.9", 18: "101"}), event(), horizon_s=1800)
    assert (result.valid, result.value, result.state, result.first_hit_s) == (
        True, 1, "downside-first", 17)


def test_recovery_first_is_zero():
    result = label_event(path({17: "100.8", 18: "98"}), event(), horizon_s=1800)
    assert (result.valid, result.value, result.state) == (True, 0, "recovery-first")


def test_unresolved_is_zero_but_not_exhaustion():
    result = label_event(path(), event(), horizon_s=1800)
    assert (result.valid, result.value, result.state) == (True, 0, "neither-by-horizon")


def test_missing_before_hit_makes_label_unavailable():
    result = label_event(path({19: "98.9"}, gap=18), event(), horizon_s=1800)
    assert (result.valid, result.value, result.reason) == (False, None, "missing_price_before_hit")


def test_gap_after_first_hit_does_not_invalidate_label():
    result = label_event(path({17: "98.9"}, gap=18), event(), horizon_s=1800)
    assert (result.valid, result.value, result.first_hit_s) == (True, 1, 17)


def test_missing_decision_price_is_unavailable():
    result = label_event(path(gap=16), event(), horizon_s=1800)
    assert (result.valid, result.reason) == (False, "missing_decision_price")


def test_label_availability_is_no_earlier_than_grid_hit_or_horizon():
    early_receipts = [CompositePoint(s, Decimal("100"), s * 1000 - 500)
                      for s in range(1817)]
    early_receipts[17] = CompositePoint(17, Decimal("98.9"), 16500)
    hit = label_event(early_receipts, event(), horizon_s=1800)
    assert hit.available_ms == 17000
    early_receipts[17] = CompositePoint(17, Decimal("100"), 16500)
    neither = label_event(early_receipts, event(), horizon_s=1800)
    assert neither.available_ms == 1816000
