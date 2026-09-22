# MFSM Research and Extension Protocol

Status: Canonical workflow companion  
Date: 2026-09-22  
Role: Instructions for humans or LLMs applying, testing, criticizing, or extending the Market Feedback-State Model.

---

## 0. Why this file exists

MFSM is vulnerable to a particular failure mode: because the framework is cross-disciplinary and expressive, it can explain almost anything after the fact unless extension and testing are disciplined.

This protocol exists to prevent that.

A future researcher or LLM should not merely produce another clever analogy. It should preserve causal structure, evidence levels, falsifiability, and out-of-sample discipline.

The model should become **harder to satisfy** as it matures, not easier.

---

## 1. Required reading order

Before extending MFSM, read:

1. Market_Feedback_State_Model_Canonical.md
2. Mathematical_Foundations.md
3. Empirical_Finance_Foundations.md
4. this file

Do not infer the model only from the shorthand variables \(A,R,H,C,D,\tau\).

The mature framework is a state-dependent dynamical system, not a checklist.

---

# Part I — Application protocol

## 2. Define the system boundary

State explicitly:

- asset or market;
- jurisdiction / venue if relevant;
- participant classes;
- time horizon;
- funding system;
- derivative layer;
- market-making layer;
- whether the question concerns continuation, shock-conditioned consequence, structural susceptibility, propagation, or a subset of these.

A mechanism can be stabilizing at one scale and destabilizing at another.

---

## 3. Define the disturbance class, structural intervention, and horizon

First define a human-readable disturbance class \(c\).

Examples:

- ordinary information shock;
- fund redemption;
- margin increase;
- volatility shock;
- funding withdrawal;
- collateral haircut;
- rollover refusal;
- supply shock;
- policy shock.

Then define the human-readable intervention descriptor

\[
\boxed{
\delta
=
(c,V,a,d,t_0,p,\nu)
}
\]

with:

- \(V\): intervention target;
- \(a\ge0\): amplitude;
- \(d\): direction;
- \(t_0\): onset;
- \(p(s)\): temporal profile / duration;
- \(\nu\): optional stochastic component;
- \(h\): evaluation horizon.

The tuple is **not yet the mathematical intervention**. Define the pre-intervention latent-state law

\[
\mu_t
=
\mathcal L(
\mathbf Z_t
\mid
\mathcal I_{t^-}
)
\]

and the structural intervention operator on the full counterfactual specification

\[
\boxed{
\mathfrak I_{\delta}:
(\mu_t,\mathcal G)
\mapsto
(\mu_t^{\delta},\mathcal G^{\delta}).
}
\]

Record whether the intervention changes:

- the initial / jump state law \(\mu_t\);
- an equation / transition kernel / parameter / constraint / jump rule / forcing term in \(\mathcal G\);
- or both.

Also record:

- amplitude units and whether the change is additive, multiplicative, percentage-point, or otherwise;
- law of \(\nu\), if stochastic;
- coupling of \(\nu\) to baseline exogenous shocks;
- timing convention and pre-intervention information set.

Do not use an endogenous outcome such as "bank run", "liquidation cascade", or "market crash" as though it were itself the intervention. A friendly label such as "coordination/run shock" is acceptable only if it is instantiated through an upstream variable such as withdrawal demand, rollover availability, or a common signal.

The default absolute stressed consequence is

\[
F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho),
\]

not a context-free scalar.

Where the research question is **structural susceptibility**, vary intervention amplitude within a fixed disturbance family. Define canonical economic units for \(a\). If cross-system comparison is required, prespecify a dimensionless normalization such as \(\tilde a=a/a_{\mathrm{ref}}(c)\).

Do not compare susceptibility slopes across systems under different amplitude conventions.

---

## 4. Build the causal graph before selecting indicators

List the proposed arrows.

For each arrow record:

| Field | Required content |
|---|---|
| Source state | What changes first? |
| Target state | What changes next? |
| Sign | Reinforcing or opposing? |
| Mechanism | Why does the target react? |
| Timescale | How quickly? |
| Constraint | What limits the reaction? |
| Forced or voluntary | Can the actor choose not to react? |
| Evidence level | Theory / empirical / causal / hypothesis |
| Proxy | What data could observe it? |
| Stress-state proxy failure | How can that proxy fail in the regime of interest? Give expected sign + rationale; `ambiguous` is valid when opposing failure modes are plausible. |
| Falsifier | What would contradict the mechanism? |

