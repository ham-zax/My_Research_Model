# My Research Model

This repository contains the canonical specification and supporting foundations for the **Market Feedback-State Model (MFSM)**.

MFSM is a research framework for diagnosing how a market's structural state changes the law governing its own response to future disturbances. Trends are one important state-transforming process, but the model also covers coordination runs, funding stress, collateral feedback, threshold failure, and propagation without requiring a prior trend.

Its invariant question is:

> **How is the current structural state changing the system's response law for the next disturbance?**

## Repository map

- [Market_Feedback_State_Model_Canonical.md](./Market_Feedback_State_Model_Canonical.md)
  The authoritative conceptual specification. Start here.

- [Mathematical_Foundations.md](./Mathematical_Foundations.md)
  Exact mathematical foundations for delay, distributed memory, local stability, stochastic recovery, adaptive networks, nonlinear thresholds, and the MFSM state-space template.

- [Empirical_Finance_Foundations.md](./Empirical_Finance_Foundations.md)
  Finance-side evidence base, mechanism-to-literature mapping, candidate measurements, and the minimum empirical tests required before treating MFSM as predictive.

- [Research_Protocol.md](./Research_Protocol.md)
  Application, extension, falsification, evidence, versioning, and future-LLM discipline for evolving the model without turning it into an unfalsifiable story.

- [Model improvement plan](./docs/mfsm_model_improvement_plan.md)
  Model weaknesses, canonical corrections, distinct sources of error, and remaining work with acceptance criteria. Start here for what to improve next.

- [Reference sensitivity and observation result](./docs/mfsm_reference_sensitivity_result.md)
  Frozen synthetic structural comparisons and an explicit case where identical limited observations conceal different market responses.

- [MFSM_Reference_Economy.md](./MFSM_Reference_Economy.md)
  Complete deterministic reference economy with finite budgets, inventory-dependent execution, margin rules, delayed buying, and derived response conditions. Includes executable mathematical checks; parameters are synthetic and uncalibrated.

- [CHANGELOG.md](./CHANGELOG.md)
  Material model changes and preserved definitions, so the framework is not silently redefined after results.

- [artifacts/source_review_extended_2026-09-22.md](./artifacts/source_review_extended_2026-09-22.md)
  Source-by-source audit of the extended finance/control literature that motivated the shock-conditioned response, strategic coordination, constraint-sensitivity, and observation-model revisions.

- [artifacts/independent_review_synthesis_2026-09-22.md](./artifacts/independent_review_synthesis_2026-09-22.md)
  Convergence report from the five independent mathematical, causal-identification, empirical-finance, crypto-quant, and adversarial reviews that motivated the theory-freeze cleanup.

- [artifacts/operationalization_source_audit_2026-09-22.md](./artifacts/operationalization_source_audit_2026-09-22.md)
  Selective audit of the later operationalization draft: incorporates finite-horizon transient amplification, consequence- and flow-profile-qualified absorptive capacity, and stress-state proxy-bias discipline while rejecting universal threshold overclaims.

- [experiments/Experiment_001_Crypto_Liquidation_Response.md](./experiments/Experiment_001_Crypto_Liquidation_Response.md)
  First prespecified empirical program: test whether a narrow MFSM feature set improves 30-minute downside-before-recovery prediction after BTC downside events, with ETH as a strict frozen confirmatory holdout.

- [experiments/Experiment_001_Freeze_Manifest.yaml](./experiments/Experiment_001_Freeze_Manifest.yaml)
  Administrative freeze manifest for the canonical model tag/commit, experiment-spec version/commit, data-feature-label schema versions, freeze timestamp, and first ETH access record.

- [MFSM next steps and agent handoff](./docs/superpowers/plans/2026-09-23-mfsm-next-steps.md)
  Ordered implementation tasks, acceptance criteria, evidence gates, and a copyable prompt for a coding model to begin the BTC pipeline while preserving the ETH holdout.

- [BTC spot reference audit](./artifacts/e001_spot_reference_audit.md)
  Measured quote coverage across three BTC sample days, the approved provisional midpoint rule, and the remaining feed-health and model-evaluation gates. Resume from the [implementation status](./artifacts/e001_implementation_status.md).

