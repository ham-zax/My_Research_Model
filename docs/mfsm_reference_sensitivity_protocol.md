# MFSM reference: structural sensitivity and observation protocol

Version: `MFSM-RE-SENS-1`
Date: 2026-09-24
Status: rules and synthetic scenarios fixed before running the comparison

This protocol tests how strongly the results of
[MFSM-RE-1](../MFSM_Reference_Economy.md) depend on three chosen structural
rules. It also checks what an observer can infer when the holder's debt is
hidden. The inputs below are synthetic. No variant may be chosen by a favorable
price path, and none is calibrated to an exchange.

## Shared economy and response measures

At tick 0, before the transition, holder L has 10 asset units, 0 cash, and debt
750. Dealer D has 0 units and 1000 cash. Buyer S has 0 units and 1000 cash.
Prehistory is zero. Benchmark value before intervention is 100 currency per
asset; the named intervention sets it permanently to 98 before tick 0. The
no-intervention baseline keeps value 100 with all accounts identical.

Unless a row below changes it, use impact coefficient 0.01 per asset, dealer
inventory ceiling 20 units, maintenance ratio 0.25, restoration ratio 0.30,
buyer response 20 asset units per tick per unit of observed discount, pure lag
2 ticks, and deadline 10 ticks. The baseline inventory mark is
`v * exp(-lambda * q_D)` and its forced order targets the restoration ratio.
Run at most 20 transitions or stop at first absorbing failure/default.

For every row, report terminal mode, minimum headroom over the recorded path,
total forced sale, first tick with nonnegative headroom after an initial breach
or `none`, final mark, and maximum dealer inventory. A terminal mark records
only the mark at failure; no later recovery is inferred. Also report the sum of
cash/units and whether any account became negative. These are synthetic path
descriptions, not statistical estimates.

## Frozen structural comparisons

| ID | Change from value-98 reference | Reason |
|---|---|---|
| E | Exponential curve, restoration-target order, pure lag 2 | Reference |
| H | Hyperbolic curve `p(q)=v/(1+lambda*q)` | Same mark and first derivative at zero dealer inventory, different finite impact |
| L | Fixed forced lot of 2 asset units per breached tick | Different liquidation sizing, same maintenance/failure rule |
| K | Buyer signal weights 0.5 at lag 1 and 0.5 at lag 3 | Same mean lag 2, different arrival profile |

Curve H uses the integral of its marginal mark for each buyer/dealer trade.
Both curves must return `p=v` and amount `v*f` when impact is zero.
For L, the fixed lot is capped by remaining holder assets, dealer cash, and
dealer inventory room; it is requested only while maintenance headroom is
negative. K uses the same bounded history state and no future observations.
The lag weights sum to one; a zero synthetic prehistory is explicit.

Controls are fixed separately and must be reported without replacing E:

| ID | Change | Purpose |
|---|---|---|
| Z | Impact zero | Accounting/no-impact limit |
| N | Buyer response zero | Seller exhaustion without counterflow |
| C | Dealer starts with zero cash | Missing immediate absorption |
| D | Dealer starts with zero cash, buyer lag 5, deadline 2 | Capital arrives after the forced-action deadline |

Rows C and D deliberately change the available cash; their response magnitudes
are not evidence for a particular impact curve. A mechanism proposition is
*conditional* if these prespecified variants disagree on its response or on a
failure/restoration call. Aggregate min/max across rows are scenario envelopes,
not confidence intervals. Keep a separate summary for each row.

## Frozen observation counterexamples

Define a deliberately generous limited observation at a decision boundary:
current mark, the declared benchmark value, and dealer inventory. It reveals
neither L's cash, holdings, and debt nor D/S cash. Equal limited observations
do not imply equal latent states.

Use two admissible initial states with the shared accounts and reference
exponential law at value 100, except L debt is 750 in state A and 700 in state B.
Both have the same limited observation before the named value-98 intervention.
Under the same post-intervention law, compare tick-0 forced sale, headroom, and
mark. If they differ, the response is not identified from this observation alone.
Name L's collateral/debt or directly measured margin headroom as the missing
information. A reported range over A/B is a finite scenario set, not a
probabilistic interval.

For structural uncertainty, hold state A fixed and compare E versus H. Both
give the same pre-intervention limited observation at zero dealer inventory,
yet their finite post-shock execution rules may yield different paths. Keep this
law uncertainty separate from A/B's hidden-state uncertainty.

## Acceptance and failure handling

- All variants conserve transaction cash and asset units, respect cash/holding
  and inventory limits, and retain unpaid debt after default.
- H's buy/sell integrals and cash caps are consistent with its curve; E's
  existing results remain unchanged under default parameters.
- K uses only start-of-tick signals whose lags have elapsed.
- The A/B observation equality is exact under the stated map; differing
  responses are reported as non-identification, not averaged into a forecast.
- No model probability, market fit, causal estimate, or trading edge is claimed.

Record code/protocol hashes in the output receipt. Keep this protocol and its
results separate from the BTC Experiment 001 protocols and data.
