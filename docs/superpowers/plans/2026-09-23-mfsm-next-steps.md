# MFSM Empirical Implementation Plan and Agent Handoff

> **For agentic workers:** Use `superpowers:executing-plans` when available to implement this plan task by task. Execute sequentially by default. Use parallel agents only when the user or applicable instructions authorize them. Checkboxes track completed, verified work.

**Goal:** Determine whether a narrow, reproducible MFSM implementation improves post-selloff crypto risk prediction beyond a strong baseline, then evaluate whether it improves an actual risk decision.

**Architecture:** Preserve the canonical theory while implementing Experiment 001 as an observational prediction pipeline. Separate immutable observations, event/label construction, shared features, model fitting, and evaluation. Trading execution and stock-market applications follow separate evidence gates.

**Tech stack:** Proposed Python package using Parquet, Polars, scikit-learn, and pytest. Select and lock compatible versions during implementation; use DuckDB only if a concrete data-access need warrants it. No trading engine is required for the first milestone.

**Spec:** [Experiment 001](../../../experiments/Experiment_001_Crypto_Liquidation_Response.md), governed by the [canonical model](../../../Market_Feedback_State_Model_Canonical.md) and [research protocol](../../../Research_Protocol.md).

**Status:** Proposed execution handoff, created 2026-09-23 against repository commit `02436fb`. This document creates no empirical result, frozen release, or authority to access the ETH holdout. Recheck repository state before execution.

## 1. Start here

The repository currently contains a conceptual model, mathematical and empirical foundations, and a pre-freeze experiment specification. At the reviewed revision there is no executable implementation, research dataset, fitted model, or empirical performance report. The freeze manifest is pending.

The immediate priority is **Milestone 1: Tasks 1–4**. Deliver a BTC data-readiness audit and a reproducible pipeline verified against synthetic cases. Real BTC extraction requires the audited schema and authorized data access. Missing data access does not prevent construction of the synthetic pipeline.

Read these sources in order before changing scientific definitions:

1. [Canonical model](../../../Market_Feedback_State_Model_Canonical.md).
2. [Mathematical foundations](../../../Mathematical_Foundations.md), especially state closure, measurement, delay, and the application workflow.
3. [Empirical foundations](../../../Empirical_Finance_Foundations.md), especially measurement and validation requirements.
4. [Research protocol](../../../Research_Protocol.md).
5. [Experiment 001](../../../experiments/Experiment_001_Crypto_Liquidation_Response.md) and its [freeze manifest](../../../experiments/Experiment_001_Freeze_Manifest.yaml).

The experiment owns numerical definitions. This plan organizes implementation and proposes additional diagnostics; it does not silently amend those definitions. If the current specification differs from this plan, record the difference and follow the authoritative specification. Escalate material scientific conflicts before dependent work.

## 2. Global constraints

- Follow applicable `AGENTS.md` instructions and preserve existing user changes. Inspect index status before index use or mutation, following the active code-intelligence policy.
- Keep ETH observations sealed until all Experiment 001 confirmation gates are satisfied. Pre-freeze ETH planning may use public field documentation without observations, statistics, or event counts.
- Apply the published trigger, one-second grid, two-hour lockout, 15-second decision delay, barriers, primary 30-minute horizon, and missing-label rules exactly. Keep the 120-minute horizon secondary.
- Every feature must use information actually available by the decision timestamp. Record event time and receipt/availability time separately. Missing receipt history must be disclosed; manufactured receipt times are not historical evidence.
- Give B4 and MFSM identical normalized neutral inputs, episode rows, timestamps, and calibration/scoring treatment. MFSM adds only the specified deterministic combinations. B4's search budget must be no smaller.
- Keep liquidation flow, aggressive selling, open interest, actual leverage, and collateral headroom distinct. Estimated proxies retain their identification limits.
- Version material changes to labels, features, data semantics, holdout rules, or scoring in the experiment specification and `CHANGELOG.md` before affected evaluation. Preserve original definitions and results.
- Keep new scientific ideas experimental. Canonical state expansion requires the evidence specified by the research protocol.
- Use synthetic data solely to verify software behavior. Label every synthetic artifact visibly; it provides no evidence of market realism or predictive edge.
- Store raw data and large model artifacts outside tracked source files. Record their locations, hashes, schema versions, and access conditions. Preserve original raw observations.
- Obtain missing data-access or spending authorization when required. Continue independent local work while access is unresolved. This document does not authorize purchases, account creation, live trading, publication, or uploading private data.

## 3. Review focus

