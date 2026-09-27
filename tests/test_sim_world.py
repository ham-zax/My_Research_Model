from dataclasses import replace
from math import isclose
from random import Random

import pytest

from mfsm_reference.economy import Account, Parameters, State, step as reference_step
from mfsm_sim.scenarios import Priors, draws_for, run_episode, sample_episode
from mfsm_sim.world import Draws, Holder, World, WorldLaw, step


REFERENCE_STATE = State(Account(0, 10), Account(1000, 0), Account(1000, 0), debt=750)
BASELINE = Parameters(value=100, impact=0.01, inventory_limit=20)
REFERENCE_LAWS = {
    "baseline": BASELINE,
    "value_drop_with_delayed_buyer": replace(BASELINE, value=98),
    "value_drop_without_buyer": replace(BASELINE, value=98, buyer_speed=0),
    "value_drop_strong_impact": replace(BASELINE, value=98, impact=0.08),
    "value_drop_no_impact": replace(BASELINE, value=98, impact=0),
    "hyperbolic": replace(BASELINE, value=98, impact_curve="hyperbolic"),
    "fixed_lot": replace(BASELINE, value=98, liquidation_rule="fixed_lot"),
    "no_delay": replace(BASELINE, value=98, delay=0),
    "short_deadline": replace(BASELINE, value=98, impact=0.08, deadline=2),
}


def reference_limit(state: State, law: Parameters) -> tuple[World, WorldLaw]:
    world = World(
        value=law.value, anchor=law.value, dealer=state.dealer, buyer=state.buyer,
        holders=(Holder(state.holder, state.debt, state.breach_ticks, state.mode),),
        noise=Account(0, 0), dumper=Account(0, 0), trader=Account(0, 0),
        signals=state.signals, tick=state.tick)
    return world, WorldLaw(base=law, terminal_liquidation=False,
                           freeze_when_all_terminal=True)


@pytest.mark.parametrize("name", sorted(REFERENCE_LAWS))
def test_declared_limit_reproduces_reference_economy_exactly(name):
    law = REFERENCE_LAWS[name]
    state = REFERENCE_STATE
    world, world_law = reference_limit(state, law)
    for _ in range(25):
        transition = reference_step(state, law)
        world, record = step(world, world_law)
        state = transition.state
        holder = world.holders[0]
        assert holder.account == state.holder
        assert holder.debt == state.debt
        assert (holder.mode, holder.breach_ticks) == (state.mode, state.breach_ticks)
        assert (world.dealer, world.buyer) == (state.dealer, state.buyer)
        assert (world.signals, world.tick) == (state.signals, state.tick)
        assert record.public.mark == transition.mark_after
        assert record.mark_before == transition.mark_before
        assert record.holder_sales == (transition.forced_sale,)
        assert record.buyer_purchase == transition.buyer_purchase


def totals(world: World) -> tuple[float, float]:
    accounts = [world.dealer, world.buyer, world.noise, world.dumper, world.trader,
                *(h.account for h in world.holders)]
    return sum(a.cash for a in accounts), sum(a.units for a in accounts)


@pytest.mark.parametrize("seed", range(12))
def test_episodes_conserve_cash_and_units_with_trader_orders(seed):
    episode = sample_episode(seed)
    world = episode.world
    cash0, units0 = totals(world)
    orders = Random(seed)
    for draw in draws_for(seed, Priors().ticks):
        world, _ = step(world, episode.law, draw, orders.choice((-5.0, 0.0, 5.0)))
        cash, units = totals(world)
        assert isclose(cash, cash0, rel_tol=1e-12, abs_tol=1e-6)
        assert isclose(units, units0, rel_tol=1e-12, abs_tol=1e-9)
        assert 0 <= world.dealer.units <= episode.law.base.inventory_limit


def test_same_seed_gives_identical_paths():
    episode = sample_episode(7)
    draws = draws_for(7, 120)
    assert run_episode(episode, draws) == run_episode(sample_episode(7), draws_for(7, 120))


def test_zero_trader_orders_match_the_no_trader_path():
    episode = sample_episode(3)
    draws = draws_for(3, 150)
    assert run_episode(episode, draws) == run_episode(episode, draws, lambda tape: 0.0)


def test_order_function_sees_only_published_rows():
    episode = sample_episode(5)
    seen = []

    def spy(tape):
        seen.append(len(tape))
        return 0.0

    _, records = run_episode(episode, draws_for(5, 30), spy)
    assert seen == list(range(30))
    assert all(type(row).__name__ == "PublicRow" for row in (r.public for r in records))


def test_news_is_permanent_and_liquidity_dump_leaves_value_unchanged():
    base = Parameters(value=100, impact=0.001, inventory_limit=400, buyer_speed=300, delay=2)
    world = World(value=100, anchor=100, dealer=Account(50_000, 150), buyer=Account(20_000, 0),
                  holders=(), noise=Account(0, 0), dumper=Account(0, 40),
                  trader=Account(0, 0))
    news = WorldLaw(base=base, reference_inventory=150, shock_tick=0, news_size=4)
    dump = WorldLaw(base=base, reference_inventory=150, shock_tick=0, dump_units=40)
    news_world, dump_world = world, world
    for _ in range(60):
        news_world, news_record = step(news_world, news, Draws())
        dump_world, dump_record = step(dump_world, dump, Draws())
    assert news_world.value == 96 and isclose(news_record.public.mark, 96, rel_tol=1e-9)
    assert dump_world.value == 100
    assert isclose(dump_record.public.mark, 100, rel_tol=2e-3)


def test_informed_trader_sells_back_above_value():
    base = Parameters(value=100, impact=0.001, inventory_limit=400, buyer_speed=300, delay=0)
    world = World(value=100, anchor=100, dealer=Account(50_000, 100), buyer=Account(0, 30),
                  holders=(), noise=Account(0, 0), dumper=Account(0, 0),
                  trader=Account(0, 0))
    law = WorldLaw(base=base, reference_inventory=150)
    world, record = step(world, law)
    assert record.buyer_purchase < 0 and world.buyer.units < 30


def test_invalid_world_laws_are_rejected():
    with pytest.raises(ValueError):
        WorldLaw(base=BASELINE, anchor_speed=0)
    with pytest.raises(ValueError):
        WorldLaw(base=BASELINE, reference_inventory=21)
    with pytest.raises(ValueError):
        WorldLaw(base=replace(BASELINE, impact_curve="hyperbolic", impact=0.1),
                 reference_inventory=10)
