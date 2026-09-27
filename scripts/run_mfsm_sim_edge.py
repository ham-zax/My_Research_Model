"""Development runs of MFSM-SIM-EDGE (docs/mfsm_sim_edge_plan.md).

Only development seeds are allowed until a frozen protocol exists. Output is a
synthetic, uncalibrated development diagnostic, never a market or edge claim.
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path
from random import Random
from statistics import fmean, pstdev

from mfsm_sim.harness import OracleStrategy, TradeSpec, run_paired_episode
from mfsm_sim.strategies import BuyDip, Flat, FlowRule, SellDip


DEV_SEEDS = range(0, 1_000_000)
BOOTSTRAP = 2000


def paired_interval(differences, seed=0):
    rng = Random(f"mfsm-sim-edge/bootstrap/{seed}")
    n = len(differences)
    means = sorted(fmean(rng.choices(differences, k=n)) for _ in range(BOOTSTRAP))
    return means[int(0.025 * BOOTSTRAP)], means[int(0.975 * BOOTSTRAP) - 1]


def summarize(rows, names, comparators):
    out = {}
    for name in names:
        pnl = [row["pnl"][name] for row in rows]
        entry = {"mean_pnl": fmean(pnl), "sd_pnl": pstdev(pnl),
                 "trade_rate": fmean(row["actions"][name] != 0 for row in rows),
                 "hit_rate_when_trading": (
                     fmean(p > 0 for p, row in zip(pnl, rows) if row["actions"][name])
                     if any(row["actions"][name] for row in rows) else None),
                 "cvar_5pct": fmean(sorted(pnl)[:max(1, len(pnl) // 20)]),
                 "paired_minus": {}}
        for other in comparators:
            if other == name:
                continue
            diff = [row["pnl"][name] - row["pnl"][other] for row in rows]
            low, high = paired_interval(diff)
            entry["paired_minus"][other] = {"mean": fmean(diff), "ci95": [low, high]}
        out[name] = entry
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--oracle-rollouts", type=int, default=16)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seeds = range(args.start, args.start + args.count)
    if seeds.start < DEV_SEEDS.start or seeds.stop > DEV_SEEDS.stop:
        raise SystemExit("only development seeds may be run before a protocol is frozen")

    strategies = [Flat(), BuyDip(), SellDip(), FlowRule(),
                  OracleStrategy(args.oracle_rollouts)]
    names = [s.name for s in strategies]
    spec = TradeSpec()
    rows = [run_paired_episode(seed, strategies, spec) for seed in seeds]
    triggered = [row for row in rows if row["triggered"]]
    by_scenario = defaultdict(list)
    for row in triggered:
        by_scenario[row["scenario"]].append(row)
    comparators = ["S0_flat", "S1_buy_dip", "S6_state_oracle"]
    result = {
        "status": "development_diagnostic_synthetic_uncalibrated",
        "seeds": [seeds.start, seeds.stop],
        "trade_spec": spec.__dict__,
        "episodes": len(rows), "triggered": len(triggered),
        "all": summarize(triggered, names, comparators),
        "by_scenario": {
            scenario: {"n": len(group),
                       "mean_forward_return": fmean(r["forward_return"] for r in group),
                       "strategies": {n: {"mean_pnl": fmean(r["pnl"][n] for r in group),
                                          "trade_rate": fmean(r["actions"][n] != 0 for r in group)}
                                      for n in names}}
            for scenario, group in sorted(by_scenario.items())},
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
