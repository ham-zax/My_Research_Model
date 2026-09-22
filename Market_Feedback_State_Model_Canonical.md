# Market Feedback-State Model (MFSM)
## Canonical Deep Specification

Version: Current canonical synthesis
Date: 2026-09-22
Status: Research framework, not a validated trading system
Primary purpose: Diagnose the internal feedback state of reflexive markets and generate falsifiable hypotheses about continuation, exhaustion, instability, and failure propagation.

Companion specifications:

- `Mathematical_Foundations.md` — exact delay, memory-kernel, local-stability, stochastic-recovery, network, threshold, and adaptive-capacity mathematics.
- `Empirical_Finance_Foundations.md` — finance-native evidence base, measurement map, falsification standards, and durable source list.
- `Research_Protocol.md` — required procedure for applying, testing, extending, and versioning MFSM.

The canonical file defines the model. The mathematical file preserves exact formal results. The empirical file determines what is finance-supported. The protocol controls how the model may evolve.

---

## 0. Executive definition

The Market Feedback-State Model (MFSM) is a causal framework for analyzing markets as complex adaptive systems whose current structural state changes the law governing their own future response.

Its central proposition is:

> A market state is not merely a collection of prices and positions. It is a response-generating architecture. As the state evolves, it changes leverage, collateral, risk budgets, liquidity, positioning, incentives, participant synchronization, network exposure, expectations, the availability of stabilizing capital, and the timing or topology of counterforces. Those changes alter how the market will respond to the next disturbance.

A directional trend is one important way this state transformation can occur, but it is not required. Bank-run-like coordination, funding stress, or threshold-sensitive vulnerability can exist even without a preceding trend.

The model therefore does not begin with the question:

> Will price go up or down next?

It begins with:

> What structural state is the market in, what feedbacks and constraints define that state, which disturbance classes matter, how quickly can reinforcing or stabilizing forces respond, and how would the next shock propagate through the current architecture?

The deepest operational question is:

> How is the current structural state changing the system's response law for the next disturbance?

MFSM is explicitly not a universal crash predictor, not a scalar fragility score, not a claim that markets are literally biological systems, and not a claim that natural systems have solved market instability. Cross-domain analogies are used only to discover recurrent causal architectures. Financial validity must come from financial mechanisms, data, and empirical tests.

---

## 1. Origin and intellectual stance

MFSM began from a cross-domain structural analogy question:

> What do robust natural systems use to prevent locally useful positive feedback from becoming globally catastrophic?

The investigation considered mechanisms from biology, ecology, neuroscience, chemistry, control theory, reaction-diffusion systems, adaptive networks, and collective behavior. The valuable result was not a library of metaphors. It was a set of recurring structural primitives:

- positive feedback can be useful and necessary;
- finite capacities constrain amplification;
- activation can reduce future activation capacity;
- delayed antagonistic responses can oppose fast amplification;
- response gain can saturate;
- signals can decay without reinforcement;
- heterogeneous reaction rules can reduce synchronization in some regimes;
- local failures can be compartmentalized or can propagate through networks;
- relative response times matter as much as absolute response times;
- thresholds can convert smooth behavior into forced behavior;
- the same feedback architecture that amplifies a boom can reverse sign and amplify a bust.

The framework was then cross-checked against financial economics and market microstructure. A substantial part of the causal architecture already exists in established finance under different names: funding-liquidity spirals, leverage cycles, limits to arbitrage, fire sales, common-exposure contagion, endogenous risk, heterogeneous-agent dynamics, flow-induced price pressure, momentum crashes, credit booms, and systemic network instability.

MFSM therefore treats natural systems as idea generators and finance as the evidentiary authority for financial claims.

---

## 2. Epistemic status

Every claim made with MFSM should be labeled mentally as one of four evidence levels.

### Level 1: Established source-domain mechanism

A mechanism is experimentally, formally, or empirically supported in the source domain, such as neuronal refractoriness, delayed density dependence, or adaptive transport networks.

This does not establish financial relevance.

### Level 2: Structural financial analogue

A financial mechanism has a similar causal topology: comparable state variables, feedback direction, constraints, delay structure, or propagation architecture.

This establishes that the analogy is more than linguistic, but it still does not establish predictive power.

### Level 3: Empirically supported financial relationship

Financial data show that the proposed mechanism or state variable is associated with meaningful outcomes under specified conditions.

This may support use as a diagnostic input, but causal interpretation still depends on identification quality.

### Level 4: Validated predictive contribution

A prespecified implementation improves genuine out-of-sample prediction, calibration, or decision value beyond strong finance-specific baselines.

MFSM as a complete framework has not yet reached Level 4.

---

## 3. The three outputs that must remain separate

MFSM separates three quantities that ordinary market commentary often conflates.

### 3.1 Trend Strength: T

Trend Strength describes the observed directional process.

Conceptually:

T = strength, persistence, breadth, and acceleration of directional movement.

Possible empirical components include:

- multi-horizon returns;
- breadth;
- persistence;
- realized directional volume;
- flow direction;
- cross-sectional participation;
- acceleration.

T is descriptive. High T does not imply sustainability, high stressed consequence, or high structural susceptibility.

### 3.2 Trend Sustainability: U

Trend Sustainability asks whether the process generating the trend still has the capacity to continue.

Conceptually:

U = sustainability of the mechanism producing the current directional movement.

U depends on factors such as:

- replenishment of same-direction capacity;
- continuing external confirmation;
- mechanism-specific remaining continuation capacity;
- response of opposing supply;
- price impact of new flows;
- changes in financing conditions;
- whether the amplifying loop remains active.

A strong trend can have low U.

### 3.3 Shock-conditioned consequence

MFSM does not attach one context-free fragility number to a market. It first asks what happens under a **specified structural intervention operator** and what form of damage matters.

Let \(\delta\) be the human-readable intervention descriptor, \(\mathfrak I_{\delta}\) the corresponding intervention operator on the structural system, \(h\) the horizon, \(\ell_{\mathrm{abs}}\) a one-path **loss-oriented** functional, and \(\rho\) a risk / severity functional. The canonical absolute stressed consequence is

\[
\boxed{
F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)
=
\rho_{\mathcal P_{t,h}^{\delta}}
\left[
\ell\!\left(\mathbf Z_{[t,t+h]}^{\delta}\right)
\right].
}
\]

The loss orientation must be fixed so that larger values mean worse outcomes. For example, use probability of **failure to recover** rather than probability of recovery if the quantity is to be interpreted as severity.

Examples include:

- probability that a liquidation threshold is crossed;
- expected maximum adverse excursion;
- expected cascade size;
- expected shortfall of path loss;
- probability that liquidity fails to recover by horizon \(h\).

If the research question is the **incremental causal consequence of the intervention**, the loss must depend on both potential paths, for example \(\ell_{\Delta}(\mathbf Z^{\delta},\mathbf Z^0)\). A distribution of such pathwise causal losses requires an explicit joint coupling of the two potential paths; it cannot be recovered from \(\mathcal P^{\delta}\) alone.

This matters because the same structural state can be robust to one intervention and vulnerable to another, because absolute stressed risk is not the same as causal incremental harm, and because two users may care about different failure functionals.

For trend applications, one can still observe

\[
T\uparrow,\qquad U\downarrow,
\]

while the consequences of a specified adverse intervention rise sharply.

### 3.4 Structural susceptibility

Shock consequence and structural susceptibility are not identical. A large intervention can produce a large loss even in a comparatively resilient system.

For a disturbance class \(c\), define an intervention family \(\delta(c,a)\) indexed by amplitude \(a\). The susceptibility profile is the response curve

\[
\boxed{
a
\longmapsto
F_t^{\mathrm{abs}}(\delta(c,a),h;\ell_{\mathrm{abs}},\rho).
}
\]

The numerical slope depends on how amplitude is parameterized. Therefore each disturbance family must define canonical economic units. Cross-system comparisons should use the **same units and intervention semantics**, or a prespecified dimensionless normalization such as

\[
\tilde a
=
\frac{a}{a_{\mathrm{ref}}(c)}.
\]

Only then is a derivative such as

\[
\frac{\partial F_t}{\partial \tilde a}
\]

meaningfully comparable.

A critical disturbance amplitude can be defined as

\[
\boxed{
a_q^*
=
\inf
\left\{
a:
\Pr_{\mathcal P_{t,h}^{\delta(c,a)}}
\left(
\ell(\mathbf Z_{[t,t+h]}^{\delta(c,a)})
\ge
\ell^*
\right)
\ge q
\right\}.
}
\]

A system that fails after a very small standardized disturbance can therefore be structurally more susceptible than one that suffers a larger absolute loss only after a much larger intervention. MFSM should report shock-conditioned consequence and susceptibility separately.

---

## 4. Canonical model objects

The mature representation is not a seven-factor checklist. The central requirement is that the dynamic state be **closed**.

\[
\boxed{
\mathcal M_t
=
\{\mathbf Z_t;\mathcal G,\mathcal O\}
}
\]

where:

- \(\mathbf Z_t\) = the **closed augmented latent state** containing every endogenous or stochastic time-varying coordinate required to determine future dynamics under the model;
- \(\mathcal G\) = the fixed structural form: transition equations / kernels, mappings from state to delay-memory and propagation operators, controller architecture, disturbance law, and parameterization;
- \(\mathcal O\) = the true observation mechanism linking latent state to recorded data.

Closure rule: any object written with a time index—such as \(K_t\), \(W_t\), \(\Sigma_t\), a time-varying coefficient, funding regime, or controller state—must satisfy exactly one of the following:

1. it is a deterministic / predetermined input known at the decision time;
2. it is exogenous with an explicit law included in \(\mathcal G\); or
3. its future-relevant coordinates are components of \(\mathbf Z_t\).

Thus, when delay kernels or network topology evolve endogenously, write them as mappings such as \(K(\mathbf Z_t)\) and \(W(\mathbf Z_t)\), or include the state variables that determine them inside \(\mathbf Z_t\). They may not remain free time-varying objects outside the closed state.

Named objects such as buffers \(B_t\), expectation / coordination state \(Q_t\), capacities, discrete threshold modes, and control states are therefore either **components or measurable projections of \(\mathbf Z_t\)**. The local Jacobian \(J_t\) is derived from a local linearization of \(\mathcal G\); \(M_t^{term}\) is a derived prospective classification, not a primitive state variable.