If an arrow cannot be completed, it should not enter the operational model.

### 4.1 Separate latent state, observation mechanism, and analyst model

For each state variable distinguish:

- latent structural quantity;
- observed proxy;
- candidate measurement/kernel/model choice;
- timestamp availability;
- expected bias in ordinary conditions;
- **stress-state failure mode**;
- **expected sign of proxy error during the state of interest, plus rationale; use `ambiguous` when opposing failure modes are plausible**;
- alternative proxy;
- identification status: point-identified / partially identified / structurally identified / unidentified;
- closest plausible observationally equivalent data-generating process.

The last two bias fields matter because a proxy can fail most severely in exactly the regime MFSM is trying to diagnose. For example, visible order-book depth may overstate prospective \(R^-\) if quotes cancel during aggressive flow.

Conceptually distinguish the true observation mechanism

\[
p_*(\mathbf Y_t\mid\mathbf Z_t)
\]

from the analyst's candidate probabilistic measurement model

\[
\boxed{
p_m(
\mathbf Y_t
\mid
\mathbf Z_t;
\psi^{(m)}
).
}
\]

An additive-noise equation may be used as a special case, but the noise law must be part of the measurement specification.

For important latent quantities, prespecify a finite set of reasonable measurement alternatives and state which conclusions must survive them.

Do not silently treat a fitted endogeneity, crowding, liquidity, strategic-complementarity, or criticality statistic as the latent state itself.

### 4.2 Define the counterfactual path target

Let \(\mathcal I_t\) denote the information genuinely available at the analysis timestamp. If the structural state is latent, \(\mathcal I_t\) implies a posterior over \(\mathbf Z_t\) rather than exact knowledge of it. For the specified intervention operator \(\mathfrak I_{\delta}\), the theoretical response object is

\[
\boxed{
\mathcal P_{t,h}^{\delta}
=
\mathcal L(
\mathbf Z_{[t,t+h]}^{\delta}
\mid
\mathcal I_t
).
}
\]

Also define the no-intervention baseline \(\mathcal P_{t,h}^{0}\).

Do **not** require the empirical system to estimate the unrestricted path distribution nonparametrically. Instead prespecify the projections needed for the research or trading question, such as:

- threshold-hit probability;
- maximum adverse excursion;
- cascade size;
- tail loss / expected shortfall;
- recovery probability or recovery time.

The mean causal response is

\[
\mathbf m_t^{\delta}(s)
=
\mathbb E[
\mathbf Z_{t+s}^{\delta}
-
\mathbf Z_{t+s}^{0}
\mid
\mathcal I_t
].
\]

If the analysis uses the **distribution** of a pathwise counterfactual difference \(\mathbf Z^{\delta}-\mathbf Z^0\), state the structural coupling that makes those two potential paths jointly defined.

---

## 5. Identify endogenous amplification

Do not label price momentum itself as \(A\).

Ask:

> Does the current state cause behavior that creates additional same-direction pressure?

Examples:

\[
P\uparrow
\rightarrow
\text{collateral capacity}\uparrow
\rightarrow
\text{buying}\uparrow
\rightarrow
P\uparrow
\]

or

\[
P\downarrow
\rightarrow
\text{margin pressure}\uparrow
\rightarrow
\text{forced selling}\uparrow
\rightarrow
P\downarrow.
\]

If the causal return-to-flow or flow-to-return link is absent, observed momentum alone is not endogenous amplification.

---

## 6. Separate the capacity categories

Always distinguish the **family** of mechanism-specific continuation capacities

\[
\boxed{
\{R_{k,t}^+\}_k
}
\]

where each \(k\) is a separately identified reinforcing mechanism. \(R^+\) is a category label, not a default market-wide scalar.

\[
H
=
\text{distance to forced-action constraints},
\]

\[
R^-_t(h;\delta,\varepsilon,\varphi)
=
\text{opposing absorptive capacity usable by horizon }h
\text{ under the specified intervention and incoming-flow profile}
\text{ before consequence exceeds }\varepsilon.
\]

