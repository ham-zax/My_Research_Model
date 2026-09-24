"""Run the prespecified MFSM-RE-SENS-1 synthetic sensitivity matrix."""

import argparse
from dataclasses import asdict, replace
from hashlib import sha256
import json
from pathlib import Path

from mfsm_reference.economy import (
    Account, Parameters, State, TERMINAL_MODES,
    headroom, observe_limited, price, step,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/mfsm_reference_sensitivity_protocol.md"
MODEL_CODE = ROOT / "src/mfsm_reference/economy.py"


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _initial(*, debt: float = 750, dealer_cash: float = 1000) -> State:
    return State(Account(0, 10), Account(dealer_cash, 0), Account(1000, 0), debt)


def _law(**changes) -> Parameters:
    fields = dict(value=98, impact=0.01, inventory_limit=20,
                  maintenance=0.25, restore=0.30, buyer_speed=20,
                  delay=2, deadline=10)
    fields.update(changes)
    return Parameters(**fields)


def _path(initial: State, law: Parameters, steps: int = 20) -> dict:
    state = initial
    initial_accounts = (initial.holder, initial.dealer, initial.buyer)
    initial_cash = sum(a.cash for a in initial_accounts)
    initial_units = sum(a.units for a in initial_accounts)
    seen_breach = headroom(state, law) < -law.currency_tolerance
    first_restored = None
    min_headroom = headroom(state, law)
    max_inventory = state.dealer.units
    total_sale = 0.0
    max_cash_error = 0.0
    max_unit_error = 0.0
    minimum_account_balance = min(a.cash for a in initial_accounts)
    minimum_account_balance = min(minimum_account_balance,
                                  *(a.units for a in initial_accounts))
    rows = []
    for _ in range(steps):
        if state.mode in TERMINAL_MODES:
            break
        transition = step(state, law)
        state = transition.state
        current_headroom = headroom(state, law)
        if current_headroom < -law.currency_tolerance:
            seen_breach = True
        elif seen_breach and first_restored is None:
            first_restored = state.tick
        min_headroom = min(min_headroom, current_headroom)
        max_inventory = max(max_inventory, state.dealer.units)
        total_sale += transition.forced_sale
        accounts = (state.holder, state.dealer, state.buyer)
        max_cash_error = max(max_cash_error,
                             abs(sum(a.cash for a in accounts) - initial_cash))
        max_unit_error = max(max_unit_error,
                             abs(sum(a.units for a in accounts) - initial_units))
        minimum_account_balance = min(
            minimum_account_balance,
            *(a.cash for a in accounts), *(a.units for a in accounts),
        )
        rows.append({"tick": state.tick, "mark": transition.mark_after,
                     "headroom": current_headroom, "mode": state.mode,
                     "forced_sale": transition.forced_sale,
                     "buyer_purchase": transition.buyer_purchase})
    return {
        "initial_state": asdict(initial), "parameters": asdict(law),
        "terminal_mode": state.mode, "end_tick": state.tick,
        "minimum_headroom": min_headroom, "total_forced_sale": total_sale,
        "first_margin_restoration_tick": first_restored,
        "final_mark": price(state, law), "maximum_dealer_inventory": max_inventory,
        "maximum_cash_conservation_error": max_cash_error,
        "maximum_unit_conservation_error": max_unit_error,
        "minimum_account_balance": minimum_account_balance,
        "path": rows,
    }


def build_report() -> dict:
    initial = _initial()
    rows = {
        "B0": (initial, _law(value=100)),
        "E": (initial, _law()),
        "H": (initial, _law(impact_curve="hyperbolic")),
        "L": (initial, _law(liquidation_rule="fixed_lot", lot_units=2)),
        "K": (initial, _law(delay_weights=(0.0, 0.5, 0.0, 0.5))),
        "Z": (initial, _law(impact=0)),
        "N": (initial, _law(buyer_speed=0)),
        "C": (_initial(dealer_cash=0), _law()),
        "D": (_initial(dealer_cash=0), _law(delay=5, deadline=2)),
    }
    scenarios = {name: _path(state, law) for name, (state, law) in rows.items()}

    pre_law = _law(value=100)
    low_debt = _initial(debt=700)
    obs_a = observe_limited(initial, pre_law)
    obs_b = observe_limited(low_debt, pre_law)
    if obs_a != obs_b:
        raise AssertionError("hidden-state counterexample has unequal observations")
    response_a = step(initial, _law())
    response_b = step(low_debt, _law())
    law_e = _law(value=100)
    law_h = _law(value=100, impact_curve="hyperbolic")
    if observe_limited(initial, law_e) != observe_limited(initial, law_h):
        raise AssertionError("structural counterexample has unequal observations")
    model_e = step(initial, replace(law_e, value=98))
    model_h = step(initial, replace(law_h, value=98))

    return {
        "schema": "MFSM-RE-SENS-1-result-1",
        "status": "synthetic_theoretical_comparison_only",
        "protocol_sha256": _hash(PROTOCOL),
        "economy_code_sha256": _hash(MODEL_CODE),
        "intervention": "permanent benchmark-value change 100 to 98 before tick 0",
        "max_transitions": 20,
        "scenarios": scenarios,
        "limited_observation": {
            "fields": ["mark", "benchmark", "dealer_units"],
            "common_pre_intervention_value": asdict(obs_a),
            "hidden_state_uncertainty": {
                "candidate_debts": [750, 700],
                "post_shock_headrooms_before": [headroom(initial, _law()),
                                                headroom(low_debt, _law())],
                "tick_0_forced_sales": [response_a.forced_sale, response_b.forced_sale],
                "tick_0_headrooms_after": [headroom(response_a.state, _law()),
                                           headroom(response_b.state, _law())],
                "tick_0_mark_range": [min(response_a.mark_after, response_b.mark_after),
                                      max(response_a.mark_after, response_b.mark_after)],
                "identified_from_limited_observation": False,
            },
            "structural_law_uncertainty": {
                "candidate_curves": ["exponential", "hyperbolic"],
                "tick_0_marks": [model_e.mark_after, model_h.mark_after],
                "identified_from_limited_observation": False,
            },
            "range_interpretation": "finite_scenario_envelope_not_confidence_interval",
        },
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
                      report["protocol_sha256"], "scenarios": len(report["scenarios"])},
                     sort_keys=True))


if __name__ == "__main__":
    main()
