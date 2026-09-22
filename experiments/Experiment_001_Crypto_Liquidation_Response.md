# Experiment 001 — Crypto Liquidation Exhaustion vs Continuing Deleveraging

Status: experimental, non-canonical
Primary market: BTC perpetuals with independent BTC spot reference
Confirmatory holdout: ETH
Purpose: test whether a narrow observable MFSM state adds prospective information beyond standard crypto variables.

## 0. Freeze and reproducibility contract

This file is a **pre-freeze candidate specification**. No confirmatory ETH analysis and no claim of a frozen Experiment 001 may occur until the model/spec commits are finalized and tagged.

Required immutable references:

- MFSM architecture tag: `mfsm-v1.0`;
- Experiment 001 specification tag: `e001-v1.0`;
- raw-data schema version: **TBD before data extraction**;
- feature-schema version: **TBD before model fitting**;
- label-schema version: `E001-label-v1`;
- freeze timestamp: **TBD**.

Because a Git commit cannot contain its own final hash without changing that hash, the exact resolved commit SHAs are recorded **after** the frozen commits/tags exist in `Experiment_001_Freeze_Manifest.yaml`. That manifest is an administrative research record and may be committed after the tagged model/spec commit or archived with the research run.

Any later change to labels, feature definitions, data semantics, holdout policy, or evaluation rules requires a new experiment-spec version and changelog entry.

## 1. Research question

Can observable MFSM-style state distinguish:

1. **forced-liquidation exhaustion** — the initial deleveraging wave has largely cleared and liquidity is recovering;

from

2. **continuing deleveraging cascade** — losses are still generating forced same-direction flow faster than opposing capacity can replenish?

The target is **not** generic BTC direction prediction.

The target is:

> given a standardized downside event and information available shortly after it occurs, estimate the distribution of the subsequent path.

## 2. Epistemic boundary

The first implementation is an **observational predictive experiment**, not proof of a structural do-intervention.

The event definition below is a conditioning event. It does not by itself identify

\[
\mathcal P^\delta_{t,h}.
\]

The experiment estimates selected observable projections that are motivated by MFSM.

If these projections do not add stable out-of-sample information beyond strong same-data baselines, the experiment should be counted as a failure of the proposed trading edge.

## 3. Universe

Development market:

- BTC perpetual futures;
- independent BTC spot composite;
- multiple liquid venues where feed semantics can be audited.

Preferred venue set for research:

- Bybit;
- Binance;
- OKX;

subject to historical data quality and feed-semantic validation.

Confirmatory holdout:

- ETH, with definitions and model specification frozen before evaluation.

**Strict holdout rule:** no ETH data may be inspected, summarized, plotted, used for feature selection, threshold selection, model tuning, propagation analysis, or narrative development before the BTC development specification is frozen and the confirmatory protocol is locked. After the frozen ETH confirmatory score has been computed, ETH may be used for clearly labeled post-confirmatory secondary analysis.

Do not pool incompatible venue fields merely because they have the same name.

## 4. Event definition

Let \(P_t^{spot}\) be the frozen independent BTC spot-composite price sampled on the experiment's canonical one-second grid. The composite's venue constituents, weighting rule, stale-price handling, and missing-data rule must be fixed in the raw-data schema before event extraction.

Define the five-minute point-to-point return

\[
r_{5m}(t)
=
\frac{
P_t^{spot}
}{
P_{t-300s}^{spot}
}
-1.
\]

A candidate trigger occurs when

\[
r_{5m}(t)
\le
-0.0100.
\]

Define \(t_0\) as the first eligible one-second timestamp satisfying

\[
r_{5m}(t_0)\le-0.0100,
\qquad
r_{5m}(t_0-1s)>-0.0100,
\]

with both grid values valid, subject to the episode lockout below.

This definition is point-to-point over exactly 300 seconds. It is **not** a drawdown from the maximum inside the preceding five-minute window and not an arbitrary pairwise decline inside that window.

### Episode lockout

After an accepted event at \(t_0\), define the episode

\[
[t_0,t_0+2\text{ h}).
\]

