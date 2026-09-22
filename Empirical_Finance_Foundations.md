# Empirical Finance Foundations for the Market Feedback-State Model (MFSM)

Status: Canonical evidence companion  
Date: 2026-09-22  
Role: Finance-side evidence, measurement discipline, and falsification standards for Market_Feedback_State_Model_Canonical.md

---

## 0. Purpose

MFSM began from cross-domain structural analogy, but analogy is not financial evidence.

This document answers a stricter question:

> Which parts of MFSM already correspond to established financial mechanisms, which parts are empirically supported only under conditions, and which parts remain hypotheses that must earn predictive validity?

The current evidence supports MFSM primarily as a **conditional map of state-dependent response mechanisms**, especially:

- funding constraints and leverage feedback;
- collateral-sensitive borrowing capacity;
- forced liquidation and deadline mismatch;
- common-exposure fire sales;
- slow-moving stabilizing capital and limits to arbitrage;
- strategic complementarity / run-like coordination;
- endogenous risk and strategy convergence;
- flow-induced price pressure;
- network propagation;
- state-dependent strategy vulnerability;
- measurement risk when latent endogeneity is inferred from noisy or misspecified proxies.

The evidence does **not** currently establish:

- a universal MFSM fragility score;
- a universal crash threshold;
- that any one estimated endogeneity/criticality statistic identifies the latent feedback state;
- that saturation predicts tops;
- that biological analogy supplies predictive power;
- that the current full state vector or shock-response representation improves out-of-sample decisions.

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

## 18A. Strategic complementarity and bank-run coordination

### Diamond and Dybvig — Bank Runs, Deposit Insurance, and Liquidity

Primary source:
https://www.journals.uchicago.edu/doi/10.1086/261155

Diamond and Dybvig (1983), *Journal of Political Economy* 91(3), pp. 401-419, model demand-deposit arrangements with multiple equilibria, including a bank-run equilibrium.

Core mechanism:

A participant's optimal action can depend on expected actions of others. This creates multiple-equilibrium / coordination fragility that does not require a preceding price trend.

MFSM mapping:

- \(Q_t\): expectations and coordination state;
- \(\Gamma_t\): MFSM's abstraction of strategic-complementarity / coordination dependence;
- path-law and susceptibility analysis for run-like responses.

The exact quantity

\[
\Gamma_t
\sim
\frac{\partial a_i^*}{\partial \bar a_{-i}}
\]

is an MFSM abstraction; it is not presented as a formula taken from Diamond-Dybvig.

MFSM lesson:

Do not require visible momentum before diagnosing run-like fragility.

---

## 18B. Collateral constraints and state-sensitive headroom

### Kiyotaki and Moore — Credit Cycles

Source:
https://msuweb.montclair.edu/~lebelp/KyotakiMooreCreditCyclesJPE1997.pdf

Core mechanism:

Asset prices affect collateral capacity; collateral capacity affects future spending / demand; this feeds back into asset prices and propagation.

MFSM mapping:

- \(H_t\): current headroom;
- \(\mathbf\Chi_{B,t}\): local Jacobian of future buffers with respect to current latent state;
- \(\Delta\mathbf B_t^{\delta}\): finite-shock buffer response;
- \(A_t\): collateral-price amplification.

MFSM lesson:

Two states with identical current headroom can have different vulnerability if price changes destroy headroom at different rates.

---

## 18C. Slow-moving stabilizing capital

### Duffie — slow-moving capital / Presidential Address

Source:
https://web.stanford.edu/~duffie/PresidentialAddressApril15NormalFormat.pdf

Core mechanism:

Potential stabilizing capital can arrive gradually after a shock because capital raising, search, approval, funding, or position entry takes time.

MFSM mapping:

\[
R^-_t(h)
=
\text{opposing capacity able to act by horizon }h.
\]

MFSM lesson:

"Buyers exist" is not enough. The empirical question is whether they can act before forced sellers must act.

---

