# MFSM reference: one-step responses visible from the pre-shock mark

Version: `MFSM-RE-OBS-1`
Date: 2026-09-25
Status: completed synthetic observability check under the [frozen protocol](../experiments/mfsm_reference_observability_001.json)

Question: after the named benchmark shock, which one-step responses are determined by information visible before the shock?

The restricted observer sees only the pre-intervention mark from `price(state, law)`. In both frozen cases that mark is 100. The declared shock then sets the benchmark from 100 to 98, and the existing reference transition runs for one step. Neither case determines the next mark. The hidden-debt case also leaves the forced-sale indicator undetermined.

## Receipt

The [machine-readable receipt](../artifacts/mfsm_reference_observability_result.json) keeps three separate objects: the full-state oracle table, the restricted observer's answer, and a headroom-enhanced privileged diagnostic. Reproduce it with:

```bash
uv run --locked python scripts/run_mfsm_reference_observability.py \
  --output /tmp/mfsm_reference_observability_result.json
```

The script refuses to overwrite an existing output. It uses the invented accounts and parameters in the protocol. No prices, order books, fitted parameters, probabilities, or trading returns enter the check.

| Source | SHA-256 |
|---|---|
| Protocol | `75188639e3bc85e4decf108aabccec25cdeb428fc73bc02ddaed93942670902f` |
| `src/mfsm_reference/economy.py` | `8bf6864af83b8697ede73cc973958871cc10fd9a8590b73b66087526fefbb840` |
| `src/mfsm_reference/observation.py` | `f751a5405b60bd408c2cbf36c72e8dfe1c5f9079ee0a51dbd103dc1167914c87` |
| Runner | `1e3630ca613dfb3d622270878cb6feeb192d518f6a5b1bb122b50d541de4e0c1` |

The economy-source hash is the same value stored in the [MFSM-RE-SENS-1 receipt](../artifacts/mfsm_reference_sensitivity_result.json). This run used that transition file unchanged.

## Exact assumptions

The transition is the deterministic MFSM-RE-1 member in [the reference economy](../MFSM_Reference_Economy.md). This check adds no market mechanism. Each candidate is one fully specified initial state and law. The oracle applies `value=100` to `value=98`, then calls `step()` once. That benchmark change is a declared scenario input. The public mark is not treated as a signal that reveals it.

The public observation is the scalar pre-intervention mark. It does not include debt, dealer inventory, the benchmark, account balances, a forced sale, or any post-intervention value. Comparison uses absolute tolerance `1e-9`. A forced sale counts as occurring when its quantity is strictly greater than that tolerance. Candidates are the MFSM-RE-SENS-1 pair with holder debt 750 versus 700, plus the same debt-750 state under hyperbolic impact.

Shared accounts are holder cash 0 and 10 units, dealer cash 1000 and 0 units, buyer cash 1000 and 0 units, and an empty signal history. The shared law uses impact 0.01, inventory ceiling 20, maintenance 0.25, restoration target 0.30, buyer response 20, pure lag 2, deadline 10, and restoration-target sizing. At zero dealer inventory every curve quotes the benchmark, so the common pre-shock mark is 100. Dealer inventory is zero in every candidate, and the buyer purchase is capped by current dealer inventory, so the buyer does not trade on this step.

A reported span is the minimum and maximum next mark among the declared candidates compatible with the observed mark. It carries no probability. When those candidates agree, the status is `invariant_within_declared_candidates`. That label applies only inside the declared set. When none of the declared candidates match the mark, the status is `incompatible_observation`. The two frozen cases match the mark, so their statuses come from disagreement. The empty-match status is part of the same rule and is covered by the tests.

## Oracle audit table

The oracle knows the state and the law. These rows are the audit record. They are separate from the observer's answer. In the receipt, each stored law is the pre-shock law, with benchmark 100. The next mark is the result of setting that benchmark to 98 and calling `step()` once.