The true observation relation can be written conceptually as a conditional law

\[
\boxed{
p_*(\mathbf Y_t\mid\mathbf Z_t).
}
\]

An additive-noise special case is

\[
\mathbf Y_t
=
g_*(\mathbf Z_t)
+
\boldsymbol\eta_t.
\]

An analyst does not know \(p_*\) exactly. Each empirical implementation therefore supplies one or more candidate probabilistic measurement models

\[
\boxed{
p_m(
\mathbf Y_t
\mid
\mathbf Z_t;
\psi^{(m)}
),
}
\]

or an equivalent explicitly stated noise model. The implementation must report which conclusions survive the prespecified alternatives \(m\). A fitted proxy or conditional mean is not automatically the latent state.

MFSM distinguishes a disturbance **class** from a structural intervention. The tuple

\[
\boxed{
\delta
=
(c,V,a,d,t_0,p,\nu)
}
\]

is a required human-readable **descriptor**: class, structural target, amplitude, direction, onset, temporal profile, and any stochastic component. It is not, by itself, the mathematical intervention.

Let

\[
\mu_t
=
\mathcal L(
\mathbf Z_t
\mid
\mathcal I_{t^-}
)
\]

denote the pre-intervention latent-state law. The application must define an intervention operator on the **full counterfactual specification**,

\[
\boxed{
\mathfrak I_{\delta}:
(\mu_t,\mathcal G)
\longmapsto
(\mu_t^{\delta},\mathcal G^{\delta}).
}
\]

This contract supports:

- **state-setting / jump interventions**, which change \(\mu_t\) or the realized initial condition while leaving the structural form fixed;
- **structural interventions**, which change an equation, transition kernel, parameter, constraint, or forcing term in \(\mathcal G\);
- **hybrid interventions**, which change both.

Each application must state exactly what changes, the units and amplitude convention, the law of any stochastic component, and its coupling to baseline exogenous shocks. Endogenous outcomes such as "bank run" or "liquidation cascade" are responses, not interventions.

Let \(\mathcal I_t\) denote the information genuinely available at the decision time; if the intervention begins exactly at \(t\), use the pre-intervention information set \(\mathcal I_{t^-}\). When \(\mathbf Z_t\) is latent, conditioning on \(\mathcal I_t\) integrates over state-estimation uncertainty rather than pretending the exact latent state is observed. Given \((\mu_t,\mathcal G)\) and the intervention \(\mathfrak I_\delta\), the fundamental response object is the **conditional counterfactual path law**

\[
\boxed{
\mathcal P_{t,h}^{\delta}
=
\mathcal L
\left(
\{\mathbf Z_{t+s}^{\delta}\}_{0\le s\le h}
\mid
\mathcal I_t
\right).
}
\]

The no-intervention baseline is \(\mathcal P_{t,h}^{0}\).

The mean causal response is only a derived projection:

\[
\boxed{
\mathbf m_t^{\delta}(s)
=
\mathbb E
\left[
\mathbf Z_{t+s}^{\delta}
-
\mathbf Z_{t+s}^{0}
\mid
\mathcal I_t
\right].
}
\]

In practice, an empirical implementation need not estimate the unrestricted path law; it should target decision-relevant projections such as threshold probabilities, maximum stress, tail loss, cascade size, or recovery time.

---

## 5. \(\mathbf Z_t\): closed augmented latent state

\(\mathbf Z_t\) contains the minimal economically meaningful **dynamic state required to close the model**. It should not be overstuffed by default, but every independently evolving buffer, control state, coordination state, or discrete regime required to determine the future must either be inside \(\mathbf Z_t\) or have an explicit evolution equation that is incorporated into the augmented state. Observed proxies belong to \(\mathbf Y_t\) and need not equal the latent state exactly.

Candidate components include:

- price and returns;
- order flow;
- volatility;
- positioning;
- leverage;
- collateral state;
- risk limits;
- funding costs;
- liquidity depth;
- dealer inventory;
- realized and expected fundamentals;
- flows;
- ownership concentration;
- common exposures;
- short interest;
- derivative positioning;
- issuance or producer supply;
- investor mandates;
- policy state.

The model should include only variables with a plausible causal role in the specific market being studied.

---

## 6. J_t: response matrix and endogenous amplification

A rising market is not automatically a positive-feedback market.

Positive feedback exists when a state change causes behavior that reinforces that state change.

Examples:

price up -> attention up -> inflows up -> price up

price up -> collateral value up -> borrowing capacity up -> buying up -> price up

price down -> collateral value down -> margin pressure up -> forced selling up -> price down

The full object should be represented locally by a state-dependent response matrix or Jacobian:

Delta x_dot approximately equals J_t Delta x.

J_t captures how small perturbations in one state variable affect others around the current regime.

### 6.1 Derived amplification diagnostic A_t

A_t can remain as a convenient summary statistic:

A_t = effective endogenous same-direction loop gain.

It should not be estimated as momentum alone.

A conceptual loop-gain decomposition is:

Lambda_t(h) = (partial Q_endo(t+h) / partial r_t) * (partial r_(t+h) / partial Q_endo(t+h)).

The first factor asks how strongly a return generates future endogenous same-direction flow.

The second asks how strongly that flow moves price.

The causal estimation problem is difficult because price, flow, and information are simultaneous and endogenous.

### 6.2 Local stability is not enough

Even if all local eigenvalues imply asymptotic stability, a non-normal or thresholded system may display large transient amplification.

The relevant questions are therefore:

- does a small perturbation decay monotonically?
- does it oscillate while decaying?
- does it transiently amplify before decaying?
- does it generate an oscillatory instability?
- does it generate a monotonic instability?
- does it cross a nonlinear threshold into a different regime?

The model must not equate one mathematical instability type with all financial crashes.

---

## 7. B_t: capacities, buffers, and thresholds

One of the most important discoveries in the model is that generic "resource" or "liquidity" is too crude.

At minimum, three economically distinct capacities must be separated.

### 7.1 \(R_k^+\): mechanism-specific remaining continuation capacity

\(R^+\) is a **category**, not one universal market-wide scalar. For each identified continuation mechanism \(k\), define

\[
\boxed{
R_{k,t}^+
=
\text{capacity still available for mechanism }k
\text{ to reinforce the current direction.}
}
\]

Examples of distinct mechanisms include:

- undeployed directional risk capital;
- potential new fund inflows;
- unused leverage / balance-sheet capacity;
- remaining short exposure capable of generating buy-to-cover demand;
- uncommitted marginal participants;
- capital that can still rotate into the asset.

These quantities should remain mechanism-indexed unless a specific aggregation rule is economically justified and prespecified. A decline in a relevant \(R_{k,t}^+\) can be stabilizing because it deprives that reinforcing mechanism of further fuel.

Exhaustion of one \(R_k^+\) predicts possible weakening of that mechanism, not necessarily exhaustion of every continuation channel and not necessarily a crash.

### 7.2 H: financing, collateral, and risk headroom

H = distance between current positions and forced behavioral thresholds.

Examples:

- margin headroom;
- collateral buffer;
- liquidation distance;
- VaR headroom;
- dealer inventory limit distance;
- mandate or risk-limit headroom;
- available eligible collateral before a deadline.

A decline in \(H\) is categorically different from a decline in any mechanism-specific \(R_{k,t}^+\).

Low H means a small adverse move can transform voluntary actors into forced actors.

### 7.3 R_minus: opposing absorptive capacity

R_minus = capacity available to take the opposite side of an unwind.

The stronger canonical form is horizon-qualified and, when the disturbance changes willingness or financing conditions, disturbance-conditioned:

\[
\boxed{
R^-_t(h;\delta)
=
\text{opposing capacity that can actually act by horizon }h
\text{ under intervention }\delta.
}
\]

When a disturbance family and amplitude are already fixed by the research design, \(R^-_t(h)\) is acceptable shorthand.

Examples:

- dealer balance-sheet capacity;
- market-making inventory capacity;
- arbitrage capital;
- contrarian risk capital;
- usable order-book depth;
- available financing for stabilizing traders;
- investors with mandate and horizon to absorb distressed flow.

This distinction matters because a market can have abundant eventual buyers but almost no capital able to act before a margin or redemption deadline, and because the same nominal flow may attract liquidity under a routine rebalance but repel it under a suspected information or collateral shock.

Low short-horizon \(R^-_t(h;\delta)\) means the market may have difficulty absorbing forced flow even if longer-horizon fundamental value appears attractive.

### 7.4 Effective capacity is time-dependent

Aggregate money or nominal wealth is not the relevant quantity.

The important quantity is usable capacity under the relevant constraints and deadline.

A participant may be economically solvent but operationally forced to sell if:

margin deadline < time required to mobilize eligible collateral.

Therefore:

available resources != usable resources within the required timescale.

This creates a direct link between buffers and delay.

### 7.5 Constraint sensitivity and finite-shock buffer response

Current headroom and the sensitivity of future headroom are different objects.

If \(\mathbf B_t\in\mathbb R^m\) is a vector of buffers / constraints and \(\mathbf Z_t\in\mathbb R^n\) is the latent structural state, the local sensitivity is an \(m\times n\) Jacobian:

\[
\boxed{
\mathbf\Chi_{B,t}(h)
=
D_{\mathbf z}
\,
\mathbb E
\left[
\mathbf B_{t+h}^{0}
\mid
\mathbf Z_t=\mathbf z,\mathcal I_t
\right].
}
\]

This Jacobian is specifically an **initial-state sensitivity**. For a small intervention that acts solely through an instantaneous displacement of the initial state, with induced direction \(\mathbf v_{\delta}=D_{\delta}\mathbf Z_t[\dot\delta]\), the chain rule gives

\[
\boldsymbol\chi_{B,t}^{\delta}(h)
=
\mathbf\Chi_{B,t}(h)\mathbf v_{\delta}.
\]

That projection is **not valid for a general intervention** on a parameter, margin rule, transition kernel, constraint, or temporal forcing. For a general local intervention use the direct intervention derivative

\[
D_{\delta}
\,
\mathbb E[
\mathbf B_{t+h}^{\delta}
\mid
\mathcal I_t
][\dot\delta],
\]

with the derivative taken in the appropriate parameter or function space.

If a single scalar is required, the buffer weighting and intervention direction must both be explicit.

