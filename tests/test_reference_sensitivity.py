"""Independent numerical and causal checks for the frozen MFSM-RE-SENS-1 rules."""

from dataclasses import replace
from math import exp, log

import pytest

from mfsm_reference.economy import Account, Parameters, State, observe_limited, price, step


def economy_state(*, debt=750, dealer_cash=1000, dealer_units=0):
    return State(Account(0, 10), Account(dealer_cash, dealer_units),
                 Account(1000, 0), debt=debt)


def law(**changes):
    fields = dict(value=98, impact=0.01, inventory_limit=20,
                  maintenance=0.25, restore=0.30, buyer_speed=20,
                  delay=2, deadline=10)
    fields.update(changes)
    return Parameters(**fields)


def test_hyperbolic_curve_and_integral_pay_the_full_executed_order():
    model = law(value=100, impact=0.1, impact_curve="hyperbolic",
                liquidation_rule="fixed_lot", lot_units=1, buyer_speed=100,
                delay=0)
    state = State(Account(0, 1), Account(1000, 0), Account(1000, 0), debt=80)
    sold = step(state, model)
    assert sold.forced_sale == 1
    assert sold.mark_after == pytest.approx(100 / 1.1)
    assert sold.state.holder.cash == pytest.approx(1000 * log(1.1))
    assert sold.state.dealer.cash == pytest.approx(1000 - 1000 * log(1.1))
    reversed_trade = step(sold.state, model)
    assert reversed_trade.buyer_purchase == pytest.approx(1)
    assert reversed_trade.mark_after == pytest.approx(100)
    assert reversed_trade.state.dealer.cash == pytest.approx(1000)
    assert reversed_trade.state.buyer.cash == pytest.approx(1000 - 1000 * log(1.1))


def test_hyperbolic_dealer_cash_cap_uses_integral_inverse():
    model = law(value=100, impact=0.1, impact_curve="hyperbolic",
                liquidation_rule="fixed_lot", lot_units=1)
    state = State(Account(0, 1), Account(50, 0), Account(1000, 0), debt=80)
    result = step(state, model)
    assert result.forced_sale == pytest.approx(10 * (exp(0.05) - 1))
    assert result.state.dealer.cash == pytest.approx(0, abs=1e-10)
    assert result.state.holder.cash == pytest.approx(50)


def test_same_initial_mark_and_slope_do_not_fix_finite_impact_response():
    state = economy_state()
    exponential = law(impact_curve="exponential")
    hyperbolic = law(impact_curve="hyperbolic")
    assert price(state, exponential) == price(state, hyperbolic) == 98
    assert -98 * exponential.impact == -98 * hyperbolic.impact
    exp_step = step(state, exponential)
    hyp_step = step(state, hyperbolic)
    assert exp_step.forced_sale == pytest.approx(hyp_step.forced_sale)
    assert exp_step.mark_after != pytest.approx(hyp_step.mark_after, abs=1e-6)


def test_fixed_lot_changes_the_order_but_obeys_the_same_cash_and_margin_rules():
    result = step(economy_state(), law(liquidation_rule="fixed_lot", lot_units=2))
    assert result.forced_sale == 2
    assert result.state.mode == "NORMAL"
    assert result.state.holder.units == pytest.approx(8)


def test_distributed_lag_acts_when_its_first_weight_is_available():
    state = economy_state(debt=0, dealer_units=1)
    pure = law(delay=2)
    spread = law(delay=2, delay_weights=(0.0, 0.5, 0.0, 0.5))
    pure_0 = step(state, pure)
    spread_0 = step(state, spread)
    assert pure_0.buyer_purchase == spread_0.buyer_purchase == 0
    pure_1 = step(pure_0.state, pure)
    spread_1 = step(spread_0.state, spread)
    assert pure_1.buyer_purchase == 0
    assert spread_1.buyer_purchase == pytest.approx(10 * (1 - exp(-0.01)))
    assert len(spread_1.state.signals) == 2


@pytest.mark.parametrize("variant", [
    {"impact_curve": "hyperbolic"},
    {"liquidation_rule": "fixed_lot", "lot_units": 2},
    {"delay_weights": (0.0, 0.5, 0.0, 0.5)},
])
def test_structural_variants_conserve_cash_and_inventory(variant):
    model = law(**variant)
    state = economy_state()
    for _ in range(20):
        state = step(state, model).state
        accounts = (state.holder, state.dealer, state.buyer)
        assert sum(x.cash for x in accounts) == pytest.approx(2000)
        assert sum(x.units for x in accounts) == pytest.approx(10)
        assert all(x.cash >= 0 and x.units >= 0 for x in accounts)
        assert state.dealer.units <= model.inventory_limit


@pytest.mark.parametrize("variant", [
    {"impact_curve": "unknown"},
    {"liquidation_rule": "unknown"},
    {"lot_units": 0},
    {"delay_weights": ()},
    {"delay_weights": (0.5, 0.4)},
    {"delay_weights": (0.5, -0.5, 1.0)},
    {"delay_weights": (1.0, 0.0)},
])
def test_invalid_structural_rules_are_rejected(variant):
    with pytest.raises(ValueError):
        law(**variant)


def test_same_limited_observation_can_hide_opposite_forced_sale_responses():
    pre = law(value=100)
    shocked = replace(pre, value=98)
    near = economy_state(debt=750)
    far = economy_state(debt=700)
    assert observe_limited(near, pre) == observe_limited(far, pre)
    near_result = step(near, shocked)
    far_result = step(far, shocked)
    assert near_result.forced_sale > 0
    assert far_result.forced_sale == 0
    assert near_result.mark_after < far_result.mark_after


def test_same_limited_observation_can_hide_a_different_impact_law():
    state = economy_state()
    exponential = law(value=100, impact_curve="exponential")
    hyperbolic = law(value=100, impact_curve="hyperbolic")
    assert observe_limited(state, exponential) == observe_limited(state, hyperbolic)
    a = step(state, replace(exponential, value=98))
    b = step(state, replace(hyperbolic, value=98))
    assert a.mark_after != pytest.approx(b.mark_after, abs=1e-6)