Any additional 1% five-minute threshold crossing inside that interval belongs to the same episode and **cannot** start a new observation. The next eligible event is the first new threshold crossing at or after \(t_0+2\text{ h}\).

If the spot composite lacks a valid price at either endpoint needed for \(r_{5m}(t)\), that timestamp is ineligible for event generation under the frozen data-quality rule.

Do not define the trigger from the same perpetual contract whose post-event response is being traded.

For the strict ETH confirmation, apply the **identical trigger formula, threshold, grid, lockout, and decision delay** using the frozen independent ETH spot composite. No ETH-specific threshold or timing retuning is permitted.

## 5. Decision timestamp

Allow a fixed observation interval after the trigger:

\[
t_d=t_0+15\text{ seconds}.
\]

All model features must be timestamped as available no later than \(t_d\).

The prediction and any simulated trade occur at or after \(t_d\).

This converts immediate post-trigger information into legitimate features rather than look-ahead.

## 6. Primary downside-continuation target

Let \(P_d\) be the independent BTC spot-composite price observed at the decision timestamp \(t_d\).

Define the lower and upper barriers

\[
B_- = P_d(1-0.0100),
\qquad
B_+ = P_d(1+0.0075).
\]

For \(s>t_d\), define first-passage times

\[
\tau_-
=
\inf\{s>t_d:P_s\le B_-\},
\]

\[
\tau_+
=
\inf\{s>t_d:P_s\ge B_+\}.
\]

For evaluation horizon \(h\in\{30\text{ min},120\text{ min}\}\), the primary binary target is

\[
\boxed{
Y_h
=
\mathbf 1
\{
\tau_-<\tau_+,
\;
\tau_-\le t_d+h
\}.
}
\]

Thus "additional decline" and "recovery" are both anchored to \(P_d\), not to \(P_{t_0}\) or to an ex-post extremum. If neither barrier is reached before \(t_d+h\), then \(Y_h=0\).

Interpret \(Y_h\) as **downside continuation before recovery versus not-downside-first**. It is not, by itself, a literal two-class label for "liquidation exhaustion" versus "continuing cascade," because the negative class includes both recovery-first paths and unresolved/sideways paths.

Define the secondary competing-risk state

\[
C_h
\in
\{
\text{downside-first},
\text{recovery-first},
\text{neither-by-}h
\},
\]

using the same \(\tau_-\), \(\tau_+\), and horizon. Survival / competing-risk analyses should use \(C_h\) or the underlying passage times rather than silently treating every \(Y_h=0\) path as exhaustion.

This is deliberately path-dependent.

## 7. Secondary targets

Estimate or record:

- maximum adverse excursion at 15 / 30 / 60 / 120 minutes;
- maximum favorable excursion;
- probability of 50% retracement of the initial event;
- time to 50% retracement;
- OI contraction;
- cumulative observable liquidation activity normalized by pre-event OI;
- remaining OI after the initial purge;
- spread recovery;
- executable bid-depth recovery;
- basis normalization;
- mark/index normalization;
- continuing liquidation intensity;
- realized cascade size under a prespecified definition.

For recovery-time targets, censor paths that do not recover inside the evaluation horizon.

Example depth-recovery definition:

> time until executable bid depth within 25 bps returns to at least 80% of its pre-event 30-minute median and remains there for 60 seconds.

Freeze exact thresholds before the final test period.

## 8. Narrow MFSM hypothesis

The first implementation should use only a small subset of the framework.

The proposed mechanism is approximately

\[
\text{continuation risk}\uparrow
\quad\text{when}\quad
\frac{\text{forced sell pressure}}
{R^-_{\mathrm{short}}}
\uparrow,
\]

while liquidity replenishment slows and residual leverage remains high.

The intended measured components are:

### 8.1 Liquidation-specific pressure versus generic aggressive selling

Do not call ordinary aggressive selling "forced." Keep the two observable mechanisms separate.

Define

\[
Q^{liq}_{v,\mathrm{recent}}
=
\text{venue-identified liquidation sell notional}
\]

over the frozen recent-flow window

\[
\boxed{
w_{flow}=h_R=30\text{ seconds}
}
\]