- [BTC monthly sample result](./artifacts/e001_monthly_sample_report.md)
  Completed scan of 19 first-of-month days: four nominal episodes, two with supported lockout eligibility, insufficient class support for model evaluation. Includes every sampled day, exclusions, reproducible commands and the next implementation handoff.

- [Continuous BTC capture](./docs/e001_continuous_capture.md)
  Public Binance/Bybit recording without API keys, original messages and receipt clocks, bounded storage, reconnect diagnostics, integrity audits and commands for a fixed forward recording.

- [BTC capture replay](./docs/e001_capture_replay.md)
  Receipt-ordered book/ticker reconstruction, finite-depth coverage and timing checks. Preserves the original clock failure and the successful post-repair capture verification.

- [Live BTC feature pipeline](./docs/e001_live_features.md)
  Receipt-aware trade, liquidity, OI/funding/basis and price summaries; causal normalization shared by B4/MFSM; explicit missing values for unsupported economics and incomplete depth. Includes reproducible diagnostic commands and measured data limits.

- [Next implementation plan](./docs/e001_next_implementation_plan.md)
  Ordered tasks for clock evidence and uncertainty policy, capture recovery, eligible event/label tables and gated model evaluation. Includes file ownership, regression cases, acceptance criteria and a copyable coding-agent handoff.

- [Separate exploratory BTC result](./docs/e001_exploratory_btc_result.md)
  Fixed hourly receipt-time test on 19 free first-of-month BTC sample days. The added sell-pressure interaction gave only a tiny, unstable Brier improvement and did not demonstrate trading edge. The original E001 remains blocked.

## Epistemic status

MFSM is **not a validated trading system** and is **not a universal fragility score**.

The framework distinguishes four levels of support:

1. established source-domain mechanism;
2. structural financial analogue;
3. empirically supported financial relationship;
4. validated out-of-sample predictive contribution.

Only level 4 would justify treating a component as demonstrated predictive edge. The complete MFSM has not reached level 4.

The 2026-09-24 canonical revision separately evaluates mathematical completeness,
mechanistic validity, predictive usefulness, and decision usefulness. The
reference economy supplies a complete theoretical member; it does not establish
empirical support for its chosen behavioral or valuation rules.

Run the synthetic examples and mathematical checks with:

```bash
uv run --locked python scripts/run_mfsm_reference_economy.py
uv run --locked pytest -q tests/test_reference_economy.py
```

## How another LLM or research system should use this repository

1. Read the canonical model before proposing extensions.
2. Use the mathematical foundations to preserve the exact meaning of delay, gain, stability, memory, noise, and network propagation.
3. Use the empirical foundations to distinguish finance-supported mechanisms from analogy-derived hypotheses.
4. Follow the research protocol before applying or extending the model.
5. Do not collapse the model into a scalar score without new evidence.
6. Keep **Trend Strength (T)** and **Trend Sustainability (U)** separate from **absolute stressed consequence** \(F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)\), incremental causal consequence, and structural susceptibility.
7. Distinguish a disturbance class, the descriptor \(\delta=(c,V,a,d,t_0,p,\nu)\), and the full intervention operator \(\mathfrak I_{\delta}:(\mu_t,\mathcal G)\mapsto(\mu_t^{\delta},\mathcal G^{\delta})\); do not treat an endogenous outcome such as a run or cascade as the intervention itself.
8. Treat **remaining continuation capacity** as a mechanism-indexed family \(\{R_{k,t}^+\}_k\), not one market-wide scalar; keep it separate from **headroom (H)** and **opposing absorptive capacity (R-)**; prefer \(R^-_t(h;\delta,\varepsilon,\varphi)\) when timing, shock type, tolerated consequence, and incoming-flow profile matter.
9. Distinguish current headroom from the local initial-state buffer Jacobian \(\mathbf\Chi_B\), direct intervention sensitivity, and finite-shock buffer response \(\Delta\mathbf B^{\delta}\).
10. Treat delay as a response-time structure or memory kernel when possible, not automatically as one fixed scalar.
11. Require a **closed augmented latent state**: every independently evolving buffer, control state, coordination state, hybrid regime, and necessary delay history must be included. A finite-dimensional state is exact only if the memory law admits a finite-dimensional realization; otherwise label the approximation.
12. Separate the true observation mechanism from the analyst's measurement model; record identification status and plausible observationally equivalent alternatives.
13. Allow strategic complementarity / coordination vulnerability even when no prior trend exists.
14. Treat the conditional counterfactual path law \(\mathcal P_{t,h}^{\delta}\) as the theoretical response object; estimate only decision-relevant projections when practical.
15. Always state the system boundary, intervention operator, amplitude units, horizon, loss orientation, severity functional, measurable proxy, main confounders, falsifier, and identification status.
16. Compare any proposed signal against strong finance-specific baselines **and a flexible nonlinear model using the same raw information set** out of sample.
17. If a natural analogy cannot be mapped to an independently meaningful financial mechanism, discard it.
18. Until the current empirical program is tested, do not add new canonical state variables without a demonstrated theoretical necessity or empirical evidence.

