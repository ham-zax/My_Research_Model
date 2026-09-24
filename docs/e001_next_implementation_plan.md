# Experiment 001: implementation plan to a reproducible BTC result

Updated: 2026-09-24. Tasks 1 and the synthetic software paths of Tasks 2, 3 and 6 have been implemented. The original E001 real run is `BLOCKED_TIMING`; the explicit fixture run is `PIPELINE_VERIFIED_SYNTHETIC`. Primary timing qualification, a supported real feature contract, and an original E001 BTC model result remain unfinished. A separate, owner-selected observational BTC study has now been run on free sample data; see [its result](e001_exploratory_btc_result.md). The follow-up [25 bps capacity audit](../artifacts/e001_capacity_audit_report.md) found that the downloaded books cannot measure the original proxy. A predeclared [0.5 bps near-touch experiment](e001_shallow_capacity_result.md) expanded discovery to 42 days but yielded only two valid independent measurements and no correlation. This document supersedes the earlier instruction to restart Delivery A.

## 1. Outcome and current evidence

Build one command that audits the selected BTC inputs, constructs an eligible episode dataset when the gates pass, and evaluates the prescribed B4/MFSM pair when the dataset supports it. Every run must end with a machine-readable status and a readable report, including when the correct result is insufficient evidence or insufficient data.

The research question is whether the specified MFSM feature combinations improve calibrated 30-minute downside-first prediction over the same-data B4 model. A positive BTC result permits preparation for the existing ETH confirmation protocol; it does not establish profitable trading, validate stocks, or establish a causal market mechanism.

| Verified starting point | Consequence for implementation |
|---|---|
| Public BTC recorder, immutable segments, replay and diagnostic features exist | Extend these paths; do not rebuild acquisition or start a new timing audit from scratch |
| Last recorded verification: 129 tests passed | Re-run affected checks after implementation; this number is a historical verification result |
| `receipt_v1` uses receipt-time features and always sets `primary_eligible: false` | Waiting longer or changing a Boolean cannot produce qualified data; implement evidence ingestion and qualification first |
| `_receipt_quality()` unconditionally appends missing UTC and WebSocket-delay reasons | The candidate currently has no executable transition to `qualified` |
| Candidate features use a receipt spot value internally, but `CaptureFeatureReplay.grid()` returns the parent strict grid | Expose one policy-specific grid before connecting event/label extraction; otherwise the feature and label clocks can disagree |
| Four sealed captures / six diagnostic decisions: one quarantined, five warming, zero eligible | These are software/quality observations, not six research episodes |
| Full 30-minute bid-depth scale and independently valued liquidation notional are unavailable in the audited live examples | Timing repairs alone do not make the prescribed primary feature set usable |
| 19 isolated monthly quote days yielded two history-qualified labels, both negative | This sample cannot support the matched training/calibration/evaluation design |
| The development collector was last verified stopped | Check process identity, writer lock and checkpoint; a historical `running` manifest is not live status |

Authority and evidence:

- [Experiment specification](../experiments/Experiment_001_Crypto_Liquidation_Response.md), especially Sections 4, 6, 11, 12 and 19.
- [Current implementation status](../artifacts/e001_implementation_status.md), [receipt-time revision](e001_receipt_time_revision.md), [timing contract](e001_timing_contract.md), and [live feature contract](e001_live_features.md).
- [Receipt gate results](../artifacts/e001_receipt_policy_gate_results.json), [paired feature comparison](../artifacts/e001_receipt_feature_comparison.json), and [monthly sample report](../artifacts/e001_monthly_sample_report.md).
- [Original implementation plan](superpowers/plans/2026-09-23-mfsm-next-steps.md) retains the broader confirmation and trading-evaluation work; this document supplies the next execution sequence.

## 2. Fixed constraints and decisions still outstanding

The owner chose to **prepare** a receipt-time revision and later selected a separate free observational study. Retain strict replay for reproduction. The proposed `e001-v1.3-candidate` / `E001-label-v4-candidate` versions are not activated primary definitions or freeze tags. The exploratory result does not activate either version or qualify old diagnostic rows. Primary activation requires a concrete resolved measurement/quality contract. Do not repeatedly ask for permission to write code, audit existing BTC files or run software tests.