For finite interventions, especially near thresholds, local derivatives can be misleading. The preferred object is then the finite-shock buffer response

\[
\boxed{
\Delta\mathbf B_t^{\delta}(s)
=
\mathbb E
\left[
\mathbf B_{t+s}^{\delta}
-
\mathbf B_{t+s}^{0}
\mid
\mathcal I_t
\right].
}
\]

Two systems can have the same current \(H_t\) but radically different vulnerability if a small state change destroys future headroom much faster in one than in the other. Collateral-based credit cycles are a canonical financial example.

---

## 8. K_t: delay, memory, and timescale separation

The framework initially used a scalar delay tau. That is too crude.

The core insight survives:

stability depends on both feedback strength and response delay.

For the simple delayed linear system:

z_dot(t) = a z(t) - b z(t - tau), with 0 <= a < b,

the first stability boundary depends jointly on a, b, and tau.

In the special case a = 0, stability requires:

b tau < pi / 2.

The lesson is not that this threshold applies to markets. The lesson is that delay has no universal meaning without response strength.

### 8.1 Relative timescale Theta

The useful diagnostic is:

Theta = tau_N / tau_A,

where:

- tau_A = characteristic amplification timescale;
- tau_N = characteristic inhibitory or counter-response timescale.

Interpretation:

Theta asks how quickly the reinforcing loop can operate relative to the mechanisms that counteract, replenish, or constrain it.

A large Theta can arise because:

- inhibition becomes slower;
- amplification becomes faster;
- both occur simultaneously.

The third possibility is especially important in electronic markets: the stabilizing mechanism need not get slower for the system to become more vulnerable to a specified disturbance if the reinforcing loop accelerates.

### 8.2 Gain-delay product Phi

A second conceptual quantity is:

Phi approximately equals effective loop gain times effective response delay.

Phi captures the idea that a weak amplifier with long delay may remain stable, while a strong amplifier with the same delay may not.

No universal financial threshold is assumed.

### 8.3 Delay is usually a distribution, not a point

Financial counterforces do not arrive at one deterministic lag.

Examples:

- some arbitrage capital responds within seconds;
- some funds rebalance daily;
- corporate issuance may take weeks or months;
- physical commodity supply may take years;
- regulation may take even longer;
- collateral can exist but require hours or days to mobilize.

Therefore the better representation is a memory kernel K(s):

u_t = h( integral from 0 to infinity K(s) x_(t-s) ds, expectations ) - current adjustment.

Two systems with the same mean delay can have different stability if one has a fixed delay and another has a distributed response.

The shape of K(s) can therefore matter as much as its mean.

---

## 9. W_t: network propagation topology

Raw correlation is not the same as causal connectivity.

The primitive object is \(W_t\), an exposure or transmission operator.

A scalar \(C_t\) may be used only as a **derived application-specific summary**. If retained, the application must define an explicit functional such as

\[
\boxed{
C_t
=
f_C(
W_t,
\mathbf Z_t,
\text{propagation law},
\delta,
h
).
}
\]

There is no canonical free-standing connectivity scalar. Operational analysis should prefer the actual propagation operator, exposure weights, dominant modes, or other mechanism-specific diagnostics.

Relevant links include:

- common ownership;
- common holdings;
- collateral relationships;
- shared funding sources;
- counterparties;
- benchmark membership;
- options hedging;
- volatility-control rules;
- risk-parity rebalancing;
- margin systems;
- common market makers;
- cross-asset liquidation channels.

### 9.1 Connectivity is non-monotonic

More connectivity is not always destabilizing.

Denser networks can diversify or absorb small shocks while transmitting sufficiently large shocks more widely.

Therefore, even for a fixed prespecified definition of \(C_t\),

\[
C_t\uparrow
\]

does not imply higher stressed consequence unconditionally.

Shock magnitude, loss-absorption capacity, recovery assumptions, and network structure matter jointly.

### 9.2 Spectral direction

Some network models characterize stability using the dominant eigenvalue or spectral radius of an appropriately defined leverage or exposure matrix.

The important general principle is:

Do not count connections. Identify the strongest self-reinforcing propagation mode through those connections.

Any spectral statistic must inherit its financial meaning from an explicit propagation law. A large eigenvalue of an arbitrary correlation matrix is not sufficient.

---

## 10. D_t: functional diversity

D_t is not the number of participants.

D_t = dispersion of marginal reactions to a common state change.

A market with thousands of institutions can have low functional diversity if they all respond similarly to:

- volatility increases;
- drawdowns;
- margin changes;
- benchmark deviations;
- factor shocks;
- redemptions;
- risk limits.

Conversely, a smaller set of participants can be functionally diverse if their horizons, liabilities, constraints, valuation rules, and funding structures differ.

Functional diversity is also dynamic rather than fixed. Relative strategy performance, capital flows, imitation, benchmark pressure, and constraints can change the distribution of reaction functions:

\[
\boxed{
D_{t+1}
=
g(D_t,\text{relative strategy performance},\text{flows},\text{constraints}).
}
\]

A successful strategy can therefore attract capital, reduce functional diversity, and increase the market impact of that same strategy.

### 10.1 Synchronization is not automatically harmful

Common reaction to genuine new information can improve price discovery.

The dangerous combination is more specific:

common action + forced behavior + constrained opposing capacity + transmissible network links.

Therefore low D is a conditional vulnerability, not an unconditional bearish signal.

---

## 11. Q_t: external versus endogenous confirmation

One of the most important conceptual distinctions in MFSM is the source of confirmation.

### 11.1 S_ext: external confirmation

S_ext = evidence arriving from outside the market's own price-feedback loop.

Examples:

- earnings;
- cash flows;
- adoption;
- productivity;
- physical demand;
- reserve changes;
- objectively new macro information;
- verified fundamental shocks.

### 11.2 S_end: endogenous confirmation

S_end = apparent confirmation generated substantially by market behavior itself.

Examples:

price up -> media attention up -> inflows up -> price up

price up -> collateral up -> borrowing capacity up -> buying up -> price up

price up -> performance chasing -> inflows -> price up

### 11.3 Endogeneity ratio E

A conceptual diagnostic is:

E = S_end / S_ext.

This ratio should not be treated as trivially measurable.

It expresses the question:

How much of current continuation is being validated by external information versus by the consequences of prior market movement?

An increasing E may indicate growing dependence on self-generated continuation, but estimating it requires decomposition of information, flow, and mechanical impact.

Persistent order flow, persistent information, and permanent price impact are not interchangeable.

### 11.4 Strategic complementarity and coordination state

Some run-like vulnerability is generated not by price-to-flow feedback but by the fact that one participant's optimal action depends on expected actions of others.

Represent this conceptually by:

\[
\boxed{
\Gamma_t
\sim
\frac{\partial a_i^*}{\partial \bar a_{-i}}
}
\]

where \(a_i^*\) is participant \(i\)'s optimal action and \(\bar a_{-i}\) summarizes relevant actions of others.

High positive \(\Gamma_t\) means behavior is strategically complementary: others withdrawing, selling, redeeming, or refusing rollover can make the same action individually rational for another participant.

This allows MFSM to represent run-like coordination vulnerability even when no preceding price trend exists.

---

## 12. Threshold geometry and optional derived exposure \(L_t\)

Many market processes are not smooth.

A small state change can have little effect until a switching surface is crossed, after which behavior changes discontinuously.

Examples:

- liquidation thresholds;
- margin calls;
- VaR breaches;
- stop-out rules;
- covenant thresholds;
- collateral haircuts;
- fund redemption gates;
- market-maker inventory limits;
- volatility-control rebalancing thresholds.

The primitive objects are the **actual threshold surfaces and distances to them**, represented inside \(B_t\) / \(H_t\) and the hybrid transition rules. \(L_t\) is only an optional **derived summary** of system-wide threshold concentration or convexity; it is not an independent primitive state variable.

For example, if \(d_j(\mathbf Z_t)\) is signed distance to switching surface \(j\), an application may define a prespecified near-threshold exposure statistic such as

\[
L_t(\varepsilon)
=
\sum_j
w_j
\mathbf 1\{0<d_j(\mathbf Z_t)\le\varepsilon\}.
\]

Other definitions are possible, but they must be fixed before testing. Do not add \(L_t\) if it merely repackages the same information already contained in \(H_t\), \(\mathbf\Chi_B\), and the threshold map.

The essential architecture is:

state move -> threshold crossing -> forced action -> additional state move.

This is one of the main mechanisms by which a smooth process becomes a cascade.

---

## 13. \(N_t\): endogenous counterflow and antagonism

\(N_t\) represents forces that oppose the current reinforcing process. The symbol \(N_t\) is used to avoid collision with the information set \(\mathcal I_t\).

Possible examples:

- issuance;
- producer supply;
- arbitrage;
- profit-taking;
- substitution;
- valuation-sensitive selling;
- hedging;
- tighter funding conditions;
- policy response;
- competitor entry;
- capital raising by opposing participants.

However, MFSM rejects the assumption that every trend immediately creates its antagonist.

A rising market can initially relax constraints:

price up -> collateral up -> leverage capacity up -> buying up -> price up.

The correct question is therefore not only:

What counterforce is price creating?

It is:

How is the move transforming the full state from which future amplification, restraint, and forced behavior will arise?

---

## 14. Derived termination mechanism \(M^{term}\)

\(M_t^{term}\) is a **derived prospective classification or posterior over mechanisms**, not a primitive component of the latent state.

A major use of the framework is to classify how a feedback regime is likely to end from information available **before** the outcome. If the mechanism label is assigned only after seeing the realized path, it is explanatory annotation rather than a predictive state variable.

Identical-looking price charts can conceal different causal termination modes.

At least four mechanisms must remain distinct.

### 14.1 M1: fuel exhaustion

The relevant mechanism-specific continuation capacities \(R_{k,t}^+\) become exhausted or insufficient.

The reinforcing side can no longer add enough new demand or supply through the mechanisms that had been sustaining the trend.

Typical consequence:

- stall;
- drift;
- quiet reversal;
- lower continuation probability.

Fuel exhaustion does not imply catastrophic failure.

### 14.2 M2: delayed counterflow

\(N_t\) becomes large enough to oppose the trend.

Examples:

- issuance;
- producer supply;
- new arbitrage capital;
- valuation-sensitive sellers;
- substitution;
- delayed policy or funding response.

Typical consequence:

- mean reversion;
- oscillation;
- controlled reversal;
- new equilibrium.

### 14.3 M3: gain saturation

Additional stimulus generates less marginal response.

Conceptually:

partial response / partial stimulus declines.

Possible causes:

- responsive participants are already positioned;
- opposing supply grows;
- information is already anticipated;
- liquidity or impact changes;
- the relevant receptor population is saturated in a structural analogue.

Diminishing response alone is not a reversal signal.

### 14.4 M4: threshold unwind

H becomes sufficiently low that a small adverse move crosses forced-action thresholds.

Then the positive-feedback architecture can reverse sign:

boom:
price up -> collateral up -> buying capacity up -> price up

becomes bust:
price down -> collateral down -> forced selling up -> price down.

This is categorically different from ordinary exhaustion.

It can produce highly nonlinear failure even when the initial disturbance is small.

---

## 15. Regime archetypes

MFSM does not reduce the state to bullish or bearish. It distinguishes structural regimes.

### 15.1 Healthy expansion

Typical pattern:

- T high;
- external confirmation strong;
- the relevant \(R_{k,t}^+\) channels replenishing;
- H high;
- R_minus deep;
- functional diversity adequate;
- counterforces operating on comparable timescales;
- low threshold convexity.

Interpretation:

The trend is strong and the process sustaining it is still structurally resilient.

### 15.2 Exhausting trend

Typical pattern:

- T remains high;
- one or more previously active \(R_{k,t}^+\) channels fall;
- H remains healthy;
- R_minus remains adequate;
- no large forced-action thresholds nearby.

Interpretation:

Continuation capacity is deteriorating, but catastrophic reversal is not implied.

### 15.3 Fragile acceleration

Typical pattern:

- T rises;
- endogenous amplification rises;
- leverage or threshold exposure rises;
- H falls;
- R_minus falls;
- functional diversity falls;
- propagation potential rises;
- amplification becomes faster relative to restraint;
- S_end grows relative to S_ext.

Interpretation:

The trend can continue aggressively while the consequence of a **specified adverse intervention** rises and/or the susceptibility curve steepens.

This is a central MFSM state because strong price action can coexist with high shock-conditioned consequence or high structural susceptibility. Context-free "fragility is high" language should be avoided.

### 15.4 Forced unwind

Typical pattern:

- threshold has been crossed;
- forced behavior dominates discretionary behavior;
- previously stabilizing balance sheets become sources of flow;
- the feedback loop changes sign;
- R_minus becomes critical;
- network links transmit losses.

Interpretation:

The system is no longer merely pricing information. Balance-sheet mechanics and constraints may dominate marginal price formation.

---

## 16. The current dangerous-state signature

MFSM intentionally does not define a universal scalar fragility score.

A state deserving close attention often combines:

- strong endogenous amplification;
- high nonlinear leverage / threshold exposure;
- falling financing or collateral headroom;
- falling opposing absorptive capacity;
- rising economically operative connectivity;
- falling functional diversity;
- large gain-delay or timescale separation;
- increasing dependence on endogenous rather than external confirmation.

Symbolically, as a qualitative pattern only:

A up,
L up,
H down,
R_minus down,
C up,
D down,
Theta or Phi up,
S_end / S_ext up.

This is not a deterministic crash condition.

It is a structural vulnerability configuration whose predictive value must be tested.

---

## 17. Why a scalar fragility score is currently rejected

A weighted sum such as:

F_score = w1 A + w2 C - w3 D - w4 H + ...

is currently unjustified.

Reasons:

1. several variables are non-monotonic;
2. interaction effects are likely stronger than additive effects;
3. the same connectivity can stabilize small shocks and amplify large ones;
4. low capacity in a relevant \(R_{k,t}^+\) channel can reduce continuation without increasing crash severity;
5. low H and low R_minus have different implications;
6. delay interacts with gain rather than operating independently;
7. thresholds create discontinuities;
8. regimes differ across asset classes and institutional structures;
9. estimated variables are often latent and noisy;
10. rare-event validation creates severe overfitting risk.

The first empirical goal is not to optimize a score. It is to estimate whether theoretically predicted interactions exist.

A further reason a scalar score is inadequate is that robustness is disturbance-specific. A system can be highly robust to one shock direction and highly vulnerable to another.

### 17.1 Counterfactual path law and response functionals

The fundamental response target is the conditional path law

\[
\boxed{
\mathcal P_{t,h}^{\delta}
=
\mathcal L
\left(
\mathbf Z_{[t,t+h]}^{\delta}
\mid
\mathcal I_t
\right).
}
\]

It asks:

> Given the current structural state and this fully specified intervention, what paths can the system follow, with what probabilities, what becomes forced, what stabilizing capacity can arrive in time, and where can the disturbance propagate?

Useful empirical targets are projections of this law rather than an unrestricted nonparametric estimate of the entire distribution. Examples include

\[
\Pr(\tau_{\mathrm{hit}}\le h),
\qquad
\mathbb E[\mathrm{MAE}_{0:h}],
\qquad
\mathbb E[S_{\mathrm{cascade}}],
\qquad
ES_{\alpha}(\ell),
\qquad
\Pr(\tau_{\mathrm{recovery}}\le h).
\]

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
],
\]

which is only one summary of the path law.

A distribution of pathwise individual counterfactual differences \(\mathbf Z^{\delta}-\mathbf Z^0\) requires a structural coupling of the two potential paths, not merely their marginal laws. MFSM should state that coupling when such distributional differences are used.

Absolute stressed consequence is then defined through a loss-oriented path functional and a risk / severity functional:

\[
F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)
=
\rho_{\mathcal P_{t,h}^{\delta}}
\left[
\ell_{\mathrm{abs}}(\mathbf Z_{[t,t+h]}^{\delta})
\right].
\]

Incremental causal consequence requires a two-path loss and an explicit joint counterfactual coupling.

Identification remains a separate problem. Estimation requires an explicit structural model, natural experiment, instrument, simulation calibrated to defensible mechanisms, or another justified design.

---

## 18. Mathematical template

This section is intentionally a compact bridge. Exact derivations, assumptions, stability boundaries, distributed-memory results, non-normal transient amplification, stochastic recovery mathematics, threshold/hybrid dynamics, and Physarum adaptive-network equations are preserved in `Mathematical_Foundations.md`.

A general continuous-time conceptual representation uses the **closed augmented state** \(\mathbf Z_t\):

### 18.1 Closed state dynamics

\[
d\mathbf Z_t
=
\mathbf f_{\mathcal G}
\left(
\mathbf Z_t,
\mathbb E_t[\mathbf Z_{t+h_e}]
\right)dt
+
\Sigma(\mathbf Z_t,t)d\boldsymbol\beta_t,
\]

where \(\boldsymbol\beta_t\) is Brownian motion and \(h_e\) is an expectation horizon.

Capacities, buffers, control states, and discrete regimes that evolve independently are coordinates of \(\mathbf Z_t\), not hidden side states.

### 18.2 Capacity components

If \(\mathbf r_t\) denotes the capacity coordinates of \(\mathbf Z_t\), an application may write

\[
\dot{\mathbf r}_t
=
\mathbf s(\mathbf r_t)
-
\mathbf c(\mathbf Z_t,\mathbf r_t),
\]

to separate replenishment from consumption. Relevant projections include mechanism-specific \(R^+\), headroom \(H\), and disturbance-conditioned \(R^-_t(h;\delta)\).

### 18.3 Delayed response

If \(\mathbf u_t\) is a control / counterflow coordinate inside \(\mathbf Z_t\), its dynamics may depend on

\[
\int_0^\infty K(s)\mathbf Z_{t-s}\,ds
\quad\text{and}\quad
\mathbb E_t[\mathbf Z_{t+h_e}],
\]

allowing fixed delays, distributed memory, anticipation, policy response, and strategic response.

### 18.4 Network propagation

A specified propagation law may use \(W_t\), but \(W_t\) is not itself a generic risk score. If the network evolves endogenously in a way required to predict the future, its evolving coordinates must be included in \(\mathbf Z_t\) or given an explicit law that closes the augmented state.

### 18.5 Local analysis

Linearize the closed augmented system around the current state.

Then determine whether the dominant mode implies:

- stable decay;
- damped oscillation;
- transient amplification;
- oscillatory instability;
- monotonic instability;
- or no local instability despite vulnerability to large shocks.

Nonlinear basin analysis and explicit threshold constraints are needed for large disturbances.

---

## 19. Critical slowing down: optional diagnostic, not model core

Critical slowing down (CSD) should not be treated as a privileged crash detector.

In a locally stationary Ornstein-Uhlenbeck approximation:

dZ = -kappa Z dt + sigma dW,

smaller kappa implies slower recovery and, holding sigma fixed, greater variance and persistence.

This provides a legitimate theoretical basis for some early-warning indicators.

However:

- variance can rise because noise strength rises;
- autocorrelation depends on noise color and sampling;
- oscillatory instabilities do not necessarily produce monotonic lag-one autocorrelation;
- a system can be locally resilient but vulnerable to a large shock;
- noise-induced escape may occur without local stability loss;
- rapid parameter change can cause tipping without classic CSD;
- retrospective crash selection can create prosecutor's-fallacy bias;
- empirical financial evidence is mixed across major crises.

Therefore CSD measures are optional candidates that must compete against leverage, collateral, liquidity, network, and credit variables in out-of-sample tests.

---

## 20. Self-organized criticality: separate hypothesis

Self-organized criticality (SOC) is not synonymous with:

- delayed negative feedback;
- critical slowing down;
- leverage cycles;
- oscillation;
- generic heavy tails;
- clustered volatility.

A finance-specific SOC claim requires evidence about:

- driving;
- redistribution;
- dissipation;
- threshold dynamics;
- scale behavior;
- competing stochastic explanations.

MFSM does not assume markets are self-organized critical systems.

---

## 21. Cross-domain analogies retained as discovery tools

The following analogies remain useful only at the level specified.

### 21.1 Ant pheromone systems

Useful transfer:

- decentralized reinforcement;
- signal persistence requiring continued reinforcement;
- interaction of public and private information;
- decay of stale coordinating signals.

Financial question:

How much of current continuation depends on a signal whose behavioral influence would decay without repeated confirmation?

Do not infer that price itself should decay like pheromone.

### 21.2 Physarum adaptive networks

