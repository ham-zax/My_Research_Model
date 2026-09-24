"""Economic invariants and limiting cases of the theoretical reference member."""

from dataclasses import replace
import importlib
from math import exp

import pytest


@pytest.fixture
def economy():
    # A missing implementation is an explicit red result, not a collection error.
    assert importlib.util.find_spec("mfsm_reference") is not None, "reference economy missing"
    return importlib.import_module("mfsm_reference.economy")


def initial(e, **changes):
    fields = dict(
        holder=e.Account(0.0, 10.0), dealer=e.Account(1000.0, 0.0),
        buyer=e.Account(1000.0, 0.0), debt=750.0,
    )
    fields.update(changes)
    return e.State(**fields)


def params(e, **changes):
    fields = dict(value=98.0, impact=0.01, inventory_limit=20.0,
                  maintenance=0.25, restore=0.30, buyer_speed=20.0,
                  delay=2, deadline=10)
    fields.update(changes)
    return e.Parameters(**fields)


def test_no_impact_funded_sale_reaches_restoration_target(economy):
    e = economy
    p = params(e, impact=0)
    result = e.step(initial(e), p)
    assert result.forced_sale == pytest.approx(320 / 147)
    assert result.state.holder.cash == pytest.approx(640 / 3)
    assert e.headroom(result.state, p) == pytest.approx(115 / 3)
    assert result.state.mode == "NORMAL"
    assert result.state.breach_ticks == 0


@pytest.mark.parametrize("impact", [0.0, 1e-10, 0.01, 0.08])
def test_paths_conserve_cash_shares_and_never_create_borrowing(economy, impact):
    e = economy
    p = params(e, impact=impact)
    state = initial(e)
    sold = 0.0
    for _ in range(30):
        result = e.step(state, p)
        state = result.state
        sold += result.forced_sale
        accounts = (state.holder, state.dealer, state.buyer)
        assert sum(a.cash for a in accounts) == pytest.approx(2000.0, abs=1e-8)
        assert sum(a.units for a in accounts) == pytest.approx(10.0, abs=1e-10)
        assert all(a.cash >= 0 and a.units >= 0 for a in accounts)
        assert state.dealer.units <= p.inventory_limit
        assert sold <= 10.0 + 1e-10
        assert state.debt == 750.0


def test_dealer_cash_and_inventory_are_binding_constraints(economy):
    e = economy
    cash_limited = e.step(initial(e, dealer=e.Account(10.0, 0.0)), params(e))
    assert cash_limited.state.holder.cash == pytest.approx(10.0)
    assert cash_limited.state.dealer.cash == pytest.approx(0.0, abs=1e-10)
    assert cash_limited.state.mode == "MARGIN"
    inventory_limited = e.step(initial(e), params(e, inventory_limit=0.05))
    assert inventory_limited.forced_sale == pytest.approx(0.05)
    assert inventory_limited.state.dealer.units == pytest.approx(0.05)


def test_buyer_cannot_spend_more_cash_than_it_has(economy):
    e = economy
    state = initial(e, dealer=e.Account(1000.0, 1.0), buyer=e.Account(1.0, 0.0),
                    debt=0.0)
    result = e.step(state, params(e, delay=0, buyer_speed=1000.0))
    assert result.state.buyer.cash == pytest.approx(0.0, abs=1e-10)
    assert result.state.dealer.cash == pytest.approx(1001.0)
    assert 0 < result.buyer_purchase < 1


def test_delayed_buyer_uses_only_available_start_of_tick_signals(economy):
    e = economy
    p = params(e, delay=2)
    state = initial(e, dealer=e.Account(1000.0, 1.0), debt=0.0)
    first = e.step(state, p)
    second = e.step(first.state, p)
    third = e.step(second.state, p)
    assert first.buyer_purchase == second.buyer_purchase == 0.0
    assert third.buyer_purchase == pytest.approx(20 * (1 - exp(-0.01)))
    assert third.mark_after > third.mark_before


def test_selling_exhaustion_does_not_invent_a_rebound(economy):
    e = economy
    p = params(e, buyer_speed=0)
    first = e.step(initial(e), p)
    second = e.step(first.state, p)
    assert first.forced_sale > 0
    assert second.forced_sale == 0
    assert second.mark_after == first.mark_after
    assert second.mark_after < p.value


def test_permanent_value_change_does_not_recover_old_value(economy):
    e = economy
    p = params(e, value=98, delay=0, buyer_speed=10000)
    first = e.step(initial(e), p)
    recovered = e.step(first.state, p)
    assert recovered.state.dealer.units == pytest.approx(0)
    assert recovered.mark_after == pytest.approx(98)
    assert recovered.mark_after < 100  # the pre-intervention benchmark


def test_strong_impact_can_make_a_small_sale_worsen_headroom(economy):
    e = economy
    p = params(e, impact=0.1, inventory_limit=0.00001)
    state = initial(e)
    result = e.step(state, p)
    slope = (e.headroom(result.state, p) - e.headroom(state, p)) / result.forced_sale
    # Analytic derivative: 98 * (.25 - .1 * .75 * 10) = -49.
    assert slope == pytest.approx(-49, rel=1e-5)


def test_margin_deadline_fails_before_unavailable_delayed_capital(economy):
    e = economy
    p = params(e, deadline=2, delay=5)
    state = initial(e, dealer=e.Account(0.0, 0.0))
    first = e.step(state, p)
    failed = e.step(first.state, p)
    assert first.state.mode == "MARGIN"
    assert failed.state.mode == "MARGIN_FAILURE"
    assert failed.state.breach_ticks == 2
    later = e.step(failed.state, p)
    assert later.state == failed.state
    assert later.forced_sale == later.buyer_purchase == 0


def test_insolvency_is_absorbing_without_erasing_debt(economy):
    e = economy
    state = initial(e, debt=1001.0)
    result = e.step(state, params(e))
    assert result.state.mode == "DEFAULT"
    assert result.state.debt == 1001.0
    assert result.state.holder == state.holder
    assert result.forced_sale == result.buyer_purchase == 0
    assert e.step(result.state, params(e)).state == result.state


@pytest.mark.parametrize("changes", [
    {"value": 0}, {"impact": -1}, {"maintenance": 0}, {"restore": 0.2},
    {"delay": 0.5}, {"deadline": 0}, {"buyer_speed": float("nan")},
    {"impact": 10, "inventory_limit": 20},
])
def test_invalid_laws_are_rejected_before_simulation(economy, changes):
    with pytest.raises(ValueError):
        params(economy, **changes)


def test_unavailable_inventory_and_incompatible_memory_are_rejected(economy):
    e = economy
    with pytest.raises(ValueError):
        e.step(initial(e, dealer=e.Account(1000.0, 21.0)), params(e))
    with pytest.raises(ValueError):
        e.step(replace(initial(e), signals=(0.1, 0.1, 0.1)), params(e, delay=2))
