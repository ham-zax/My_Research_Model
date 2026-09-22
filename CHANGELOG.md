# MFSM Change Log

This file records material changes to the Market Feedback-State Model so definitions are not silently rewritten after empirical failure.

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
- Added controller topology \(\mathcal C_I\) so feed-forward opposition, delayed feedback, integral feedback, depletion, saturation, and thresholds are not conflated.

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
