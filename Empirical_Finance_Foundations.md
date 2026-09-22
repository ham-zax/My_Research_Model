# Empirical Finance Foundations for the Market Feedback-State Model (MFSM)

Status: Canonical evidence companion  
Date: 2026-09-22  
Role: Finance-side evidence, measurement discipline, and falsification standards for Market_Feedback_State_Model_Canonical.md

---

## 0. Purpose

MFSM began from cross-domain structural analogy, but analogy is not financial evidence.

This document answers a stricter question:

> Which parts of MFSM already correspond to established financial mechanisms, which parts are empirically supported only under conditions, and which parts remain hypotheses that must earn predictive validity?

The current evidence supports MFSM primarily as a **conditional map of amplification mechanisms**, especially:

- funding constraints;
- leverage feedback;
- forced liquidation;
- common-exposure fire sales;
- limits to arbitrage;
- endogenous risk;
- flow-induced price pressure;
- network propagation;
- state-dependent strategy vulnerability.

The evidence does **not** currently establish:

- a universal MFSM fragility score;
- a universal crash threshold;
- that saturation predicts tops;
- that biological analogy supplies predictive power;
- that the current full state vector improves out-of-sample decisions.

Those are empirical questions.

---

## 1. Evidence taxonomy

Every finance claim should be labeled as one of the following.

### 1.1 Theory

A formal result conditional on explicit model assumptions.

Theory establishes what follows from a specified mechanism. It does not establish that the mechanism dominates real markets.

### 1.2 Empirical association

A measured relationship in financial data.

Association can be informative without identifying the full causal mechanism.

### 1.3 Mechanism-discriminating evidence

Evidence that distinguishes a proposed mechanism from plausible alternatives, for example through:

- negative controls;
- event timing;
- predetermined exposures;
- cross-sectional heterogeneity;
- quasi-experimental variation;
- subsequent reversal consistent with temporary pressure.

### 1.4 Causal evidence

Evidence with sufficiently strong identification to justify a causal interpretation.

MFSM should not silently upgrade 1.2 or 1.3 into 1.4.

### 1.5 Predictive validation

A prespecified implementation improves genuine out-of-sample prediction, calibration, or decision value beyond strong baselines.

This is the standard required before calling MFSM a demonstrated source of trading edge.

---

# Part I — Core financial mechanisms

## 2. Funding liquidity and market liquidity

### Brunnermeier and Pedersen — Market Liquidity and Funding Liquidity

Source:  
https://www.princeton.edu/~markus/research/papers/Mkt_Fun_Liquidity.pdf

Core result:

Dealer capital and margins constrain liquidity provision. Under specified conditions, reduced funding liquidity and reduced market liquidity can reinforce one another through margin and loss spirals.

MFSM mapping:

- \(A\): endogenous amplification;
- \(H\): financing and margin headroom;
- \(R^-\): liquidity-supplying balance-sheet capacity;
- \(I\): stabilizing capital that can eventually enter;
- \(K\): timing of funding and liquidity response.

Important qualification:

Margins are not mechanically destabilizing in every state. If financiers recognize a temporary liquidity discount and expect convergence, financing terms can support stabilizing capital.

### MFSM lesson

Do not encode:

\[
\text{liquidity down}\Rightarrow\text{margins up}\Rightarrow\text{crash}
\]

as a universal rule.

Encode a **state-dependent interaction**.

---

## 3. Procyclical leverage and balance sheets

### Adrian and Shin — Liquidity and Leverage

Source:  
https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr328.pdf

Core evidence:

Marked-to-market intermediaries actively adjust balance sheets and leverage procyclically. Dealer repo growth contains information about aggregate liquidity conditions.

MFSM mapping:

- \(A\): price/balance-sheet feedback;
- \(R^+\): capacity to expand exposure;
- \(H\): future vulnerability created by accumulated exposure.

Critical correction:

A price increase can initially **create more capacity**.

With liabilities fixed, a rise in asset value raises equity and mechanically lowers leverage. An active intermediary can then expand assets and borrowing to restore target leverage.

Therefore:

\[
P\uparrow
\rightarrow
\text{equity}\uparrow
\rightarrow
\text{effective balance-sheet capacity}\uparrow
\rightarrow
\text{new exposure}\uparrow
\]

can occur before fragility rises.

### MFSM lesson

The trend does not always manufacture its antagonist immediately.

Sometimes it first relaxes constraints and strengthens the amplifier.

---