Useful transfer:

- flow-dependent capacity adaptation;
- reinforcement of useful routes;
- pruning of underused routes;
- efficiency / cost / robustness tradeoffs.

Financial use:

- adaptive liquidity routing;
- network capacity allocation;
- capital routing.

Do not use Physarum as an analogy for strategic valuation or speculative expectations.

### 21.3 Quorum sensing

Useful transfer:

- thresholds;
- bistability;
- hysteresis;
- coordinated state switching.

Financial use:

- bank-run-like coordination;
- synchronized strategy shifts;
- collateral regime transitions.

Do not equate quorum sensing with a short squeeze.

### 21.4 Neuronal refractoriness

Useful transfer:

activation -> reduced immediate reactivation capacity.

Financial use:

- deployed risk budget;
- limited incremental capacity;
- recovery time of balance sheets.

Do not claim liquidated traders are literally refractory neurons or that neuronal refractory periods explain market crashes.

### 21.5 Incoherent feed-forward and delayed antagonism

Useful transfer:

one state can produce fast reinforcing effects and slower opposing effects.

Financial use:

- valuation shock -> immediate buying plus later issuance;
- price move -> immediate trend flow plus delayed supply or hedging.

Important distinction:

feed-forward antagonism and delayed feedback are not the same topology.

### 21.6 Reaction-diffusion and local-vs-global containment

Useful transfer:

local reinforcement and damping can operate over different propagation ranges.

Financial use:

- local speculation versus systemic propagation through network exposures.

Do not map physical diffusion coefficients literally to correlations.

### 21.7 Chemical potential and arbitrage

Useful transfer:

state discrepancies can generate flows that tend to reduce discrepancies.

Financial use:

- arbitrage and gradient-reducing flow.

Do not equate financial price with chemical potential or a constant-product AMM invariant with a chemical equilibrium constant.

---

## 22. Claims explicitly rejected or downgraded

The following statements should not be used as canonical MFSM claims.

1. "Nature solved instability."
   Rejected. Natural systems fail, collapse, overshoot, and go extinct.

2. "Nature prevents crashes by refusing bailouts."
   Rejected. Biological systems use repair, buffering, redundancy, isolation, and sacrifice at different scales.

3. "Higher connectivity always increases fragility."
   Rejected. Network effects are state- and shock-size-dependent.

4. "A long delay is inherently dangerous."
   Rejected. Delay matters jointly with gain, damping, saturation, topology, and memory shape.

5. "Crossing a delay threshold guarantees chaotic collapse."
   Rejected. Different systems lose stability through different bifurcations or thresholds; nonlinear terms determine subsequent dynamics.

6. "Critical slowing down universally warns of crashes."
   Rejected. Evidence is conditional and mixed.

7. "Concave price impact proves market saturation."
   Rejected. Execution impact is not the same as response to standardized information.

8. "Low market cash means buying capacity is exhausted."
   Rejected. Effective capacity depends on collateral, equity, mandates, funding, willingness, eligibility, and deadlines.

9. "Functional diversity equals number of participants."
   Rejected. Reaction functions matter more than labels.

10. "AMM x*y=k is structurally identical to chemical equilibrium."
    Rejected.

11. "Refractory periods are equivalent to liquidation."
    Rejected beyond the narrow capacity analogy.

12. "A biological analogy is evidence of alpha."
    Rejected categorically.

---

## 23. Core empirically testable hypotheses

The framework becomes useful only if its hypotheses can fail.

### H1. Capacity interaction

For comparable external shocks, pre-existing leverage, short funding maturity, and low usable collateral headroom should predict more forced selling and larger temporary deviations.

Key point:

Test interactions, not just additive correlations.

Potential confounders:

- asset risk;
- adverse selection;
- anticipated shocks;
- voluntary exposure reduction.

### H2. Overlap transmission

Unexpected redemptions or forced sales by one holder should create greater pressure on other holders and assets in proportion to predetermined exposure overlap and inverse depth.

Evidence should include:

- subsequent reversal where temporary pressure is hypothesized;
- negative controls using non-overlapping assets;
- controls for common fundamental news.

### H3. Delay mismatch

Conditional on total resources, a longer mobilization time for collateral or capital relative to the deadline for forced action should predict greater forced liquidation.

Important variable:

mobilization time / margin or settlement deadline.

### H4. Functional diversity

Conditional on gross holdings, systems with more diverse funding sources, reaction rules, horizons, and liabilities should show less synchronized forced selling after common shocks.

Counting investors or strategy labels is not sufficient.

### H5. External versus endogenous confirmation

Trends increasingly dominated by return-induced or mechanically induced flows should behave differently from equally strong trends continually validated by independent fundamental information.

Candidate outcome:

higher reversal probability after endogenous reinforcement stops.

### H6. Saturation distinction

Repeated independent positive information shocks may show diminishing conditional price response in states of extreme positioning or depleted mechanism-specific continuation capacity.

This must control for:

- surprise magnitude;
- prior expectations;
- liquidity;
- volatility;
- positioning;
- information composition.

Diminishing response alone does not imply an imminent reversal.

### H7. Incremental warning value

A prespecified MFSM implementation must improve out-of-sample calibration or decision value beyond strong baselines such as:

- momentum;
- volatility;
- leverage;
- valuation;
- credit gaps;
- debt-service ratios;
- liquidity measures;
- standard positioning measures.

If it does not, the framework may remain explanatory but should not be claimed as a predictive edge.

---

## 24. Empirical design principles

The durable finance-side literature map, mechanism-to-variable mapping, candidate proxies, and minimum evidence standard are maintained in `Empirical_Finance_Foundations.md`.

Any serious implementation should follow these rules.

### 24.1 Prespecify definitions

Do not redefine variables after seeing crashes.

Lock:

- regime labels;
- horizon definitions;
- thresholds;
- proxy definitions;
- training windows;
- evaluation metrics.

### 24.2 Use real-time data where possible

Avoid revised macro data or information unavailable at the decision time.

### 24.3 Distinguish endogenous from exogenous transitions

A protocol exploit, war, surprise policy announcement, natural disaster, or fraud revelation may cause a discontinuous jump with no preceding endogenous deterioration.

MFSM should not be judged as a failed endogenous-state model because it did not predict a genuinely exogenous event.

### 24.4 Evaluate rare events honestly

Use:

- precision-recall;
- calibration;
- false-alarm rates;
- event-level holdouts;
- country or asset holdouts;
- economic loss functions;
- not ROC alone.

Avoid treating many observations from one crisis as independent crises.

### 24.5 Compare against strong baselines

A theoretically elegant variable has no practical status until it beats simpler alternatives.

### 24.6 Prefer mechanism identification over chart resemblance

A similar-looking time series is not evidence of structural equivalence.

Require:

actors -> states -> flows -> constraints -> delays -> failure mode.

---

## 25. Application protocol for any market or asset

When applying MFSM, use the following sequence.

### Step 1: Define the system boundary

Specify:

- asset or market;
- participant set;
- time horizon;
- funding system;
- relevant derivative markets;
- key external fundamentals.

### Step 2: Define the disturbance class, intervention, and horizon

First specify the disturbance class \(c\), such as funding withdrawal, margin increase, redemption, collateral haircut, volatility shock, supply shock, or policy shock.

Then define the descriptor

\[
\delta=(c,V,a,d,t_0,p,\nu)
\]

and the structural intervention operator

\[
\mathfrak I_{\delta}:(\mu_t,\mathcal G)\mapsto(\mu_t^{\delta},\mathcal G^{\delta}).
\]

Record:

- intervention target \(V\);
- exact structural rule modified;
- amplitude \(a\) and units / normalization;
- direction \(d\);
- onset \(t_0\);
- temporal profile / duration \(p(s)\);
- stochastic component \(\nu\), if any, and its law/coupling;
- horizon \(h\).

A label such as "coordination run" can remain a friendly class name, but the intervention must act on a causally upstream variable such as withdrawal demand, rollover availability, or a common signal. Do not intervene on the endogenous outcome itself.

Do not analyze structural susceptibility without specifying the disturbance family and amplitude convention being varied.

### Step 3: Identify external drivers

What new information or fundamental state is entering the system?

Estimate \(S^{ext}\).

### Step 4: Identify endogenous reinforcing loops

For each suspected loop, write it causally.

Example:

return -> inflow -> market impact -> return.

Do not call momentum itself a feedback mechanism without identifying the behavior that closes the loop.

### Step 5: Estimate or proxy mechanism-specific continuation capacity \(R_{k,t}^+\)

Which identified mechanism \(k\) can still add same-direction pressure?

What constrains that mechanism's capacity?

Is that capacity replenishing or being consumed?

Do not aggregate distinct continuation channels into one \(R^+\) scalar unless the aggregation rule is prespecified and economically justified.

### Step 6: Estimate headroom \(H\), local constraint sensitivity, and finite-shock buffer response

Where do voluntary decisions become forced decisions?

For local analysis, estimate the Jacobian

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

If the specified intervention acts **only through an instantaneous initial-state displacement**, identify \(\mathbf v_{\delta}\) and use the projection

\[
\mathbf\Chi_{B,t}(h)\mathbf v_{\delta}.
\]

For interventions on parameters, rules, constraints, kernels, or temporal forcings, use the direct intervention derivative where justified. For finite shocks, especially near thresholds, prefer

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

Identify:

- margins;
- liquidation levels;
- collateral haircuts;
- risk limits;
- funding deadlines;
- mandate constraints.

### Step 7: Estimate opposing capacity \(R^-_t(h;\delta)\)

Who can take the other side under **this specified disturbance** by the relevant horizon?

Distinguish quoted liquidity from committed risk-bearing capacity, eventual capital from capital that can arrive before forced-action deadlines, and realized absorption from prospective willingness to absorb.

### Step 8: Identify opposing mechanisms and controller topology

What does the current state induce later?

Examples:

- issuance;
- producer supply;
- arbitrage;
- hedging;
- substitution;
- policy;
- capital raising.

Classify the topology where possible:

\[
\mathcal C_N
\in
\{
\text{feed-forward},
\text{feedback},
\text{integral},
\text{depletion},
\text{saturation},
\text{threshold}
\}.
\]

### Step 9: Measure response-time structure K and Theta

How fast does reinforcement operate?

How fast can constraints, buffers, and opposing capital respond?

