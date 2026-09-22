# Operationalization Source Audit — 2026-09-22

Status: supporting research artifact
Role: record which ideas from the supplied operationalization draft were incorporated into MFSM, which were retained only conditionally, and which were rejected.

## Source provenance

- Conversation attachment filename: `Pasted markdown(20260922-170823).md`
- Conversation-file creation timestamp: 2026-09-22T17:08:22Z
- Author: unknown from the available conversation metadata
- Original title: not available beyond the attachment filename
- Repository retention: the original attachment is **not** copied into this repository; this audit preserves the incorporated claims, caveats, and rejection boundaries.

Source-quality note: the supplied document is treated here as a **research synthesis / idea generator**, not as independent validation of every equation or empirical claim it contains. Canonical MFSM claims should continue to rely on the primary finance/control sources already documented elsewhere in the repository.

## Incorporated

### Finite-horizon non-normal amplification

MFSM already contained a non-normality section. The source review motivated a sharper finite-horizon diagnostic:

\[
\mathcal A_t^{tr}(h)
=
\sup_{0\le s\le h}
\|\Phi(t+s,t)\|_2,
\]

with local frozen-state approximation

\[
\Phi(t+s,t)=e^{J_t s}.
\]

The numerical abscissa

\[
\omega(J_t)
=
\lambda_{\max}
\left(
\frac{J_t+J_t^\ast}{2}
\right)
\]

is retained as a derived local diagnostic of immediate Euclidean perturbation growth.

The key MFSM implication is:

\[
\text{asymptotic stability}
\not\Rightarrow
\text{finite-horizon path safety}.
\]

A transient excursion matters when it reaches a financing, liquidity, or behavioral switching surface before eventual decay.

These are derived response diagnostics, not new primitive state variables and not universal failure scores.

### Opposing capacity requires a tolerated consequence and an arrival profile

The source motivated a stronger operational definition of opposing capacity relative to horizon and tolerated price impact. A later staged review identified a remaining ambiguity: the same total notional can produce different stress depending on how quickly it arrives. MFSM therefore now treats the preferred object as

\[
R^-_t(h;\delta,\varepsilon,\varphi),
\]

where:

- \(h\) is the horizon;
- \(\delta\) is the structural disturbance/intervention;
- \(\varepsilon\) is a prespecified tolerated adverse consequence;
- \(\varphi\) is a normalized prespecified incoming-flow arrival profile.

For order-book work, \(\varepsilon_P\) can be a maximum tolerated adverse price displacement. The arrival-profile argument \(\varphi\) is a repository refinement added after reviewing the source; it should not be attributed to the source itself.

This preserves the distinction:

\[
\text{visible liquidity quantity}
\neq
\text{absorptive capacity}.
\]

### Stress-state measurement bias

Proxy discipline now records not only ordinary bias but how a proxy is expected to fail in the regime of interest:

\[
\text{latent object}
\rightarrow
\text{proxy}
\rightarrow
\text{failure mode}
\rightarrow
\text{stress-state bias sign + rationale}.
\]

This is especially important when visible liquidity, refill estimates, liquidation feeds, or open interest become least reliable during cascades.

### Experiment 001 opposing-capacity proxy

Experiment 001 now defines a narrow observable proxy for short-horizon BTC opposing capacity using:

1. executable visible depth inside a fixed price-displacement tolerance; plus
2. a strictly pre-decision estimate of durable replenishment capacity;
3. a standardized incoming-flow profile for interpreting that capacity.

The replenishment estimate excludes gross add-cancel churn through a prespecified dwell/observable-execution rule. Realized replenishment after the decision timestamp is explicitly forbidden as a predictor.

The experiment also separates venue-identified liquidation flow from generic aggressive selling, records expected stress-state bias signs with rationale for its core proxies, and explicitly permits `ambiguous` when opposing failure modes are plausible.

## Retained only as model-conditional statements

### Spectral-radius thresholds

A boundary such as

\[
\rho(P)=1
\]

is valid only inside the specified linear propagation system

\[
z_{t+1}=Pz_t.
\]

It is not a universal financial-system cascade threshold once propagation weights are state-dependent, losses saturate, defaults truncate exposures, or interventions change the system.

A later staged review added a further correction: for a time-varying sequence \(z_{n+1}=P_nz_n\), pointwise \(\rho(P_n)<1\) is not an asymptotic stability theorem. Products of individually stable noncommuting matrices can still grow, so time-varying systems require product-growth, contractivity, common-Lyapunov, joint-spectral-radius, or comparable conditions.

### Strategic-complementarity thresholds

MFSM retains \(\Gamma_t\) as a local strategic-complementarity diagnostic but rejects a universal numerical run threshold such as \(\Gamma=1\) without a fully specified and normalized best-response map.

### Fixed-delay stability thresholds

Conditions such as

\[
b\tau<\frac{\pi}{2}
\]

are retained only for the exact scalar fixed-delay model in which they are derived. They are not universal market danger thresholds.

A linear eigenvalue crossing does not by itself establish a supercritical nonlinear Hopf bifurcation or an attracting limit cycle.

## Not imported

### “Crises are endogenous rather than exogenous”

MFSM does not assume that sharp market events are endogenous instead of information-driven.

The canonical question is:

> Given the current structural state, how does a specified disturbance become amplified, damped, delayed, transmitted, or converted into forced behavior?

The initiating disturbance may be external, internal, or mixed.

### LVR as generic opposing capacity

Loss-Versus-Rebalancing remains useful for understanding AMM liquidity-provider economics and adverse-selection cost.

It is not identified with generic \(R^-\).

The acceptable chain is:

\[
\text{LVR / adverse selection cost}
\rightarrow
\text{LP incentive and willingness}
\rightarrow
R^-_{\text{AMM}}.
\]

### Exact latent-order-book capacity as an observable

Experiment 001 does not attempt to infer a full latent order book. It uses executable depth and strictly pre-decision replenishment behavior, with explicit stress-bias warnings.

## Scope consequence

The new material does **not** justify expanding the primitive MFSM state.

The useful additions are:

- one derived transient-amplification diagnostic;
- a tighter operational contract for \(R^-\);
- stronger measurement-failure discipline;
- a narrower microstructure proxy for Experiment 001.

This is consistent with the theory-freeze rule: improve typing, operationalization, and falsifiability before adding new conceptual variables.
