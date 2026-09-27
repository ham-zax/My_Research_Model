"""Paired trading harness for MFSM-SIM-EDGE (see docs/mfsm_sim_edge_plan.md).

Every strategy shares the no-trade path up to its decision tick and the same
per-tick draws afterwards (common random numbers). Public strategies receive
only the published tape; the oracle alone receives the hidden world.
"""

from dataclasses import dataclass
from random import Random

from .scenarios import Episode, Priors, draws_for, sample_episode
from .world import Draws, PublicRow, World, WorldLaw, mark, step


@dataclass(frozen=True)
class TradeSpec:
    trigger_window: int = 5
    trigger_return: float = -0.02
    decision_delay: int = 1
    horizon: int = 30
    size: float = 5.0
    fee_bps: float = 5.0
    unwind_slack: int = 10


def crossed(tape: tuple[PublicRow, ...], spec: TradeSpec) -> bool:
    """Whether the latest row's return over the trigger window crosses the threshold."""
    w = spec.trigger_window
    return (len(tape) > w
            and tape[-1].mark / tape[-1 - w].mark - 1 <= spec.trigger_return)


def execute_trade(world: World, law: WorldLaw, draws: tuple[Draws, ...],
                  action: int, spec: TradeSpec) -> dict:
    """Enter ``action * size`` now, unwind after ``horizon`` ticks; cash P&L after fees."""
    if action == 0:
        return {"pnl": 0.0, "filled": 0.0, "residual": 0.0}
    if len(draws) < spec.horizon + 1:
        raise ValueError("not enough draws to hold and unwind")
    start = world.trader
    fee_rate = spec.fee_bps / 10_000
    fees = 0.0
    filled = 0.0
    for index, draw in enumerate(draws):
        if index == 0:
            order = action * spec.size
        elif index < spec.horizon:
            order = 0.0
        else:
            order = start.units - world.trader.units
            if abs(order) <= 1e-12:
                break
        before = world.trader.cash
        world, record = step(world, law, draw, order)
        fees += fee_rate * abs(world.trader.cash - before)
        if index == 0:
            filled = record.trader_trade
    residual = world.trader.units - start.units
    pnl = world.trader.cash - start.cash - fees + residual * mark(world, law)
    return {"pnl": pnl, "filled": filled, "residual": residual}


class Strategy:
    name = "base"
    uses_hidden_state = False

    def decide(self, tape: tuple[PublicRow, ...], spec: TradeSpec) -> int:
        raise NotImplementedError


class OracleStrategy:
    """Knows the hidden world and law, not future noise: Monte Carlo over it."""

    name = "S6_state_oracle"
    uses_hidden_state = True

    def __init__(self, rollouts: int = 32):
        self.rollouts = rollouts

    def decide_hidden(self, world: World, law: WorldLaw, remaining: int,
                      spec: TradeSpec, seed: int) -> int:
        rng = Random(f"mfsm-sim-edge/oracle/{seed}")
        totals = {1: 0.0, -1: 0.0}
        for _ in range(self.rollouts):
            draws = tuple(Draws(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(remaining))
            for action in totals:
                totals[action] += execute_trade(world, law, draws, action, spec)["pnl"]
        best = max(totals, key=totals.get)
        return best if totals[best] > 0 else 0


def run_paired_episode(seed: int, strategies, spec: TradeSpec = TradeSpec(),
                       priors: Priors = Priors(), episode: Episode | None = None) -> dict:
    episode = episode or sample_episode(seed, priors)
    draws = draws_for(seed, priors.ticks)
    world = episode.world
    tape: tuple[PublicRow, ...] = ()
    trigger = None
    decision_index = None
    for index, draw in enumerate(draws):
        world, record = step(world, episode.law, draw)
        tape = tape + (record.public,)
        if trigger is None and crossed(tape, spec):
            trigger = len(tape) - 1
        if trigger is not None and len(tape) == trigger + 1 + spec.decision_delay:
            decision_index = index
            break
    row = {"seed": seed, "scenario": episode.scenario, "hidden": episode.hidden,
           "triggered": decision_index is not None}
    remaining = draws[decision_index + 1:] if decision_index is not None else ()
    if decision_index is None or len(remaining) < spec.horizon + spec.unwind_slack:
        row["triggered"] = False
        return row
    marks = []
    probe = world
    for draw in remaining[:spec.horizon]:
        probe, record = step(probe, episode.law, draw)
        marks.append(record.public.mark)
    row.update({
        "trigger_tick": tape[trigger].tick,
        "decision_tick": tape[-1].tick,
        "decision_mark": tape[-1].mark,
        "forward_return": marks[-1] / tape[-1].mark - 1,
        "value_gap_at_decision": world.value / tape[-1].mark - 1,
        "actions": {}, "pnl": {},
    })
    for strategy in strategies:
        if strategy.uses_hidden_state:
            action = strategy.decide_hidden(world, episode.law, len(remaining), spec, seed)
        else:
            action = strategy.decide(tape, spec)
        result = execute_trade(world, episode.law, remaining, action, spec)
        row["actions"][strategy.name] = action
        row["pnl"][strategy.name] = result["pnl"]
    return row