| Failure condition | Required behavior | Owning task |
| --- | --- | --- |
| An exchange message occurred before the decision but arrived afterward | It cannot affect features or a trigger that was supposedly observable earlier | Tasks 2–4 |
| A liquidation side denotes position direction, or price denotes bankruptcy price | Adapter preserves those meanings and applies an explicit conversion policy | Task 2 |
| A book reset, sequence gap, cancellation, or incomplete dwell interval occurs | Required features become unavailable or receive exactly the specified conservative credit | Task 4 |
| Label data are missing during stress or have not matured at a fit cutoff | Missing is not negative; immature labels do not enter training; exclusions remain visible | Tasks 3 and 5 |
| A model run attempts ETH access before freeze or changes configuration afterward | Access/scoring is rejected and the attempt is recorded | Tasks 2 and 6 |

## 4. Proposed file ownership and interfaces

These are proposed new paths, not existing APIs. Reuse an equivalent implementation if one exists when execution begins.

| Path | Responsibility |
| --- | --- |
| `artifacts/e001_data_readiness.md` | Provider coverage, field semantics, availability limits, decisions, and blockers |
| `experiments/e001_data_schema.yaml` | Versioned observation fields, units, composite definition, validity and availability rules |
| `experiments/e001_run_config.yaml` | Resolved experiment parameters, feature list, missingness rules, split/tuning/calibration settings |
| `pyproject.toml` and a dependency lockfile | Reproducible package and test environment |
| `src/mfsm_e001/data.py` | BTC-only loading, venue adapters, schema checks, normalized observations |
| `src/mfsm_e001/events.py` | Independent spot composite and trigger/episode construction |
| `src/mfsm_e001/labels.py` | Barrier passage, competing outcomes, label eligibility and exclusions |
| `src/mfsm_e001/features.py` | Book reconstruction, shared summaries, normalized features, MFSM combinations |
| `src/mfsm_e001/validation.py` | Temporal folds, availability gates, model fitting and calibration |
| `src/mfsm_e001/evaluation.py` | Paired scores, weekly uncertainty, coverage, and diagnostics |
| `src/mfsm_e001/cli.py` | Explicit BTC build/fit/evaluate commands and a separately guarded ETH command |
| `tests/test_data.py`, `test_events.py`, `test_labels.py`, `test_features.py`, `test_validation.py`, `test_holdout.py` under `tests/` | Behavioral checks at the owned boundaries |
| `artifacts/e001_implementation_status.md` | Resumable progress and exact commands/results |

Pass versioned tables between stages: observations → composite/book state → triggered episodes → labels/features → predictions → scores. Use a stable episode identifier shared by every stage. Maintain a trigger ledger even when an episode cannot be scored.

Before implementation, define each table's keys, types, units, nullable fields, timestamp meanings, schema version, and source provenance in the data contract. Feature rows carry their decision time and latest input-availability time. Label rows carry horizon, outcome, validity/reason, and the time when the label became available. Prediction rows carry episode, model, probability, split, and run identifier.

## 5. Milestone 1 — Audit and reproducible BTC pipeline

### Task 1: Resolve data feasibility and record scientific decisions

**Files:** Create `artifacts/e001_data_readiness.md` and `artifacts/e001_implementation_status.md`. Read the current experiment and manifest; update scientific documents only when a material definition is deliberately changed.

- [ ] Inspect current Git status, existing implementation, applicable instructions, and available BTC data. Record what exists without opening ETH data or summarizing mixed-asset files.
- [ ] Audit candidate providers using their historical coverage descriptions and current official documentation. Discover external URLs through Open Web Search and archive relevant known sources through the running Khiip daemon when available. Record retrieval dates and archival failures.
- [ ] For each candidate venue, document spot/perpetual coverage, contract types, trade-side meaning, liquidation-side meaning, quantity units, price meaning, sequencing/reset behavior, OI cadence, funding semantics, receipt timestamps, gaps, cost, and access restrictions.
- [ ] Specify the independent spot composite's constituents, weighting, one-second sampling, staleness limits, missing-constituent behavior, and receipt-time construction before event extraction. Distinguish methodological choices from provider facts.
- [ ] Determine whether audited observations support the experiment's shared feature panel. Select only supported contract/venue combinations. Record any scope change and required experiment version change.
- [ ] Identify unavailable inputs and the smallest owner action needed to obtain them. Complete documentation and synthetic work that does not depend on access.

**Completion:** Every required data family is marked supported with evidence, unsupported with a reason, or dependent on a named access decision. Composite construction has an exact rule. No claim of historical availability rests only on a live endpoint's existence.

