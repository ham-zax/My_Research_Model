# Independent Review Synthesis — 2026-09-22

Status: supporting research artifact
Role: preserve the convergence of five independent reviews that motivated the post-path-law cleanup and theory freeze.

## Review mandates

The repository was independently reviewed from five deliberately different perspectives:

1. mathematical / dynamical-systems coherence;
2. causal inference / statistical identification;
3. empirical finance / market microstructure;
4. quantitative crypto implementation;
5. adversarial falsification / repository consistency.

The reviews were not asked to converge and were not given one another's conclusions.

## Consensus

The reviews broadly agreed that the current MFSM direction is coherent enough to preserve, but that the theory had reached the point where further conceptual expansion would create more risk than value.

Strongest surviving ideas:

- the market should be treated as a state-dependent response system rather than a price-only process;
- terminal expected response is insufficient when thresholds, transient amplification, tails, multimodality, and cascades matter;
- \(R^+\), \(H\), and \(R^-\) are economically distinct;
- current headroom and sensitivity of future headroom are distinct;
- capital that exists eventually is different from capacity that can act before a forced-action deadline;
- shock consequence is different from structural susceptibility;
- latent state is different from its observed proxy;
- correlation is not propagation topology;
- conceptual analogy is not financial evidence.

The reviews also converged on the view that MFSM has **not** demonstrated trading edge and should be judged by incremental out-of-sample information beyond established financial variables.

## Main problems identified

### 1. Dynamic-state closure

The former top-level representation listed \(\mathbf Z_t\) alongside buffers, expectations, networks, and other state-like objects, while the path law was defined only over \(\mathbf Z\).

This created ambiguity about whether the response path actually contained all variables required to determine threshold crossings, cascades, and recovery.

Resolution:

- \(\mathbf Z_t\) is now explicitly the **closed augmented latent state**;
- every independently evolving buffer, coordination state, control state, or hybrid mode required for prediction must be inside \(\mathbf Z_t\) or incorporated into its transition law;
- \(J_t\) is derived from local linearization;
- \(M_t^{term}\) is derived prospectively rather than primitive.

### 2. Intervention descriptor versus intervention semantics

The tuple

\[
\delta=(c,V,a,d,t_0,p,\nu)
\]

is useful metadata but does not uniquely define a counterfactual system.

Resolution:

Let \(\mu_t=\mathcal L(\mathbf Z_t\mid\mathcal I_{t^-})\). The intervention contract now acts on the full counterfactual specification:

\[
\mathfrak I_{\delta}:
(\mu_t,\mathcal G)
\mapsto
(\mu_t^{\delta},\mathcal G^{\delta}).
\]

This explicitly covers state-setting / jump interventions, structural interventions, and hybrids. Each application must define what part of the initial-state law or structural system changes, plus amplitude units, stochastic law/coupling, and timing.

### 3. Buffer sensitivity type

\(\mathbf\Chi_B\mathbf v_\delta\) is valid only when an intervention acts through an initial-state displacement.

Resolution:

- \(\mathbf\Chi_B\) is explicitly an **initial-state** Jacobian;
- general parameter/rule/kernel/forcing interventions require a direct intervention derivative;
- finite shocks use \(\Delta\mathbf B^\delta\).

### 4. Consequence versus causal effect

Risk under an intervention is not automatically risk caused by the intervention.

Resolution:

- \(F_t^{abs}\) = absolute stressed consequence under one intervention path;
- incremental causal path loss requires both \(\mathbf Z^\delta\) and \(\mathbf Z^0\) plus an explicit joint coupling;
- loss functionals inside severity objects must be oriented so larger means worse.

### 5. Coordinate dependence of susceptibility

The slope \(\partial F/\partial a\) changes if the disturbance amplitude is reparameterized.

Resolution:

- every disturbance family must define canonical economic amplitude units;
- cross-system comparison requires the same units or a prespecified normalized amplitude \(\tilde a=a/a_{ref}(c)\).

### 6. Observation versus analyst model

A flexible equation \(Y=g(Z;\psi)+\eta\) can hide the difference between the true observation process and the analyst's chosen proxy model.

Resolution:

- conceptual true mechanism: \(Y=g_*(Z)+\eta\);
- analyst models: \(g^{(m)}(Z;\psi^{(m)})\);
- important claims must survive a prespecified finite measurement-model set;
- every important latent estimate should report identification status and the closest plausible observationally equivalent alternative.

### 7. Disturbance-dependent absorption

Opposing capacity can depend on what kind of shock is occurring, not only on horizon.

Resolution:

\[
R^-_t(h;\delta)
\]

is the stronger form. \(R^-_t(h)\) remains shorthand when the disturbance is already fixed.

### 8. Redundancy and retrospective flexibility

The reviews warned that the combination of state choice, measurement model, disturbance definition, horizon, loss functional, kernel, threshold map, and termination label creates many researcher degrees of freedom.

Resolution:

- \(R^+\) is a category whose operational quantities remain mechanism-indexed as \(R_{k,t}^+\);
- \(C\) must be derived from a specified propagation operator/state/law rather than treated as a free scalar;
- \(\Theta\) is only a summary of response-time structure;
- \(L\) is optional derived threshold exposure rather than primitive;
- \(M^{term}\) must be prospectively inferred;
- new canonical variables are frozen until empirical testing shows a real missing mechanism.

## Finance novelty conclusion

The independent finance review did not identify a new fundamental financial mechanism.

The plausible contribution is instead an integrated **measurement and interaction architecture**, especially:

\[
H\times\Chi_B,
\]

\[
R^-_t(h;\delta)\times\text{forced-action deadline},
\]

and, where identifiable,

\[
D\times W.
\]

The research claim should therefore be incremental:

> Do these state-conditioned interactions improve prospective response estimation beyond standard leverage, liquidity, volatility, positioning, and network measures?

## Empirical null

The project should be considered materially weakened if a flexible conventional model using the **same raw information set** performs equally well out of sample.

MFSM gets no credit for rediscovering nonlinear combinations that a generic model can learn directly from the same inputs.

## Crypto implementation conclusion

The first crypto implementation should not attempt to estimate all MFSM variables.

The narrow candidate is:

> distinguish forced-liquidation exhaustion from a continuing deleveraging cascade after a standardized BTC downside event.

The most plausible initial use is:

\[
\text{risk controller}
>
\text{regime filter}
>
\text{direct alpha}.
\]

The first empirical test is specified separately in `experiments/Experiment_001_Crypto_Liquidation_Response.md`. Its final preregistration requires a strict untouched ETH holdout, a flexible baseline with the same primitive historical information as the MFSM feature model, and the administrative freeze record in `experiments/Experiment_001_Freeze_Manifest.yaml`.

## Theory-freeze rule

Until the first empirical program is tested, the default response to a new idea is **not** to add a new canonical variable.

A new canonical variable requires:

1. a demonstrated theoretical contradiction that the current closed-state architecture cannot represent; or
2. empirical evidence from a prespecified test showing that an omitted mechanism is required.

The research priority is now:

\[
\boxed{
\text{formal cleanup}
\rightarrow
\text{freeze}
\rightarrow
\text{prospective experiment}
\rightarrow
\text{holdout replication}
\rightarrow
\text{only then revise theory}.
}
\]
