# MFSM public-history observability: implementation plan

Date: 2026-09-26
Status: completed as `MFSM-RE-PUBHIST-1` on 2026-09-27
Scope: the existing synthetic `MFSM-RE-1` economy, before another market-data collection effort

Completion: the frozen protocol is
`experiments/mfsm_reference_public_history_001.json`; the machine-readable
receipt is `artifacts/mfsm_reference_public_history_result.json`; and the
[result](mfsm_reference_public_history_result.md) records the identification
findings and limits.

## Decision this work must make

Can a restricted observer determine a **one-step response to the declared
benchmark shock** from measurements available before the shock? If not, which
response components remain ambiguous, and does a *public* price history narrow
them? The response is the next mark and whether any holder sale occurs. A
reported mark span is conditional on a declared candidate set; it is not a
confidence interval or a forecast probability.

The completed [mark-only check](mfsm_reference_observability_result.md) is the
control. It found that the same pre-shock mark of 100 admits a forced sale or no
sale when debt is hidden, and different next marks when the impact curve is
unknown. Those two counterexamples establish insufficiency of one mark. They do
not show whether an observable *history* resolves either ambiguity.

## Fixed boundary

- Keep the transition, accounts, impact formulas, and event ordering in
  [`MFSM-RE-1`](../MFSM_Reference_Economy.md) and
  `src/mfsm_reference/economy.py` unchanged. The study changes the observation
  map and candidate filtering, not the economy or the canonical theory.
- Reuse the named `value: 100 -> 98` shock and one-step response from
  `MFSM-RE-OBS-1`. The shock is a scenario input applied **after** the history;
  it is not an observation from which the observer infers hidden state.
- An abstract tick is not an exchange second. The benchmark `value` is an
  invented exogenous input in this economy, not an observable market fundamental.
  The primary observer must treat the prelude path as hidden. A known-path
  analysis is permitted only as a separately labeled controlled diagnostic.
- Do not introduce an order book, liquidation-distance distribution, fitted
  probabilities, P&L, or a trading-edge claim. The reference economy has no
  public L2 feed from which those objects could be honestly computed.

## Freeze before running the comparison

Create `experiments/mfsm_reference_public_history_001.json`, versioned
`MFSM-RE-PUBHIST-1`, before generating response results. Pin the following
choices there and hash the protocol in the receipt:

| Choice | Initial contract |
|---|---|
| Initial accounts | The existing `MFSM-RE-OBS-1` accounts: holder 10 units and no cash; dealer 0 units and 1000 cash; buyer 0 units and 1000 cash. |
| Finite candidate catalog | Cross holder debt `{700, 725, 750}`, impact coefficient `{0.005, 0.01, 0.015}`, and impact curve `{exponential, hyperbolic}`. Hold all other existing law fields fixed. These 18 candidates are illustrative, not an inferred market distribution. |
| Common preludes | Three transitions with benchmark paths `[100, 100, 100]` and `[100, 99, 100]`, each ending before the named shock. Apply the same path to every candidate; do not choose a path because it separates candidates. |
| Observation maps | `P0`: final pre-shock mark only; `P1`: initial mark and each pre-shock post-transition mark; `P2`: `P1` plus anonymous total executed units per transition. Total units are `forced_sale + buyer_purchase` internally, but the observer never receives either component or a trader label. |
| Observation matching bands | Exact setting: `1e-9` price units and `1e-9` asset units for total volume. Synthetic wider setting: `0.05` price units and `0.1` asset units. Match every observed field within its own absolute band. These are bands around the noiseless traces generated below, not estimates of exchange feed error. |
| Response comparison | Hold the **next-mark agreement tolerance** at `1e-9` price units and the **sale-occurrence threshold** at `1e-9` asset units in both observation settings. Two responses disagree when their next marks differ by more than `1e-9` or their sale-occurrence values differ. Observation bands must never set either response threshold. |
| Truth cases | Generate one observed trace from each of the 18 candidate configurations under each prelude: 36 possible histories. Treat the configuration and path IDs as oracle metadata. The primary observer filters **all 36** possible histories without receiving either ID. A secondary known-path diagnostic may filter the 18 histories sharing the truth case's path, clearly labeled as privileged scenario knowledge. |
| Response rule | At the final pre-shock state of every compatible candidate, apply the same `100 -> 98` benchmark change and call `step()` once. Report the minimum/maximum next mark, possible sale-occurrence values, compatible count, and a pair of disagreeing witnesses where one exists. |

All initial candidates must pass the economy's parameter and state validation.
The runner must check that a prelude does not leave a candidate in a terminal
mode or with a benchmark other than 100 at the decision boundary. If a
predeclared case fails, record the failure and its cause; do not silently replace
that candidate or path after seeing responses. A later revision gets a new
protocol version.

Under these exact preludes, `P2` is an expected **negative control for volume's
incremental value**. The flat path has no trades. On `[100, 99, 100]`, debts
700 and 725 do not sell; debt 750 requests the same restoration sale,
`57 / 29.7 ≈ 1.91919` units, at the dip's pretrade mark of 99 for every impact
configuration. Initial dealer inventory is zero, its limits do not bind, and
the two-tick buyer delay with empty signal history prevents a buyer trade in
these three transitions. The price history already separates the trade/no-trade
groups at both declared price bands. Thus `P2` should match `P1`; a difference
would call for an audit of the adapter or this deduction. This design cannot
establish whether volume helps when buyer activity or repeated trading varies.
A separate, mechanically motivated prelude would need its own freeze before
testing that question; do not search paths for a favorable response result.

## Implementation sequence

### 1. Add a causal history adapter