## 4. Endogenous risk and synchronized behavior

### Danielsson, Shin, and Zigrand — Risk Appetite and Endogenous Risk

Source:  
https://conference.nber.org/confer/2009/QSRconf/riskappetite.pdf

Core result:

Risk-constrained traders can create feedback between measured risk and realized risk. Common responses can generate correlations even when fundamental shocks are independent.

MFSM mapping:

- \(A\): endogenous feedback;
- \(C\): effective propagation;
- \(D\): functional diversity / common reaction rules;
- \(Q\): distinction between external information and endogenous response.

### MFSM lesson

A large price movement is not itself evidence of pathological feedback.

The relevant question is whether participant responses are **causing further state change**.

---

# Part II — Fire sales, overlap, and propagation

## 5. Mutual-fund fire sales

### Coval and Stafford — Asset Fire Sales (and Purchases) in Equity Markets

Source:  
https://www.newyorkfed.org/medialibrary/media/research/conference/2005/liquidity/Coval_Stafford.pdf

Core evidence:

Funds experiencing extreme flows adjust existing holdings. Securities widely sold by redemption-stressed funds experience price pressure and subsequent reversal.

MFSM mapping:

- \(R^-\): absorptive liquidity;
- \(C\): propagation through common holdings;
- \(D\): common forced behavior;
- \(M_4\): threshold/constraint-driven unwind analogue.

Mechanism-discriminating feature:

Widespread selling without the distress condition does not show the same subsequent reversal pattern.

### MFSM lesson

Predetermined overlap plus forced flow is more informative than raw return correlation.

---

## 6. Common holdings and vulnerable banks

### Greenwood, Landier, and Thesmar — Vulnerable Banks

Source:  
https://www.hbs.edu/ris/Publication%20Files/vulnerable%20banks%20jfe_6542a41e-b149-44b9-b1bf-599613e6e12d.pdf

Core result:

If institutions restore leverage by selling assets, price impact can transmit losses to other institutions holding the same assets.

MFSM mapping:

- \(W_t\): common-holding exposure network;
- \(C\): propagation potential;
- \(H\): leverage-restoration pressure;
- \(R^-\): depth available to absorb sales.

Important qualification:

Estimated contagion depends on liquidation behavior and market-impact assumptions.

### MFSM lesson

Connectivity is not “correlation.”

The relevant object is an economically operative exposure network.

---

## 7. Quant deleveraging and common reaction functions

### Khandani and Lo — What Happened to the Quants in August 2007?

Source:  
https://web.mit.edu/Alo/www/Papers/august07.pdf

Core evidence:

Strategy simulations and fund evidence are consistent with rapid liquidation of similar portfolios, subsequent deleveraging, and rebound.

MFSM mapping:

- \(D\): functional diversity;
- \(C\): common portfolio and funding channels;
- \(A\): same-direction response feedback.

Important qualification:

The initiating liquidation mechanism is a hypothesis, not a cleanly identified causal fact.

### MFSM lesson

“Quantitative” is not the important category.

The relevant variables are:

- similar holdings;
- similar triggers;
- similar risk rules;
- common funding constraints.

---

## 8. Financial-network stability

### Acemoglu, Ozdaglar, and Tahbaz-Salehi — Systemic Risk and Stability in Financial Networks

Source:  
https://economics.mit.edu/sites/default/files/publications/Systemic%20Risk%20and%20Stability%20in%20Financial%20Networks..pdf

Core theoretical result:

More diversified interbank liabilities can improve resilience to sufficiently small shocks while dense networks can propagate sufficiently large shocks more widely.

MFSM mapping:

- \(W_t\): network;
- \(C\): propagation potential;
- \(B_t\): loss-absorption capacity.

### MFSM lesson

\[
C\uparrow
\]

is not unconditionally bad.

Network effects are shock-size- and state-dependent.

---

## 9. Spectral instability in financial networks

### Bardoscia et al. — Pathways towards Instability in Financial Networks

Source:  
https://www.nature.com/articles/ncomms14416

Core result:

In the specified financial-network dynamics, stability depends on a recovery-adjusted interbank leverage matrix and its dominant eigenvalue.

Multiple feedback cycles can destabilize a network even when individual institutions do not become more leveraged.

MFSM mapping:

- \(W_t\): weighted network;
- \(J_t\): local response operator;
- spectral-radius analysis;
- \(A\): effective feedback through cycles.

### MFSM lesson

