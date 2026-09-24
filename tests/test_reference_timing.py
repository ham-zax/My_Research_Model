"""Check the buyer/deadline mechanism behind MFSM-RE-TIME-1."""

import pytest

from mfsm_reference.economy import Account, Parameters, State, headroom, step


def initial_state():
    return State(Account(0, 10), Account(0, 1), Account(1000, 0), debt=740)


def law(delay, *, buyer_speed=200, value=98):
    return Parameters(value=value, impact=0.01, inventory_limit=20,
                      maintenance=0.25, restore=0.30, buyer_speed=buyer_speed,
                      delay=delay, deadline=2)


def test_buyer_can_fund_dealer_before_deadline_but_late_buyer_cannot():
    initial = initial_state()
    assert headroom(initial, law(0, value=100)) > 0
    assert headroom(initial, law(0)) < 0

    fast = step(initial, law(0))
    assert fast.buyer_purchase == pytest.approx(1)
    assert fast.forced_sale > 0
    assert fast.state.mode == "NORMAL"
    assert headroom(fast.state, law(0)) > 0
    assert sum(x.cash for x in (fast.state.holder, fast.state.dealer,
                                fast.state.buyer)) == pytest.approx(1000)
    assert sum(x.units for x in (fast.state.holder, fast.state.dealer,
                                 fast.state.buyer)) == pytest.approx(11)

    one_lag = step(initial, law(1))
    assert one_lag.buyer_purchase == 0
    assert one_lag.state.mode == "MARGIN"
    one_lag_next = step(one_lag.state, law(1))
    assert one_lag_next.buyer_purchase == pytest.approx(1)
    assert one_lag_next.state.mode == "NORMAL"

    too_late = step(initial, law(2))
    assert too_late.state.mode == "MARGIN"
    failure = step(too_late.state, law(2))
    assert failure.state.mode == "MARGIN_FAILURE"
    assert failure.buyer_purchase == 0
    absorbed = step(failure.state, law(2))
    assert absorbed.state == failure.state
    assert absorbed.buyer_purchase == 0


def test_without_buying_the_initially_cashless_dealer_cannot_fill_holder_order():
    state = initial_state()
    no_buyer = law(0, buyer_speed=0)
    first = step(state, no_buyer)
    second = step(first.state, no_buyer)
    assert first.forced_sale == second.forced_sale == 0
    assert second.state.mode == "MARGIN_FAILURE"
