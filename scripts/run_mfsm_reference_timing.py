"""Run the frozen synthetic MFSM-RE-TIME-1 buyer-arrival diagnostic."""

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from mfsm_reference.economy import (
    Account, Parameters, State, TERMINAL_MODES, headroom, price, step,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/mfsm_reference_timing_protocol.md"
MODEL_CODE = ROOT / "src/mfsm_reference/economy.py"


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _initial() -> State:
    return State(Account(0, 10), Account(0, 1), Account(1000, 0), debt=740)


def _law(*, delay: int, buyer_speed: float = 200, value: float = 98) -> Parameters:
    return Parameters(value=value, impact=0.01, inventory_limit=20,
                      maintenance=0.25, restore=0.30, buyer_speed=buyer_speed,
                      delay=delay, deadline=2)


def _path(law: Parameters) -> dict:
    state = _initial()
    initial_cash = sum(a.cash for a in (state.holder, state.dealer, state.buyer))
    initial_units = sum(a.units for a in (state.holder, state.dealer, state.buyer))
    first_buyer_tick = None
    first_restoration_tick = None
    failure_tick = None
    total_bought = 0.0
    total_sold = 0.0
    max_cash_error = 0.0
    max_units_error = 0.0
    rows = []
    for _ in range(6):
        if state.mode in TERMINAL_MODES:
            break
        action_tick = state.tick
        transition = step(state, law)
        state = transition.state
        current_headroom = headroom(state, law)
        if transition.buyer_purchase > 1e-9 and first_buyer_tick is None:
            first_buyer_tick = action_tick
        if current_headroom >= -law.currency_tolerance and first_restoration_tick is None:
            first_restoration_tick = state.tick
        if state.mode in TERMINAL_MODES:
            failure_tick = state.tick
        total_bought += transition.buyer_purchase
        total_sold += transition.forced_sale
        accounts = (state.holder, state.dealer, state.buyer)
        max_cash_error = max(max_cash_error,
                             abs(sum(a.cash for a in accounts) - initial_cash))
        max_units_error = max(max_units_error,
                              abs(sum(a.units for a in accounts) - initial_units))
        rows.append({"tick": state.tick, "buyer_purchase": transition.buyer_purchase,
                     "forced_sale": transition.forced_sale, "mark": transition.mark_after,
                     "headroom": current_headroom, "mode": state.mode})
    return {"parameters": asdict(law), "first_buyer_tick": first_buyer_tick,
            "first_restoration_tick": first_restoration_tick,
            "failure_tick": failure_tick, "end_mode": state.mode,
            "end_tick": state.tick, "total_buyer_purchase": total_bought,
            "total_forced_sale": total_sold,
            "maximum_cash_conservation_error": max_cash_error,
            "maximum_unit_conservation_error": max_units_error,
            "path": rows}


def build_report() -> dict:
    initial = _initial()
    pre = _law(delay=0, value=100)
    shocked = _law(delay=0)
    pre_headroom = headroom(initial, pre)
    shocked_headroom = headroom(initial, shocked)
    shocked_discount = 1 - price(initial, shocked) / shocked.value
    if not (pre_headroom > 0 and shocked_headroom < 0 and shocked_discount > 0):
        raise AssertionError("the fixed starting state does not isolate a new breach and signal")
    rows = {
        "F0": _law(delay=0),
        "F1": _law(delay=1),
        "F2": _law(delay=2),
        "F5": _law(delay=5),
        "N0": _law(delay=0, buyer_speed=0),
    }
    paths = {name: _path(law) for name, law in rows.items()}
    return {
        "schema": "MFSM-RE-TIME-1-result-1",
        "status": "synthetic_transition_diagnostic_only",
        "protocol_sha256": _sha(PROTOCOL),
        "economy_code_sha256": _sha(MODEL_CODE),
        "runner_sha256": _sha(Path(__file__)),
        "initial_state": asdict(initial),
        "pre_intervention_headroom": pre_headroom,
        "post_intervention_headroom": shocked_headroom,
        "post_intervention_discount_signal": shocked_discount,
        "paths": paths,
        "empirical_data_used": False,
        "model_fitted": False,
        "trading_edge_claim": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_report()
    with args.output.open("x", encoding="utf-8") as dest:
        json.dump(report, dest, indent=2, sort_keys=True, allow_nan=False)
        dest.write("\n")
    print(json.dumps({"output": str(args.output), "protocol_sha256":
                      report["protocol_sha256"], "paths": len(report["paths"])},
                     sort_keys=True))


if __name__ == "__main__":
    main()