**Known adapter trap to reverify:** Bybit's All Liquidation documentation identifies `S=Buy` as a liquidated long and `p` as bankruptcy price. A normalized sell-liquidation field needs an explicit side conversion; actual execution notional cannot be inferred from the field name alone. Source: [official documentation](https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation), checked 2026-09-23. Verify the historical feed version used by the dataset.

### Task 2: Establish the data contract and BTC-only ingestion

**Files:** Create the data schema, package/environment files, `data.py`, initial `cli.py`, and `tests/test_data.py` plus the initial `tests/test_holdout.py`.

- [ ] Convert Task 1 decisions into a versioned schema before extracting real research events. Declare precise conversion rules for each supported venue and contract; preserve raw records alongside normalized values.
- [ ] Build the smallest loader for the first audited BTC source. Make additional venue support depend on its own audited mapping rather than a universal guessed parser.
- [ ] Restrict development inputs to explicit BTC instruments and paths. Prevent directory discovery or preview operations from reading sealed ETH observations. Separate fixture mode from real-data mode in configuration and output provenance.
- [ ] Validate monotonic book sequence rules, resets, required units, duplicate semantics, and source timestamps. Return explicit missing/invalid reasons rather than silently replacing failures with zero.
- [ ] Write and run focused tests covering venue side conversion, contract-unit conversion, duplicate handling under audited semantics, reset/gap detection, and late-arriving messages. Verify rejected ETH access using synthetic records; real ETH data are unnecessary.

**Completion:** A reproducible command normalizes a small audited BTC sample, or a clearly labeled synthetic sample when access is unavailable. Invalid inputs have deterministic outcomes. Dependency versions and schema version are recorded. A real-data run cannot silently substitute fixtures.

### Task 3: Implement trigger and outcome construction

**Files:** Create `events.py`, `labels.py`, `tests/test_events.py`, and `tests/test_labels.py`; add BTC build commands to `cli.py`.

- [ ] Implement the composite and event rules from the schema and Experiment 001 Sections 4–6. Log event eligibility, threshold crossings, lockout membership, decision times, and rejected triggers.
- [ ] Keep trigger availability consistent with receipt times. If a historical source cannot support the prescribed decision timing, document the limitation and resolve it as an explicit design decision rather than shifting the clock silently.
- [ ] Implement first passage on the specified grid and retain the secondary three-way outcome. Store separate validity for each horizon and explicit exclusion reasons.
- [ ] Build the following hand-checkable synthetic cases before relying on real observations:

| Case | Expected result |
| --- | --- |
| First valid five-minute return crosses from above −1% to at/below −1% | Exactly one accepted trigger |
| Another crossing within two hours | Same episode; no second observation |
| New crossing exactly at the lockout boundary | Eligible if the other trigger rules hold |
| Decision price 100; subsequent first barrier hit is 98.9 | Downside-first; primary label 1 when within 30 minutes |
| Decision price 100; subsequent first barrier hit is 100.8 | Recovery-first; primary label 0 |
| Complete 30-minute path stays between 99 and 100.75 | Neither-by-horizon; primary label 0, not an exhaustion label |
| Missing/stale required grid price before any barrier hit | Label unavailable; exclusion recorded |
| Gap only after an already observed first barrier hit | First-passage label remains valid |
| Outcomes change when prices after the decision change | Labels may change; pre-decision features and trigger history must not |

- [ ] Run the event and label tests and export a fixture episode ledger with expected outcomes independently checked against the table above.

**Completion:** Triggered, locked-out, eligible, and excluded counts reconcile. The pipeline distinguishes unresolved outcomes from missing outcomes. Re-running identical inputs produces identical event and label tables.

### Task 4: Implement shared features and audit the capacity estimate

**Files:** Create `features.py`, `tests/test_features.py`, and the resolved feature portion of `experiments/e001_run_config.yaml`; extend the data schema and BTC build command.

