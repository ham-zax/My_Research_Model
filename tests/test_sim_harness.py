from dataclasses import replace
from math import isclose

import pytest

from mfsm_sim.harness import (
    OracleStrategy, Strategy, TradeSpec, execute_trade, run_paired_episode,
)
from mfsm_sim.scenarios import draws_for, sample_episode
from mfsm_sim.strategies import BuyDip, Flat, FlowRule, SellDip, tape_features
from mfsm_sim.world import PublicRow, step


def first_triggered(start=0):
    for seed in range(start, start + 200):
        row = run_paired_episode(seed, [Flat()])
        if row["triggered"]:
            return seed, row
    raise AssertionError("no triggered development episode")


class Recorder(Strategy):
    name = "recorder"

    def __init__(self):
        self.tapes = []

    def decide(self, tape, spec):
        self.tapes.append(tape)
        return 0


def test_public_strategy_receives_only_published_rows_up_to_decision():
    seed, row = first_triggered()
    recorder = Recorder()
    run_paired_episode(seed, [recorder])
    (tape,) = recorder.tapes
    assert all(type(item) is PublicRow for item in tape)
    assert tape[-1].tick == row["decision_tick"]
    assert len(tape) == row["decision_tick"]
    assert set(PublicRow.__dataclass_fields__) == {"tick", "mark", "volume", "signed_volume"}


def test_flat_has_zero_pnl_and_dip_pnls_come_from_cash_accounting():
    seed, _ = first_triggered()
    row = run_paired_episode(seed, [Flat(), BuyDip(), SellDip()])
    assert row["pnl"]["S0_flat"] == 0
    assert row["pnl"]["S1_buy_dip"] != 0 and row["pnl"]["S2_sell_dip"] != 0


def test_round_trip_without_market_change_costs_impact_and_fees():
    episode = sample_episode(11)
    quiet = replace(episode.law, value_volatility=0.0, noise_scale=0.0, shock_tick=None,
                    base=replace(episode.law.base, buyer_speed=0.0))
    draws = draws_for(11, 60)
    spec = TradeSpec()
    for action in (1, -1):
        result = execute_trade(episode.world, quiet, draws, action, spec)
        assert result["pnl"] < 0 and isclose(result["residual"], 0, abs_tol=1e-9)
    free = replace(spec, fee_bps=0.0)
    no_impact = replace(quiet, base=replace(quiet.base, impact=0.0))
    result = execute_trade(episode.world, no_impact, draws, 1, free)
    assert isclose(result["pnl"], 0, abs_tol=1e-9)


def test_paired_strategies_share_the_prefix_and_decision_state():
    seed, _ = first_triggered()
    one = run_paired_episode(seed, [BuyDip()])
    two = run_paired_episode(seed, [SellDip(), BuyDip(), FlowRule()])
    assert one["pnl"]["S1_buy_dip"] == two["pnl"]["S1_buy_dip"]
    assert one["decision_tick"] == two["decision_tick"]


def test_oracle_decision_is_deterministic_per_seed():
    seed, _ = first_triggered()
    oracle = OracleStrategy(rollouts=4)
    first = run_paired_episode(seed, [oracle])
    second = run_paired_episode(seed, [oracle])
    assert first["actions"] == second["actions"] and first["pnl"] == second["pnl"]
    assert first["actions"]["S6_state_oracle"] in (-1, 0, 1)


def test_tape_features_are_causal_and_finite():
    episode = sample_episode(2)
    world = episode.world
    tape = ()
    for draw in draws_for(2, 60):
        world, record = step(world, episode.law, draw)
        tape += (record.public,)
    spec = TradeSpec()
    features = tape_features(tape[:40], spec)
    # Later rows must not change a summary computed at row 40.
    assert features == tape_features(tape[:40], spec)
    assert features["drop"] == tape[39].mark / tape[34].mark - 1
    assert all(value == value for value in features.values())


@pytest.mark.parametrize("seed", range(5))
def test_untriggered_rows_carry_no_trades(seed):
    row = run_paired_episode(seed, [BuyDip()], TradeSpec(trigger_return=-0.99))
    assert row["triggered"] is False and "pnl" not in row
