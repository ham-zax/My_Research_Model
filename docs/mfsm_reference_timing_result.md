# MFSM reference: a buyer can arrive before or after the deadline

Version: `MFSM-RE-TIME-1`
Date: 2026-09-24
Status: completed synthetic diagnostic under the [frozen protocol](mfsm_reference_timing_protocol.md)

The [machine-readable receipt](../artifacts/mfsm_reference_timing_result.json)
contains the full paths, starting accounts, parameters, and protocol/model/runner
SHA-256 hashes. To reproduce it:

```bash
uv run --locked python scripts/run_mfsm_reference_timing.py \
  --output /tmp/mfsm_reference_timing_result.json
```

The output path must not exist because the script refuses to overwrite it.

## Result

The holder starts with positive maintenance headroom of +2.5374 before the
benchmark moves from 100 to 98. The shock changes that headroom to -12.3134.
The dealer begins with one asset unit and no cash, producing a positive
inventory-discount signal. A buyer who acts can pay the dealer; the dealer can
then fund a holder sale. All rows keep the same accounts and two-tick deadline.

| Row | Buyer lag | First buyer action | Holder sale | First margin restoration | End |
|---|---:|---|---:|---|---|
| F0 | 0 | decision tick 0 | 1 unit | state tick 1 | Normal at tick 6 |
| F1 | 1 | decision tick 1 | 1 unit | state tick 2 | Normal at tick 6 |
| F2 | 2 | none before termination | 0 | none | Margin failure at tick 2 |
| F5 | 5 | none before termination | 0 | none | Margin failure at tick 2 |
| N0 | 0; response disabled | none | 0 | none | Margin failure at tick 2 |

The fast cases each buy a total of two units over the six-tick horizon: the
initial dealer unit, then the unit acquired from the holder. At state tick 1
F0's mark is 97.0249, equal to the shocked starting mark because the dealer
ends that transition holding one unit again. Yet holder headroom is +12.4296
because the holder received sale proceeds. That difference is why the model
keeps financing headroom distinct from the quote or inventory discount.

All five paths conserved account cash and asset units up to floating-point
roundoff. The slow cases stop at failure; the model does not allow their buyer
to act afterward. This corrects the earlier diagnostic's missing buyer signal.

## Scope of the conclusion

In this member, arrival before the deadline can fund the dealer and restore
the holder's margin; arrival after an absorbing failure cannot. The result
depends on the initial dealer inventory, the buyer's cash and rule, the
buyer-before-margin event order, the fixed two-tick deadline, and the chosen
shock. It is an existence example for the model's timing mechanism. It does
not establish that the timing ratio is monotone in other states, estimate an
exchange's liquidation engine, identify a market causal effect, or imply a
forecast or trading edge.

The [model improvement plan](mfsm_model_improvement_plan.md) now treats the
canonical timing check as complete. The next evidence gap is whether a named
market has measurable state variables and a rule that survives comparison with
alternatives. Additional canonical mechanisms should answer a documented
failure, not fill unused symbols.