- [ ] Implement Experiment 001 Sections 8 and 11 exactly: reconstructed books, specified flow/dwell windows, current depth, persistent additions, denominator floor and indicator, causal normalization, and identical neutral preprocessing for both models.
- [ ] Preserve source availability cutoffs through every aggregation and as-of join. If a named recovery-time feature would require observing the future, exclude it from predictors or define and version a causal alternative before fitting.
- [ ] Keep per-venue capacities separate. Mark unsupported liquidation/trade de-duplication explicitly, following the specification's contamination rule.
- [ ] Verify hand-built books covering a one-second surviving addition, removal during dwell, addition too late to mature, disappearing level, reset/gap, nonpositive pre-event denominator, and same capital repeatedly quoting and cancelling. Also verify the prescribed full 15-second rate denominator.
- [ ] Verify that modifying or appending observations unavailable at the decision cannot change any feature. Verify B4 receives every neutral component used to build an MFSM interaction.
- [ ] Record the liquidity-proxy limitation: recent displayed additions do not establish that supply will remain available during future selling. Keep a synthetic churn example demonstrating this limitation; do not present it as measured market bias.
- [ ] Specify a bounded BTC-only diagnostic comparing depth alone, the published capacity proxy, and one cancellation-aware alternative. Write the alternative's exact formula, windows, target, eligibility, and scoring before inspecting its evaluation outcomes. Keep it secondary unless a versioned experiment revision explicitly changes its role.

**Completion:** A documented command produces an episode feature/label table from fixtures, and from an authorized BTC sample when available. Features contain no future inputs. The baseline has identical shared information. Remaining data blockers and any unimplemented supported features are explicit.

**Milestone 1 handoff:** Provide implemented paths, runnable commands, observed test results, fixture outputs, schema/config versions, remaining access needs, and confirmation that ETH remains sealed. Do not call this predictive validation.

## 6. Milestone 2 — BTC development and honest evaluation

### Task 5: Fit matched models and evaluate the prespecified experiment

**Prerequisite:** Milestone 1 complete; audited real BTC data available. A fixture-only implementation cannot advance through this gate.

**Files:** Create `validation.py`, `evaluation.py`, `tests/test_validation.py`, and `artifacts/e001_btc_results.md`; finalize the run configuration and BTC fit/evaluate commands.

- [ ] Freeze an explicit BTC development design: time boundaries, inner/outer folds, normalized feature list, missing-feature treatment, tuning grid, tie-break rule, calibration method, and random seeds. Record every evaluated configuration and distinguish exploratory changes from fixed evaluation.
- [ ] Implement B0–B3 and the required primary comparison: matched calibrated histogram-based gradient-boosted classifiers for B4 and MFSM, differing only in the allowed MFSM combinations.
- [ ] Keep preprocessing, fitting, tuning, and calibration inside their permitted chronological data. Include an episode in training only after its full required label horizon has ended and its label is available. Apply identical rows and cutoffs to both primary models.
- [ ] Test split boundaries, immature labels, train/calibration/validation separation, paired row alignment, shared feature equality, tuning-budget parity, and reproducibility on synthetic data before real fitting.
- [ ] Produce paired out-of-sample probabilities and the specification's metrics. Include uncertainty grouped by UTC week, calibration, log loss, precision-recall, leave-largest-events-out results, and feasible prespecified venue/time sensitivities.
- [ ] Report all triggered episodes alongside scored episodes. Break down missing features and labels by venue/time and available pre-decision stress indicators, without inventing outcomes for excluded episodes.
- [ ] Report the capacity diagnostic separately, including the possibility that the simple depth feature performs equally well. Estimate sample feasibility and uncertainty from BTC only; minimum holdout-week eligibility is not a power guarantee.
- [ ] Apply the published BTC development gate. A nonpositive paired mean primary Brier improvement is a failed development result and leaves ETH sealed. A positive result permits preparation for confirmation; it does not establish trading edge.

**Completion:** The BTC report is reproducible from immutable inputs and saved configuration, reports losses as well as improvements, and states whether the gate passed. Missing required evaluation is a limitation, not an inferred success.

## 7. Milestone 3 — Freeze and single ETH confirmation

### Task 6: Enforce the confirmation boundary

**Prerequisite:** Positive BTC development gate, finalized scientific definitions, feasible documented shared schema, and scope/authorization to perform confirmation. A request to implement Milestone 1 alone does not authorize opening ETH.

**Files:** Update the existing freeze manifest, finalize versioned specification/configuration references, create `tests/test_holdout.py` coverage for the full gate and `artifacts/e001_eth_confirmation.md`; add the guarded ETH command.

