# Plan to improve the canonical Market Feedback-State Model

Date: 2026-09-24
Scope: the canonical theory and its mathematical implementation
Owner decision: strengthen the model itself before expanding market experiments

## What we are trying to achieve

Make MFSM a family of explicit models that calculate how a specified state
responds to a specified disturbance, while saying when the response is uncertain
or not identified. A useful model should constrain the answer, make errors we can
diagnose, and become simpler when a mechanism adds nothing.

Preserve the existing distinctions: continuation capacity, financing headroom,
and opposing capacity differ; delays and deadlines matter; thresholds change
behavior; risk under a shock differs from harm caused by it; observations are
not the latent state.

The central weakness was that the transition law remained largely unspecified.
The vocabulary described many outcomes without forcing a particular response.
The next gains come from explicit rules, consistent accounting, conditional
predictions, and quantified uncertainty.

## Four different kinds of success

| Question | What would answer it |
|---|---|
| Is this mathematically complete? | Its domain, state, rules, observations, intervention, and initial conditions determine a valid path or declared solution set. |
| Does its mechanism describe the market? | Evidence distinguishes its causal explanation from competing explanations. |
| Does it forecast usefully? | Frozen forecasts improve relevant out-of-sample scores against strong comparators. |
| Does it improve a decision? | A prespecified decision improves the relevant loss after constraints and costs. |

Passing one row does not pass the others. A deterministic reference can establish
mathematical properties without producing calibrated probabilities or an edge.

## Corrections in this revision

| Weakness | Correction | Deliverable |
|---|---|---|
| Transition law left open | Require actions, execution, accounting, expectations, event ordering, and termination | Canonical section 4.1 and reference economy |
| Capacities can reuse the same capital | Require a joint feasible action set and consistent transfers | Canonical section 7 and accounting checks |
| Absorption can be inferred circularly from its outcome | Derive operational R-minus from resources and the response law | Canonical section 7.3 |
| Dangerous-state checklist can become an informal score | Replace it with conditional propositions and exceptions | Canonical section 16 |
| Missing belief/history rules leave the model open | Supply a complete delayed buyer rule and finite signal history | Reference sections 2–4 |
| Complete-looking reports can hide ignorance | Default unsupported outputs to `not identified`; report structural disagreement | Canonical section 26 and Research Protocol |
| Prediction can be mistaken for causal evidence | Assess mathematical, mechanistic, predictive, and decision support separately | Canonical section 2.1 and companion updates |

The [reference economy](../MFSM_Reference_Economy.md), MFSM-RE-1, contains one
asset, a leveraged holder, a dealer with finite cash/inventory room, and a delayed
buyer. Its deterministic transition and limited propositions have explicit
assumptions. Parameters are synthetic. Reproducing those propositions does not
validate the financial assumptions.

## What “reduce error” means

There is no single MFSM error number yet. These errors need different fixes:

| Error | How to detect it | Appropriate correction |
|---|---|---|
| Implementation/arithmetic | Cash or assets created; impossible balances; future information; disagreement with an analytic limit | Fix the transition/code and add a regression check |
| Incomplete model | Undefined action, counterparty, belief, reset, or event-order rule | Close that rule before interpreting paths |
| Structural misspecification | A mechanism-specific response repeatedly fails where the assumptions are meant to hold | Compare a named alternative; change the law with a documented reason |
| Observation error | Different hidden states fit the same data; stress changes proxy bias | Specify the observation law and propagate state uncertainty |
| Parameter uncertainty | Plausible parameters change the response or decision | Report ranges and seek discriminating information |
| Approximation error | Time step, truncated memory, or aggregation changes the response | Refine the approximation and show convergence or bounds |
| Forecast error | Poor calibration/loss on data not used to select the model | Diagnose the sources above and compare simple alternatives; preserve holdouts |

A solver tolerance is not forecast uncertainty. A scenario range is not a
confidence interval without further assumptions. Better historical fit is not
proof of better prediction.

## Ordered work and acceptance criteria

### Stage 1 — Complete and verify one reference member

**Deliverables in this revision:** canonical corrections, the full reference
specification, a small Python implementation, synthetic examples, and tests.

Acceptance:

- Every evolving object is state, a fixed input, or has an explicit exogenous law.
- Trades preserve cash and asset units within the declared boundary.
- The same resources cannot fund incompatible actions simultaneously.
- Buying respects signal availability and the failure deadline.
- Default does not erase unpaid debt or invent recovery.
- The no-impact limit and local headroom derivative match the equations.
- Exhaustion without buying does not create a rebound; permanent benchmark
  repricing differs from removal of an inventory discount.

These are mathematical/software checks. They do not establish market validity.

### Stage 2 — Test sensitivity to structural rules

**Completed for one synthetic parameter set in MFSM-RE-SENS-1.** The
[prespecified comparison](mfsm_reference_sensitivity_protocol.md) changes the
dealer impact curve, liquidation-sizing rule, and delayed buyer kernel while
preserving accounting and failure definitions. The
[result](mfsm_reference_sensitivity_result.md) records all paths and limits.

The comparison reports headroom, total forced sales, failure before the
deadline, and restoration of margin, with zero-impact, no-buyer, depleted-cash,
and long-delay controls. The curves share a local slope but produce different
finite marks; the lot and kernel change path magnitude or timing. These rows do
not disagree on margin restoration or failure, so no general robustness claim
follows. The no-cash/long-delay row cannot identify a delay effect because no
initial inventory discount activates buying. Preserve that diagnostic failure
rather than interpreting it as confirmation of the clock mechanism.

Acceptance: every conclusion names its required assumptions; disagreement yields
a range or `not identified`. No variant is selected because it draws a convincing
crash. An alternative curve is a new member, not evidence for the original curve.