Node count, density, or correlation alone are poor substitutes for the actual propagation operator.

---

# Part III — Flows, impact, and momentum

## 10. Momentum crashes

### Daniel and Moskowitz — Momentum Crashes

Source:  
https://www.kentdaniel.net/papers/published/mom12.pdf

Core evidence:

Momentum earns substantial historical average returns but can suffer severe state-dependent crashes, especially during market rebounds after drawdowns and high-volatility states.

MFSM mapping:

- \(T\): trend strength;
- \(U\): strategy sustainability;
- \(F\): conditional failure fragility.

Critical counterexample:

A momentum crash need not be an exhausted bull market collapsing.

A crash in a momentum strategy can occur while aggregate conditions improve.

### MFSM lesson

Trend strength, sustainability, and failure fragility must remain separate.

---

## 11. Flow-induced price effects

A central research direction for MFSM is to separate:

\[
\text{return}
=
\text{external-information component}
+
\text{endogenous-flow component}
+
\text{liquidity-impact component}.
\]

Evidence from fund-flow research supports the existence of temporary flow-induced price pressure and subsequent reversal in some settings.

MFSM mapping:

- \(S^{ext}\): external information;
- \(S^{end}\): return-induced or flow-induced reinforcement;
- \(A\): return-to-flow-to-return loop.

### MFSM lesson

Two trends with identical realized returns may have different sustainability if one is supported by continuing external information and another increasingly depends on endogenous flow.

---

## 12. Concave market impact

### Tóth et al. — Anomalous Price Impact and the Critical Nature of Liquidity in Financial Markets

Source:  
https://www.cfm.com/wp-content/uploads/2022/12/76-2011-anomalous-price-impact-and-the-critical-nature-of-liquidity-in-financial-markets.pdf

Core evidence:

Large trading programs exhibit concave price impact, approximately square-root in traded quantity under the studied conditions.

MFSM mapping:

- local price impact;
- effective \(A\) through flow-to-return sensitivity;
- liquidity-state dependence.

Critical non-inference:

Concave execution impact does **not** prove:

- information saturation;
- declining marginal response to bullish news;
- an approaching market top.

### MFSM lesson

Execution-response saturation and information-response saturation are different hypotheses.

---

## 13. Slow decay of impact

### Bucci et al. — Slow Decay of Impact in Equity Markets

Source:  
https://www.cfm.com/wp-content/uploads/2022/12/247-Slow-decay-of-impact-in-equity-markets.pdf

Core evidence:

Institutional metaorders show price relaxation after execution. Estimated decay depends on accounting for multiday correlation among trade signs.

MFSM mapping:

- \(K_t\): impact-memory kernel;
- distinction between mechanical impact and information;
- \(S^{end}\) versus \(S^{ext}\).

### MFSM lesson

Do not equate:

- persistent order flow;
- persistent information;
- permanent price change.

They are different objects.

---

# Part IV — Institutional stress episodes

## 14. UK LDI crisis, 2022

### Bank of England — December 2022 Financial Stability Report, LDI chapter

Source:  
https://www.bankofengland.co.uk/-/media/boe/files/financial-stability-report/2022/financial-stability-report-december-2022.pdf

Core reconstruction:

Falling gilt prices generated collateral demands. Insufficient usable buffers and operational delays impeded recapitalization, particularly for pooled LDI funds. Asset sales could reinforce further price declines.

MFSM mapping:

- \(H\): collateral headroom;
- \(R^-\): available absorption;
- \(K_t\): mobilization delay;
- \(\Psi=\tau_{mobilize}/\tau_{deadline}\);
- \(A\): price-to-margin-to-sale feedback;
- \(C\): propagation across institutions and assets.

### MFSM lesson

Nominal resources and **resources usable before the deadline** are different quantities.

This is one of the strongest real-world examples for the MFSM delay-mismatch hypothesis.

---

## 15. May 6, 2010 Flash Crash

### CFTC–SEC Joint Report

Source:  
https://www.sec.gov/news/studies/2010/marketevents-report.pdf

Core reconstruction:

Very high trading volume coexisted with collapsing depth and limited net inventory absorption. Withdrawal by liquidity providers amplified the shortage. A brief E-mini trading pause coincided with replenished buying and stabilization.

MFSM mapping:

- \(R^-\): absorption capacity;
- \(D\): synchronized withdrawal;
- \(A\): same-direction feedback;
- \(K_t\): replenishment timing.

### MFSM lesson