Preserve source, receipt and monotonic timestamps, raw hashes, the 119 clean segments of interrupted run `53d688bfe33349aaab40dc8e7463c802`, and its separate `.unclean` tail. Never certify old periods from new timing probes. Use only information available by each decision; future evidence cannot repair earlier values. Preserve both spot venues, the five-second candidate quote limit, actual missingness, and the declared feature economics.

The present 100 ms source-lead rejection was copied from the collector's local-step threshold. It is a **diagnostic protective guard**, not a measured WebSocket offset or delay allowance. The present 1,815-second wait after every event-loop-delay record is also a conservative diagnostic rule, not proof that the intervening history is complete. Neither rule should be treated as a validated primary quality policy merely because tests pass.

Keep ETH sealed. Implement the model software using fixtures while real-data eligibility is unresolved; real BTC fitting must fail closed until all required contracts and data checks pass. Do not use model scores or future label outcomes to choose timing thresholds, feature proxies, acquisition dates or exclusions.

The original authorized live acquisition deadline is **2026-09-25 00:19:49 UTC**, with a **16 GiB directory-wide raw cap**, including preserved runs. Check time at execution. A run must stop within both limits. If the period has expired or cannot support the planned capture, report that fact and request a new concrete period only when needed; this plan does not silently extend authorization. No credentials, purchases or account creation are needed for the existing public collector.

## 3. Execution sequence

### Task 1 — Add the experiment runner and a useful blocked result

**Implemented for the fixed BTC inputs.** The latest run is `data/derived/e001_readiness_003`; `evaluate` reproduced the same blockers and stopped before fitting.

**Existing inputs:** `experiments/e001_run_config.yaml`, `CaptureInput`, the timing/feature audit reports and the fixed BTC manifests. **New files:** `src/mfsm_e001/readiness.py`, `scripts/run_e001_experiment.py`, `experiments/e001_execution_config.yaml`, and focused runner tests.

- [x] Define and validate an execution config referencing exact input manifests, sealed-prefix segment limits, timing-policy version, feature/label versions, and an immutable output run directory. Declare separate `real_inputs` and explicitly synthetic `fixture_inputs`; mode selects the intended section and never falls back to the other. Refuse to overwrite an existing result directory. Keep orchestration settings separate from scientific parameters. JSON syntax is used as a YAML 1.2 subset.
- [x] Implement `--mode readiness`, `--mode evaluate` and `--mode fixture`. Fixture mode requires explicit synthetic provenance and never substitutes for a failed real-data run.
- [x] Readiness verifies integrity/provenance, timing evidence and feature feasibility independently. Dependent dataset/evaluation stages report `not_run` with reasons.
- [x] Produce `result.json`, `report.md` and a manifest of input/config/protocol/code/output hashes. Errors after output creation retain an `ERROR` receipt.
- [x] `evaluate` invokes readiness before fitting and refuses unresolved gates, unsupported features or ineligible rows. Later stages stay `not_run` while blocked.
- [x] Use exit code 0 for completed results, 2 for expected blocked/insufficient conditions, and 1 for corrupt input or execution failure. A completed negative BTC result maps to exit 0 when real evaluation becomes available.

Use these bounded real inputs for the initial readiness config; verify their current manifest/segment hashes rather than assuming an earlier artifact certifies today's selected inputs:

| Input manifest under `data/raw/` | Selection |
|---|---|
| `live_btc_final/23b5d4a3f0614020a96bbb58344c725a.manifest.json` | Completed original bad-clock smoke |
| `live_btc_clock_fixed_smoke/094532e21b2946268a5d829746463ee7.manifest.json` | Completed repaired-clock smoke |
| `live_btc_timing_probe_smoke/a0c8d57cfdef496e8ed786f0456534cc.manifest.json` | Completed HTTP-probe smoke |
| `live_btc_development/53d688bfe33349aaab40dc8e7463c802.manifest.json` | Explicit sealed prefix, first 26 segments; exclude every later segment and unclean tail |

**Observed acceptance:** `readiness_003` and `btc_evaluation_001` selected the same 29 sealed segments and six diagnostic decisions, had matching config/protocol/code/input hashes and identical substantive results apart from mode, and returned `BLOCKED_TIMING` with zero eligible rows. The report distinguishes missing independent UTC records from the public WebSocket source-delay evidence gap. It also reports feature deficiencies and does not suggest that waiting another 30 minutes will resolve them.

### Task 2 — Implement timing evidence ingestion and a real qualification decision