### Stage 3 — Determine what incomplete observations can identify

**Completed as a constructive counterexample in MFSM-RE-SENS-1.** The observer
sees mark, benchmark, and dealer inventory but not holder debt. Two admissible
states with identical observations yield a forced sale versus no sale after the
same shock. The impact curves also agree on the initial observation but differ
on the finite next mark. See the [result](mfsm_reference_sensitivity_result.md).

The later [mark-only observability check](mfsm_reference_observability_result.md)
made the stricter public information boundary explicit and reproduced both
counterexamples. The subsequent
[public-history check](mfsm_reference_public_history_result.md), implemented from
the [frozen plan](mfsm_public_observability_implementation_plan.md), tested a
causal pre-shock price and anonymous-volume history over a declared 18-member
candidate catalog and two fixed preludes. With the prelude hidden, exact price
history narrowed the response for the dip-return cases, but flat histories
retained the hidden-debt ambiguity. Widening the price matching band restored
impact-law ambiguity in cases that exact measurements separated. The
predeclared anonymous-volume extension added no discrimination beyond the price
history (`P2 = P1`) for these preludes.

Acceptance met for this map: hidden debt and impact-law uncertainty remain
separate, and the result shows when the declared public history does and does
not narrow them. Holder margin headroom distinguishes the flat hidden-debt pair
only as a privileged diagnostic; sufficiently precise execution-response
measurements away from zero inventory are needed for the law pair. This does not
prove that those observations are sufficient or available in a real market.

### Stage 4 — Resolve a named limitation before adding a mechanism

**Timing diagnostic completed in MFSM-RE-TIME-1; extensions remain conditional.**
The [frozen timing protocol](mfsm_reference_timing_protocol.md) gives the
cashless dealer starting inventory and a positive buyer signal. The
[result](mfsm_reference_timing_result.md) shows that lags 0 and 1 fund the
dealer before the holder's two-tick margin deadline; lags 2 and 5, and the
no-buyer control, reach margin failure. This repairs the earlier comparison's
diagnostic flaw.
It is a theoretical existence example, not a calibrated market delay law.

Potential extensions are both long and short constraints, participant
heterogeneity, changing margin terms, or anticipation. These are optional
directions, not a requirement to add every mechanism.

For an addition, document the current member's limitation, the missing economic
rule, its update equation and observation implications, and a limiting case that
reduces to the prior member. Require a consequence that distinguishes the new law.

Acceptance: the change addresses a demonstrated limitation while preserving
accounting and falsifiability. Do not discard a mechanism merely because one
inadequate proxy fails, or retain a coordinate solely because it has a symbol.

**Simulated edge (next).** The [simulated edge plan](mfsm_sim_edge_plan.md)
adds hidden value, noise traders, many holders and an outside public-tape
trader, then tests whether an MFSM model-based trader beats naive and flexible
same-information traders after costs on frozen seeds. Each addition reduces
exactly to MFSM-RE-1 in a declared limit.

### Stage 5 — Assess a real application against its actual claims

**Underway.** The [BTC edge evaluation plan](mfsm_btc_edge_evaluation_plan.md)
defines a narrow observational forecast and short-or-flat decision test. Its
execution rules and data gates still need to be frozen and implemented before
any edge result is scored. The separately frozen
[free spot-flow screen](mfsm_free_btc_flow_001_result.md) found that one taker-sell
fraction worsened a reserved 2026 forecast against price and volume alone.
This constrains that measured proxy; it neither estimates the canonical latent
state nor tests the proposed L2 absorption interaction.

The next empirical member is now the
[observable-response development protocol](../experiments/mfsm_btc_response_001_protocol.json).
Its [field/calendar feasibility result](mfsm_btc_response_feasibility.md) found
32 local first-of-month dates with both spot quote feeds plus Bybit perpetual
L2/trades, zero required-header failures, and 20 price-defined accepted BTC
candidate events across 16 UTC weeks on those complete-input dates. This is
development feasibility only: the sample is non-continuous and previously used
for development, and the audit did not replay L2, compute response coefficients,
read new labels, fit models, or score P&L. The next gate is outcome-blind
construction of the two pretrigger response coefficients followed by freezing
same-information comparator summaries and a genuinely fresh evaluation calendar.

Select the institution, information set, observational question and path loss
explicitly; measurement and identification determine which claims are supportable.

Acceptance: financial sources, identified/partially identified quantities, and
frozen comparisons are recorded separately from mathematical checks. A flexible
same-information predictor remains a comparator for forecasting; a tie is not a
causal refutation. Decision claims also require relevant costs and constraints.

## Instructions for the next model or coding agent

1. Read the canonical file and reference economy before changing symbols.
2. Preserve primitive accounts, derived responses, and observed measurements as
   distinct objects. Do not add a universal fragility score.
3. Work on the earliest incomplete task above with one coherent change. The
   public-history Stage 3 task and the MFSM-BTC-RESPONSE-1 field/calendar
   feasibility gate are complete. Next implement only outcome-blind response-
   feature extraction on the declared development dates, report availability and
   feature distributions, then freeze neutral same-information comparator
   summaries and a fresh evaluation calendar before any scoring. Do not collect
   more data to compensate for an unobservable variable, and do not add a
   mechanism solely because a canonical symbol lacks an equation.
4. State the error or unanswered question and its discriminating check first.
   Do not choose a mechanism after seeing a desired result.
5. After a transition change, run accounting, timing, limiting-case, and relevant
   mathematical checks. Record assumptions, version, verification, and limits.
6. Preserve previous empirical protocols/results. A theory revision does not
   silently revise an earlier frozen empirical claim.

The reference and its structural comparison supply response-generating members
and one explicit non-identification result. Whether any member describes a real
market remains open.