Gross volume is not a good proxy for opposing absorptive capacity.

A market can trade enormous volume while the side capable of **net absorption** disappears.

---

# Part V — Early warning and macro-financial baselines

## 16. Banking-crisis early-warning indicators

### Aldasoro, Borio, and Drehmann — Early Warning Indicators of Banking Crises: Expanding the Family

Source:  
https://www.bis.org/publications/early-warning-indicators-banking-crises-expanding-family_0.pdf

Core evidence:

Credit gaps and debt-service ratios contain useful warning information at particular horizons. Property-price gaps can lose informativeness near crises.

MFSM mapping:

- baseline vulnerability measures;
- slow-moving state variables;
- benchmark for incremental-warning tests.

### MFSM lesson

A theoretically elegant nonlinear-dynamics indicator must outperform or add value beyond established finance-specific vulnerability variables.

---

## 17. Real-time credit-gap measurement

### Drehmann and Yetman — Why You Should Use the Hodrick–Prescott Filter—At Least to Generate Credit Gaps

Source:  
https://www.bis.org/publications/working-paper-744-why-you-should-use-hodrick-prescott-filter-least-generate-credit-gaps

Core lesson:

Conceptually attractive alternatives do not automatically outperform practical baselines.

### MFSM lesson

The right standard is comparative forecasting performance, not theoretical beauty.

---

## 18. Money, liquidity, and the “running out of cash” error

### McLeay, Radia, and Thomas — Money Creation in the Modern Economy

Bank of England, 2014.

Core institutional lesson:

Bank lending can create deposits; asset purchases transfer deposits; loan repayment can destroy deposits.

MFSM consequence:

Do not model market continuation as if a fixed aggregate stock of “cash” is mechanically consumed by buying.

Distinguish:

- aggregate money;
- transferable collateral;
- intermediary equity;
- funding lines;
- mandate headroom;
- risk tolerance;
- balance-sheet capacity;
- deadline-specific usable resources.

---

# Part VI — What MFSM should test

## 19. Hypothesis H1 — Capacity interaction

For comparable external shocks:

> pre-existing leverage, short funding maturity, and low usable collateral headroom should predict more forced selling and larger temporary price deviations.

Key MFSM variables:

\[
A,\quad H,\quad R^-.
\]

Important confounders:

- asset risk;
- adverse selection;
- anticipated shocks;
- voluntary exposure reduction.

Test interactions, not merely additive effects.

---

## 20. Hypothesis H2 — Overlap transmission

Unexpected redemptions or balance-sheet pressure at one holder should generate greater price pressure and secondary sales where:

- predetermined portfolio overlap is high;
- market depth is low;
- alternative absorbers are constrained.

Key MFSM objects:

\[
W_t,\quad R^-,\quad D.
\]

Negative controls should include non-overlapping assets.

---

## 21. Hypothesis H3 — Delay mismatch

Conditional on total resources:

> a longer time to mobilize usable collateral relative to the deadline for margin or funding action should predict greater forced liquidation.

Operational quantity:

\[
\Psi
=
\frac{\tau_{mobilize}}
{\tau_{deadline}}.
\]

The UK LDI episode is a natural institutional setting for this hypothesis.

---

## 22. Hypothesis H4 — Functional diversity

Conditional on gross holdings:

> greater diversity of funding sources, liabilities, horizons, and reaction rules should reduce synchronized forced sales.

Do not measure \(D\) by counting firms, models, or asset labels.

Candidate measure:

dispersion in marginal responses to the same identified shock.

---

## 23. Hypothesis H5 — External versus endogenous confirmation

Decompose trend continuation into:

\[
S^{ext}
\]

and

\[
S^{end}.
\]

Hypothesis:

> trends increasingly dominated by endogenous reinforcement should behave differently after the reinforcing flow stops than trends continuously validated by external information.

This requires causal or quasi-causal decomposition, not narrative classification.

---

## 24. Hypothesis H6 — Saturation distinction

Test whether repeated **independent informational surprises** have diminishing conditional price response after controlling for:

- surprise magnitude;
- prior expectations;
- liquidity;
- volatility;
- positioning.

Do not use square-root execution impact as evidence for this hypothesis.

Diminishing response alone does not imply reversal.

---

## 25. Hypothesis H7 — Incremental warning value

A prespecified MFSM implementation must improve genuine out-of-sample performance beyond baselines such as:

- momentum;
- volatility;
- leverage;
- valuation;
- credit gaps;
- debt-service ratios;
- liquidity;
- standard network measures.

