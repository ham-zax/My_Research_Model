# MFSM reference: buyer arrival before a margin deadline

Version: `MFSM-RE-TIME-1`
Date: 2026-09-24
Status: synthetic rule and comparison fixed before running its paths

This separately versioned diagnostic repairs the limitation of row D in
[MFSM-RE-SENS-1](mfsm_reference_sensitivity_result.md). Its zero-cash dealer
also had zero inventory, so there was no discount to trigger a buyer. Here the
dealer starts with one asset unit and the buyer can purchase it before the
leveraged holder's deadline if the signal lag permits. This is a demonstration
of the stated transition law, not an empirical test of market timing.

## Frozen initial state and law

- L: cash 0, holdings 10 asset units, debt 740 currency.
- D: cash 0, holdings 1 asset unit; maximum holdings 20.
- S: cash 1000, holdings 0.
- Benchmark value 100 before the intervention. At the tick-0 decision boundary,
  set it permanently to 98; leave accounts and empty signal history unchanged.
- Exponential marginal mark `p=v*exp(-0.01*q_D)` and its integral execution
  payments; maintenance ratio 0.25, restoration target 0.30.
- Buyer response coefficient 200 asset units per tick per unit of observed
  inventory discount. Consecutive-breach deadline 2 ticks. Process buyer order
  before holder margin processing at each tick, as in MFSM-RE-1.
- Run at most 6 transitions, stopping at any absorbing failure.

The pre-intervention maintenance headroom must be positive, and the shock must
make it negative. At the shocked boundary, dealer inventory makes the buyer
signal strictly positive. With zero lag, buyer cash is sufficient to purchase
the dealer's one unit; that payment is then the dealer's only funding source for
the holder order. These are feasibility checks on the starting state, not
observed market facts.

## Fixed comparisons and measures

Use the same state and all unchanged parameters in every row:

| ID | Buyer lag | Buyer response | Purpose |
|---|---:|---:|---|
| F0 | 0 ticks | 200 | Buyer can act immediately |
| F1 | 1 tick | 200 | Buyer can act after one breached tick |
| F2 | 2 ticks | 200 | Buyer arrives only after the two-tick deadline |
| F5 | 5 ticks | 200 | Longer-lag limit |
| N0 | 0 ticks | 0 | No-buyer control |

For each row report the first buyer tick or `none`, buyer purchases, forced
sales, post-transition headroom/mode, first restoration tick, failure tick if
any, and cash/asset conservation. The starting inventory may support a buyer
order even when the dealer cannot fund a holder order beforehand. No external
capital, borrowing, implicit rescue, or post-failure recovery may be inserted.

Interpret a difference only as conditional on this transition ordering,
synthetic state, and deadline definition. Buyer arrival need not improve all
possible states or shocks. Do not combine these paths with the historical BTC
experiment or use them as evidence of a trading edge.
