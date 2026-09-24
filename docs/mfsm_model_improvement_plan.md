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

**Remaining; the recommended next step.** Prespecify a small set of alternatives:
another admissible dealer impact curve, a different liquidation-sizing rule,
and a distributed buyer delay with its own closed state. Preserve the accounting
and failure definitions so the comparison has a clear meaning.

Compare headroom response, total forced sales, failure before the deadline, and
restoration of margin. Include zero-impact, no-buyer, depleted-cash, and long-delay
limits. State which conclusions survive, which depend on assumptions, and which
disappear.

Acceptance: every conclusion names its required assumptions; disagreement yields
a range or `not identified`. No variant is selected because it draws a convincing
crash. An alternative curve is a new member, not evidence for the original curve.

### Stage 3 — Determine what incomplete observations can identify

**Remaining.** Use this same economy and hide participant cash/positions. Specify
what the observer receives and when. Construct two hidden states compatible with
those observations and check whether their disturbance responses differ.

Acceptance: separate state uncertainty from law/parameter uncertainty. If the
observations permit opposite responses, report non-identification and name the
additional observation needed. Do not fill missing information with a score.

### Stage 4 — Add a mechanism only for a named limitation

**Remaining and conditional.** Potential extensions are both long and short
constraints, participant heterogeneity, changing margin terms, or anticipation.
These are optional directions, not a requirement to add every mechanism.

For an addition, document the current member's limitation, the missing economic
rule, its update equation and observation implications, and a limiting case that
reduces to the prior member. Require a consequence that distinguishes the new law.

Acceptance: the change addresses a demonstrated limitation while preserving
accounting and falsifiability. Do not discard a mechanism merely because one
inadequate proxy fails, or retain a coordinate solely because it has a symbol.

### Stage 5 — Assess a real application against its actual claims

**Later.** Select the institution, information set, intervention or observational
question, and path loss once the applicable member is explicit. Measurement and
identification determine which claims are supportable.

Acceptance: financial sources, identified/partially identified quantities, and
frozen comparisons are recorded separately from mathematical checks. A flexible
same-information predictor remains a comparator for forecasting; a tie is not a
causal refutation. Decision claims also require relevant costs and constraints.

## Instructions for the next model or coding agent

1. Read the canonical file and reference economy before changing symbols.
2. Preserve primitive accounts, derived responses, and observed measurements as
   distinct objects. Do not add a universal fragility score.
3. Work on the earliest incomplete stage above with one coherent change.
4. State the error or unanswered question and its discriminating check first.
   Do not choose a mechanism after seeing a desired result.
5. After a transition change, run accounting, timing, limiting-case, and relevant
   mathematical checks. Record assumptions, version, verification, and limits.
6. Preserve previous empirical protocols/results. A theory revision does not
   silently revise an earlier frozen empirical claim.

The current revision supplies a specific response-generating member. Whether
its rules describe a real market remains open.