Extend `src/mfsm_reference/observation.py` or add a small adjacent module.
Generate each prelude by applying its benchmark value and calling the existing
`step()` once per tick. Store a public record only after each completed pre-shock
transition: mark and, for `P2`, total executed units. Include the initial mark
as a separate record. The adapter may read the full state to simulate candidate
paths, but its public record must exclude debt, balances, dealer inventory,
benchmark or prelude ID, margin mode, attributed forced sales, headroom, and all
post-shock values. The oracle table may retain those fields for audit in a
separate section.

Use absolute fieldwise compatibility against the observed trace. Do not sort,
backdate, impute, or normalize away a missing tick. Different trace lengths are
incompatible. For a fixed candidate catalog and error bands, `P2` matches must
be a subset of `P1` matches, which must be a subset of `P0` matches. Wider error
bands cannot remove a previously compatible candidate. Keep observation matching,
next-mark response agreement, and sale occurrence as separate arguments or
types. The existing mark-only `observer_envelope()` passes one tolerance to all
three purposes; do not reuse that single-tolerance interface for the wider
observation setting or change the frozen `MFSM-RE-OBS-1` behavior.

### 2. Run every truth case through every map

Add `scripts/run_mfsm_reference_public_history.py`. Load the frozen protocol,
generate all 36 candidate histories, and form the `P0`/`P1`/`P2` observer records
at both error settings. Report the pooled, path-hidden observer first and the
known-path diagnostic separately. Preserve the existing labels:
`not_identified`, `invariant_within_declared_candidates`, and
`incompatible_observation`. Invariance means only agreement among the matched
members of this catalog. Keep the oracle's hidden state, benchmark path, and
response values separate from each observer record.

Write a new, non-overwriting receipt in
`artifacts/mfsm_reference_public_history_result.json` with the protocol and
source hashes, all case outputs, mismatched or invalid candidates, and the exact
interpretation limits. Summarize the result in
`docs/mfsm_reference_public_history_result.md`. Do not turn counts of
compatible cases into probabilities.

### 3. Verify the discriminating question

Add `tests/test_reference_public_history.py` for these behavioral checks:

1. In the separately labeled flat-path diagnostic, the original debt-750/debt-700
   and exponential/hyperbolic configurations at impact `0.01` reproduce their
   old mark-only one-step responses.
2. Each candidate remains compatible with its own pre-shock trace; no future
   mark, sale, post-shock headroom, or prelude ID enters a public record.
3. The `P2 ⊆ P1 ⊆ P0` and wider-error monotonicity rules hold for every truth
   case, including traces with no trades. For the two declared preludes, check
   the predicted `P2 = P1` result and audit any failure before interpreting it.
4. Every `not_identified` witness really shares the selected observation within
   its error bands and disagrees under the fixed response tolerances. Widening
   observation bands may change compatibility but must leave every candidate's
   response and pairwise response disagreement unchanged; in particular, the
   original impact-curve mark gap of about `0.0224` must not disappear merely
   because the observation price band becomes `0.05`. Also test that a positive
   sale between `1e-9` and the `0.1` volume band still counts as a sale.
5. Unequal trace lengths are incompatible, and a trace matching no catalog
   member returns `incompatible_observation` with no invented response span.
6. Accounting and transition results match the unmodified reference economy;
   the prior observability receipt remains reproducible.

Run the focused reference-economy, sensitivity, timing, old observability, and
new history tests. Review the generated receipt and final diff for hidden-field
leakage and unintended theory or empirical-protocol changes.

## Interpretation and stopping rule

The result must answer, separately for hidden debt and impact-law uncertainty:

- Which candidates and response values survive `P0`, `P1`, and `P2`?
- Does a public pre-shock trace narrow the response when the benchmark prelude
  is hidden, and how much narrower is the separately labeled known-path result?
- Does declared bounded observation error restore ambiguity that exact
  measurements appeared to remove?
- Does the predicted `P2 = P1` negative control hold? It says nothing about
  volume in other trading histories.
- Which missing quantity would actually discriminate the remaining candidates,
  and is that quantity public in the *model*? Privileged headroom is a diagnostic,
  never a proposed public feature.

If the answer remains ambiguous, publish the span and `not_identified`; that is
a successful identification check. If compatible candidates agree, state only
`invariant_within_declared_candidates`. Neither outcome licenses the claim that
the catalog is complete or that the economy describes BTC.

The error comparison starts from **noiseless** truth traces and widens matching
bands around those particular observations. It does not test all observations
that measurement error could produce inside a band. Do not describe its result
as robust over every perturbation. Such a claim would require separately
predeclared perturbed observations and a new analysis.

After this check, decide whether a public-data response question exists that can
be measured with a small existing BTC sample. Any empirical protocol must map
each required synthetic observation to a real feed field and timestamp, name a
forecast target, preserve a fresh evaluation period, and compare against simple
and flexible models on the same information. If that map cannot be made without
hidden benchmark, debt, or trader attribution, stop at partial identification;
do not collect a large archive to compensate for an unobservable variable.

## Effort and handoff

The causal history adapter, frozen protocol, focused tests, and first receipt
should take roughly 2–3 working days for one developer familiar with this repo.
Checking candidate admissibility, error bands, and interpretation may take
another 2–4 days. These are estimates, not a deadline or a promise of an edge.
No API key, paid dataset, or long live capture is required for this synthetic
stage.

Start by reading the [canonical model](../Market_Feedback_State_Model_Canonical.md),
the [reference economy](../MFSM_Reference_Economy.md), the
[existing observability protocol](../experiments/mfsm_reference_observability_001.json),
and its [result](mfsm_reference_observability_result.md). Freeze the new protocol
before inspecting its generated response table. Keep `MFSM-RE-OBS-1` immutable.