- [ ] Verify release/tag status against actual Git objects. Follow Research Protocol Section 31.1; record resolved hashes only after the relevant frozen objects exist. Use a new experiment version when material definitions changed.
- [ ] Before ETH access, fix the BTC cutoff, ETH end timestamp, schema versions, features, model artifacts, fitting/calibration configuration, eligibility, and exclusion rules. Hash configuration, data manifests, code references, and models. Keep mutable access/status records separate from the immutable scoring configuration.
- [ ] Test that incomplete gates, mismatched immutable hashes, a nonpositive BTC gate, or an invalid evaluation period reject scoring. Use synthetic ETH-like fixtures for these software tests.
- [ ] Record first ETH access before opening observations. Check actual schema compatibility under the frozen rule. Incompatibility makes confirmation inconclusive; follow the specification rather than adapting the model to ETH.
- [ ] Score the frozen models on the identical eligible ETH episodes strictly after the BTC cutoff, with full primary windows ending within the fixed evaluation period. Apply the exact paired Brier, UTC-week bootstrap, seed, replicate count, and minimum-week rules in Section 19.
- [ ] Report success, failure, or inconclusive using the primary criterion. Preserve secondary metrics without letting them replace the endpoint. Preserve the original result before any post-confirmatory exploration.

**Completion:** A single auditable confirmation report identifies every frozen input and reports exclusion counts and the primary interval. Prediction success is described as incremental performance of an engineered representation, not identification of a causal mechanism.

## 8. Later work — separate decisions and specifications

### Task 7: Test a risk policy on untouched data

**Prerequisite:** Adequate predictive evidence and an explicit trading-policy specification. Create a separate policy document before its evaluation sample is opened.

- [ ] Select a concrete reference strategy, instrument, sizing rule, risk threshold, holding/exit rules, and treatment of unavailable signals. If no reference strategy exists, resolve that product decision before claiming decision value.
- [ ] Define the MFSM-controlled policy, original strategy, and simple volatility/liquidity filter comparator. Select thresholds using development data only.
- [ ] Specify executable contract-price fills, fees, spread, depth-dependent slippage, latency, funding, and outage behavior. A spot-composite barrier label is not a perpetual-contract fill or P&L record.
- [ ] Evaluate on data untouched by policy selection. Treat ETH used to develop a policy after confirmation as development data for that policy, not a fresh test.
- [ ] Report net return, drawdown/tail loss, turnover, exposure, missed profitable trades, and sensitivity to costs/latency. Evaluate the operational fallback during missing data.

**Completion:** Net decision value is measured against prespecified comparators on untouched observations. Any result is scoped to the tested policy, market, and period.

### Task 8: Create a stock application or simulator only when requested

For **stocks**, write a separate experiment for one mechanism, universe, and horizon. Specify auctions, market sessions, gaps/halts, corporate actions, delistings and universe selection, relevant public news availability, and borrow constraints if shorting is used. Establish stock-specific baselines and holdouts. Crypto confirmation does not validate equity behavior.

For a **market simulator**, first specify agents or aggregate transition laws, price formation, orders/cancellations, accounting, collateral/margin rules, shocks, and observation mechanisms. Define acceptance metrics against held-out real data: returns/tails, volatility persistence, order-flow dependence, spread/depth, impact, and stress recovery. Match joint and conditional behavior rather than chart appearance alone. Simulator implementation is outside Experiment 001's prediction task.

These branches require separate plans. Neither is a reason to expand the canonical state vector before the current empirical evidence exists.

## 9. Resume and completion contract

At the end of each task, update `artifacts/e001_implementation_status.md` with:

- Completed task and concrete deliverables.
- Exact commands run and observed outcomes; distinguish failed tests from unavailable checks.
- Input/configuration/schema versions and reproducibility instructions.
- Remaining scientific decisions and external blockers, with the responsible owner.
- ETH access status and next eligible task.

Mark checkboxes complete only when their outputs and acceptance conditions exist. Reconcile scope with the user's current instruction before moving to another milestone. Use the repository's commit workflow when authorized; preserve existing work and frozen references.

## 10. Copy this prompt to the next coding model

```text
Read docs/superpowers/plans/2026-09-23-mfsm-next-steps.md and the authoritative
repository documents it names. Implement Milestone 1, Tasks 1–4, sequentially.
Check current repository state first and reuse any work already completed.

Deliver a BTC data-readiness audit, exact versioned data contracts, a small
reproducible event/label/feature pipeline, and focused behavioral tests.
Use authorized BTC observations where available and clearly labeled synthetic
fixtures to verify software behavior. Keep ETH observations sealed.

Preserve the current Experiment 001 scientific definitions. Version and explain
any necessary material changes before dependent work. Ask only for missing
access, cost authorization, or decisions that materially affect correctness;
continue independent work while those are unresolved.

Finish with runnable commands, observed verification results, remaining blockers,
and an updated artifacts/e001_implementation_status.md. Stop at the Milestone 1
boundary. Do not report synthetic success as market validation or trading edge.
```