Evaluation should include:

- rolling or expanding real-time tests;
- country/asset/episode holdouts;
- calibration;
- precision-recall as well as ROC where events are rare;
- economic loss functions;
- false-alarm costs.

---

# Part VII — Measurement map

## 26. \(A\): amplification / loop gain

Do not proxy \(A\) with momentum alone.

Candidate empirical objects:

- return-induced flow sensitivity;
- flow-induced return impact;
- price-to-collateral-to-position feedback;
- dealer-hedging response;
- volatility-to-exposure response.

A conceptual local loop gain is

\[
\mathcal G_t(h)
=
\left(
\frac{\partial Q^{endo}_{t+h}}
{\partial r_t}
\right)
\left(
\frac{\partial r_{t+h}}
{\partial Q^{endo}_{t+h}}
\right).
\]

Identification is difficult because information, prices, and flow are simultaneous.

---

## 27. \(R^+\): remaining continuation capacity

Possible proxies depend on the asset:

- uncommitted fund flows;
- remaining short interest in a squeeze;
- available directional risk budget;
- untapped leverage;
- new-account or new-capital inflow;
- issuance-adjusted demand.

Low \(R^+\) primarily predicts loss of continuation, not necessarily severe failure.

---

## 28. \(H\): headroom

Possible proxies:

- margin distance;
- liquidation distance;
- collateral buffer;
- risk-limit distance;
- covenant headroom;
- dealer inventory limits;
- fund redemption buffer.

Low \(H\) is specifically about **forced-action sensitivity**.

---

## 29. \(R^-\): opposing absorptive capacity

Possible proxies:

- order-book depth;
- dealer balance-sheet capacity;
- market-maker inventory tolerance;
- contrarian fund capital;
- arbitrage balance sheet;
- committed backstop liquidity;
- stress-period replenishment rate.

Gross trading volume is not sufficient.

---

## 30. \(K_t\): response-time distribution

Estimate separate kernels for:

- collateral mobilization;
- issuance;
- producer supply;
- arbitrage capital;
- hedging;
- liquidity replenishment;
- policy response.

Do not force all mechanisms into one \(\tau\).

---

## 31. \(W_t\): propagation network

Construct from:

- common holdings;
- direct liabilities;
- shared collateral;
- counterparties;
- funding links;
- benchmark rules;
- hedge dependencies.

Raw correlation can be an outcome of \(W_t\), not a substitute for it.

---

## 32. \(D\): functional diversity

Candidate measurements:

- dispersion of flow response to the same shock;
- heterogeneity in funding maturity;
- heterogeneity in risk-control rules;
- horizon dispersion;
- liability structure diversity.

A thousand entities running the same reaction rule can have low \(D\).

---

## 33. \(S^{ext}\) and \(S^{end}\)

Potential external shocks:

- standardized earnings surprises;
- macro-release surprises;
- protocol/fundamental changes;
- physical supply-demand shocks.

Potential endogenous components:

- return-induced fund flows;
- mechanical hedging;
- collateral feedback;
- liquidation flow;
- trend following.

The decomposition must allow for anticipation.

---

# Part VIII — Empirical design discipline

## 34. Pre-registration mindset

Before testing:

- define variables;
- define horizons;
- define transition labels;
- define interaction terms;
- define evaluation metrics;
- define baselines.

Avoid hindsight-selected thresholds.

---

## 35. Real-time data

Prefer data available at the decision timestamp.

Revised macro data, reconstructed positions, and ex-post classifications can produce unrealistic apparent predictability.

---

## 36. Rare-event evaluation

Crashes are rare.

Avoid relying only on accuracy or ROC.

Track:

- precision;
- recall;
- false alarms;
- event clustering;
- episode dependence;
- calibration;
- economic cost.

Do not count many observations from one crisis as many independent crises.

---

## 37. Negative controls

A proposed mechanism is stronger when it predicts:

- affected assets but not similar unaffected assets;
- forced sellers but not unconstrained sellers;
- high-overlap links but not low-overlap links;
- low-headroom states but not high-headroom states.

---

## 38. Endogenous versus exogenous transitions

MFSM is primarily a framework for endogenous amplification and state-dependent vulnerability.

A genuinely exogenous discontinuity may produce a jump with no prior deterioration in MFSM variables.

Failure to predict an exogenous jump is not automatically evidence against an endogenous-risk model.

