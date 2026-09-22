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
- whether the question concerns continuation, fragility, propagation, or all three.

A mechanism can be stabilizing at one scale and destabilizing at another.

---

## 3. Define the disturbance class

Specify what kind of disturbance the model is intended to diagnose.

Examples:

- ordinary information shock;
- fund redemption;
- margin increase;
- volatility shock;
- funding withdrawal;
- supply shock;
- policy shock;
- liquidation cascade.

Do not analyze “fragility” without specifying fragility to what.

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
| Falsifier | What would contradict the mechanism? |

If an arrow cannot be completed, it should not enter the operational model.

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

## 6. Separate the three capacity states

Always distinguish:

\[
R^+
=
\text{remaining continuation capacity},
\]

\[
H
=
\text{distance to forced-action constraints},
\]

\[
R^-
=
\text{opposing absorptive capacity}.
\]

Do not use “liquidity” as a catch-all.

Ask what is scarce, for whom, in what form, and by what deadline.

---

## 7. Map response times

For each important response, estimate or describe:

- earliest possible response;
- typical response;
- tail of the response-time distribution;
- deadline imposed by constraints.

Prefer a kernel \(K(s)\) or distributed lag when responses are heterogeneous.

A single \(\tau\) is acceptable only when an institutionally meaningful fixed delay exists.

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

## 9. Measure functional diversity

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

## 11. Classify the candidate termination mechanism

Use at least these categories:

### M1 — Fuel exhaustion

Continuation capacity is depleted.

### M2 — Delayed counterflow

Opposing flow arrives after a lag.

### M3 — Gain saturation

Additional stimulus has diminishing marginal effect.

### M4 — Threshold unwind

A constraint converts state deterioration into forced same-direction action.

Do not merge these into one “exhaustion” label.

---

## 12. Produce separate outputs

Always report separately:

### Trend Strength \(T\)

What is the observed directional state?

### Trend Sustainability \(U\)

How viable is the continuation-generating mechanism?

### Failure Fragility \(F\)

How severe could the response become if the regime is disturbed?

Do not infer \(F\) from \(T\).

---

# Part II — Extension protocol

## 13. Gate 1: Is the new concept causally necessary?

Ask:

> Does this proposed variable or mechanism explain behavior not already represented by the current model?

If not, do not add it.

Avoid synonym proliferation.

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

- variable definitions;
- transformations;
- lag structure;
- interaction terms;
- event label;
- forecast horizon;
- benchmark;
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
- standard network concentration measures.

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

## \(R^+\)

What continuation capacity remains?

## \(H\)

How far are current participants from forced action?

## \(R^-\)

Who can absorb the opposite flow?

## Response-time structure

What are the relevant kernels or delays?

## Network \(W\)

How can stress propagate?

## Functional diversity \(D\)

How differently do participants react?

## Thresholds \(L\)

What constraints cause discontinuous behavior?

## Signal-source balance

What is external versus endogenous confirmation?

## Termination mechanism

Which of M1–M4 is plausible?

## Trend Strength \(T\)

Descriptive directional state.

## Trend Sustainability \(U\)

Continuation mechanism.

## Failure Fragility \(F\)

Conditional failure severity.

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

> **Every extension must make the framework more falsifiable, more measurable, or more causally precise. If it only makes the story richer, it should not enter the canonical model.**