ending at \(t_d\), i.e. \((t_d-30s,t_d]\).

Separately define

\[
Q^{aggr,exliq}_{v,\mathrm{recent}}
=
\text{aggressive sell notional in }(t_d-30s,t_d]
\text{ excluding executions identified as liquidation flow where possible}.
\]

Where venue identifiers permit matching, executions already represented in the liquidation feed must be removed from \(Q^{aggr,exliq}\). If the venue feed cannot support reliable de-duplication, report \(Q^{liq}\) separately but flag \(Q^{aggr,exliq}\) as potentially contaminated. Even after removing identified liquidations, \(Q^{aggr,exliq}\) is **not assumed voluntary**; it may still contain unidentified forced, hedging, informed, or discretionary flow.

The primary mechanism-specific MFSM interaction is liquidation pressure relative to short-horizon opposing capacity:

\[
\boxed{
\mathrm{LFP}_{v,t_d}
=
\frac{
Q^{liq}_{v,\mathrm{recent}}
}{
\widetilde R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi_{unif})
}
}
\]

The secondary generic sell-pressure interaction is

\[
\boxed{
\mathrm{SPP}_{v,t_d}
=
\frac{
Q^{aggr,exliq}_{v,\mathrm{recent}}
}{
\widetilde R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi_{unif})
}.
}
\]

If only \(\mathrm{SPP}\) predicts continuation while \(\mathrm{LFP}\) does not, the result should not be described as evidence for forced-liquidation pressure specifically.

For comparison, retain ordinary aggressive-sell notional divided by executable visible depth as a conventional microstructure baseline feature.

Liquidation-feed and trade-feed semantics must be audited venue by venue.

### 8.2 Short-horizon opposing capacity

The canonical theoretical object is flow-profile-qualified:

\[
R^-_t(h;\delta,\varepsilon_P,\varphi).
\]

Experiment 001 does **not** identify a structural intervention \(\delta\). It conditions on an observed downside-trigger state. Therefore the empirical quantity below deliberately drops \(\delta\):

\[
\boxed{
\widehat R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi)
}
\]

is an **observed-state liquidity-capacity proxy motivated by the canonical \(R^-\)**, not an estimate of disturbance-conditioned causal capacity.

Here \(\varepsilon_P\) is a maximum tolerated adverse price displacement and \(\varphi\) specifies how the standardized incoming sell flow arrives through the horizon.

For Experiment 001, use a **primary microstructure tolerance**

\[
\boxed{
\varepsilon_P=25\text{ bps}
}
\]

from each venue's local mid-price at \(t_d\), a primary opposing-capacity horizon

\[
\boxed{
h_R=30\text{ seconds},
}
\]

and the standardized uniform arrival profile

\[
\boxed{
\varphi_{unif}(s)
=
\frac{1}{h_R}
\mathbf 1_{[0,h_R]}(s).
}
\]

This is a standardized benchmark, not a claim that realized liquidation pressure is uniform. More front-loaded flow can imply lower effective capacity. Any secondary front-loaded profile must be specified before freeze.

For venue \(v\), define the observable proxy

\[
\boxed{
\widehat R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi_{unif})
=
D^{exec}_{v,t_d}(\varepsilon_P)
+
h_R
\widehat q^{repl}_{v,t_d}(\varepsilon_P).
}
\]

where \(D^{exec}_{v,t_d}(\varepsilon_P)\) is immediately executable bid notional within \(\varepsilon_P\).

#### Durable replenishment estimator

Set the primary replenishment lookback to

\[
\boxed{
w_{repl}=15\text{ seconds}
}
\]

ending at \(t_d\), and the minimum durability interval to

\[
\boxed{
\tau_{dwell}=1\text{ second}.
}
\]

Within \([t_d-w_{repl},t_d]\), track positive bid-depth deltas at fixed price levels that are inside the contemporaneous \(\varepsilon_P\) band.

A positive depth delta added at time \(t_{add}\) contributes to **durable replenishment** only if its qualifying evidence is fully observable by \(t_d\):