**Partial:** the causal qualification evaluator, synthetic positive/expiry/domain tests, receipt replay integration and bounded official-source review are implemented. No independent UTC recorder or supported public WebSocket delay contract exists in the selected captures. The real gate stays blocked.

**Existing files:** `timing.py`, `collect.py`, `replay.py`, `capture_features.py`, and the timing/revision contracts. **New files:** `src/mfsm_e001/qualification.py`, UTC evidence recording/probe tooling, and focused qualification tests.

- [ ] Move shared eligibility into a policy component used by replay, features and the future label grid. Separate local epoch continuity, UTC alignment evidence, feed delivery/initialization, quote freshness, and feature-history completeness. Preserve distinct statuses for each check instead of relying on `clock_valid` alone.
- [ ] Define immutable UTC evidence records: source and actual upstream reference, local wall/monotonic request and receipt times, offset/error interval, evidence availability, epoch, synchronization state, provenance, and explicit expiry/drift policy. Reject malformed, stale, contradictory or wrong-epoch evidence. Collect without blocking market receive loops and preserve failures.
- [ ] Assess an independent public UTC reference or recorded host synchronization evidence with a bounded query. WSL PHC/chrony alignment to its Windows host is not an independent UTC reference by itself. If using NTP evidence, validate the response and synchronization/error fields and document the assumptions; do not claim that several names necessarily represent independent clocks. Source selection and library/API details need official documentation during implementation.
- [ ] Conduct one bounded WebSocket evidence review. Cover Binance depth `E`, Bybit spot/perpetual book `ts`, ticker `ts`, trade/liquidation item `T`, and snapshot availability. Record supported clock relationships, error/drift bounds, expiry and missing guarantees in a per-role evidence table. The existing HTTP probes remain in their own domain unless a documented bridge supports reuse.
- [ ] Give that review a terminal outcome: implement supported bounds, or record `source_delay_evidence_unavailable` with the exact unsupported roles and the evidence checked. Another near-zero REST offset, ping response or short recapture does not resolve an absent clock relationship.
- [ ] Replace hardcoded missing-evidence reasons with actual evidence evaluation only where a supported contract exists. Implement causal `unknown`, `qualified`, `expired` and `quarantined` transitions. A later successful probe cannot backdate qualification.
- [ ] Specify recovery: after a local step, begin a new epoch, invalidate affected evidence/state, require fresh evidence and feed initialization, and rebuild each dependent history. Distinguish reconnects, sequence gaps, snapshot resets and application scheduling delay. Inspect actual affected intervals; do not automatically treat every delayed watchdog tick as proof of packet loss or proof of uninterrupted delivery.
- [ ] Preserve the old 100 ms guard in diagnostic reproduction. Before primary selection, independently justify any rejection/delay thresholds and record their limitations. Do not weaken them to rescue the original bad-clock sample.

**Decision if the public feeds cannot support the current delay requirement:** write a short feasibility result with the recommended next route: an independently audited provider with the needed evidence, or a separately specified observational receipt-time experiment with explicit weaker freshness assumptions and a narrower claim. Neither route is silently substituted for the current primary experiment. Prepare the concrete contract and cost/access requirements before asking the owner about a material scientific change or paid access. Continue Tasks 3–6 on synthetic fixtures while this decision is pending.

**Acceptance:** synthetic evidence exercises positive qualification, expiry, wrong-domain rejection and recovery; missing evidence still blocks the real captures. A verified real path qualifies only when its required evidence actually exists. The readiness report distinguishes an implementation gap from a source that cannot supply the required evidence.

### Task 3 — Expose one grid for receipt features, triggers and labels

**Synthetic path implemented:** receipt grid, policy/epoch-checked joins, conservative lockout audit, both label horizons, full-horizon maturity, four hand-checkable episode outcomes and a dataset CLI. Real primary extraction remains gated.

**Files:** `replay.py`, `capture_features.py`, `events.py`, `labels.py`, `sampling.py`; new `scripts/build_e001_dataset.py` and integration tests; update the candidate data schema.