Is the response a fixed delay, a broad distribution, or immediate state-dependent action?

### Step 10: Map \(W\) and derive \(C\) only from a specified propagation law

What links transmit disturbances?

Examples:

- common holdings;
- common lenders;
- collateral;
- derivatives;
- benchmarks;
- shared market makers.

Do not treat \(C\) as an independent primitive or substitute raw correlation for \(W\).

### Step 11: Estimate functional diversity \(D\) and strategic complementarity \(\Gamma\)

How differently will important participants react to the same shock?

Is \(D_t\) changing because successful strategies are attracting capital or reaction rules are converging?

Do participant actions become more individually attractive when others take the same action?

\[
\Gamma_t
\sim
\frac{\partial a_i^*}{\partial \bar a_{-i}}.
\]

### Step 12: Map threshold geometry; derive \(L\) only if useful

Which state changes can force discrete behavior?

Record the switching surfaces and distances first. Use \(L\) only as a prespecified summary that adds information beyond \(H\), \(\mathbf\Chi_B\), and the threshold map.

### Step 13: Derive the prospective termination mechanism \(M^{term}\)

Using only information available before the realized path, classify or assign probabilities among:

- fuel exhaustion;
- delayed counterflow;
- gain saturation;
- threshold unwind;
- or explicitly state that no dominant termination mechanism is identified.

### Step 14: Define loss orientation and severity functional

Specify the absolute stressed loss \(\ell_{\mathrm{abs}}\) so that **larger means worse**, for example:

- maximum drawdown;
- liquidation-threshold crossing;
- cascade notional;
- order-book impairment;
- stablecoin depeg;
- failure to recover by horizon \(h\).

Then specify how uncertainty is summarized through \(\rho\), such as expectation, exceedance probability, quantile, or expected shortfall.

If incremental causal harm is required, define a separate two-path loss \(\ell_{\Delta}(\mathbf Z^{\delta},\mathbf Z^0)\) and state the counterfactual coupling.

### Step 15: Report consequence and structural susceptibility separately

For trend applications, report \(T\) and \(U\) separately.

Report the absolute stressed consequence

\[
F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)
\]

for the specified intervention operator.

Then, where the task is structural susceptibility rather than scenario consequence, vary disturbance amplitude within the class \(c\) using fixed economic units or a prespecified normalization \(\tilde a\), and report the response curve, normalized local slope, or critical amplitude \(a_q^*\).

Never convert "strong" directly into "safe", and never compare susceptibility slopes produced under incompatible shock parameterizations.

### Step 16: State missing information, measurement assumptions, and falsifiers

For every strong conclusion, state what observation would weaken or reverse it. Distinguish latent quantities from their proxies and record model/kernel choices that could change the estimate.

---

## 26. Recommended output schema for an LLM using MFSM

When another LLM applies this model, it should return something structurally similar to:

### System boundary
- Market:
- Relevant participants:
- Funding / derivatives context:

### Disturbance definition
- Disturbance class \(c\):
- Structural target \(V\):
- Amplitude \(a\):
- Direction \(d\):
- Onset \(t_0\):
- Temporal profile \(p(s)\):
- Stochastic component \(\nu\), if any:
- Horizon \(h\):
- Observed / hypothetical:


### External confirmation S_ext
- Current evidence:
- Confidence:

### Endogenous reinforcement
- Loop 1:
- Loop 2:
- Estimated strength / uncertainty:

### Capacities
- mechanism-specific \(R^+\):
- \(H\):
- local initial-state \(\mathbf\Chi_B\):
- direct intervention sensitivity, if identified:
- finite-shock \(\Delta\mathbf B^{\delta}\):
- \(R^-_t(h;\delta)\):

### Counterforces and timing
- \(N\): endogenous counterflow / antagonism
- controller topology \(\mathcal C_N\):
- \(K(s)\) or qualitative delay distribution:
- \(\Theta\) / \(\Phi\) interpretation:

### Network
- \(W\) channels:
- specified propagation law:
- derived \(C\) / propagation potential:

### Functional diversity and coordination
- \(D_t\):
- Is \(D_t\) rising or falling?
- Strategic complementarity \(\Gamma_t\):

### Threshold geometry
- switching surfaces / distances:
- optional derived \(L\), if nonredundant:

### Signal-source balance
- S_ext:
- S_end:
- Qualitative E = S_end / S_ext:

### Derived termination mechanism
- Prospective \(M^{term}\) probabilities / classification:
- Alternatives:
- Information timestamp used:

### Path-response targets
- Mean causal response \(\mathbf m_t^{\delta}(s)\):
- Threshold-hit probability:
- Maximum adverse excursion / maximum stress:
- Cascade-size functional:
- Recovery probability / recovery-time functional:

### Loss and severity definition
- Absolute loss-oriented path functional \(\ell_{\mathrm{abs}}\):
- Risk / severity functional \(\rho\):
- Incremental two-path loss \(\ell_{\Delta}\), if used:
- Counterfactual coupling assumption, if used:

### State outputs
- \(T\): trend strength, if a trend is present
- \(U\): trend sustainability, if a trend is present
- \(F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)\): absolute stressed consequence
- Incremental causal consequence, if identified:
- Susceptibility profile versus standardized amplitude \(\tilde a\), if required
- Critical amplitude \(a_q^*\), if identified

### Shock-response path
- Expected sequence after \(\delta\):
- What becomes forced?
- What can absorb the shock before horizon \(h\)?
- Where can it propagate?

### Observation and identification
- Latent quantities:
- Observed proxies:
- Candidate measurement model(s):
- Identification status:
- Closest observationally equivalent alternative:
- Kernel / measurement assumptions:
- Main measurement risks:

### Dominant feedback mode
- Stable decay / damped oscillation / transient amplification / threshold risk / other:

### Missing data
- ...

### Falsifiers
- ...

### Epistemic status
- Established mechanism:
- Structural analogy:
- Empirical support:
- Speculative component:

---

## 27. Rules for extending the framework

These gates are summarized here; the mandatory operational workflow, evidence labels, stop conditions, versioning rules, and future-LLM output schema are maintained in `Research_Protocol.md`.

Any proposed new variable or analogy must pass the following gate.

### Gate 1: Causal necessity

What specific mechanism is missing from the existing model?

If the proposal merely renames an existing variable, do not add it.

### Gate 2: Domain-neutral structure

Describe the mechanism without biological, financial, or domain-specific vocabulary.

### Gate 3: Explicit mapping

Identify:

- actors;
- state variables;
- flow;
- amplifier;
- limiter;
- delay;
- threshold;
- propagation path;
- failure mode.

### Gate 4: Analogy boundary

State exactly where the source-domain analogy stops working.

### Gate 5: Financial counterpart

Show that finance contains an independently meaningful causal node, not merely similar language.

### Gate 6: Measurement

Propose an observable proxy or state-estimation method.

### Gate 7: Falsifiability

State what empirical result would weaken or reject the proposed mechanism.

### Gate 8: Incremental value

Explain what the new component contributes beyond existing variables and literature.

---

## 28. Known weaknesses and unresolved problems

### 28.1 Reflexivity and strategic anticipation

Financial agents model the future and each other.

An anticipated counterforce can act before its mechanical delay.

Policy expectations, bailout beliefs, front-running, and strategic positioning can change effective coefficients in real time.

This makes finance different from many physical systems.

### 28.2 Latent-state measurement

The most important variables are often not directly observable:

- mechanism-specific remaining continuation capacity;
- true collateral headroom;
- counterparty constraints;
- functional reaction rules;
- opposing absorptive capacity.

Proxies may be noisy or biased.

### 28.3 Endogeneity

Price, flow, volatility, leverage, and liquidity often determine one another simultaneously.

Correlation does not identify loop gain.

### 28.4 Nonstationarity

Rules, regulation, market structure, participants, leverage products, and technology change.

A stable historical parameter may not remain stable.

### 28.5 Scale dependence

A mechanism can stabilize one level while destabilizing another.

Examples:

- a stop-loss can protect one trader but synchronize many traders;
- a central counterparty can reduce bilateral risk while concentrating systemic dependence;
- diversification can reduce small idiosyncratic shocks while increasing common exposure.

### 28.6 Exogenous shocks

No endogenous vulnerability framework can predict genuinely unpredictable external jumps.

The model should separate vulnerability from trigger prediction.

### 28.7 Rare-event overfitting

Crashes are few, heterogeneous, and often clustered.

A flexible model can explain history after the fact without genuine forecasting value.

### 28.8 Analogy seduction

Natural analogies are cognitively powerful and therefore dangerous.

They can make weak financial mappings feel inevitable.

Every analogy must be subordinated to explicit causal structure and financial evidence.

### 28.9 Goodhart effects

If a diagnostic becomes widely used, participants may adapt to it.

Market state variables are not passive measurements when agents respond strategically to the measurement itself.

### 28.10 Aggregation problems

A market-level variable can hide offsetting participant-level states.

For example, average collateral headroom can look healthy while a systemically important subset is near forced liquidation.

---

## 29. What would count as success

MFSM should be considered practically useful only if a prespecified implementation can do at least one of the following out of sample:

1. discriminate materially different path responses to prespecified structural intervention operators using calibrated functionals of \(\mathcal P_{t,h}^{\delta}\);
2. estimate absolute stressed consequence \(F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)\) with useful calibration for prespecified loss and severity definitions;
3. distinguish structural susceptibility across otherwise comparable states through standardized amplitude-response curves or critical disturbance amplitudes;
4. distinguish continuation from quiet exhaustion better than ordinary momentum and valuation measures;
5. identify when similarly strong trends have materially different intervention-conditioned outcomes;
6. improve prediction of forced-liquidation or fire-sale episodes using headroom, local constraint sensitivity, finite-shock buffer response, and capacity interactions;
7. identify propagation risk beyond raw correlation using exposure topology;
8. separate flow-driven temporary price pressure from information-driven permanent repricing;
9. identify run-like or coordination vulnerability not captured by trend variables alone;
10. improve calibration of transition hazards without unacceptable false-alarm rates;
11. remain materially robust to a **prespecified finite set** of reasonable alternative measurement models, kernels, proxy definitions, and intervention specifications;
12. add information beyond a flexible nonlinear baseline using the same raw information set.

The framework does not need to predict exact tops to be useful.

Structural state and shock-response diagnosis are the primary objectives.

---