## 18D. Measurement risk when inferring endogeneity

### Filimonov and Sornette

Source:
https://ideas.repec.org/a/taf/quantf/v15y2015i8p1293-1314.html

Core warning:

Estimated branching / endogeneity measures can be distorted by kernel misspecification, outliers, nonstationarity, edge effects, and regime mixtures.

MFSM mapping:

\[
\mathbf Y_t=g(\mathbf Z_t;\psi_t)+\boldsymbol\eta_t.
\]

MFSM lesson:

\(\hat A_t\), \(\hat C_t\), or a fitted "criticality" statistic is an estimator of latent structure, not the latent structure itself.

---

## 18E. Dynamic strategy composition

### Hommes / in 't Veld and heterogeneous-expectations work

Source reviewed:
https://papers.tinbergen.nl/15088.pdf

Core mechanism:

Relative strategy performance can cause agents/capital to switch among forecasting or trading rules, creating self-reinforcing changes in market composition.

MFSM mapping:

\[
D_{t+1}=g(D_t,\text{relative performance},\text{flows},\text{constraints}).
\]

MFSM lesson:

Crowding can be produced by prior strategy success. Functional diversity should be modeled dynamically, not as a fixed market characteristic.

---

## 18F. Crypto carry as a joint state variable

### BIS — Crypto Carry

Source:
https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf

Core evidence:

In the studied crypto markets, carry is linked to leveraged speculative demand / attention and limited arbitrage capacity, and high carry contains information about subsequent downside risk.

MFSM mapping:

- \(A\): speculative reinforcement;
- \(H\): leverage / margin state;
- \(R^-\): arbitrage capacity.

MFSM lesson:

Carry is a candidate composite observable for a specific asset class, not a universal crash threshold.

---

## 18G. Economics of passive absorptive liquidity

### Milionis et al. — Loss-Versus-Rebalancing

Source:
https://arxiv.org/pdf/2208.06046v2

Core mechanism:

Passive AMM liquidity provision can incur a predictable loss-versus-rebalancing cost associated with arbitrage / adverse selection and foregone rebalancing.

MFSM mapping:

Opposing capacity should have its own economics:

\[
\dot R^-_t
=
\rho^-(\text{fees, spreads, convergence, capital cost})
-
c^-(\text{losses, adverse selection, margin, redemptions}).
\]

MFSM lesson:

Quoted liquidity is not equivalent to durable risk-bearing capacity.

---

## 18H. Gilt crisis as interaction evidence

### Bank of England — An anatomy of the 2022 gilt market crisis

Source:
https://www.bankofengland.co.uk/working-paper/2023/an-anatomy-of-the-2022-gilt-market-crisis

Core evidence:

Leveraged derivative/repo exposures, collateral demands, forced gilt sales, and market/intermediary capacity interacted during the episode.

MFSM mapping:

\[
H \times R^-_t(h) \times W_t \times \Psi.
\]

MFSM lesson:

Stress severity is better described by interaction among headroom, deadlines, absorptive capacity, and propagation than by the initial price move alone.

---

## 18I. Financing composition can deteriorate during favorable states

Sources:
- Minsky: https://www.levyinstitute.org/pubs/wp74.pdf
- Federal Reserve credit-market sentiment paper: https://www.federalreserve.gov/econresdata/feds/2015/files/2015028pap.pdf

Core insight:

Favorable financing conditions can change the composition and quality of financing, refinancing dependence, or marginal borrowers before overt stress appears.

MFSM lesson:

Buffer state \(B_t\) should allow liability maturity/composition and borrower/issuer quality, not only aggregate leverage.

---

## 18J. Mechanism decomposition in squeeze-like episodes

### SEC staff report on early 2021 equity/options conditions

Source:
https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf

Core lesson:

Potential fuel, realized covering flow, options hedging, margin/clearing demands, and retail/speculative demand must be separated rather than inferred from one popular narrative.

MFSM implication:

Short interest is potential \(R^+\), not proof that short-covering is the realized amplifier.

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

## 25A. Hypothesis H8 — Shock-conditioned path response and consequence

For prespecified disturbance classes \(c\), instantiate concrete interventions \(\delta=(c,V,a,d,t_0,p,\nu)\) and horizons \(h\).

> the same latent market state can have materially different path outcomes across intervention classes, amplitudes, and horizons.

Let \(\mathcal I_t\) denote the information available at the prediction timestamp, including uncertainty about the latent state. Test whether functionals of

\[
\mathcal P_{t,h}^{\delta}
=
\mathcal L(
\mathbf Z_{[t,t+h]}^{\delta}
\mid
\mathcal I_t
)
\]

improve discrimination of outcomes after funding shocks, redemptions, margin changes, collateral haircuts, or other identified interventions.

Candidate empirical targets include:

- liquidation-threshold probability;
- maximum adverse excursion;
- cascade size;
- recovery probability / time;
- expected shortfall of a prespecified path loss.

Any reported consequence must specify

\[
F_t(\delta,h;\ell,\rho).
\]

Where data allow, use disturbance-class and disturbance-amplitude holdouts in addition to date/episode holdouts.

---

## 25B. Hypothesis H9 — Constraint sensitivity

Conditional on current headroom \(H_t\):

> states in which buffers are more sensitive to price or collateral movements should exhibit more nonlinear deleveraging after comparable shocks.

The local object is the Jacobian

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

For the intervention \(\delta\), the directional local response is

\[
\boldsymbol\chi_{B,t}^{\delta}(h)
=
\mathbf\Chi_{B,t}(h)\mathbf v_{\delta}.
\]

For finite shocks, especially near thresholds, test the finite-shock response

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

---

## 25C. Hypothesis H10 — Strategic complementarity

Conditional on balance-sheet capacity:

> run-like outcomes should be more likely or more severe when participant actions are strong strategic complements.

Candidate settings include withdrawal, redemption, rollover, and collateral coordination problems.

The challenge is identification: \(\Gamma_t\) is generally latent.

---

## 25D. Hypothesis H11 — Measurement robustness

A candidate endogeneity / feedback state should survive plausible alternatives for:

- kernel specification;
- regime segmentation;
- outlier treatment;
- sampling frequency;
- edge correction;
- proxy construction.

If an estimated "critical" state disappears under reasonable observation models, it should not be promoted as structural evidence.

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

## 28. \(H\): headroom, \(\mathbf\Chi_B\): local sensitivity, and \(\Delta\mathbf B^{\delta}\): finite-shock response

Possible headroom proxies:

- margin distance;
- liquidation distance;
- collateral buffer;
- risk-limit distance;
- covenant headroom;
- dealer inventory limits;
- fund redemption buffer.

Low \(H\) is specifically about **distance to forced action**.

Separately estimate, where possible, the local buffer Jacobian

\[
\mathbf\Chi_{B,t}(h)
=
D_{\mathbf z}
\mathbb E[
\mathbf B_{t+h}^{0}
\mid
\mathbf Z_t=\mathbf z,\mathcal I_t
],
\]

and the intervention-specific finite-shock response

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

Candidate empirical designs include collateral-price shocks, margin schedule changes, or cross-sectional differences in collateralization.

---

## 29. \(R^-\): opposing absorptive capacity

The preferred object is horizon-qualified:

\[
R^-_t(h)
=
\text{opposing capacity usable by horizon }h.
\]

Possible proxies:

- order-book depth by horizon;
- dealer balance-sheet capacity;
- market-maker inventory tolerance;
- contrarian fund capital;
- arbitrage balance sheet;
- committed backstop liquidity;
- stress-period replenishment rate;
- measured arrival time of new risk-bearing capital.

Gross trading volume is not sufficient. Eventual capital is not equivalent to capital available before a forced-action deadline.

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

Because strategy success can attract capital, measure changes in \(D_t\) over time as well as its level. Candidate drivers include relative strategy performance, fund flows, benchmark migration, and risk-rule convergence.