- [ ] Publish the selected policy's spot grid explicitly. Do not attach receipt-time features to the strict grid currently returned by `CaptureFeatureReplay.grid()`. Reuse the same quote selection, receipt cutoff, epoch, validity and timestamp precision throughout.
- [ ] Separate spot-reference validity from feature readiness: a missing 30-minute depth denominator does not by itself invalidate an otherwise valid future spot reference used for a label. Conversely, a fresh quote alone cannot qualify a feature window.
- [ ] Build explicit episode IDs from asset, trigger time and experiment/policy version. Implement the specified 300-second crossing, 7,200-second lockout and 15-second decision delay, retaining the conservative missing-history audit in `sampling.py`. Missing pre-capture history cannot be assumed to contain no earlier triggers.
- [ ] Build the 30-minute primary and 120-minute secondary labels on the same policy grid, starting strictly after the decision. A missing required price before the first hit/horizon yields an unavailable label, never a negative example.
- [ ] Keep label observation time and training maturity separate: even an early barrier hit cannot enter fitting before the full prescribed horizon has ended and the label was available, as required by the experiment's chronological evaluation rule.
- [ ] Store episode, decision-feature, label and exclusion tables with unique keys, policy/schema versions, availability times, source hashes and explicit missing reasons. No join may mix strict labels with receipt features, different policy versions or different epochs across an invalid boundary.
- [ ] Make a deterministic synthetic capture cover a crossing, a locked-out crossing, both barrier directions, an unresolved horizon, a gap, an immature label and recovery after a new epoch. Mark every fixture output as synthetic software verification.

**Acceptance:** an end-to-end fixture produces correct hand-checkable episodes and labels with identical row identities for both models. Changes to later records do not change earlier features. Real primary event extraction remains gated by the selected resolved policy; existing monthly results stay reproducible under their original contract.

### Task 4 — Resolve feature feasibility and the supported comparison

**Original E001 feature contract unresolved; separate liquidity-state contract now frozen:** see [field matrix](e001_feature_feasibility.md), [capacity audit](../artifacts/e001_capacity_audit_report.md), and the separate [E001-LIQ-OBS-1 protocol](../experiments/e001_liquidity_observational_protocol.yaml). The original 25 bps claim remains unsupported. The separate observational study now has a fixed common feature list and two MFSM interactions, but no real rows are promoted until its forward capture is sealed and quality/sufficiency gates pass.

**Files:** `capture_features.py`, the data/run schemas, a new feature-feasibility audit, and `artifacts/e001_implementation_status.md`.

- [x] Audit full 25-bps bid coverage, known versus newly revealed levels, persistent-addition histories, the exact 1,800-second pre-trigger depth denominator and source continuity on all 22 predefined BTC crossings. Eight December crossings lack prehistory. All 14 later crossings fail 25 bps bid coverage: their per-event minimum coverage is 0.718–1.198 bps and the largest coverage observed is 5.278 bps. Zero capacity measurements are eligible. Ask-band coverage is not required for this bid-capacity audit; a regression test protects that distinction.
- [x] Produce a field matrix: economic meaning, units, source, observable status, missingness, neutral B4 input and any dependent MFSM combination. Distinguish measured zero from unavailable data.
- [ ] Keep bankruptcy-price liquidation notional and aggregate-L2 cancellation/execution attribution unavailable. Test whether an audited source supports the required liquidation valuation. Size/OI or mark-valued substitutes require a separately versioned scientific choice; do not activate them as implementation fixes.
- [ ] Resolve the original E001 common feature list before any original-claim real fitting. Do not require every diagnostic column merely because it exists, and do not impute an economically undefined required feature or fit a purported primary MFSM comparison with its defining interactions absent.
- [x] For the separate narrower observable comparison, freeze the changed claim and feature contract before model scores. `E001-LIQ-OBS-1` gives both learners the same eight observable top-level-liquidity inputs and adds only two deterministic MFSM interactions. It is not an activation of original E001.

**Capacity-audit implementation:** `experiments/e001_capacity_audit_protocol.yaml` freezes the 22-event source hash, receipt-time clock, 25 bps band, 15-second persistent-addition window, 30-second projection and outcomes, and a minimum of five independent episodes before descriptive rank correlations. `src/mfsm_e001/capacity_audit.py` reconstructs Tardis snapshot/delta cohorts, rejects unknown or incomplete bands, values aggressor trades, preserves right censoring, and separates locked-out crossings. `scripts/audit_e001_capacity.py` verifies raw hashes and writes a JSON result, report and manifest. The run used no model and changed no threshold after its result.

