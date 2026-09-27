"""Seeded episode generation for MFSM-SIM-1 (development priors, uncalibrated).

Two independent random streams per seed: one draws the hidden structure and
scenario, the other draws per-tick value and noise shocks. Strategies never see
either stream; they receive public rows only.
"""

from dataclasses import dataclass, field
from random import Random
from typing import Callable

from mfsm_reference.economy import Account, Parameters

from .world import Draws, Holder, PublicRow, TickRecord, World, WorldLaw, step


SCENARIOS = ("NEWS", "NEWS_CASCADE", "LIQUIDITY", "NULL")


@dataclass(frozen=True)
class Priors:
    """Declared development priors. Ranges are uniform (low, high)."""

    ticks: int = 200
    shock_tick: tuple[int, int] = (60, 100)
    initial_value: float = 100.0
    scenario_weights: tuple[float, ...] = (0.3, 0.3, 0.3, 0.1)
    impact: tuple[float, float] = (0.0003, 0.0012)
    impact_curve: str = "exponential"
    inventory_limit: float = 400.0
    reference_inventory: float = 150.0
    dealer_cash: tuple[float, float] = (10_000.0, 40_000.0)
    buyer_speed: tuple[float, float] = (100.0, 600.0)
    buyer_delay: tuple[int, int] = (1, 8)
    buyer_cash: tuple[float, float] = (3_000.0, 20_000.0)
    holder_count: int = 8
    holder_units: tuple[float, float] = (5.0, 15.0)
    holder_deadline: tuple[int, int] = (1, 4)
    maintenance: float = 0.25
    restore: float = 0.30
    value_volatility: tuple[float, float] = (0.0002, 0.001)
    anchor_speed: tuple[float, float] = (0.15, 1.0)
    noise_scale: tuple[float, float] = (0.5, 2.0)
    news_size: dict = field(default_factory=lambda: {
        "NEWS": (3.0, 6.0), "NEWS_CASCADE": (1.5, 3.0),
        "LIQUIDITY": (0.0, 0.0), "NULL": (0.0, 0.0)})
    margin_distance: dict = field(default_factory=lambda: {
        "NEWS": (0.10, 0.30), "NEWS_CASCADE": (0.005, 0.04),
        "LIQUIDITY": (0.01, 0.08), "NULL": (0.02, 0.30)})
    dump_units: dict = field(default_factory=lambda: {
        "NEWS": (0.0, 0.0), "NEWS_CASCADE": (0.0, 0.0),
        "LIQUIDITY": (20.0, 60.0), "NULL": (0.0, 0.0)})
    trader_cash: float = 100_000.0
    trader_units: float = 100.0


@dataclass(frozen=True)
class Episode:
    seed: int
    scenario: str
    law: WorldLaw
    world: World
    hidden: dict


def _uniform(rng: Random, bounds) -> float:
    low, high = bounds
    return low if low == high else rng.uniform(low, high)


def sample_episode(seed: int, priors: Priors = Priors()) -> Episode:
    rng = Random(f"mfsm-sim-1/structure/{seed}")
    scenario = rng.choices(SCENARIOS, weights=priors.scenario_weights)[0]
    base = Parameters(
        value=priors.initial_value,
        impact=_uniform(rng, priors.impact),
        inventory_limit=priors.inventory_limit,
        maintenance=priors.maintenance,
        restore=priors.restore,
        buyer_speed=_uniform(rng, priors.buyer_speed),
        delay=rng.randint(*priors.buyer_delay),
        deadline=rng.randint(*priors.holder_deadline),
        impact_curve=priors.impact_curve,
    )
    law = WorldLaw(
        base=base,
        value_volatility=_uniform(rng, priors.value_volatility),
        anchor_speed=_uniform(rng, priors.anchor_speed),
        reference_inventory=priors.reference_inventory,
        noise_scale=_uniform(rng, priors.noise_scale),
        terminal_liquidation=True,
        shock_tick=rng.randint(*priors.shock_tick),
        news_size=_uniform(rng, priors.news_size[scenario]),
        dump_units=_uniform(rng, priors.dump_units[scenario]),
    )
    p0 = priors.initial_value
    holders = []
    distances = []
    for _ in range(priors.holder_count):
        units = _uniform(rng, priors.holder_units)
        distance = _uniform(rng, priors.margin_distance[scenario])
        debt = (1 - distance) * (1 - priors.maintenance) * p0 * units
        holders.append(Holder(Account(0.0, units), debt))
        distances.append(distance)
    world = World(
        value=p0, anchor=p0,
        dealer=Account(_uniform(rng, priors.dealer_cash), priors.reference_inventory),
        buyer=Account(_uniform(rng, priors.buyer_cash), 0.0),
        holders=tuple(holders),
        noise=Account(1e8, 1e6),
        dumper=Account(0.0, law.dump_units),
        trader=Account(priors.trader_cash, priors.trader_units),
    )
    hidden = {"scenario": scenario, "margin_distances": tuple(distances),
              "impact": base.impact, "buyer_speed": base.buyer_speed,
              "buyer_delay": base.delay, "holder_deadline": base.deadline,
              "anchor_speed": law.anchor_speed, "news_size": law.news_size,
              "dump_units": law.dump_units, "shock_tick": law.shock_tick,
              "noise_scale": law.noise_scale,
              "value_volatility": law.value_volatility}
    return Episode(seed, scenario, law, world, hidden)


def draws_for(seed: int, ticks: int) -> tuple[Draws, ...]:
    rng = Random(f"mfsm-sim-1/draws/{seed}")
    return tuple(Draws(rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)) for _ in range(ticks))


OrderFn = Callable[[tuple[PublicRow, ...]], float]


def run_episode(episode: Episode, draws: tuple[Draws, ...],
                order_fn: OrderFn | None = None) -> tuple[World, tuple[TickRecord, ...]]:
    """Run all ticks. ``order_fn`` sees only public rows published so far."""
    world = episode.world
    records = []
    public: tuple[PublicRow, ...] = ()
    for draw in draws:
        order = order_fn(public) if order_fn is not None else 0.0
        world, record = step(world, episode.law, draw, order)
        records.append(record)
        public = public + (record.public,)
    return world, tuple(records)
