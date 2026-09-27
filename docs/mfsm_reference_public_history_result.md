# MFSM reference public-history observability result

Version: `MFSM-RE-PUBHIST-1-result-1`
Date: 2026-09-27
Status: synthetic observability check completed; no empirical data or model fit

Frozen protocol:
`experiments/mfsm_reference_public_history_001.json`
Protocol SHA-256:
`f97ad41660885847975d76025fc9ae6ec9ca74217e9febbeb475ba4c12bca7a9`

Machine-readable receipt:
`artifacts/mfsm_reference_public_history_result.json`
Receipt SHA-256:
`0c166ea53ef7c8ccb269674f0965f4247340b6b6cfe893fa2854e9216abe4af2`

## Question

Can a causal public price history available before the named `100 -> 98`
benchmark shock narrow the one-step MFSM-RE-1 response relative to one final
pre-shock mark? Does anonymous total executed volume add anything beyond that
price history for the two predeclared preludes?

The answer is conditional on the frozen 18-member catalog crossed with two
three-tick preludes. It is not an identification claim for markets outside that
catalog and it is not a probability statement.

## Frozen comparison

The catalog crosses holder debt `{700, 725, 750}`, impact coefficient
`{0.005, 0.01, 0.015}`, and `{exponential, hyperbolic}` impact curves.
All other MFSM-RE-1 law fields are fixed. The two preludes are
`[100, 100, 100]` and `[100, 99, 100]`, giving 36 possible histories.

The public maps are:

- `P0`: final pre-shock mark only.
- `P1`: initial mark plus the mark after each completed pre-shock transition.
- `P2`: `P1` plus anonymous total executed units per transition.

Exact matching uses `1e-9` price and unit bands. The wider synthetic setting
uses `0.05` price units and `0.1` asset units. The one-step response
comparison remains fixed at `1e-9` for the next mark and `1e-9` units for
sale occurrence in both settings.

## Aggregate result

The table counts truth histories whose compatible candidate responses are
invariant within the declared catalog versus not identified.

| Observer scope | Setting | Map | Invariant | Not identified |
|---|---|---:|---:|---:|
| path hidden | exact | P0 | 6 | 30 |
| path hidden | exact | P1 | 18 | 18 |
| path hidden | exact | P2 | 18 | 18 |
| path hidden | wide | P0 | 0 | 36 |
| path hidden | wide | P1 | 12 | 24 |
| path hidden | wide | P2 | 12 | 24 |
| known-path diagnostic | exact | P0 | 18 | 18 |
| known-path diagnostic | exact | P1 | 18 | 18 |
| known-path diagnostic | exact | P2 | 18 | 18 |
| known-path diagnostic | wide | P0 | 12 | 24 |
| known-path diagnostic | wide | P1 | 12 | 24 |
| known-path diagnostic | wide | P2 | 12 | 24 |

The compatible-set invariants held for every truth case:
`P2 subseteq P1 subseteq P0`, and widening an observation band never removed
a previously compatible history.

The predeclared negative control also held everywhere: `P2 = P1` for all 36
truth histories, both observer scopes, and both observation settings. Anonymous
total volume adds no incremental discrimination in this frozen design.

## What the price history actually changes

For low-debt dip-return histories, the final pre-shock mark alone is ambiguous
when the prelude is hidden because it also matches flat histories. For example,
the `d700/i010/exponential` dip-return truth history has:

- exact pooled `P0`: 30 compatible histories, next-mark span
  `94.8516808579 .. 98.0`, both sale and no-sale responses, status
  `not_identified`;
- exact pooled `P1`: 12 compatible histories, next mark exactly `98.0`,
  no forced sale, status `invariant_within_declared_candidates`;
- `P2`: the same 12 histories and the same response as `P1`.

Thus public price history can narrow the response by revealing which pre-shock
path is consistent with the observation. Once the path is given as privileged
scenario knowledge, this particular gain disappears: the known-path `P0`
diagnostic already has the same aggregate exact identification pattern as
`P1`.

Flat histories remain ambiguous. With a flat public trace, debt 700/725 and
debt 750 are observationally compatible while the named shock can produce
no sale or a forced sale. For the flat `i010` cases, the old mark-only
counterexample is reproduced: debt 700 gives next mark `98.0` and no sale,
while debt 750 under the exponential curve gives next mark
`95.8897190448` with a forced sale. A price history that never activates the
hidden constraint does not reveal that hidden debt.

## Bounded observation error restores structural-law ambiguity

Under exact observations, each debt-750 dip-return history is a singleton
within the declared catalog. The wider `0.05` price band merges the
exponential and hyperbolic histories at the same debt and impact coefficient.

At impact `0.01`, for example:

- exponential: next mark `96.1371251698`;
- hyperbolic: next mark `96.1546085233`.

Both have no forced sale after the named shock, but the marks differ by much
more than the fixed `1e-9` response tolerance. The wider observation band
therefore changes compatibility while leaving the response-disagreement rule
unchanged, and the status becomes `not_identified`.

This is a comparison around noiseless generated traces. It does not establish
robustness over every perturbation inside the declared bands.

## What remains unobserved

Two distinct limitations remain.

First, on flat histories the decisive quantity for sale occurrence is hidden
holder constraint state, represented here by debt/headroom. No public price or
anonymous-volume event occurs before the shock to reveal it. Privileged
headroom would separate those candidates, but it is not a public observation
and is not proposed as a market feature.

Second, after the debt-750 dip has created inventory, the impact-law choice can
remain ambiguous once price measurements are widened. Distinguishing those
curves requires information about execution response away from zero inventory
that is precise enough to separate their price-impact laws. The anonymous
total-volume field used here cannot do so because it is the same restoration
quantity across those configurations and adds no information beyond the price
path.

## Verification

The focused new checks passed:

- 7/7 `tests/test_reference_public_history.py`.

The plan-authorized reference suite also passed:

- 56/56 across `test_reference_economy.py`,
  `test_reference_sensitivity.py`, `test_reference_timing.py`,
  `test_reference_observability.py`, and
  `test_reference_public_history.py`.

The new runner writes the receipt create-only, keeps oracle metadata separate
from observer records, checks map-subset and wider-band monotonicity, and refuses
to write the official result if the predeclared `P2 = P1` negative control
fails.

## Interpretation boundary

This result establishes only a finite synthetic observability statement about
MFSM-RE-1. It does not estimate a latent market state, validate the reference
economy on BTC, provide a confidence interval, fit a predictive model, or show a
trading edge.

A real-data continuation should proceed only if each required public synthetic
observation can be mapped to a causal feed field and timestamp without importing
hidden benchmark, debt, headroom, or trader attribution. More market data cannot
repair a variable that is not observable under the proposed information set.