**Next data requirement:** obtain historical BTCUSDT perpetual L2 with continuous bid coverage of at least 25 bps, receipt timestamps, recoverable snapshots/sequences, and at least 30 minutes before predefined sharp declines. Existing Bybit trades can supply the 30-second aggressive sell-flow outcome. A 1–5 bps or fixed-level proxy is a different scientific definition and must be versioned before its outcomes are inspected.

**Separate shallow experiment completed:** [E001-near-touch-capacity-observational-1](e001_shallow_capacity_result.md) fixed a 0.5 bps band and expanded the free calendar to 42 first-of-month days before reading its L2/trade outcomes. Event discovery found 90 crossings and 12 history-qualified independent episodes. Only five crossings and two independent episodes passed the capacity gates. Fifty-nine crossings had zero bid depth inside the midpoint band during at least one required scale second, 17 had stale/invalid history, and nine lacked complete replenishment history. Both valid independent rows were no-breach observations with gross 30-second sell flow above the proxy. The fixed five-episode minimum was not met, so no rank correlation or model was computed.

**Do not iterate the band again on these outcomes.** That next observable candidate is now frozen as [E001-LIQ-OBS-1](../experiments/e001_liquidity_observational_protocol.yaml): fixed top-50 liquidity state normalized by its own 30-minute history, evaluated only on the separately selected forward capture or later separately frozen fresh data. The 42 dates used here may support engineering tests but are development-only for this feature family.

**Acceptance:** a frozen-for-the-run supported feature contract exists, or readiness emits `BLOCKED_FEATURES` with the exact missing source/measurement. Model software may be complete while real feature feasibility is blocked.

### Task 5 — Verify acquisition and construct a real BTC dataset

**Files:** existing capture/audit tooling, dataset builder, execution config and run manifests. Do not launch a collector as part of a default readiness command.

- [ ] Verify actual process/lock/checkpoint state, free space and the remaining authorized acquisition period. Preserve interrupted inputs and their previous audit artifacts.
- [ ] When the candidate's timing contract is resolved, first perform a bounded 60-second capture to verify subscriptions, recording and evidence fields. This checks plumbing and cannot satisfy 1,815 seconds of feature history.
- [ ] Follow with a fixed 45-minute qualification capture only if the deadline/cap permit it. Measure policy eligibility after warm-up, full-band coverage and why rows are excluded. A quiet liquidation stream does not prove missing subscription or completeness.
- [ ] Distinguish that qualification check from a research dataset. Even without unknown lockout history, 1,815 seconds of feature warm-up plus a full 1,800-second primary label horizon already require over an hour for the earliest matured decision. Market crossings and sufficient independent episodes can require much longer.
- [ ] Resume bounded research capture only after timing/feature feasibility passes. Stop before the original UTC deadline, maintain the directory-wide cap and record process identity, new run ID, policy/code hashes and checkpoint. A longer approved acquisition period, if needed, must be specified separately; do not stop or extend according to model scores.
- [ ] Build the dataset over qualified real input periods with complete provenance. Report rejected intervals and episodes, unknown lockout history, class counts, calendar span/weeks, feature coverage, and label maturity.
- [ ] Create a data-sufficiency check against the prespecified split/calibration design. For E001-LIQ-OBS-1 the frozen minimum is 130 eligible episodes with 50 initial fit, 20 calibration, 20 inner validation, 20-row outer test blocks and at least two full outer test blocks; both classes are required in fit and calibration. Do not lower this after inspecting the forward capture.

**Acceptance:** hash-verified episode/feature/label/exclusion artifacts and a sufficiency report exist, or the runner returns `BLOCKED_TIMING`, `BLOCKED_FEATURES` or `INSUFFICIENT_DATA`. A capture launch receipt is never reported as a completed dataset. No API key is required for the existing free collector; request one only if an explicitly selected provider actually needs it.

### Task 6 — Implement and run the matched BTC evaluation

**Software path implemented on invented rows:** pinned scikit-learn 1.8.0, same-family boosted models, disjoint sigmoid calibration, equal two-candidate grids, deterministic walk-forward fixtures and [candidate protocol](../experiments/e001_btc_evaluation_protocol.yaml). The real feature list and BTC fit remain disabled.

**New files:** `src/mfsm_e001/validation.py`, `models.py`, `evaluation.py`, evaluation tests and `experiments/e001_btc_evaluation_protocol.yaml`. **Extend:** the experiment runner and dependencies/lockfile. Implement and test with fixtures while data collection or external evidence is pending.

