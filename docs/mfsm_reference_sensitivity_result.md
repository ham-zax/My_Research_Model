# MFSM reference: structural sensitivity and incomplete observation

Version: `MFSM-RE-SENS-1`
Date: 2026-09-24
Status: completed synthetic comparison under the [frozen protocol](mfsm_reference_sensitivity_protocol.md)

The [machine-readable receipt](../artifacts/mfsm_reference_sensitivity_result.json)
contains all nine paths, the exact parameter sets, and SHA-256 hashes of the
protocol and transition code. Reproduce it with:

```bash
uv run --locked python scripts/run_mfsm_reference_sensitivity.py \
  --output /tmp/mfsm_reference_sensitivity_result.json
```

The script refuses to overwrite an existing output. It uses invented initial
accounts and parameters. No prices, order books, fitted parameters, forecast
probabilities, or trading returns enter the comparison.

## What the fixed scenario produced

The reference starts with ten leveraged asset units and a dealer with 1000
currency of cash. A permanent benchmark-value change from 100 to 98 creates
initial maintenance headroom of -15 currency. The unshocked baseline, B0,
stays at mark 100 with no forced sale.

| Rule | Forced sale, units | Mark after tick 1 | First margin restoration | End at or before tick 20 |
|---|---:|---:|---:|---|
| E: exponential impact, target order, lag 2 | 2.1769 | 95.8897 | tick 1 | Normal; mark 98 |
| H: hyperbolic impact | 2.1769 | 95.9121 | tick 1 | Normal; mark 98 |
| L: fixed lot of 2 | 2.0000 | 96.0595 | tick 1 | Normal; mark 98 |
| K: buyer lags 1 and 3, equal weights | 2.1769 | 95.8897 | tick 1 | Normal; mark 98 |
| Z: zero impact | 2.1769 | 98.0000 | tick 1 | Normal; mark 98 |
| N: no buyer | 2.1769 | 95.8897 | tick 1 | Normal; mark 95.8897 |
| C: dealer cash zero | 0 | 98.0000 | none | Margin failure at tick 10 |
| D: dealer cash zero, lag 5, deadline 2 | 0 | 98.0000 | none | Margin failure at tick 2 |

“Normal” here is the mode at the 20-tick reporting horizon, not a claim that the
market reached a terminal state. The minimum headroom in every shocked row is
-15 at the initial revaluation. The report includes each later headroom value.
Cash and asset quantities were conserved in every path, with maximum numerical
unit error about 1.8e-15; no account balance became negative.

The alternative impact curves have the same initial mark and local slope at
zero dealer inventory. Their finite executions differ: after the same 2.1769-unit
sale, H's mark is about 0.0224 currency higher than E's. Changing the forced
order to a fixed lot changes the first mark more. The distributed delay first
buys at tick 3, while the pure lag-2 reference first buys at tick 4. Those are
path differences even though all four rows restore margin at tick 1 and reach
the same final benchmark mark in this parameter set. The run does not show that
failure or recovery is generally insensitive to these rules.

Without a buyer, the inventory discount persists through the horizon. Zero
impact removes that discount. A dealer with no cash cannot take the holder's
order and misses the margin deadline. Row D **does not isolate a delay effect**:
the dealer also has zero starting inventory, so no discount signal exists to
activate the buyer. Its earlier failure is explained by the shorter deadline;
the chosen row provides no evidence about whether slower capital arrival
caused it. A future timing comparison must first construct a path on which
capital can actually arrive and change the fill, then freeze both deadline
variants before inspecting their outcomes.

## What cannot be inferred from the limited observation

The synthetic observer sees `(mark=100, benchmark=100, dealer_units=0)` before
the shock. Two admissible states have exactly that observation and the same
reference law. With holder debt 750, the post-shock headroom is -15 and tick 0
forces a sale of 2.1769 units, leaving mark 95.8897. With debt 700, headroom is
+35, no sale occurs, and mark remains 98. Thus the forced-sale decision and
next mark are **not identified** by those three observations. Holder debt or
directly measured margin headroom would distinguish this pair under the known
law.

Even with the holder state fixed, exponential and hyperbolic impact agree on
the same pre-shock limited observation but put the next mark at 95.8897 and
95.9121. Discriminating that law requires execution/price measurements away
from zero inventory; merely observing the initial quote cannot do it. This is
structural uncertainty, separate from the hidden debt example. These finite
scenario ranges are neither confidence intervals nor market forecasts.

## Consequences for the model

1. Transaction accounting, a unique path under a fully specified member, and
   the impossibility of an inventory-driven rebound without buying survive all
   admissible curves tested here. They are conditional on this closed economy.
2. The magnitude and timing of the mark response depend on the impact, forced
   order, and delay rules. A named rule is part of the model, not a cosmetic
   parameter choice.
3. A public-looking price/inventory snapshot cannot reveal the holder's
   headroom or the impact law. An MFSM application should return a response set
   or `not identified` until it has the missing measurements and a justified
   structural member.
4. Nothing in this result establishes that the reference economy describes an
   exchange, identifies a causal effect in market data, forecasts better than
   a baseline, or contains a trading edge.

Next work follows the [model improvement plan](mfsm_model_improvement_plan.md):
repair the timing diagnostic only with a separately frozen scenario, then add
new mechanisms only for a named limitation with a distinct predicted consequence.