1. **dwell-qualified:** \(t_{add}+\tau_{dwell}\le t_d\) and the added quantity remains resting at that same price level through \(t_{add}+\tau_{dwell}\); or
2. **execution-qualified:** the added quantity is observably executed against incoming sell flow at some \(t_{exec}\le t_d\) before cancellation.

Orders added too late to complete the dwell interval by \(t_d\) receive **no dwell credit**, unless they satisfy the execution-qualified rule by \(t_d\).

If the historical feed cannot distinguish execution from cancellation at the required granularity, use the conservative dwell-only rule. Under no circumstance may post-\(t_d\) book state, executions, or cancellations be consulted when constructing \(\widehat q^{repl}_{v,t_d}\).

Define

\[
\boxed{
\widehat q^{repl}_{v,t_d}(\varepsilon_P)
=
\frac{
\sum \text{durable bid replenishment notional}
}{
w_{repl}
}.
}
\]

This excludes gross add-cancel churn from the replenishment estimate. It also uses only the frozen primitive history

\[
X^{raw}_{[t_d-w,t_d]}
\]

available by the decision timestamp. Do not use realized replenishment after \(t_d\) as a predictor.

#### Near-zero capacity rule

The denominator floor must transfer unchanged from BTC development to the strict ETH holdout, so it is defined from each event's own **pre-trigger observable liquidity scale**, not from the holdout distribution.

Let

\[
D^{pre}_{v,t_0}(\varepsilon_P)
=
\operatorname{median}_{s\in[t_0-30\mathrm{m},t_0)}
D^{exec}_{v,s}(\varepsilon_P).
\]

Freeze the scale fraction

\[
\boxed{
\eta_{floor}=0.01
}
\]

and define

\[
\boxed{
R^{floor}_{v,t_0}
=
\eta_{floor}
D^{pre}_{v,t_0}(\varepsilon_P).
}
\]

Then use

\[
\boxed{
\widetilde R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi_{unif})
=
\max
\left[
\widehat R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi_{unif}),
R^{floor}_{v,t_0}
\right].
}
\]

In ratio features also include the low-capacity indicator

\[
\boxed{
I^{lowcap}_{v,t_d}
=
\mathbf 1
\left\{
\widehat R^-_{v,t_d}
(h_R;\varepsilon_P,\varphi_{unif})
\le R^{floor}_{v,t_0}
\right\}.
}
\]

If the venue lacks a valid positive pre-trigger depth median over the required window, exclude that venue-specific capacity feature for the event rather than inventing an ad hoc denominator. This rule is deterministic and uses only information available before the event/decision timestamp, so it can be applied unchanged to ETH without inspecting its outcome distribution.

Do not automatically sum venue capacities: capital, inventory, and transferability constraints can make apparent cross-venue depth non-fungible. Venue-specific values should remain separate unless an aggregation rule is justified and frozen.

This is an observable proxy for short-horizon absorptive capacity under the standardized \(\varphi_{unif}\) profile, not a claim to measure the full latent \(R^-\).

### 8.3 Response-time structure

Approximate \(K\) with:

- bid-depth refill time;
- spread normalization time;
- basis convergence time;
- cross-venue response delay.

### 8.4 Residual leverage

Candidate proxies:

- remaining OI relative to pre-event level;
- OI contraction during the initial event;
- funding state;
- basis state.

Do not interpret OI changes mechanically as one position direction without supporting flow evidence.

### 8.5 Derivative / spot stress

Candidate variables:

- perp/spot basis;
- mark/index divergence;
- funding;
- cross-venue basis dispersion.

### 8.6 Propagation proxy

Candidate **BTC-development** variables:

- cross-venue BTC synchronization;
- whether BTC perpetual selling leads or lags the independent BTC spot composite.

ETH variables are excluded from development because ETH is the strict confirmatory holdout. BTC-to-ETH propagation may be examined only after the frozen ETH confirmation has been scored, and then only as explicitly post-confirmatory secondary analysis.

Do not call lead-lag or correlation a causal network without a stronger design.

### 8.7 Measurement failure-direction contract

For every Experiment 001 proxy, record not only ordinary measurement error but how that proxy is expected to fail **during a liquidation cascade**.