State the consequence metric attached to \(\varepsilon\) and the normalized incoming stress-flow profile \(\varphi\) explicitly. \(\varphi\) describes the flow whose absorptive capacity is being measured and is distinct from the intervention-time profile already encoded in \(\delta\). For an order-book study this may pair a price-displacement tolerance \(\varepsilon_P\) with a uniform, front-loaded, or otherwise prespecified sell-flow schedule. When \(\varphi\) is fixed by design, \(R^-_t(h;\delta,\varepsilon)\) may be used as shorthand; when tolerance and profile are fixed, \(R^-_t(h;\delta)\) is acceptable shorthand.

Also record local **initial-state constraint sensitivity** separately from current headroom:

\[
\mathbf\Chi_{B,t}(h)
=
D_{\mathbf z}
\mathbb E[
\mathbf B_{t+h}^{0}
\mid
\mathbf Z_t=\mathbf z,\mathcal I_t
].
\]

Only if the intervention acts solely through an instantaneous initial-state displacement should one use

\[
\mathbf\Chi_{B,t}(h)\mathbf v_{\delta}.
\]

For a parameter, rule, kernel, constraint, or temporal forcing intervention, use the direct intervention derivative \(D_{\delta}\mathbb E[\mathbf B_{t+h}^{\delta}]\) or the finite response.

For finite interventions near thresholds, prefer

\[
\Delta\mathbf B_t^{\delta}(s)
=
\mathbb E[
\mathbf B_{t+s}^{\delta}
-
\mathbf B_{t+s}^{0}
\mid
\mathcal I_t
].
\]

Do not use "liquidity" as a catch-all.

Ask what is scarce, for whom, in what form, by what deadline, and how quickly a market-state change alters future capacity.

---

## 7. Map response times

For each important response, estimate or describe:

- earliest possible response;
- typical response;
- tail of the response-time distribution;
- deadline imposed by constraints.

Prefer a kernel \(K(s)\) or distributed lag when responses are heterogeneous.

A single \(\tau\) is acceptable only when an institutionally meaningful fixed delay exists.

The dynamic state must carry the memory needed by the chosen response law. An exact fixed delay requires the relevant history segment; a general distributed kernel may also require a function-valued history. Use a finite-dimensional state and matrix Jacobian only for a justified exact realization or an explicitly labeled approximation. Record the approximation before interpreting eigenvalues as stability evidence for the financial mechanism.

---

## 8. Map propagation

Build \(W_t\) from economically operative links.

Possible links:

- common holdings;
- direct liabilities;
- shared collateral;
- common dealer;
- common funding source;
- benchmark rule;
- derivative hedge;
- redemption mechanism.

Do not use raw return correlation as the causal network.

---

## 9. Measure functional diversity and coordination

Ask how participants respond to the **same identified shock**.

Do not count:

- number of funds;
- number of strategies;
- number of asset labels.

Measure or proxy differences in:

- funding;
- horizon;
- mandate;
- leverage;
- risk rule;
- liability;
- inventory tolerance.

Treat \(D_t\) as dynamic. Ask whether relative strategy performance, imitation, benchmark migration, or capital flows are causing reaction functions to converge.

Separately ask whether actions are strategically complementary:

\[
\Gamma_t
\sim
\frac{\partial a_i^*}{\partial \bar a_{-i}}.
\]

A common response to the same public information is not the same as strategic complementarity.

---

## 10. Identify thresholds

Record any condition that changes behavior discontinuously:

- margin call;
- liquidation;
- stop-out;
- covenant breach;
- risk limit;
- regulatory threshold;
- trading halt;
- collateral haircut.

These belong in a hybrid / threshold model, not merely a smooth linear equation.

---

## 11. Classify the candidate termination mechanism and controller topology

Treat \(M_t^{term}\) as a **derived prospective output**, not a primitive state variable. The classification must be based on information available before the realized termination path; a label assigned only afterward is explanatory annotation.

Use at least these termination categories:

### M1 — Fuel exhaustion

Continuation capacity is depleted.

### M2 — Delayed counterflow

Opposing flow arrives after a lag.

### M3 — Gain saturation

Additional stimulus has diminishing marginal effect.

### M4 — Threshold unwind

A constraint converts state deterioration into forced same-direction action.

