# My Research Model

This repository contains the canonical specification and supporting foundations for the **Market Feedback-State Model (MFSM)**.

MFSM is a research framework for diagnosing how reflexive market trends change the conditions governing their own continuation, exhaustion, instability, and failure propagation.

Its invariant question is:

> **How is the current trend changing the system's response to the next disturbance?**

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
6. Keep **Trend Strength (T)**, **Trend Sustainability (U)**, and **Failure Fragility (F)** separate.
7. Keep **remaining trend fuel (R+)**, **headroom (H)**, and **opposing absorptive capacity (R-)** separate.
8. Treat delay as a response-time structure or memory kernel when possible, not automatically as one fixed scalar.
9. Always state the system boundary, mechanism, measurable proxy, main confounders, and falsifier.
10. Compare any proposed signal against strong finance-specific baselines out of sample.
11. If a natural analogy cannot be mapped to an independently meaningful financial mechanism, discard it.

## Current modeling direction

The mature MFSM object is conceptually

$$
\mathcal{M}_t = \{\mathbf{X}_t, J_t, K_t, W_t, B_t, Q_t, M_t^{term}, \Sigma_t\}.
$$

where:

- $\mathbf{X}_t$: market state;
- $J_t$: local state-dependent response matrix;
- $K_t$: delay and memory kernels;
- $W_t$: economic propagation topology;
- $B_t$: usable buffers, capacities, and thresholds;
- $Q_t$: signal-source and expectation state;
- $M_t^{term}$: candidate termination mechanism;
- $\Sigma_t$: disturbance structure.

The model should eventually be judged by whether these state descriptions improve out-of-sample discrimination among:

- continuation;
- quiet exhaustion;
- controlled counterflow;
- threshold-driven unwind;
- cross-asset propagation;

beyond ordinary momentum, volatility, leverage, valuation, liquidity, credit, and network baselines.

## Change discipline

When extending the repository:

- preserve causal definitions;
- distinguish theorem/model result from analogy and empirical evidence;
- state assumptions beside equations;
- preserve failed or rejected mappings;
- add measurement and falsification criteria for every new state variable;
- avoid retrospective explanations that cannot be prospectively tested.