- [ ] Specify exact BTC chronological outer/inner folds, training and disjoint calibration periods, label-maturity cutoffs, the supported features/missingness policy, learner/library version, tuning grid, tie-break rule and seeds before real fitting. Specify minimum data requirements for that design before inspecting performance; do not reduce them repeatedly until a tiny sample fits.
- [ ] Implement the required same-family calibrated histogram-based gradient-boosted B4 and MFSM models. Both receive identical eligible episodes and neutral normalized inputs; MFSM adds only the specified combinations. B4's search budget is no smaller. Pin the learner dependency after checking its official API documentation during implementation.
- [ ] Keep preprocessing, tuning and calibration inside allowed past data. Select parameters by pooled, episode-weighted Brier score of calibrated 30-minute inner-validation predictions. Never use the outer evaluation data to choose calibration or thresholds.
- [ ] Test time boundaries, full-horizon maturity, train/calibration/validation separation, paired row equality, shared feature parity, search-budget parity and deterministic prediction output. A synthetic score verifies software only.
- [ ] Run real fitting only after readiness and the selected evaluation protocol pass. Write per-episode out-of-sample paired probabilities and split/model identifiers, fitted artifacts, exclusions and hashes.
- [ ] Report primary paired BTC Brier improvement `mean((p_B4-y)^2 - (p_MFSM-y)^2)`, Brier scores, sample/calendar coverage and the exact evaluated configuration. Report calibration, log loss and prespecified sensitivities as secondary results. Fix any BTC uncertainty method before scoring; do not present the ETH-specific minimum-week rule as a BTC power calculation.
- [ ] Apply the published BTC development gate: a nonpositive paired mean improvement is `BTC_DEVELOPMENT_FAILED`; positive is `BTC_DEVELOPMENT_PASSED`. Inadequate data or uncomputable evaluation is `INSUFFICIENT_DATA`, not a model failure or success.
- [ ] Leave ETH sealed after this command, including when BTC passes. A pass prepares the separate immutable freeze and one-time confirmation procedure in the existing specification; it does not launch ETH access automatically.

**Acceptance:** the runner returns a reproducible real BTC score with paired predictions when eligible data exist, or an explicit earlier terminal status. No fixture result, in-sample fit or hand-selected decision row is presented as out-of-sample research evidence.

## 4. Run interface and output contract

### Commands that exist now

From the repository root, these verify software and reproduce a candidate diagnostic; they do not fit a model:

```bash
uv run --locked --extra collect --extra test pytest -q

uv run --locked --extra collect python scripts/build_e001_capture_features.py \
  data/raw/live_btc_clock_fixed_smoke/094532e21b2946268a5d829746463ee7.manifest.json \
  --timing-candidate receipt_v1 \
  --decision-second 1790211898 \
  --output data/derived/e001_receipt_plan_preflight
```

Choose a new output directory if that reproduction directory already contains a result to preserve. A successful exit from this existing diagnostic builder does not indicate research eligibility.

### Implemented runner commands

The execution config uses JSON syntax, which is valid YAML 1.2, so no YAML parser is required. Add `--extra eval` for fixture model evaluation. Use a new output directory each time; the runner refuses overwrite.

```bash
uv run --locked --extra collect --extra eval python scripts/run_e001_experiment.py \
  --config experiments/e001_execution_config.yaml \
  --mode readiness --output data/derived/e001_readiness_003

uv run --locked --extra collect --extra eval python scripts/run_e001_experiment.py \
  --config experiments/e001_execution_config.yaml \
  --mode fixture --output data/derived/e001_fixture_004

uv run --locked --extra collect --extra eval python scripts/run_e001_experiment.py \
  --config experiments/e001_execution_config.yaml \
  --mode evaluate --output data/derived/e001_btc_evaluation_001

uv run --locked python scripts/audit_e001_capacity.py \
  --output data/derived/e001_capacity_audit_REPRO

uv run --locked python scripts/discover_e001_shallow_capacity_events.py \
  --download --workers 2 --output data/derived/e001_shallow_event_discovery_REPRO

uv run --locked python scripts/finalize_e001_shallow_event_source.py \
  --discovery data/derived/e001_shallow_event_discovery_REPRO/result.json \
  --output data/derived/e001_shallow_event_source_REPRO
```