| Latent target | Observable proxy | Stress-state failure mode | Expected sign + rationale |
| --- | --- | --- | --- |
| Short-horizon \(R^-\) | executable visible bid depth | quotes can cancel before impact, while hidden liquidity/new capital are absent from the displayed book | **ambiguous**: cancellation biases displayed capacity high; hidden/new capacity biases it low |
| Replenishment component of \(R^-\) | durable pre-decision refill-rate estimate | liquidity providers can withdraw when toxicity/volatility jumps | usually **high/optimistic** if recent refill behavior fails to persist |
| Liquidation pressure | venue liquidation feed | sampled/delayed/incomplete messages or duplicated event semantics | usually **low** if incomplete, but can be **high** if duplicate/repeated events are not removed |
| Generic aggressive selling | aggressive sell trade flow | mixes informed, discretionary, hedging, inventory, and possibly unidentified forced flow | **ambiguous mechanism attribution** rather than a simple level bias |
| Residual leverage | open interest level/change | openings and closings can offset; venue aggregation masks position direction | **ambiguous** |
| Derivative/spot stress | funding, basis, mark/index divergence | update-frequency and index-methodology differences | **ambiguous / venue-dependent**, often lagged |

"Ambiguous" is an admissible preregistered bias sign when opposing failure modes are economically plausible. The requirement is **expected sign plus rationale**, not forced certainty. Any change after viewing holdout performance requires a new experiment version.

## 9. Exhaustion signature

A candidate exhaustion pattern is:

- large initial liquidation burst;
- material OI purge;
- falling marginal liquidation intensity;
- rapid bid-depth replenishment;
- spread improvement;
- basis / mark dislocation normalization.

The core idea is that a large realized liquidation burst can mean either:

1. acceleration of forced selling; or
2. clearing of the positions that created the vulnerability.

The response of residual OI, marginal forced-flow intensity, and opposing capacity is what should separate those cases.

## 10. Variables excluded from Experiment 001

Do not make success depend on estimating:

- market-wide \(D_t\);
- primitive strategic-complementarity \(\Gamma_t\);
- literal \(E=S_{end}/S_{ext}\);
- complete market-wide headroom \(H\);
- true counterparty/exposure network \(W_t\);
- unrestricted causal counterfactual path law;
- generic controller topology;
- a universal \(R^+\) scalar;
- full-system non-normal transient amplification \(\mathcal A_t^{tr}(h)\) or pseudospectral diagnostics unless a separate identification design is developed.

These may remain theoretical objects or future research targets. Experiment 001 should not become a catch-all implementation of the full MFSM architecture.

## 11. Baseline ladder

MFSM receives no credit for renaming familiar variables.

Use at least:

### B0 — Event-only baseline

- event amplitude;
- event speed;
- time of day;
- basic market state.

### B1 — Price/volatility baseline

B0 plus:

- multi-horizon returns;
- momentum / reversal;
- realized volatility.

### B2 — Derivatives baseline

B1 plus:

- funding;
- OI level and change;
- basis;
- raw liquidation activity.

### B3 — Microstructure baseline

B2 plus:

- spread;
- depth;
- ordinary book imbalance.

### B4 — Flexible same-information-set baseline

Define a frozen primitive information panel

\[
X^{raw}_{[t_d-w,t_d]},
\]

with \(w=30\) minutes by default, containing the exact primitive observations available by \(t_d\): prices/returns, raw trades and aggressor flags, liquidation messages and event identifiers where available, raw L2 order-book snapshots/deltas or the highest-fidelity historical book feed used to reconstruct fixed-price-level depth changes, OI, funding/basis state, mark/index state, venue-status fields, and any other primitive series required to construct an MFSM feature.

B4 must receive this **same primitive historical information**, not merely contemporaneous B3 snapshots. If an MFSM feature requires an additional primitive history, that history must also be available to B4 before freeze.

#### Shared neutral preprocessing layer

To prevent MFSM from winning merely because a human supplied it a better event-stream representation, define one frozen neutral preprocessing map

\[
\boxed{
U_{t_d}
=
U\!\left(
X^{raw}_{[t_d-w,t_d]}
\right)
}
\]