| Candidate | Debt | Curve | Pre-shock headroom | Next mark | Forced sale | Sale occurs | Mode |
|---|---:|---|---:|---:|---:|---|---|
| `debt_750_exponential` | 750 | exponential | 0 | 95.88971904482011 | 2.17687074829932 | yes | `NORMAL` |
| `debt_700_exponential` | 700 | exponential | 50 | 98.0 | 0 | no | `NORMAL` |
| `debt_750_hyperbolic` | 750 | hyperbolic | 0 | 95.91211717709719 | 2.17687074829932 | yes | `NORMAL` |

Pre-shock headroom is maintenance headroom at benchmark 100. It is recorded here because the oracle can compute it. It is not part of the public observation.

## Restricted observer

Both cases condition on the observed pre-shock mark 100. Two declared candidates are compatible in each case.

| Case | Compatible candidates | Next-mark minimum | Next-mark maximum | Forced-sale outcomes | Status | Witnesses |
|---|---:|---:|---:|---|---|---|
| `hidden_debt` | 2 | 95.88971904482011 | 98.0 | no, yes | `not_identified` | `debt_750_exponential`, `debt_700_exponential` |
| `impact_law` | 2 | 95.88971904482011 | 95.91211717709719 | yes | `not_identified` | `debt_750_exponential`, `debt_750_hyperbolic` |

The witness pair is the first protocol-order pair whose one-step responses disagree. The observer record names those candidate ids and the response span. It does not contain debt, inventory, balances, headroom, or mode. The ids are labels in the declared catalog; reading the hidden debt or the curve requires the oracle table.

## What remains unidentified

From the pre-shock mark alone:

- In `hidden_debt`, the two compatible candidates produce next marks 95.88971904482011 and 98.0. Debt 750 sells 2.17687074829932 units. Debt 700 sells none, and the mark stays at the shocked benchmark because dealer inventory remains zero. The forced-sale indicator therefore takes both values.
- In `impact_law`, both candidates sell 2.17687074829932 units. Both quote the shocked benchmark at zero inventory, and the restoration size uses that quote. The next marks still differ: 95.88971904482011 on the exponential curve and 95.91211717709719 on the hyperbolic curve. The shared sale indicator leaves the mark response unidentified.

Each span is the set of one-step responses of the two declared candidates in that case.

## Which added measurement separates the candidates

The privileged diagnostic adds pre-intervention maintenance headroom to the public mark. It is an audit reading, not public data. In this run it only removed candidates.

For `hidden_debt`, headroom 0 retains `debt_750_exponential` and removes `debt_700_exponential`. Headroom 50 does the reverse. The holder's debt balance separates the same pair. With either reading, one declared candidate remains, and that candidate's oracle row is the one-step response inside the reduced list. Headroom 0 gives the debt-750 exponential row. Headroom 50 gives the debt-700 row.

For `impact_law`, both candidates have pre-shock headroom 0, so the same reading removes nobody. Both remain compatible, and the next mark remains unidentified. Separating these curves requires a price or execution measurement at nonzero dealer inventory. The one-step marks above are one such measurement, and they are available only after the transition. The pre-shock mark does not supply them. The [sensitivity result](mfsm_reference_sensitivity_result.md) records the same finite-mark gap for this state.

The sensitivity receipt also reports post-shock headroom before trading of -15 for debt 750 and +35 for debt 700. Those figures were reproduced by this state under the shocked law. They use the benchmark change, so they are not information visible before the shock. This check does not treat them as a public observation or as the privileged diagnostic.

## Scope

The check reproduces the stored sensitivity responses exactly: debt-750 and debt-700 next marks 95.88971904482011 and 98.0, forced sales 2.17687074829932 and 0, and exponential versus hyperbolic next marks 95.88971904482011 and 95.91211717709719. No candidate was altered to obtain that match.

The result is a statement about this closed economy, this candidate list, and one transition. It leaves the reference's accounting and transition rules as they were. It does not revise MFSM-RE-1, MFSM-RE-SENS-1, MFSM-RE-TIME-1, or any empirical protocol. It does not show that the reference describes an exchange, identify a causal effect in market data, or contain a trading edge.