## Current modeling direction

The mature MFSM object is conceptually

$$
\mathcal{M}_t =
\{\mathbf{Z}_t;\mathcal G,\mathcal O\}.
$$

where:

- $\mathbf{Z}_t$: **closed augmented latent dynamic state**;
- $\mathcal G$: fixed structural form plus any explicit exogenous laws;
- $\mathcal O$: true observation mechanism.

Any endogenously or stochastically evolving topology, kernel, coefficient, buffer, coordination state, or hybrid regime required for prediction belongs inside $\mathbf Z_t$ unless it is a predetermined input or has an explicit exogenous law in $\mathcal G$. The local Jacobian $J_t$ and termination classification $M_t^{term}$ are derived objects.

Closure also includes memory: a fixed delay generally requires a history segment rather than an instantaneous finite vector. A finite matrix $J_t$ applies to a justified finite-dimensional realization or a labeled approximation; exact delay stability requires the corresponding history-state analysis.

A disturbance descriptor \(\delta=(c,V,a,d,t_0,p,\nu)\) must be paired with a structural intervention operator on the full counterfactual specification:

$$
\mu_t
=
\mathcal L(\mathbf Z_t\mid\mathcal I_{t^-}),
\qquad
\mathfrak I_{\delta}:
(\mu_t,\mathcal G)
\mapsto
(\mu_t^{\delta},\mathcal G^{\delta}).
$$

This permits pure state-setting interventions, pure structural interventions, and hybrids.

Given that operator, the theoretical response object is the conditional counterfactual path law

$$
\mathcal P_{t,h}^{\delta}
=
\mathcal L(
\mathbf Z_{[t,t+h]}^{\delta}
\mid
\mathcal I_t
).
$$

The mean causal response

$$
\mathbf m_t^{\delta}(s)
=
\mathbb E[
\mathbf Z_{t+s}^{\delta}
-
\mathbf Z_{t+s}^{0}
\mid
\mathcal I_t
]
$$

is one projection of that law. Absolute stressed consequence is defined through a loss-oriented path functional \(\ell_{\mathrm{abs}}\) and risk/severity functional \(\rho\). Incremental causal consequence requires a two-path loss and explicit counterfactual coupling. Structural susceptibility studies how stressed consequence changes as a **standardized** disturbance amplitude varies.

The model should eventually be judged by whether these state descriptions improve out-of-sample discrimination among:

- shock-specific response severity;
- continuation;
- quiet exhaustion;
- controlled counterflow;
- threshold-driven unwind;
- coordination/run transitions;
- cross-asset propagation;

beyond ordinary momentum, volatility, leverage, valuation, liquidity, credit, and network baselines, while remaining robust to alternative measurement specifications.

## Current research phase

The conceptual architecture is now in **pre-freeze / empirical-testing preparation mode**. Freeze sequence: (1) commit the current cleanup, (2) create immutable annotated tags such as `mfsm-v1.0` and `e001-v1.1`, and then (3) populate the Experiment 001 freeze manifest with the resolved commit SHAs, schema versions, freeze timestamp, and holdout-access record. Confirmatory work begins only after that manifest is complete. After the freeze, progress should come primarily from falsifiable implementations rather than additional conceptual variables.

## Change discipline

When extending the repository:

- preserve causal definitions;
- distinguish theorem/model result from analogy and empirical evidence;
- state assumptions beside equations;
- preserve failed or rejected mappings;
- add measurement and falsification criteria for every new state variable;
- avoid retrospective explanations that cannot be prospectively tested.