that is supplied to **both** B4 and the MFSM feature model.

The shared neutral layer must include, over the frozen windows

\[
\mathcal W
=
\{1s,5s,15s,30s,60s,5m\},
\]

where the underlying feed supports them:

- liquidation notional / rate;
- aggressive-buy and aggressive-sell notional / rate;
- gross bid/ask add rate;
- durable bid/ask add rate under the frozen dwell rule;
- cancel rate;
- observable execution rate;
- current and lagged executable depth;
- spread and ordinary book imbalance;
- OI level and percentage/log change;
- funding, basis, and mark/index divergence;
- returns and realized-volatility summaries.

These are **neutral summaries**, not MFSM interactions. For example, B4 receives durable replenishment rate itself, not only raw order-book deltas, because MFSM also uses that event-stream information.

#### Frozen scale-normalization policy

BTC-to-ETH confirmation must not be confounded by raw notional scale. Both models therefore receive the same causally available dimensionless / relative versions of scale-sensitive variables.

Use only pre-trigger or decision-time denominators defined without holdout-distribution fitting:

- executable depth: divide by \(D^{pre}_{v,t_0}(\varepsilon_P)\);
- trade, liquidation, add, cancel, and execution notional: provide versions divided by \(D^{pre}_{v,t_0}(\varepsilon_P)\), and where available by pre-trigger OI;
- OI: define
  \[
  OI^{pre}_{v,t_0}
  =
  \operatorname{median}_{s\in[t_0-30m,t_0)}
  OI_{v,s},
  \]
  then provide percentage/log changes relative to \(OI^{pre}_{v,t_0}\) rather than relying on raw level alone;
- spread, basis, funding, and mark/index divergence: represent in bps / dimensionless units;
- returns and volatility: already dimensionless.

If a required pre-trigger scale denominator is missing, nonpositive, or fails the frozen data-quality rule, omit that normalized feature for the event / venue rather than substituting a value learned from BTC or ETH distributions.

For the **primary BTC-to-ETH confirmatory comparison**, define

\[
U^{norm}_{t_d}
\]

as the neutral preprocessing panel after the frozen causal scale normalizations above. Both B4 and the MFSM model must use this same normalized neutral representation as their shared base.

Raw scale-sensitive values may be retained only for clearly labeled **within-BTC secondary diagnostics**. They are excluded from the primary cross-asset confirmatory models so MFSM cannot appear to transfer better merely because its ratios are dimensionless while B4 is exposed to BTC-scale notionals.

The primary \(U^{norm}_{t_d}\) schema may contain only features whose field semantics and historical availability pass the frozen data-schema audit for both the BTC development universe and the ETH confirmatory universe. Venue/asset-specific extras may appear only in secondary within-BTC analyses.

A flexible nonlinear learner receiving \(U^{norm}_{t_d}\) is the mandatory primary B4 comparator.

### MFSM feature model

For the primary confirmatory test, MFSM receives the same \(U^{norm}_{t_d}\), then adds only deterministic, prespecified **theory-motivated combinations** of those shared components, such as:

- \(\mathrm{LFP}=Q^{liq}/\widetilde R^-\);
- \(\mathrm{SPP}=Q^{aggr,exliq}/\widetilde R^-\);
- prespecified response-time ratios or interactions.

MFSM receives no raw feed, event-stream summary, history window, timestamp, venue field, or normalization unavailable to B4.

Model-selection parity is required:

- identical outer train/test episodes;
- identical timestamp cutoff;
- identical neutral preprocessing \(U(\cdot)\) and identical normalized base \(U^{norm}_{t_d}\) for the primary BTC-to-ETH comparison;
- comparable inner validation;
- B4 hyperparameter-search budget no smaller than the MFSM feature model's tuning budget;
- identical calibration and scoring procedures where applicable.

If MFSM beats B1/B2 but not B4, classify the result as useful feature engineering rather than demonstrated incremental structural information.

## 12. Initial model family

Start with:

- regularized logistic regression;
- survival / competing-risk models where appropriate;
- simple calibrated gradient boosting as nonlinear comparison.