### 32.1 \(\Gamma\): strategic complementarity

Candidate settings:

- depositor/creditor withdrawal;
- rollover refusal;
- fund redemptions;
- collateral hoarding;
- dealer withdrawal.

A useful empirical design must distinguish strategic response to others from common reaction to the same public information.

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

## 33.1 Observation model

Measured state variables are proxies for latent structure.

Use the conceptual observation equation

\[
\mathbf Y_t
=
g(\mathbf Z_t;\psi_t)
+
\boldsymbol\eta_t.
\]

For every latent quantity, record:

- proxy definition;
- model/kernel choice;
- timestamp availability;
- expected bias;
- regime sensitivity;
- alternative proxy constructions.

This is especially important for inferred endogeneity, crowding, network state, and criticality.

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

1. **Prespecified latent-state variables, observed proxies, and transformations.**
2. **Prespecified disturbance class and fully specified structural intervention, including amplitude and path.**
3. **Prespecified path-level loss functional \(\ell\) and risk / severity functional \(\rho\).**
4. **Out-of-sample testing.**
5. **Comparison against strong finance baselines.**
6. **Robustness across multiple assets or episodes.**
7. **False-alarm accounting.**
8. **No look-ahead data.**
9. **Mechanism-consistent signs and interactions.**
10. **Incremental decision value after transaction costs where trading is the application.**
11. **Stability to reasonable alternative observation, kernel, and intervention specifications.**
12. **Failure analysis showing when and why the signal stops working.**

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

17. Diamond, Douglas W., and Philip H. Dybvig. **Bank Runs, Deposit Insurance, and Liquidity.** *Journal of Political Economy* 91(3), 1983, 401-419.
    https://www.journals.uchicago.edu/doi/10.1086/261155

18. Kiyotaki, Nobuhiro, and John Moore. **Credit Cycles.** 1997.
    https://msuweb.montclair.edu/~lebelp/KyotakiMooreCreditCyclesJPE1997.pdf

19. Darrell Duffie. **Presidential Address / Slow-Moving Capital.**
    https://web.stanford.edu/~duffie/PresidentialAddressApril15NormalFormat.pdf

20. Vladimir Filimonov and Didier Sornette. **Apparent criticality and Hawkes-model specification in financial markets.**
    https://ideas.repec.org/a/taf/quantf/v15y2015i8p1293-1314.html

21. Bank for International Settlements. **Crypto Carry.**
    https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf

22. Jason Milionis et al. **Loss-Versus-Rebalancing.**
    https://arxiv.org/pdf/2208.06046v2

23. Bank of England. **An anatomy of the 2022 gilt market crisis.**
    https://www.bankofengland.co.uk/working-paper/2023/an-anatomy-of-the-2022-gilt-market-crisis

24. Baker, Malcolm, and Jeffrey Wurgler. **Market Timing and Capital Structure.**
    https://pages.stern.nyu.edu/~jwurgler/papers/capstruct.pdf

25. Hyman Minsky. **Financial instability / financing composition working paper.**
    https://www.levyinstitute.org/pubs/wp74.pdf

26. Hommes / in 't Veld, heterogeneous expectations and endogenous regime dynamics.
    https://papers.tinbergen.nl/15088.pdf

27. SEC. **Staff Report on Equity and Options Market Structure Conditions in Early 2021.**
    https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf

For the complete link-by-link audit that motivated the latest revisions, see `artifacts/source_review_extended_2026-09-22.md`.

---

## Final empirical invariant

The finance evidence supports the following stance:

> **MFSM should be judged by whether its latent-state estimates and state-dependent interactions improve real out-of-sample estimation of decision-relevant functionals of fully specified counterfactual path responses, while separating shock consequence from structural susceptibility and remaining robust to alternative measurement, kernel, and intervention specifications.**

Until that test is passed, MFSM is a structured research program, not a validated trading system.