## 30. What would falsify or materially weaken the framework

The framework should be downgraded if, after careful implementation:

- its variables add no out-of-sample information beyond standard leverage, liquidity, momentum, valuation, volatility, and credit indicators;
- estimated interaction effects are unstable across samples and cannot be tied to institutional differences;
- latent-state proxies prove too noisy to identify the intended mechanisms;
- the same outcomes are explained equally well by simpler models;
- regime labels require hindsight to work;
- the framework repeatedly predicts high stressed consequence or susceptibility for healthy states without decision value;
- purported feedback loops disappear under causal identification;
- cross-domain concepts fail to produce any measurable variable or testable financial implication.

An explanatory vocabulary without incremental empirical value should not be presented as a market edge.

---

## 31. Research priorities

The current highest-value research directions are:

### Priority 1: Counterfactual path-response estimation

Estimate decision-relevant functionals of \(\mathcal P_{t,h}^{\delta}\) for prespecified intervention operators rather than relying on terminal expected-state response alone.

Priority targets include threshold-hit probability, maximum adverse excursion, cascade size, tail loss, and recovery probability.

### Priority 2: Consequence-versus-susceptibility separation

Estimate amplitude-response curves

\[
\tilde a\mapsto F_t^{\mathrm{abs}}(\delta(c,\tilde a),h;\ell_{\mathrm{abs}},\rho)
\]

and critical disturbance amplitudes where possible. Test whether these susceptibility measures add information beyond consequence under one arbitrarily chosen shock.

### Priority 3: Headroom x constraint sensitivity x amplification

Test whether strong same-direction feedback becomes especially dangerous when current headroom is low **and/or** a small state change rapidly destroys future headroom. Compare local \(\mathbf\Chi_{B,t}\) with finite-shock \(\Delta\mathbf B_t^{\delta}\).

### Priority 4: Horizon- and disturbance-dependent opposing capacity

Estimate \(R^-_t(h;\delta)\): who can actually absorb forced flow under the specified disturbance by the relevant deadline, not merely who may eventually find the asset attractive.

### Priority 5: Delay and deadline mismatch

Measure mobilization time of buffers and stabilizing capital relative to forced-action deadlines.

### Priority 6: Strategic complementarity and dynamic diversity

Test whether run-like coordination and performance-driven convergence of reaction functions add explanatory value beyond ordinary crowding and positioning measures.

### Priority 7: Functional synchronization x connectivity

Test whether common reaction functions become dangerous primarily when the network can transmit their common behavior and opposing capacity is limited.

### Priority 8: External vs endogenous confirmation

Develop credible decomposition of fundamental information, return-induced flows, and mechanical impact.

### Priority 9: Termination-mechanism and controller-topology classification

Determine whether fuel exhaustion, delayed counterflow, saturation, threshold unwind, feed-forward opposition, feedback, and other controller structures can be empirically distinguished.

### Priority 10: State-dependent response matrix

Move from a verbal checklist toward estimated local dynamics.

### Priority 11: Measurement-model robustness

Stress-test estimated amplification, crowding, criticality, and network state against plausible kernels, regime definitions, sampling choices, and proxy constructions.

---

## 32. Canonical interpretation for future LLMs

When loading this file, treat the following as authoritative for the current version of MFSM:

1. MFSM is a market-state and feedback-dynamics framework, not a directional trading rule.
2. The central object is the evolving **structural response architecture**, not price alone and not trend alone.
3. Trend Strength \(T\) and Trend Sustainability \(U\) are trend-specific outputs. Absolute stressed consequence is \(F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)\); incremental causal consequence requires a two-path loss and coupling assumption; structural susceptibility is a response profile across disturbance amplitude.
4. Distinguish a disturbance class, the descriptor \(\delta=(c,V,a,d,t_0,p,\nu)\), and the full intervention operator \(\mathfrak I_{\delta}:(\mu_t,\mathcal G)\mapsto(\mu_t^{\delta},\mathcal G^{\delta})\). Do not place an endogenous outcome such as a run or cascade directly inside \(do(\cdot)\).
5. The fundamental theoretical response object is the conditional counterfactual path law \(\mathcal P_{t,h}^{\delta}\). Mean response is only one projection of that law.
6. The mechanism-indexed family \(\{R_{k,t}^+\}_k\), \(H\), and \(R^-\) must never be collapsed into a generic resource variable without explicit justification; \(R^+\) alone is only a category label.
7. Opposing absorptive capacity should be horizon- and disturbance-qualified as \(R^-_t(h;\delta)\) when timing or shock type matters.
8. Current headroom, the local initial-state constraint-sensitivity Jacobian \(\mathbf\Chi_{B,t}\), the direct intervention derivative, and the finite-shock buffer response \(\Delta\mathbf B_t^{\delta}\) are distinct.
9. Delay must be interpreted jointly with gain and response timescale; prefer a kernel or distribution when data allow.
10. Connectivity is not monotonically destabilizing; use explicit propagation mechanisms.
11. Functional diversity means diversity of reaction functions, not participant count, and \(D_t\) can evolve endogenously through strategy performance and capital flows.
12. Separate external confirmation from endogenous market-generated reinforcement.
13. Allow strategic complementarity / coordination vulnerability through \(Q_t\) or \(\Gamma_t\); run-like vulnerability need not be preceded by a trend.
14. Distinguish fuel exhaustion, delayed counterflow, gain saturation, and threshold unwind as different termination mechanisms; \(M_t^{term}\) is a derived prospective classification, not a primitive state variable.
15. Distinguish controller topology: feed-forward opposition, feedback, integral control, depletion, saturation, and threshold switching are not interchangeable.
16. Treat measured indicators as observations of latent state, not as the state itself; distinguish the true observation mechanism from the analyst's candidate measurement model and state identification status.
17. Do not build a scalar universal fragility score. Losses used in severity objects must be loss-oriented, and absolute stressed consequence must be separated from incremental causal consequence.
18. Biological and physical analogies generate hypotheses; they do not validate financial predictions.
19. Any extension must specify mechanism, mapping, measurement, falsifier, and incremental value.
20. Prefer out-of-sample state and path-response diagnosis over retrospective crash storytelling.

---

## 33. Compact canonical statement

The entire framework can be compressed to the following:

> A financial market is a state-dependent response system. Its current **closed augmented state** determines how new disturbances are amplified, damped, delayed, transmitted, or converted into forced behavior. Price trends are one state-transforming process among several: coordination runs, collateral feedback, funding stress, strategy imitation, and network spillovers can also rewrite the response law. MFSM therefore requires a structural intervention operator, evaluates that intervention through a conditional counterfactual path law, derives decision-relevant path functionals from that law, separates absolute stressed consequence from incremental causal consequence, and treats structural susceptibility as the change in loss-oriented consequence as a standardized intervention amplitude varies. The relevant state includes same-direction capacity, financing and collateral headroom, horizon- and disturbance-dependent opposing absorptive capacity, local and finite-shock buffer response, delayed or distributed counterforces, participant reaction diversity, strategic complementarity, network propagation, and threshold geometry. The same market can be robust to one disturbance and vulnerable to another.

The deepest operating question is:

> **How is the current structural state changing the system's response law for the next disturbance?**

---

## 34. Source foundations and reading list

The following works are especially relevant to the current framework.

### Financial feedback, leverage, liquidity, and contagion

- Markus Brunnermeier and Lasse Pedersen, "Market Liquidity and Funding Liquidity." Working paper version: https://www.princeton.edu/~markus/research/papers/Mkt_Fun_Liquidity.pdf
- Tobias Adrian and Hyun Song Shin, "Liquidity and Leverage." Federal Reserve Bank of New York Staff Report: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr328.pdf
- Jon Danielsson, Hyun Song Shin, and Jean-Pierre Zigrand, "Risk Appetite and Endogenous Risk." https://conference.nber.org/confer/2009/QSRconf/riskappetite.pdf
- Joshua Coval and Erik Stafford, "Asset Fire Sales (and Purchases) in Equity Markets." https://www.newyorkfed.org/medialibrary/media/research/conference/2005/liquidity/Coval_Stafford.pdf
- Robin Greenwood, Augustin Landier, and David Thesmar, "Vulnerable Banks." https://www.hbs.edu/ris/Publication%20Files/vulnerable%20banks%20jfe_6542a41e-b149-44b9-b1bf-599613e6e12d.pdf
- Amir Khandani and Andrew Lo, "What Happened to the Quants in August 2007?" https://web.mit.edu/Alo/www/Papers/august07.pdf
- Kent Daniel and Tobias Moskowitz, "Momentum Crashes." https://www.kentdaniel.net/papers/published/mom12.pdf
- Daron Acemoglu, Asuman Ozdaglar, and Alireza Tahbaz-Salehi, "Systemic Risk and Stability in Financial Networks." https://economics.mit.edu/sites/default/files/publications/Systemic%20Risk%20and%20Stability%20in%20Financial%20Networks..pdf
- Marco Bardoscia et al., "Pathways towards Instability in Financial Networks." https://www.nature.com/articles/ncomms14416

### Price impact and flow persistence

- Bence Toth et al., "Anomalous Price Impact and the Critical Nature of Liquidity in Financial Markets." https://www.cfm.com/wp-content/uploads/2022/12/76-2011-anomalous-price-impact-and-the-critical-nature-of-liquidity-in-financial-markets.pdf
- Fabrizio Bucci et al., "Slow Decay of Impact in Equity Markets." https://www.cfm.com/wp-content/uploads/2022/12/247-Slow-decay-of-impact-in-equity-markets.pdf

### Official market-stress evidence

- Bank of England, Financial Stability Report, December 2022, LDI chapter. https://www.bankofengland.co.uk/-/media/boe/files/financial-stability-report/2022/financial-stability-report-december-2022.pdf
- CFTC-SEC, "Findings Regarding the Market Events of May 6, 2010." https://www.sec.gov/news/studies/2010/marketevents-report.pdf
- Mathias Drehmann and James Yetman, work on credit-gap early-warning measures. BIS: https://www.bis.org/publications/working-paper-744-why-you-should-use-hodrick-prescott-filter-least-generate-credit-gaps
- Inaki Aldasoro, Claudio Borio, and Mathias Drehmann, "Early Warning Indicators of Banking Crises: Expanding the Family." BIS: https://www.bis.org/publications/early-warning-indicators-banking-crises-expanding-family_0.pdf
- Michael McLeay, Amar Radia, and Ryland Thomas, "Money Creation in the Modern Economy," Bank of England, 2014.

