"""Print uncalibrated examples of MFSM-RE-1; no market files or model fits."""

from dataclasses import asdict, replace
import json

from mfsm_reference.economy import (
    Account, Parameters, State, TERMINAL_MODES, equity, headroom, price, step,
)


def main():
    initial = State(Account(0, 10), Account(1000, 0), Account(1000, 0), debt=750)
    baseline = Parameters(value=100, impact=0.01, inventory_limit=20)
    scenarios = {
        "baseline": baseline,
        "value_drop_with_delayed_buyer": replace(baseline, value=98),
        "value_drop_without_buyer": replace(baseline, value=98, buyer_speed=0),
        "value_drop_strong_impact": replace(baseline, value=98, impact=0.08),
        "value_drop_no_impact": replace(baseline, value=98, impact=0),
    }
    output = {"model": "MFSM-RE-1", "status": "synthetic_theoretical_examples",
              "market_calibrated": False, "initial_state": asdict(initial), "scenarios": {}}
    for name, law in scenarios.items():
        state = initial
        rows = [{"tick": 0, "price": price(state, law), "headroom": headroom(state, law),
                 "equity": equity(state, law), "phase": "before_first_transition"}]
        for _ in range(20):
            transition = step(state, law)
            state = transition.state
            rows.append({"tick": state.tick, "price": transition.mark_after,
                         "headroom": headroom(state, law), "equity": equity(state, law),
                         "forced_sale": transition.forced_sale,
                         "buyer_purchase": transition.buyer_purchase,
                         "mode": state.mode})
            if state.mode in TERMINAL_MODES:
                break
        output["scenarios"][name] = {"parameters": asdict(law), "path": rows,
                                     "final_state": asdict(state)}
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