The first two shown output directories are already occupied by preserved results; use a fresh name to rerun. `evaluate` currently stops at readiness and emits `BLOCKED_TIMING` before any real fit. The pinned optional `eval` extra supplies scikit-learn 1.8.0. For the isolated grid fixture, run `scripts/build_e001_dataset.py --fixture tests/fixtures/e001_receipt_grid_fixture.json --output NEW_DIRECTORY`.

| Terminal status | Meaning and required output |
|---|---|
| `READINESS_PASSED` | The selected real run's required readiness stages passed; fitting has not yet been requested |
| `BLOCKED_TIMING` | Evidence or policy implementation is missing/invalid; list exact roles, periods and next actions |
| `BLOCKED_FEATURES` | Required economics, depth/scale coverage or a resolved feature contract is missing |
| `INSUFFICIENT_DATA` | Resolved dataset/design cannot support required fitting, calibration or evaluation |
| `PIPELINE_VERIFIED_SYNTHETIC` | Fixture tables and model plumbing passed; no empirical predictive claim |
| `BTC_DEVELOPMENT_FAILED` | Eligible real evaluation completed with nonpositive primary Brier improvement |
| `BTC_DEVELOPMENT_PASSED` | Eligible real evaluation completed with positive primary Brier improvement; confirmation still pending |
| `ERROR` | Corrupt inputs, invalid configuration or execution failure; preserve error evidence |

If multiple gates fail, choose the earliest blocking stage for the top-level status and retain every independently established blocker in the report. Every result includes `data_kind`, primary eligibility, whether a model was fitted, whether a score exists, exact inputs/versions/hashes and stage outcomes. Score fields are null until a real eligible evaluation finishes.

## 5. Delivery order, verification and handoff

1. **Completed:** fixed-input runner and reproducible blocked result; receipt grid and synthetic dataset; matched synthetic model plumbing.
2. **Completed as a separate study:** the owner chose a free receipt-time observational route. Its fixed hourly Tardis sample protocol, dataset builder, matched evaluation and result are documented in [the exploratory result](e001_exploratory_btc_result.md). The original E001 status remains blocked.
3. **Next original E001 evidence decision:** obtain an auditable per-role UTC/delay contract and supported liquidation/depth measurements if the original claim remains the objective. The [source review](e001_websocket_evidence_review.md), [feature matrix](e001_feature_feasibility.md), and [capacity audit](../artifacts/e001_capacity_audit_report.md) identify what is missing. The current archive reaches at most 5.278 bps during the audited histories and cannot measure the fixed 25 bps proxy. Any new live acquisition must respect its authorized deadline and cap.
4. **For a stronger observational test:** do not select another book band on the 42 already-scored days. Predeclare an explicitly observable fixed-level liquidity-state feature, then use fresh continuous days with feed continuity evidence and a no-lookahead execution-cost benchmark. The current first-of-month studies cannot establish trading edge. No completion date or positive result is promised for evidence-dependent stages.

Regression coverage must include one-nanosecond receipt cutoffs; invariance to future records/probes; old 3.3-second error rejection; wrong-domain and expired evidence; epoch and connection recovery; quote-age boundaries; gaps inside feature/label windows; same-timestamp book cohorts; unknown newly revealed levels; full-band missingness; unknown lockout history; feature/label policy mismatches; full-horizon training maturity; and identical B4/MFSM shared rows. Run relevant focused tests during implementation and the full suite at integration. Validate output/source hashes and inspect the final diff for unrelated changes and sensitive data. Do not repeatedly rerun unchanged long captures without a concrete verification reason.

At each delivery, update the implementation status with changed files, runnable commands, passed/failed/not-run checks, measured results and exact remaining gates. Retain earlier artifacts with their original code/policy hashes.

Copyable instruction for the next coding model:

> Continue `docs/e001_next_implementation_plan.md` from the original E001 `BLOCKED_TIMING` result and the separate [exploratory BTC result](e001_exploratory_btc_result.md). Preserve their outputs and hashes; do not use the exploratory score to change its dates, barriers, features or sample gates. If testing observational edge further, version a continuous-day protocol with feed continuity and a predeclared execution-cost check before scoring. If restoring the original liquidation claim, first obtain auditable per-role UTC/delay evidence and supported depth/liquidation measurements. Do not fabricate WebSocket bounds, treat bankruptcy price as execution price, fit unqualified original E001 rows, extend the authorized capture deadline or open ETH. Return exact gates and verification evidence.