Do not merge these into one "exhaustion" label.

Also classify the topology of the opposing/control mechanism where relevant:

- feed-forward opposition;
- feedback;
- integral feedback;
- depletion;
- saturation;
- threshold switching.

Do not call every delayed opposing force "negative feedback."

---

## 12. Produce separate outputs

Always report separately:

### Trend Strength \(T\)

What is the observed directional state?

### Trend Sustainability \(U\)

How viable is the continuation-generating mechanism?

### Absolute stressed consequence \(F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)\)

For this structural intervention, what is the consequence under a **loss-oriented** path functional \(\ell_{\mathrm{abs}}\) and severity functional \(\rho\)?

If the research question is the incremental causal harm of the intervention, define a separate two-path loss \(\ell_{\Delta}(\mathbf Z^{\delta},\mathbf Z^0)\) and state the joint counterfactual coupling required to identify its distribution.

### Structural susceptibility

How rapidly does absolute stressed consequence increase as intervention amplitude varies within a fixed disturbance family?

Use the same amplitude units across systems, or compare with respect to a prespecified normalized amplitude \(\tilde a\). Do not compare raw slopes \(\partial F/\partial a\) across incompatible amplitude parameterizations.

Do not infer shock consequence or susceptibility from \(T\).

---

# Part II — Extension protocol

## 13. Gate 1: Is the new concept causally necessary?

Ask:

> Does this proposed variable or mechanism explain behavior not already represented by the current model?

If not, do not add it.

Avoid synonym proliferation.

**Theory-freeze rule:** while the current empirical program remains untested, do not add a new canonical state variable merely because it is interesting. A new canonical variable requires either:

1. a demonstrated contradiction that the existing architecture cannot represent; or
2. empirical evidence from a prespecified test showing a missing mechanism or interaction.

Prefer simplifying or deriving existing quantities over expanding the state vocabulary.

---

## 14. Gate 2: Write the concept in domain-neutral form

Before naming a natural or financial example, describe the structure abstractly.

Example:

> activation consumes future activation capacity and recovers with a finite timescale.

This prevents superficial analogy.

---

## 15. Gate 3: Map every role

For a proposed cross-domain analogy identify:

- state variable;
- flow;
- amplifier;
- opposing mechanism;
- resource;
- delay;
- threshold;
- propagation path;
- failure mode.

If more than one or two mappings need to be forced metaphorically, reject the analogy.

---

## 16. Gate 4: State where the analogy fails

Every retained analogy must include an explicit boundary.

Example:

Physarum transfers flow-dependent capacity adaptation.

It does not transfer strategic expectations, leverage, or valuation.

An analogy without a failure boundary is not admissible.

---

## 17. Gate 5: Find the finance-native counterpart

Before adding a new MFSM variable, search for existing financial literature under finance-native names.

Possible literatures include:

- funding liquidity;
- market microstructure;
- limits to arbitrage;
- leverage cycles;
- fire sales;
- network contagion;
- intermediary asset pricing;
- heterogeneous agents;
- liquidity spirals;
- crowded trades;
- dealer balance sheets;
- option hedging;
- margin dynamics;
- credit cycles.

The goal is not to rename established finance with biological language.

---

## 18. Gate 6: Define measurement

A concept that cannot even in principle be operationalized should remain conceptual.

State:

- candidate data;
- proxy;
- frequency;
- timestamp availability;
- measurement error;
- latent-state problem.

---

## 19. Gate 7: Define falsification

A valid extension needs a result that would weaken it.

Examples:

- no interaction after controlling for standard leverage and liquidity;
- effect appears equally in negative-control assets;
- estimated lag has no relationship to the predicted response;
- sign reverses across samples without a mechanism;
- out-of-sample value disappears.

---

## 20. Gate 8: Require incremental value

Even a true mechanism may be redundant.

Ask whether the new variable improves:

- mechanism identification;
- state classification;
- forecast calibration;
- economic decision value;

beyond existing MFSM states and strong finance baselines.

---

# Part III — Evidence discipline

## 21. Claim labels

Every nontrivial claim should be classifiable as:

- **Established mechanism**
- **Structural analogy**
- **Empirical association**
- **Mechanism-discriminating evidence**
- **Causal evidence**
- **Speculative hypothesis**
- **Validated predictive contribution**