### Additional finance and control foundations

- Douglas W. Diamond and Philip H. Dybvig, "Bank Runs, Deposit Insurance, and Liquidity," Journal of Political Economy 91(3), 1983, pp. 401-419. The paper supplies the multiple-equilibrium / self-fulfilling run mechanism; MFSM's \(\Gamma_t\) is its own abstraction of coordination dependence. https://www.journals.uchicago.edu/doi/10.1086/261155
- Nobuhiro Kiyotaki and John Moore, "Credit Cycles," 1997: collateral-value feedback and constraint amplification. https://msuweb.montclair.edu/~lebelp/KyotakiMooreCreditCyclesJPE1997.pdf
- Darrell Duffie, slow-moving capital / Presidential Address: horizon-dependent arrival of stabilizing capital. https://web.stanford.edu/~duffie/PresidentialAddressApril15NormalFormat.pdf
- Vladimir Filimonov and Didier Sornette, Hawkes-process criticality diagnostics: measurement and specification risk when inferring endogeneity. https://ideas.repec.org/a/taf/quantf/v15y2015i8p1293-1314.html
- William Brock / Cars Hommes and related heterogeneous-expectations work; source reviewed here: https://papers.tinbergen.nl/15088.pdf
- Bank for International Settlements, crypto carry and leveraged/arbitrage-capacity state: https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf
- Jason Milionis et al., "Loss-Versus-Rebalancing": economics of passive AMM liquidity provision. https://arxiv.org/pdf/2208.06046v2
- Bank of England, "An anatomy of the 2022 gilt market crisis": collateral deadlines, forced selling, and intermediary capacity. https://www.bankofengland.co.uk/working-paper/2023/an-anatomy-of-the-2022-gilt-market-crisis
- Malcolm Baker and Jeffrey Wurgler, market timing and capital structure: valuation-sensitive issuance as delayed supply. https://pages.stern.nyu.edu/~jwurgler/papers/capstruct.pdf
- Hyman Minsky, financing-composition / financial-instability work: https://www.levyinstitute.org/pubs/wp74.pdf
- Uri Alon / Mangan–Alon feed-forward-loop motif work: controller topology and timing. https://www.weizmann.ac.il/mcb/alon/sites/mcb.UriAlon/files/structure_and_function_of_the_feed-forward_loop_network_motif.pdf
- Yi, Huang, Simon, and Doyle, integral feedback in bacterial chemotaxis: https://www.pnas.org/doi/pdf/10.1073/pnas.97.9.4649
- Carlson and Doyle, Highly Optimized Tolerance: robustness can coexist with shock-specific fragility. https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.84.2529/fulltext
- Extended source-by-source audit: `artifacts/source_review_extended_2026-09-22.md`

### Delay, dynamics, and natural-system inspiration

- G. E. Hutchinson, "Circular Causal Systems in Ecology," 1948. https://people.wku.edu/charles.smith/biogeog/HUTC1948.htm
- Michael Elowitz and Stanislas Leibler, "A Synthetic Oscillatory Network of Transcriptional Regulators," Nature, 2000. https://www.nature.com/articles/35002125
- Richard Field and Richard Noyes, Oregonator / chemical oscillation work, 1974.
- Benjamin Schaefer et al., delayed decentralized frequency control in power grids, 2016.
- John Drake and Blaine Griffen, experimental early-warning signals before population collapse, Nature, 2010. https://www.nature.com/articles/nature09389.pdf
- Carl Boettiger and Alan Hastings, "Early Warning Signals and the Prosecutor's Fallacy." https://www.uu.nl/sites/default/files/boettiger_and_hastings_2012_-_fallacy_of_early_warning_signals.pdf
- Per Bak, Chao Tang, and Kurt Wiesenfeld, self-organized criticality, 1987. https://link.aps.org/doi/10.1103/PhysRevLett.59.381
- Kestutis Pyragas, time-delayed feedback control, 1992. https://privat.ftmc.lt/pyragas/pdffiles/1992/pla92.pdf

---

## 35. Machine-readable conceptual core

```yaml
model:
  name: Market Feedback-State Model
  acronym: MFSM
  status: research_framework
  objective: diagnose_structural_market_response_state
  primary_question: "How is the current structural state changing the system's response law for the next disturbance?"

outputs:
  T: trend_strength_when_a_trend_is_present
  U: trend_sustainability_when_a_trend_is_present
  F_abs: absolute_stressed_consequence
  F_delta: incremental_causal_consequence_only_with_explicit_counterfactual_coupling
  susceptibility_profile: loss_oriented_consequence_as_function_of_standardized_intervention_amplitude
  critical_amplitude: minimum_standardized_amplitude_reaching_prespecified_failure_probability
  M_term: derived_prospective_termination_mechanism_classification

primitive_objects:
  Z_t: closed_augmented_latent_dynamic_state
  G: fixed_structural_form_and_explicit_exogenous_laws
  O_true: true_observation_distribution
  measurement_models: prespecified_candidate_probabilistic_measurement_models

structural_operators:
  J_t: derived_local_response_jacobian
  K_t: delay_and_memory_operator
  W_t: economic_propagation_operator
  controller_topology: opposing_mechanism_topology
  Sigma_t: disturbance_loading

capacity_components:
  R_plus_k: family_of_mechanism_specific_remaining_same_direction_capacities
  H: financing_collateral_and_risk_headroom
  R_minus_h_delta: opposing_absorptive_capacity_available_by_horizon_under_intervention
  Chi_B: local_initial_state_buffer_sensitivity_jacobian
  intervention_buffer_derivative: direct_local_derivative_with_respect_to_general_intervention
  Delta_B_delta: finite_shock_buffer_response

coordination_and_behavior:
  Gamma: strategic_complementarity
  D: dynamic_functional_diversity
  S_ext: external_confirmation
  S_end: endogenous_confirmation

derived_diagnostics:
  A: endogenous_loop_gain
  Theta: summary_of_response_timescale_structure_not_substitute_for_K
  Phi: gain_delay_interaction
  C: derived_effective_propagation_potential_from_specified_W_and_propagation_law
  E: conceptual_endogenous_to_external_confirmation_ratio_not_literal_default_estimator
  L: optional_derived_threshold_concentration_summary_not_primitive_state

termination_mechanisms:
  - fuel_exhaustion
  - delayed_counterflow
  - gain_saturation
  - threshold_unwind

controller_topologies:
  - feed_forward_opposition
  - feedback
  - integral_feedback
  - depletion
  - saturation
  - threshold_switching

response_objects:
  intervention_descriptor: delta_c_V_a_d_t0_p_nu
  intervention_operator: I_delta_maps_mu_and_G_to_counterfactual_mu_and_G
  path_law: conditional_counterfactual_path_law_P_delta
  baseline_path_law: no_intervention_path_law_P_zero
  mean_response: counterfactual_mean_difference_m_delta
  absolute_loss_functional: one_path_loss_larger_is_worse
  incremental_loss_functional: two_path_loss_requires_joint_counterfactual_coupling
  severity_functional: risk_summary_of_loss_oriented_scalar

core_constraints:
  - dynamic_state_must_be_closed
  - every_time_varying_structural_object_must_be_state_predetermined_or_have_explicit_exogenous_law
  - do_not_collapse_R_plus_k_family_H_R_minus
  - make_R_minus_horizon_and_disturbance_qualified_when_relevant
  - distinguish_headroom_from_initial_state_sensitivity_general_intervention_sensitivity_and_finite_shock_response
  - distinguish_disturbance_class_descriptor_and_intervention_operator
  - do_not_intervene_on_endogenous_outcome_labels
  - distinguish_absolute_stressed_consequence_incremental_causal_consequence_and_structural_susceptibility
  - require_loss_orientation_and_severity_functionals_for_F
  - normalize_amplitude_before_cross_system_susceptibility_comparisons
  - do_not_treat_connectivity_as_monotonic_risk
  - do_not_treat_delay_without_gain
  - do_not_equate_participant_count_with_diversity
  - allow_run_like_vulnerability_without_prior_trend
  - separate_true_observation_distribution_from_analyst_probabilistic_measurement_model
  - report_identification_status_and_observationally_equivalent_alternative
  - do_not_treat_CSD_as_universal_crash_warning
  - do_not_use_biological_analogy_as_predictive_evidence
  - do_not_create_scalar_universal_fragility_score
  - do_not_add_new_canonical_variables_without_theoretical_necessity_or_empirical_evidence

empirical_priority:
  - counterfactual_path_response_functionals
  - shock_consequence_vs_susceptibility
  - headroom_x_amplification
  - horizon_dependent_absorptive_capacity
  - local_and_finite_shock_constraint_response
  - delay_mismatch
  - strategic_complementarity
  - synchronization_x_connectivity
  - external_vs_endogenous_confirmation
  - termination_mechanism_classification
  - state_dependent_response_matrix
  - measurement_identification

validation_standard:
  - prespecified_definitions
  - explicit_disturbance_class_descriptor_operator_amplitude_units_path_and_horizon
  - explicit_path_loss_orientation_and_severity_functionals
  - explicit_counterfactual_coupling_if_incremental_pathwise_effects_are_reported
  - real_time_data
  - strong_baselines
  - flexible_same_raw_information_set_baseline
  - out_of_sample_evaluation
  - disturbance_class_amplitude_and_episode_holdouts_where_possible
  - rare_event_correction
  - causal_identification_where_possible
  - prespecified_finite_measurement_model_set
  - explicit_identification_status
  - explicit_falsifiers
```

---

## 36. Final note

MFSM should remain a living research object.

Its purpose is not to force every market event into one grand theory. Its purpose is to provide a disciplined language for asking whether a market move is being sustained by healthy external information, self-generated reinforcement, finite buffers, delayed constraints, synchronized behavior, or threshold-sensitive balance sheets, and to determine how those elements interact.

The framework should become simpler, not larger, when empirical testing shows that some variables are redundant or uninformative.

**Theory-freeze rule:** until the current empirical program has been tested, new canonical state variables should not be added merely because they are interesting. Additions require either a contradiction the current architecture cannot represent or empirical evidence that a missing mechanism is needed.

A future version is justified only when it improves causal clarity, measurement, or falsifiable predictive content.