But the framework must not relabel every surprise as “exogenous” after the fact. Classification rules should be explicit.

---

# Part IX — Minimum bar for claiming predictive edge

Before saying MFSM supplies market edge, require all of the following:

1. **Prespecified variables and transformations.**
2. **Out-of-sample testing.**
3. **Comparison against strong finance baselines.**
4. **Robustness across multiple assets or episodes.**
5. **False-alarm accounting.**
6. **No look-ahead data.**
7. **Mechanism-consistent signs and interactions.**
8. **Incremental decision value after transaction costs where trading is the application.**
9. **Stability to reasonable alternative definitions.**
10. **Failure analysis showing when and why the signal stops working.**

Without these, MFSM remains a research lens rather than demonstrated alpha.

---

# Part X — Durable source map

## 39. Core sources

1. Brunnermeier, Markus K., and Lasse Heje Pedersen. **Market Liquidity and Funding Liquidity.**  
   https://www.princeton.edu/~markus/research/papers/Mkt_Fun_Liquidity.pdf

2. Adrian, Tobias, and Hyun Song Shin. **Liquidity and Leverage.**  
   https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr328.pdf

3. Danielsson, Jon, Hyun Song Shin, and Jean-Pierre Zigrand. **Risk Appetite and Endogenous Risk.**  
   https://conference.nber.org/confer/2009/QSRconf/riskappetite.pdf

4. Coval, Joshua, and Erik Stafford. **Asset Fire Sales (and Purchases) in Equity Markets.**  
   https://www.newyorkfed.org/medialibrary/media/research/conference/2005/liquidity/Coval_Stafford.pdf

5. Greenwood, Robin, Augustin Landier, and David Thesmar. **Vulnerable Banks.**  
   https://www.hbs.edu/ris/Publication%20Files/vulnerable%20banks%20jfe_6542a41e-b149-44b9-b1bf-599613e6e12d.pdf

6. Khandani, Amir, and Andrew Lo. **What Happened to the Quants in August 2007?**  
   https://web.mit.edu/Alo/www/Papers/august07.pdf

7. Daniel, Kent, and Tobias Moskowitz. **Momentum Crashes.**  
   https://www.kentdaniel.net/papers/published/mom12.pdf

8. Acemoglu, Daron, Asuman Ozdaglar, and Alireza Tahbaz-Salehi. **Systemic Risk and Stability in Financial Networks.**  
   https://economics.mit.edu/sites/default/files/publications/Systemic%20Risk%20and%20Stability%20in%20Financial%20Networks..pdf

9. Bardoscia et al. **Pathways towards Instability in Financial Networks.**  
   https://www.nature.com/articles/ncomms14416

10. Tóth et al. **Anomalous Price Impact and the Critical Nature of Liquidity in Financial Markets.**  
    https://www.cfm.com/wp-content/uploads/2022/12/76-2011-anomalous-price-impact-and-the-critical-nature-of-liquidity-in-financial-markets.pdf

11. Bucci et al. **Slow Decay of Impact in Equity Markets.**  
    https://www.cfm.com/wp-content/uploads/2022/12/247-Slow-decay-of-impact-in-equity-markets.pdf

12. Bank of England. **Financial Stability Report, December 2022 — LDI episode.**  
    https://www.bankofengland.co.uk/-/media/boe/files/financial-stability-report/2022/financial-stability-report-december-2022.pdf

13. CFTC and SEC. **Findings Regarding the Market Events of May 6, 2010.**  
    https://www.sec.gov/news/studies/2010/marketevents-report.pdf

14. Aldasoro, Borio, and Drehmann. **Early Warning Indicators of Banking Crises: Expanding the Family.**  
    https://www.bis.org/publications/early-warning-indicators-banking-crises-expanding-family_0.pdf

15. Drehmann and Yetman. **Why You Should Use the Hodrick-Prescott Filter—At Least to Generate Credit Gaps.**  
    https://www.bis.org/publications/working-paper-744-why-you-should-use-hodrick-prescott-filter-least-generate-credit-gaps

16. McLeay, Radia, and Thomas. **Money Creation in the Modern Economy.** Bank of England, 2014.

---

## Final empirical invariant

The finance evidence supports the following stance:

> **MFSM should be judged by whether its state-dependent interactions improve real out-of-sample discrimination among continuation, quiet exhaustion, counterflow, threshold unwind, and propagation beyond established financial baselines.**

Until that test is passed, MFSM is a structured research program, not a validated trading system.