Do not blend these categories in prose.

---

## 22. Source hierarchy

Prefer, in order:

1. original peer-reviewed or primary formal research;
2. official institutional reports for market events;
3. high-quality review papers;
4. reputable working papers when primary publication is unavailable;
5. secondary summaries only for orientation.

---

## 23. Do not use analogy as evidence

The following form is invalid:

> natural system X does Y; therefore market Y should predict Z.

The valid form is:

1. source-domain mechanism X is established;
2. finance contains independently identified mechanism Y with the same causal topology;
3. Y has a measurable implication Z;
4. Z is tested against alternatives.

---

# Part IV — Empirical testing protocol

## 24. Lock the hypothesis first

Before examining the test sample, specify:

- latent-state definitions and observed proxies;
- disturbance class and descriptor;
- the full intervention operator \(\mathfrak I_{\delta}:(\mu_t,\mathcal G)\mapsto(\mu_t^{\delta},\mathcal G^{\delta})\);
- intervention amplitude units / path;
- loss orientation and absolute one-path loss functional \(\ell_{\mathrm{abs}}\);
- any two-path incremental loss and counterfactual coupling assumption;
- risk / severity functional \(\rho\);
- transformations;
- lag / kernel structure;
- interaction terms;
- event label;
- forecast horizon;
- benchmark;
- primitive information set available to every compared model;
- model-selection / tuning budget;
- evaluation metric.

---

## 25. Respect timestamps

Use only data available at the prediction timestamp.

Beware:

- revised macro series;
- final holdings data;
- reconstructed liquidation prices;
- future realized volatility;
- ex-post crisis labels.

---

## 26. Separate state diagnosis from timing

A useful MFSM output can be:

> the system is highly vulnerable to a particular disturbance.

It need not imply:

> the crash will happen tomorrow.

Do not judge a vulnerability model solely as a precise top-timing system unless that is the prespecified task.

---

## 27. Compare against strong baselines

At minimum compare against relevant combinations of:

- momentum;
- realized / implied volatility;
- leverage;
- valuation;
- funding spreads;
- market depth;
- credit growth;
- debt-service burden;
- standard network concentration measures;
- a flexible nonlinear model using the **same primitive information set**.

If the candidate model receives deterministic features computed from a richer history, later timestamp, extra venue/feed, or cleaner field, that underlying primitive information must also be available to the nonlinear baseline. Use comparable inner-validation and tuning budgets.

---

## 28. Evaluate rare-event models correctly

For rare transitions, report:

- precision;
- recall;
- false positive rate;
- false negatives;
- calibration;
- lead time;
- event clustering;
- economic loss.

Do not rely on accuracy alone.

---

## 29. Use holdouts that break narrative dependence

Possible holdouts:

- time periods;
- countries;
- asset classes;
- exchanges;
- crisis families.

A model explaining the same episode it was invented from is weak evidence.

---

# Part V — Versioning and change discipline

## 30. Canonical versus experimental content

The canonical specification should contain only concepts that survive review.

Experimental ideas should first be recorded separately with:

- motivation;
- causal diagram;
- evidence level;
- proposed measurement;
- falsifier;
- status.

Only promote them after they improve the model.

---

## 31. Change record

For every material model change record:

- date;
- old definition;
- new definition;
- reason;
- evidence;
- consequences for earlier claims.

Do not silently redefine variables after empirical failure.

### 31.1 Freeze / release procedure

A theory-freeze policy is not itself a reproducible release. Before a confirmatory experiment begins:

1. commit the canonical model and experiment specification;
2. create immutable annotated Git tags for the frozen references, e.g. `mfsm-v1.0` and `e001-v1.1` for the current candidate;
3. record the resolved commit SHAs in a separate freeze manifest **after** the tags exist;
4. record data-schema, feature-schema, label-schema, and freeze timestamp;
5. record the first-access timestamp for any strict holdout;
6. do not amend the tagged commits to insert their own hashes.

A material post-freeze change requires a new version/tag and changelog entry.

---

## 32. Rejected ideas should remain visible

Do not delete important failed mappings.

Preserve why they were rejected so future systems do not rediscover the same error.

Examples already rejected or downgraded include:

- chemical equilibrium constant = constant-product AMM invariant;
- quorum sensing = short squeeze;
- neuron refractory period = literal market liquidation;
- more connectivity = always more fragile;
- critical slowing down = universal crash signal;
- rising variance = proof of weakening stability;
- low trend fuel = crash;
- exponential price impact claim for constant-product AMMs.

---

# Part VI — Required output schema for another LLM

When an LLM applies MFSM to a market, require this structure.

## System boundary

What exactly is being modeled?

## External driver

What information or fundamental shock originates outside the feedback loop?

## Reinforcing loop

What state change creates additional same-direction action?

## \(\{R_k^+\}_k\)

Which specific continuation mechanisms remain active, and how much capacity remains in each? Do not aggregate them unless the aggregation rule is prespecified.

## \(H\)

How far are current participants from forced action?

## \(R^-_t(h;\delta,\varepsilon,\varphi)\)

Who can absorb the opposite flow **under this disturbance, arrival profile, and horizon, without breaching the prespecified consequence tolerance**?

## Response-time structure

What are the relevant kernels or delays?

## Network \(W\)

How can stress propagate?

## Functional diversity \(D\)

How differently do participants react?

## Threshold geometry / optional \(L\)

What constraints cause discontinuous behavior? If \(L\) is used, what prespecified threshold-distance summary does it represent beyond \(H\) and \(\Chi_B\)?

## Signal-source balance

What is external versus endogenous confirmation?

## Derived termination mechanism

Which of M1–M4 is prospectively plausible from pre-outcome information?

## Trend Strength \(T\)

Descriptive directional state.

## Trend Sustainability \(U\)

Continuation mechanism.

## Structural intervention

State the descriptor \(\delta\), amplitude units, and the operator \(\mathfrak I_{\delta}:(\mu_t,\mathcal G)\mapsto(\mu_t^{\delta},\mathcal G^{\delta})\), including any initial-state-law change, exact structural rule modified, stochastic-law/coupling assumptions, timing, and horizon.

## Path-response targets

Which projections of \(\mathcal P_{t,h}^{\delta}\) are being estimated?

Examples: mean causal response, threshold-hit probability, maximum adverse excursion, cascade size, recovery probability, or tail loss.

## Loss and severity definition

What is the loss-oriented one-path functional \(\ell_{\mathrm{abs}}\)? What is the risk / severity functional \(\rho\)? If incremental causal harm is used, what two-path loss and counterfactual coupling are assumed?

## Absolute stressed consequence \(F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)\)

Consequence for the specified intervention operator.

## Structural susceptibility

What does the standardized amplitude-response curve look like? State the amplitude units or normalization. If identified, report normalized local slope or critical amplitude \(a_q^*\).

## Shock-response path

What is the expected sequence of state changes after \(\delta\)? What becomes reinforced, forced, delayed, or absorbed?

## Constraint sensitivity and finite-shock buffer response

Report the local initial-state Jacobian \(\mathbf\Chi_B\), any valid initial-state projection, the direct intervention derivative for non-state interventions where identified, and the finite-shock response \(\Delta\mathbf B^{\delta}\) where relevant.

## Strategic complementarity \(\Gamma\)

Do participant actions become individually more attractive when others take the same action?

## Observation model

Which quantities are latent, which are proxies, and what specification choices could bias the estimate?

## Missing data

What cannot currently be measured?

## Falsifiers

What observations would weaken the diagnosis?

## Evidence level

Which statements are established, empirical, analogical, or speculative?

---

# Part VII — Stop conditions

A future researcher or LLM should stop extending and instead test the model when any of the following occurs:

- new concepts mostly rename existing variables;
- analogies outnumber measurable hypotheses;
- the state vector grows faster than the evidence base;
- every historical event can be explained regardless of outcome;
- variables are redefined after failures;
- a proposed score needs arbitrary weights;
- causal arrows lack independently measurable counterparts;
- predictions cannot be compared with baselines.

At that point, more theorizing reduces value.

---

## Final research invariant

The model should evolve according to this rule:

> **Every extension must make the framework more falsifiable, more measurable, or more causally precise. It should sharpen the state-to-response mapping for specified disturbances rather than merely enrich the narrative. If it only makes the story richer, it should not enter the canonical model.**
