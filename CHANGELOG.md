# MFSM Change Log

This file records material changes to the Market Feedback-State Model so definitions are not silently rewritten after empirical failure.

## 2026-09-22 - Repository review corrections before Experiment 001 freeze

These corrections amend the pre-freeze specification. They are **not** a completed experiment freeze, dataset audit, or empirical result.

The candidate experiment version advances from `e001-v1.0` to `e001-v1.1`, and the label schema from `E001-label-v1` to `E001-label-v2`; neither candidate tag has been created. The experiment title and research question now describe the measured downside-first outcome rather than claiming that the binary label directly distinguishes liquidation mechanisms.

- **Primary decision:** Previously, multiple horizons and qualitative success conditions left the confirmatory conclusion open to selection. Experiment 001 now makes 30-minute downside-before-recovery the sole primary label and paired Brier improvement over the same-data B4 model on ETH episodes inside a precommitted evaluation period the sole primary comparison. A positive BTC walk-forward improvement is the development gate; ETH success requires the lower endpoint of a prespecified week-block bootstrap interval to exceed zero. Insufficient eligible weeks is inconclusive. Secondary horizons and metrics cannot reverse that result. The consequence is a falsifiable, reproducible predictive claim, distinct from a trading-edge claim.
- **Observable replenishment:** Previously, the estimator called aggregate L2 additions "durable" and allowed execution qualification as though per-order dwell or fate were observable. The [Bybit public order-book feed](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook) reports price-level aggregate sizes and updates; it does not supply order identities. Experiment 001 now uses a conservative **observed price-level persistence** proxy with a full one-second pre-decision interval and explicitly disclaims order-level survival and execution attribution. Both B4 and MFSM receive the same neutral proxy. The consequence is a narrower, auditable measurement claim and possible undercount/hidden-replacement bias.
- **State closure:** Previously, the finite-vector stochastic template could be read as exact for fixed delays and arbitrary kernels. The canonical model, foundations, protocol, and overview now require the history state for exact delays, or a justified finite-dimensional realization; a finite matrix Jacobian for an approximation must be labeled as such. This follows standard [delay differential equation state-space treatment](https://people.uleth.ca/~roussel/nld/delay.pdf). The consequence is that finite-dimensional eigenvalue conclusions cannot silently substitute for exact delayed-system stability.
- **Lookback and labels:** Previously, a 30-minute panel ending at \(t_d=t_0+15s\) omitted the first 15 seconds of the pre-trigger 30-minute denominator. The panel now extends 30 minutes plus 15 seconds. The primary one-second first-passage label now excludes an episode if a required composite price is missing before the barrier hit or horizon; a feed gap cannot become a negative label. The freeze manifest records the BTC development cutoff, ETH evaluation end, and period rule.
- **Pre-freeze contract follow-up:** Qualified the buffer-sensitivity Jacobian as finite-dimensional, with an operator on the history space for exact delay models. Restricted pre-freeze ETH schema planning to public, observation-free feed descriptions and made incompatible required ETH fields an inconclusive confirmation. Kept the persistence rate's right-edge censoring in its 15-second denominator, and set pooled inner-validation Brier score on calibrated probabilities as the shared tuning objective.
- Corrected the prior entry's future-dated 2026-09-23 heading to the 2026-09-22 date of its repository commit.

## 2026-09-22 - Experiment 001 preregistration completion pass

This revision verifies commit `4623b4f` against its stated empirical contracts and tightens Experiment 001 without reopening the canonical MFSM architecture.

### Timestamp and label integrity

- Fixed a look-ahead edge case in the durable-replenishment estimator: dwell-qualified additions must complete the full dwell interval by \(t_d\), and execution-qualified additions must execute by \(t_d\). Post-decision book state is prohibited.
- Defined the event trigger exactly as the first crossing of a 1% **point-to-point 300-second spot-composite return** on the canonical one-second grid.
- Replaced the vague nearby-trigger rule with an exact two-hour episode lockout.
- Renamed the primary binary endpoint as **downside continuation before recovery versus not-downside-first** and added an explicit three-state competing-risk endpoint so unresolved paths are not silently labeled exhaustion.

### Observational typing

- Retained the canonical causal object \(R^-_t(h;\delta,\varepsilon,\varphi)\), but removed \(\delta\) from the Experiment 001 empirical capacity proxy because the experiment conditions on an observed state rather than identifying a structural intervention.
- Fixed the liquidation/aggressive-flow window to the same 30-second horizon used by the primary capacity proxy.

### Baseline parity and transfer

- Added a shared neutral preprocessing map \(U(X^{raw})\) supplied to both B4 and the MFSM feature model.
- B4 now receives the same event-stream summaries used by MFSM, including durable replenishment, cancellation, execution, liquidation, and aggressive-flow rates across frozen windows.
- Added a common causal scale-normalization policy so BTC-to-ETH confirmation is not confounded by raw notional/depth/OI scale.
- MFSM may add only prespecified theory-motivated combinations of neutral shared features; it receives no representation unavailable to B4.

### Provenance and source hygiene

- Corrected the operationalization-audit upload timestamp against the conversation-file metadata.
- Added primary/reference sources for non-normal transient growth, pseudospectral motivation, and numerical-abscissa/nonmodal analysis.
- Updated the machine-readable proxy-bias contract to **sign with rationale**, preserving `ambiguous` as an allowed preregistered outcome.

## 2026-09-22 - Operationalization refinement: transient amplification, flow-conditioned capacity, and stress-bias discipline

This revision follows a later operationalization pass over the conversation-supplied document `Pasted markdown(20260922-170823).md` and a subsequent staged review. It refines measurement and experiment contracts without adding new primitive MFSM state variables.

### Finite-horizon response

- Added the derived transient-amplification diagnostic
  \[
  \mathcal A_t^{tr}(h)=\sup_{0\le s\le h}\|\Phi(t+s,t)\|_2,
  \]
  together with the locally frozen numerical abscissa \(\omega(J_t)\).
- Linked transient amplification explicitly to switching-surface geometry: asymptotic stability does not imply finite-horizon path safety.
- Corrected the spectral-radius theorem so \(\rho(P)<1\) is an asymptotic result for a fixed time-invariant propagation matrix \(P\). Pointwise \(\rho(P_t)<1\) for a time-varying sequence is only a locally frozen diagnostic unless stronger product-growth conditions are established.
- Retained \(\Gamma_t\) without adopting a universal \(\Gamma=1\) run threshold.

### Opposing absorptive capacity

- Strengthened the preferred operational object to
  \[
  R^-_t(h;\delta,\varepsilon,\varphi),
  \]
  where \(\varepsilon\) names the tolerated adverse consequence and \(\varphi\) specifies the normalized incoming-flow arrival profile.
- Added an admissible-profile formulation for conservative capacity when a set \(\Phi\) of plausible arrival schedules is prespecified.
- This prevents equal total notionals delivered instantaneously and gradually from being treated as the same stress.

### Measurement discipline

- Added a stress-state proxy contract recording ordinary bias, failure mode, and **expected sign plus rationale** during the regime of interest.
- Explicitly permits `ambiguous` when economically plausible failure modes push measurement error in opposite directions.

### Experiment 001

- Split venue-identified liquidation flow \(Q^{liq}\) from aggressive sell flow excluding identified liquidation executions \(Q^{aggr,exliq}\); ordinary aggressive selling is no longer labeled forced flow, and the residual aggressive-flow measure is not assumed voluntary.
- Defined liquidation pressure and generic sell-pressure interactions separately so generic selling cannot be mistaken for evidence of forced deleveraging.
- Fixed the standardized capacity profile to uniform arrival over the primary 30-second horizon; any front-loaded sensitivity profile must be frozen before evaluation.
- Defined durable replenishment from positive bid-depth deltas that survive a one-second dwell interval or are observably executed, preventing gross add-cancel churn from masquerading as refill capacity.
- Unified the primitive-history notation to \(X^{raw}_{[t_d-w,t_d]}\).
- Added a deterministic near-zero denominator rule using 1% of each event's pre-trigger median executable depth plus a low-capacity indicator; this transfers unchanged to the strict ETH holdout without inspecting its feature/outcome distribution.

### Provenance

- Added `artifacts/operationalization_source_audit_2026-09-22.md` to preserve what was incorporated, retained only conditionally, and rejected from the conversation-supplied operationalization document.

## 2026-09-22 - Five-review convergence cleanup and theory freeze

This revision incorporates the convergent findings of independent mathematical, causal-identification, empirical-finance, adversarial, and crypto-implementation reviews. It is intentionally a **contraction / typing pass**, not a conceptual expansion.

### State architecture

- Replaced the loose top-level collection of partially overlapping state objects with a requirement for one **closed augmented latent state** \(\mathbf Z_t\).
- Defined \(\mathcal G\) as the fixed structural transition form and added a universal closure rule: any future-relevant time-varying kernel, network, disturbance parameter, coefficient, buffer, coordination state, control state, or hybrid mode must be inside \(\mathbf Z_t\), be predetermined, or have an explicit exogenous law.
- Clarified that buffers \(B_t\), expectation/coordination state \(Q_t\), control states, hybrid modes, and endogenously evolving topology/coefficients are components or measurable projections of \(\mathbf Z_t\) when they evolve dynamically.
- Reclassified \(J_t\) as a derived local Jacobian and \(M_t^{term}\) as a derived prospective mechanism classification rather than a primitive state variable.

### Intervention contract

- Reclassified \(\delta=(c,V,a,d,t_0,p,\nu)\) as a required **human-readable intervention descriptor**, not the mathematical intervention itself.
- Added the full intervention operator
  \[
  \mathfrak I_{\delta}:(\mu_t,\mathcal G)\mapsto(\mu_t^{\delta},\mathcal G^{\delta}),
  \]
  so pure state-setting/jump interventions, pure structural interventions, and hybrids are all typed explicitly.
- Applications must now state whether the initial-state law, a structural rule/equation/kernel/parameter/constraint/forcing term, or both are modified, plus amplitude units, stochastic law/coupling, and timing convention.
- Added amplitude-normalization discipline for cross-system susceptibility comparisons.

### Consequence and susceptibility typing

- Split absolute stressed consequence from incremental causal consequence:
  - \(F_t^{abs}\): one-path stressed risk under \(\mathcal P^{\delta}\);
  - incremental causal consequence: requires a two-path loss and explicit counterfactual coupling.
- Required all losses used inside severity objects to be oriented so **larger means worse**.
- Required recovery-style quantities to be reported separately or converted to loss orientation.
- Clarified that susceptibility slopes are coordinate-dependent unless amplitude units or normalization are fixed.

### Capacity and constraint cleanup

- Recast continuation capacity as a mechanism-indexed family \(\{R_{k,t}^+\}_k\); \(R^+\) is now a category label rather than a default market-wide scalar.
- Upgraded opposing absorptive capacity to the stronger form \(R^-_t(h;\delta)\) when shock type affects willingness or financing.
- Clarified that \(\mathbf\Chi_B\) is an **initial-state** sensitivity.
- Restricted \(\mathbf\Chi_B\mathbf v_{\delta}\) to interventions that act solely through an initial-state displacement.
- General structural interventions require a direct intervention derivative or the finite response \(\Delta\mathbf B^{\delta}\).

### Measurement and identification

- Split the conceptual true observation distribution \(p_*(Y\mid Z)\) from the analyst's candidate probabilistic measurement model \(p_m(Y\mid Z;\psi^{(m)})\).
- Added mandatory identification labels: point-identified / partially identified / structurally identified / unidentified.
- Added a requirement to record a plausible observationally equivalent alternative data-generating process.
- Replaced open-ended measurement robustness with a **prespecified finite set** of alternative measurement specifications.

### Derived diagnostics and redundancy control

- Clarified that \(C\) must be derived through a prespecified functional of the propagation operator/state/law rather than treated as a free primitive; operational analysis should prefer the actual network/operator diagnostics.
- Clarified that \(\Theta\) summarizes response-time structure and is not a substitute for \(K\).
- Recast \(L\) as an optional derived threshold-concentration statistic; the primitive objects are the actual switching surfaces and distances.
- Added a theory-freeze rule: no new canonical state variable until the current empirical program is tested, unless a demonstrated contradiction cannot be represented by the existing architecture.

### Empirical standard

- Added a mandatory **flexible nonlinear baseline using the same raw information set**. MFSM does not demonstrate incremental structural information merely by beating a weaker linear baseline.
- Strengthened the minimum edge standard to require explicit identification status, loss orientation, intervention operator, amplitude units, finite measurement-model alternatives, and transaction-cost-aware out-of-sample value where trading is the application.

### Symbol cleanup

- Renamed endogenous counterflow from \(I_t\) to \(N_t\) and controller topology from \(\mathcal C_I\) to \(\mathcal C_N\) so counterforce notation cannot be confused with the information set \(\mathcal I_t\).
- Renamed lag/control timescale symbols that conflicted with Trend Strength \(T\).
- Renamed the expectation horizon so it no longer conflicts with headroom \(H\).
- Renamed Brownian noise so it no longer collides with economic network \(W_t\).

### Experiment 001 preregistration tightening

- Added an exact first-passage definition for the primary downside-before-recovery label, anchored to the decision-time spot composite.
- Enforced a strict ETH holdout: no ETH inspection, plotting, feature selection, tuning, or propagation analysis before frozen confirmatory evaluation.
- Defined a primitive historical information panel shared by B4 and MFSM so response-time features cannot give MFSM a richer raw information set.
- Required comparable model-selection/tuning budgets for B4 and the MFSM feature model.
- Added a freeze/reproducibility manifest requiring immutable model/spec tags, resolved commit SHAs, data/feature/label schema versions, freeze timestamp, and first ETH-access record before confirmatory use. The manifest is populated after the frozen tags exist so the tagged commits do not attempt to embed their own hashes.

### Research phase

The conceptual architecture is now in **pre-freeze / empirical-testing preparation mode**. Freeze sequence: commit the cleanup, create immutable model/spec tags, then populate the Experiment 001 freeze manifest with the resolved SHAs and schema metadata. Confirmatory work starts only after the manifest is complete. Thereafter, progress should primarily come from falsifiable experiments and simplification, not from adding new conceptual variables.

Added supporting artifacts:

- `artifacts/independent_review_synthesis_2026-09-22.md` — synthesis of the five independent reviews and their convergent corrections.
- `experiments/Experiment_001_Crypto_Liquidation_Response.md` — prespecified first crypto experiment on liquidation exhaustion versus continuing deleveraging.
- `experiments/Experiment_001_Freeze_Manifest.yaml` — post-tag administrative record for frozen model/spec tags, resolved commits, schema versions, freeze timestamp, and first ETH-holdout access.

## 2026-09-22 - Counterfactual path-law and susceptibility refinement

This revision supersedes the earlier terminal-mean shock-response formulation while preserving it as historical context below.

### Canonical changes

- Replaced the terminal expected-state response as the fundamental object with the conditional counterfactual path law:
  \[
  \mathcal P_{t,h}^{\delta}
  =
  \mathcal L(
  \mathbf Z_{[t,t+h]}^{\delta}
  \mid
  \mathcal I_t
  ).
  \]
- Retained the mean causal response only as a derived projection:
  \[
  \mathbf m_t^{\delta}(s)
  =
  E[
  \mathbf Z_{t+s}^{\delta}
  -
  \mathbf Z_{t+s}^{0}
  \mid
  \mathcal I_t
  ].
  \]
- Distinguished disturbance class \(c\) from a fully specified structural intervention
  \[
  \delta=(c,V,a,d,t_0,p,\nu).
  \]
- Explicitly prohibited intervening on endogenous outcome labels such as "bank run" or "liquidation cascade"; interventions must target causally upstream variables.
- Recast \(F\) as shock-conditioned consequence:
  \[
  F_t(\delta,h;\ell,\rho)
  =
  \rho_{\mathcal P_{t,h}^{\delta}}
  [
  \ell(\mathbf Z_{[t,t+h]}^{\delta})
  ].
  \]
- Separated shock consequence from structural susceptibility through amplitude-response curves, local slopes, and critical disturbance amplitudes \(a_q^*\).
- Replaced scalar constraint sensitivity with the local Jacobian \(\mathbf\Chi_{B,t}\), intervention-direction projections, and finite-shock buffer response \(\Delta\mathbf B_t^{\delta}\).
- Added the counterfactual-coupling caveat: distributions of pathwise differences require a joint structural coupling, not only the two marginal path laws.
- Clarified recovery metrics and recommended probability / truncated recovery targets when some paths do not recover inside the horizon.

### Empirical and source changes

- Promoted the original Diamond-Dybvig paper as the canonical bank-run source:
  - Douglas W. Diamond and Philip H. Dybvig, "Bank Runs, Deposit Insurance, and Liquidity," *Journal of Political Economy* 91(3), 1983, 401-419.
  - https://www.journals.uchicago.edu/doi/10.1086/261155
- Clarified that \(\Gamma_t\) is an MFSM abstraction of coordination dependence, not a formula taken from Diamond-Dybvig.
- Updated empirical hypotheses to test decision-relevant path-law functionals, finite-shock buffer responses, and consequence-versus-susceptibility separation.
- Updated the research protocol so intervention amplitude/path, loss functional \(\ell\), and severity functional \(\rho\) are prespecified.

### Canonical distinctions added

- disturbance class != structural intervention;
- shock consequence != structural susceptibility;
- terminal mean response != full path response;
- local buffer Jacobian != finite-shock buffer response;
- marginal potential-path laws != joint distribution of pathwise counterfactual differences.

## 2026-09-22 - Shock-conditioned response architecture and extended source integration

### Canonical changes

- Broadened the invariant from a trend-only question to:
  - **How is the current structural state changing the system's response law for the next disturbance?**
- Recast Failure Fragility as a disturbance- and horizon-conditioned object \(F_t(\delta,h)\), rather than a context-free scalar.
- Added the conceptual shock-response operator:
  \[
  \mathcal R_t(\delta,h)
  =
  \mathbb E[\Delta\mathbf Z_{t+h}\mid do(\delta),\mathbf Z_t].
  \]
- Distinguished latent structural state \(\mathbf Z_t\) from observed data \(\mathbf Y_t\) through an explicit observation model.
- Horizon-qualified opposing absorptive capacity as \(R^-_t(h)\).
- Added constraint sensitivity \(\chi_{B,t}\), distinct from current headroom \(H_t\).
- Added strategic complementarity / coordination state \(\Gamma_t\), allowing run-like fragility without a preceding trend.
- Made functional diversity \(D_t\) explicitly dynamic.
- Added controller topology (now denoted \(\mathcal C_N\)) so feed-forward opposition, delayed feedback, integral feedback, depletion, saturation, and thresholds are not conflated.

### Mathematical foundations

Added:

- horizon-dependent opposing capacity;
- constraint-sensitivity derivatives;
- latent-state / observation-model separation;
- dynamic functional diversity;
- strategic complementarity;
- controller-topology formalization;
- shock-conditioned fragility surface;
- shock-response operator;
- measurement-model robustness research priorities.

### Empirical foundations

Integrated new mechanism evidence and research warnings from:

- Diamond–Dybvig bank-run coordination;
- Kiyotaki–Moore collateral cycles;
- Duffie slow-moving capital;
- Filimonov–Sornette measurement / apparent-criticality work;
- heterogeneous-expectations strategy switching;
- BIS crypto carry;
- AMM loss-versus-rebalancing;
- Bank of England gilt-crisis reconstruction;
- Minsky / credit-financing composition;
- SEC early-2021 squeeze-mechanism decomposition.

### Research protocol

Now requires:

- disturbance class and horizon;
- latent-state versus proxy separation;
- horizon-qualified \(R^-_t(h)\);
- constraint sensitivity;
- dynamic diversity and strategic complementarity;
- controller topology;
- shock-response path;
- measurement-model disclosure.

### Supporting artifact

- Added artifacts/source_review_extended_2026-09-22.md, preserving the complete link-by-link review and the reasoning behind these revisions.

### Definitions preserved

Still canonical:

- \(T\) != \(U\);
- \(R^+\) != \(H\) != \(R^-\);
- fixed delay != distributed memory;
- correlation != propagation topology;
- analogy != evidence;
- no universal scalar fragility score;
- predictive edge requires genuine out-of-sample incremental value.

## 2026-09-22 - Companion foundations added

### Added

- `Mathematical_Foundations.md`
  - exact scalar delayed-feedback stability boundary;
  - crossing-direction derivation;
  - two-state lagged-inhibitor system;
  - distributed-memory kernel formulation;
  - gain-delay and relative-timescale interpretation;
  - Ornstein-Uhlenbeck critical-slowing-down derivation and limits;
  - capacity/deadline mechanics;
  - general stochastic MFSM template;
  - network/spectral formulation;
  - threshold and hybrid-system representation;
  - exact Physarum adaptive-network equations;
  - mathematical workflow and rejected inferences.

- `Empirical_Finance_Foundations.md`
  - finance-native mechanism map;
  - primary/official source list;
  - measurement map for MFSM variables;
  - prespecified test hypotheses;
  - empirical design and validation standards.

- `Research_Protocol.md`
  - mandatory application and extension workflow;
  - evidence labels;
  - falsification requirements;
  - out-of-sample testing requirements;
  - stop conditions for further theorizing;
  - future-LLM output schema.

- `README.md`
  - repository map and usage guidance.

### Canonical model updates

`Market_Feedback_State_Model_Canonical.md` now explicitly delegates:

- exact mathematics to `Mathematical_Foundations.md`;
- finance-side evidence and measurement to `Empirical_Finance_Foundations.md`;
- extension and validation discipline to `Research_Protocol.md`.

### Definitions preserved

The following distinctions remain canonical:

- Trend Strength (T) != Trend Sustainability (U) != Failure Fragility (F);
- continuation fuel (R^+) != headroom (H) != opposing absorptive capacity (R^-);
- fixed delay != distributed memory;
- trend termination by fuel exhaustion != delayed counterflow != gain saturation != threshold unwind;
- correlation != propagation topology;
- natural analogy != financial evidence;
- state diagnosis != validated predictive edge.

### Epistemic status

No change: MFSM remains a research framework, not a validated trading system or universal fragility score.
