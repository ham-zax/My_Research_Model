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

- [CHANGELOG.md](./CHANGELOG.md)
  Material model changes and preserved definitions, so the framework is not silently redefined after results.

- [artifacts/source_review_extended_2026-09-22.md](./artifacts/source_review_extended_2026-09-22.md)
  Source-by-source audit of the extended finance/control literature that motivated the shock-conditioned response, strategic coordination, constraint-sensitivity, and observation-model revisions.

## Epistemic status

MFSM is **not a validated trading system** and is **not a universal fragility score**.

The framework distinguishes four levels of support:

1. established source-domain mechanism;
2. structural financial analogue;
3. empirically supported financial relationship;
4. validated out-of-sample predictive contribution.

Only level 4 would justify treating a component as demonstrated predictive edge. The complete MFSM has not reached level 4.

## How another LLM or research system should use this repository

1. Read the canonical model before proposing extensions.
2. Use the mathematical foundations to preserve the exact meaning of delay, gain, stability, memory, noise, and network propagation.
3. Use the empirical foundations to distinguish finance-supported mechanisms from analogy-derived hypotheses.
4. Follow the research protocol before applying or extending the model.
5. Do not collapse the model into a scalar score without new evidence.
6. Keep **Trend Strength (T)** and **Trend Sustainability (U)** separate from **shock-conditioned consequence** \(F_t(\delta,h;\ell,\rho)\) and from structural susceptibility across disturbance amplitude.
7. Distinguish a disturbance class from a fully specified structural intervention \(\delta\); do not treat an endogenous outcome such as a run or cascade as the intervention itself.
8. Keep **remaining trend fuel (R+)**, **headroom (H)**, and **opposing absorptive capacity (R-)** separate; horizon-qualify \(R^-_t(h)\) when timing matters.
9. Distinguish current headroom from the local constraint-sensitivity Jacobian \(\mathbf\Chi_B\) and from the finite-shock buffer response \(\Delta\mathbf B^{\delta}\).
10. Treat delay as a response-time structure or memory kernel when possible, not automatically as one fixed scalar.
11. Separate latent structural state from observed proxies and record measurement-model choices.
12. Allow strategic complementarity / coordination fragility even when no prior trend exists.
13. Treat the conditional counterfactual path law \(\mathcal P_{t,h}^{\delta}\) as the theoretical response object; estimate only decision-relevant projections when practical.
14. Always state the system boundary, structural intervention, horizon, path-level loss functional, severity functional, measurable proxy, main confounders, and falsifier.
15. Compare any proposed signal against strong finance-specific baselines out of sample.
16. If a natural analogy cannot be mapped to an independently meaningful financial mechanism, discard it.

## Current modeling direction

The mature MFSM object is conceptually

$$
\mathcal{M}_t =
\{\mathbf{Z}_t,J_t,K_t,W_t,B_t,Q_t,\mathcal C_{I,t},M_t^{term},\Sigma_t,\mathcal O_t\}.
$$

where:

- $\mathbf{Z}_t$: latent structural market state;
- $J_t$: local state-dependent response matrix;
- $K_t$: delay and memory kernels;
- $W_t$: economic propagation topology;
- $B_t$: usable buffers, capacities, and thresholds;
- $Q_t$: signal-source, expectation, and coordination state;
- $\mathcal C_{I,t}$: opposing/control topology;
- $M_t^{term}$: candidate termination mechanism;
- $\Sigma_t$: disturbance structure;
- $\mathcal O_t$: observation / measurement process.

For a fully specified structural intervention \(\delta\), the theoretical response object is the conditional counterfactual path law

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

is one projection of that law. Shock-conditioned consequence is defined through a path-level loss functional \(\ell\) and risk / severity functional \(\rho\), while structural susceptibility studies how consequence changes as disturbance amplitude varies.

The model should eventually be judged by whether these state descriptions improve out-of-sample discrimination among:

- shock-specific response severity;
- continuation;
- quiet exhaustion;
- controlled counterflow;
- threshold-driven unwind;
- coordination/run transitions;
- cross-asset propagation;

beyond ordinary momentum, volatility, leverage, valuation, liquidity, credit, and network baselines, while remaining robust to alternative measurement specifications.

## Change discipline

When extending the repository:

- preserve causal definitions;
- distinguish theorem/model result from analogy and empirical evidence;
- state assumptions beside equations;
- preserve failed or rejected mappings;
- add measurement and falsification criteria for every new state variable;
- avoid retrospective explanations that cannot be prospectively tested.