Do not begin with a large neural state-space model.

The first question is whether any stable incremental information exists.

## 13. Validation design

Use episode-level walk-forward or expanding-window evaluation.

Do not randomly split ticks from the same cascade across train and test.

Required checks:

- calibration;
- Brier score;
- log loss;
- precision-recall for rare continuation/cascade events;
- episode-clustered confidence intervals;
- economic value after costs;
- sensitivity to event-threshold choices fixed before holdout;
- leave-largest-events-out analysis;
- venue holdout where feasible;
- BTC development -> strict frozen ETH confirmation, with no ETH inspection before the confirmatory lock.

## 14. Timestamp discipline

Store both:

- exchange event timestamp;
- local receipt timestamp.

A cross-venue lead-lag feature that exists only under exchange timestamps but disappears under realistic receipt times should not be trusted as live edge.

All features must respect actual historical availability.

## 15. Data requirements

Raw immutable store should ideally contain:

- spot trades;
- perpetual trades;
- L2 order-book deltas / snapshots;
- spread and depth;
- mark price;
- index price;
- open interest;
- funding;
- basis;
- liquidation messages;
- venue status / outage markers;
- contract specification changes.

Historical liquidation feeds must be audited individually. A sampled liquidation stream is not equivalent to an exhaustive event feed.

## 16. Execution assumptions

For Experiment 001, prefer taker-style or deliberately conservative execution assumptions.

Public L2 data normally do not identify exact queue position well enough to justify optimistic maker fills.

Every strategy translation must include:

- maker/taker fees;
- spread;
- depth-dependent slippage;
- fixed decision/execution latency scenarios;
- funding if a position crosses funding time;
- outages / feed gaps;
- venue and contract changes.

Stress costs and latency rather than using one optimistic estimate.

## 17. Trading use hierarchy

The intended first use is

\[
\boxed{
\text{risk controller}
>
\text{regime filter}
>
\text{direct alpha}.
}
\]

### Risk-controller interpretation

Suppose an existing strategy normally fades sharp BTC selloffs.

MFSM-derived features should suppress or downsize the fade while:

- liquidation pressure \(\mathrm{LFP}\) remains high relative to short-horizon opposing capacity;
- residual OI remains elevated;
- book replenishment is weak;
- spreads remain impaired;
- derivative/spot stress has not normalized.

It may permit normal fade behavior after:

- material leverage clearing;
- falling marginal liquidation intensity;
- rapid bid replenishment;
- normalization of derivative dislocations.

MFSM does not need standalone directional alpha to have economic value if it prevents enough severe losses without suppressing too many profitable reversals.

## 18. Kill criteria

The trading thesis should be materially weakened if any of the following occur:

1. B4, the flexible raw-feature baseline, matches MFSM out of sample.
2. Performance disappears after realistic taker costs and slippage.
3. Results depend on one or two extreme episodes.
4. Results fail after episode-level rather than tick-level resampling.
5. Frozen BTC definitions fail materially on ETH or a venue/time holdout.
6. The sign of key interactions changes repeatedly across adjacent test periods without institutional explanation.
7. Liquidation-feed semantics or timestamp corrections remove the effect.
8. Performance requires repeatedly redefining latent MFSM proxies after seeing results.

If these occur, do not add more conceptual variables to rescue the test.

## 19. Success criterion

A result becomes scientifically interesting if the prespecified MFSM feature set:

1. improves out-of-sample probability calibration or path-target prediction over B4;
2. survives episode-clustered uncertainty;
3. preserves mechanism-consistent directions;
4. transfers with frozen definitions to ETH and/or another holdout;
5. produces net economic value after realistic costs when used as a risk controller or regime filter.

Only after those conditions are met should the project consider a more complex latent-state implementation or live execution integration.

## 20. Implementation boundary

Recommended research stack:

raw venue data -> immutable Parquet -> Polars / DuckDB -> event-level feature tables -> scikit-learn models.

Recommended later event-driven execution/backtest layer:

NautilusTrader.

Do not make the execution engine the owner of the scientific dataset or the research definitions. The empirical model should be reproducible outside the trading engine.
