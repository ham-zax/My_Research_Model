# Mathematical Foundations of the Market Feedback-State Model (MFSM)

Status: Canonical companion specification  
Date: 2026-09-22  
Role: Exact mathematical layer beneath Market_Feedback_State_Model_Canonical.md

---

## 0. Purpose

This document preserves the mathematics behind MFSM at higher fidelity than the canonical conceptual specification.

It exists to prevent a future researcher or LLM from quietly making any of these errors:

- treating delay alone as a universal danger variable;
- assuming the same mean response time implies the same stability;
- confusing oscillation with instability or collapse;
- interpreting a Hopf boundary as a guaranteed crash;
- treating rising variance as proof that restoring force is weakening;
- substituting correlation for a propagation mechanism;
- collapsing continuation fuel, financing headroom, and opposing liquidity into one resource variable;
- assuming local eigenvalue stability rules out transient amplification, threshold failure, or large-shock escape;
- treating an equation from biology or physics as a financial model without an independently specified financial mechanism.

MFSM uses mathematics as a language for causal structure, not as decoration and not as proof of predictive edge.

---

## 1. Canonical mathematical object

The mature MFSM is represented conceptually as

\[
\mathcal{M}_t
=
\left\{
\mathbf X_t,
J_t,
K_t,
W_t,
B_t,
Q_t,
M_t^{term},
\Sigma_t
\right\}.
\]

Interpretation:

- \(\mathbf X_t\): interacting market state variables;
- \(J_t\): local state-dependent response matrix or Jacobian;
- \(K_t\): delay / memory / response-time kernel;
- \(W_t\): economic propagation network;
- \(B_t\): usable capacities, buffers, and nonlinear thresholds;
- \(Q_t\): signal-source decomposition and expectations state;
- \(M_t^{term}\): candidate termination mechanism;
- \(\Sigma_t\): stochastic disturbance structure.

Useful derived diagnostics include

\[
A,\quad
R^+,\quad
H,\quad
R^-,\quad
I,\quad
\Theta,\quad
\Phi,\quad
C,\quad
D,\quad
S^{ext},\quad
S^{end},\quad
L.
\]

These are not assumed to enter a universal additive score.

---

# Part I — Local response, modes, and finite-time amplification

## 2. Local linearization

Let a deterministic nonlinear state system be

\[
\dot{\mathbf x}
=
\mathbf f(\mathbf x;\theta).
\]

If \(\mathbf x^\ast\) is an equilibrium,

\[
\mathbf f(\mathbf x^\ast;\theta)=0,
\]

and

\[
\delta\mathbf x
=
\mathbf x-\mathbf x^\ast,
\]

then locally

\[
\delta\dot{\mathbf x}
=
J\,\delta\mathbf x
+
O(\|\delta\mathbf x\|^2),
\]

where

\[
J
=
\left.
\frac{\partial\mathbf f}{\partial\mathbf x}
\right|_{\mathbf x^\ast}.
\]

For

\[
\dot{\mathbf z}=J\mathbf z,
\]

local asymptotic stability requires

\[
\Re(\lambda_i(J))<0
\qquad
\text{for all }i.
\]

This is only a local result. It does not imply global basin safety, absence of thresholds, or absence of stochastic escape.

---

## 3. Non-normal transient amplification

If

\[
JJ^\ast\neq J^\ast J,
\]

then \(J\) is non-normal.

A non-normal system can exhibit large finite-time amplification even when every eigenvalue has negative real part.

The finite-time propagator is

\[
e^{Jt}.
\]

The largest possible Euclidean amplification at horizon \(t\) is

\[
G_{max}(t)
=
\|e^{Jt}\|_2
=
\sigma_{\max}(e^{Jt}).
\]

Therefore

\[
\Re(\lambda_i)<0
\quad\forall i
\]

does not imply

\[
G_{max}(t)\le1
\quad\forall t.
\]

### MFSM interpretation

A market can be locally mean-reverting in an asymptotic sense and still be capable of large temporary displacement when several response channels align.

Potential financial contributors include:

- common risk constraints;
- dealer inventory feedback;
- hedging flows;
- overlapping liquidations;
- funding stress;
- synchronized volatility targeting.

This is why MFSM should study response modes, not only long-run equilibrium stability.

---

# Part II — Exact scalar delay foundation

## 4. Delayed reinforcing-versus-opposing system

Consider

\[
\dot z(t)
=
a z(t)-b z(t-\tau),
\qquad
0\le a<b,
\qquad
\tau\ge0,
\]

with constant coefficients and a continuous initial history on \([-\tau,0]\).

Interpretation:

- \(a\): instantaneous reinforcing gain;
- \(b\): delayed opposing gain;
- \(\tau\): discrete response delay.

This is a minimal control model, not a universal market equation.

---

## 5. Characteristic equation

Assume

\[
z(t)=e^{\lambda t}.
\]

Substitution yields

\[
\lambda-a+b e^{-\lambda\tau}=0.
\]

Hence the characteristic equation is

\[
\boxed{
\lambda-a+b e^{-\lambda\tau}=0
}.
\]

Because of the delay, the equation has infinitely many characteristic roots.

---

## 6. First imaginary-axis crossing

At a stability boundary write

\[
\lambda=i\omega.
\]

Then

\[
i\omega-a+b e^{-i\omega\tau}=0.
\]

Using

\[
e^{-i\omega\tau}
=
\cos(\omega\tau)-i\sin(\omega\tau),
\]

the real and imaginary parts are

\[
\boxed{
a=b\cos(\omega\tau)
}
\]

and

\[
\boxed{
\omega=b\sin(\omega\tau).
}
\]

Squaring and adding gives

\[
a^2+\omega^2=b^2,
\]

so

\[
\boxed{
\omega_c=\sqrt{b^2-a^2}.
}
\]

The first positive stability boundary is

\[
\boxed{
\tau_c
=
\frac{\arccos(a/b)}
{\sqrt{b^2-a^2}}.
}
\]

Under \(0\le a<b\), the equilibrium is exponentially stable for

\[
\boxed{
0\le\tau<\tau_c
}
\]

and loses exponential stability at the first crossing.

---

## 7. Crossing direction

Define

\[
F(\lambda,\tau)
=
\lambda-a+b e^{-\lambda\tau}.
\]

Implicit differentiation of

\[
F(\lambda,\tau)=0
\]

gives

\[
\frac{d\lambda}{d\tau}
=
\frac{b\lambda e^{-\lambda\tau}}
{1-b\tau e^{-\lambda\tau}}.
\]

At the crossing,

\[
b e^{-i\omega_c\tau_c}
=
a-i\omega_c.
\]

Therefore

\[
\frac{d\lambda}{d\tau}
=
\frac{\omega_c^2+i a\omega_c}
{1-a\tau_c+i\omega_c\tau_c}.
\]

Its real part is

\[
\boxed{
\Re\left(\frac{d\lambda}{d\tau}\right)
=
\frac{\omega_c^2}
{(1-a\tau_c)^2+(\omega_c\tau_c)^2}
>0.
}
\]

Thus, at the first boundary, the conjugate pair crosses toward instability as delay increases.

---

## 8. Special case \(a=0\)

If

\[
a=0,
\]

then

\[
\dot z(t)
=
-b z(t-\tau).
\]

The critical frequency is

\[
\omega_c=b
\]

and

\[
\boxed{
b\tau_c=\frac{\pi}{2}.
}
\]

Therefore exponential stability requires

\[
\boxed{
b\tau<\frac{\pi}{2}.
}
\]

### Key interpretation

Delay has units. Delay alone cannot define universal danger.

The stability quantity combines response strength and response time.

---

## 9. What the scalar delay result does not imply

It does not prove that:

- every market with a long response lag will crash;
- crossing \(\tau_c\) implies an unrecoverable collapse;
- a financial market obeys a scalar fixed-delay equation;
- a Hopf bifurcation automatically occurs in an arbitrary nonlinear extension;
- observed cycles identify delayed feedback as their cause.

The linear equation itself does not create a bounded attracting cycle.

A Hopf bifurcation in a nonlinear system requires additional regularity, transversality, and nondegeneracy conditions. Nonlinear terms determine the post-bifurcation behavior.

---

# Part III — Lagged inhibition as an explicit state

## 10. Two-state model

A useful alternative is

\[
\dot x
=
a x-b y,
\]

\[
T\dot y
=
x-y,
\qquad
T>0.
\]

Interpretation:

- \(x\): active market or feedback state;
- \(y\): lagging inhibitory / control state;
- \(T\): adjustment timescale.

The system matrix is

\[
\begin{pmatrix}
a & -b\\
1/T & -1/T
\end{pmatrix}.
\]

---

## 11. Characteristic polynomial and stability

The characteristic polynomial is

\[
\boxed{
T\lambda^2
+
(1-aT)\lambda
+
(b-a)
=
0.
}
\]

The eigenvalues are

\[
\boxed{
\lambda_\pm
=
\frac{
aT-1
\pm
\sqrt{(1-aT)^2-4T(b-a)}
}
{2T}.
}
\]

For \(T>0\), the Routh-Hurwitz conditions give asymptotic stability exactly when

\[
\boxed{
b>a
}
\]

and

\[
\boxed{
aT<1.
}
\]

For \(a>0\), the candidate oscillatory boundary is

\[
T=\frac1a.
\]

At that boundary,

\[
\lambda^2+a(b-a)=0,
\]

so the oscillation frequency is

\[
\boxed{
\omega
=
\sqrt{a(b-a)}.
}
\]

---

# Part IV — Distributed memory

## 12. Exponential memory kernel

The first-order lag equation

\[
T\dot y=x-y
\]

has the consistent-history solution

\[
\boxed{
y(t)
=
\int_0^\infty
T^{-1}e^{-s/T}x(t-s)\,ds.
}
\]

Hence the kernel is

\[
\boxed{
K_T(s)
=
T^{-1}e^{-s/T},
\qquad
s\ge0.
}
\]

It satisfies

\[
\int_0^\infty K_T(s)\,ds=1
\]

and has mean delay

\[
\int_0^\infty sK_T(s)\,ds=T.
\]

This turns the lagged control state into an exponentially weighted memory of past activity.

---

## 13. Fixed delay and distributed delay are not equivalent

A fixed delay of length \(T\) corresponds formally to

\[
K(s)=\delta(s-T).
\]

An exponential memory with the same mean is

\[
K(s)=T^{-1}e^{-s/T}.
\]

These kernels have different stability properties.

When \(a=0\):

### Fixed delay

\[
\dot x(t)
=
-bx(t-T)
\]

loses stability when

\[
bT>\frac{\pi}{2}.
\]

### Exponential-memory lag

\[
\dot x=-by,
\qquad
T\dot y=x-y
\]

is asymptotically stable for every finite \(T\) when \(b>0\).

Therefore

\[
\boxed{
\text{equal mean response times do not imply equal dynamics}.
}
\]

The shape of the response-time distribution matters.

---

## 14. General memory kernel

A general scalar delayed-feedback model can be written

\[
\dot x(t)
=
a x(t)
-
b\int_0^\infty
K(s)x(t-s)\,ds,
\]

where \(K(s)\ge0\) and usually

\[
\int_0^\infty K(s)\,ds=1.
\]

For an exponential trial solution \(x(t)=e^{\lambda t}\),

\[
\lambda-a+b\widehat K(\lambda)=0,
\]

where

\[
\widehat K(\lambda)
=
\int_0^\infty
K(s)e^{-\lambda s}\,ds
\]

is the Laplace transform of the memory kernel.

Hence

\[
\boxed{
\lambda-a+b\widehat K(\lambda)=0
}
\]

is the natural generalization of the fixed-delay characteristic equation.

Examples:

### Fixed delay

\[
K(s)=\delta(s-\tau)
\]

gives

\[
\widehat K(\lambda)=e^{-\lambda\tau}.
\]

### Exponential memory

\[
K(s)=T^{-1}e^{-s/T}
\]

gives

\[
\widehat K(\lambda)
=
\frac{1}{1+T\lambda},
\]

which yields

\[
T\lambda^2+(1-aT)\lambda+(b-a)=0.
\]

This provides the exact bridge between the fixed-delay model and the two-state lag model.

---

# Part V — Relative timescale and gain-delay diagnostics

## 15. Relative timescale

A useful conceptual quantity is

\[
\boxed{
\Theta
=
\frac{\tau_I}{\tau_A},
}
\]

where

- \(\tau_A\): characteristic timescale of amplification;
- \(\tau_I\): characteristic timescale of opposing response.

Large \(\Theta\) means the reinforcing mechanism can act through many cycles before the counterforce becomes effective.

But \(\Theta\) is not a universal instability theorem.

---

## 16. Gain-delay quantity

For a local scalar model, a dimensionless quantity often has the form

\[
\boxed{
\Phi\sim g\tau,
}
\]

where \(g\) is an effective gain with reciprocal-time units.

In the special case

\[
\dot z(t)=-bz(t-\tau),
\]

\[
\Phi=b\tau
\]

and the stability boundary is

\[
\Phi=\frac{\pi}{2}.
\]

In higher-dimensional financial systems there is no reason to expect one universal scalar \(\Phi\). The relevant stability object depends on:

- feedback matrix structure;
- damping;
- coupling;
- thresholds;
- nonlinearities;
- memory kernel;
- stochastic forcing.

---

# Part VI — Stochastic recovery and critical slowing down

## 17. Ornstein-Uhlenbeck local model

Consider

\[
\boxed{
dZ_t
=
-\kappa Z_t\,dt
+
\sigma\,dW_t,
\qquad
\kappa>0.
}
\]

For the stationary process,

\[
\boxed{
\operatorname{Var}(Z)
=
\frac{\sigma^2}{2\kappa}.
}
\]

The lag-\(\Delta\) correlation is

\[
\boxed{
\operatorname{Corr}[Z(t),Z(t+\Delta)]
=
e^{-\kappa\Delta}.
}
\]

The characteristic recovery time is

\[
\boxed{
t_{rec}
=
\frac1\kappa.
}
\]

Holding the noise process fixed, decreasing \(\kappa\) produces:

- slower recovery;
- higher variance;
- greater persistence.

That is the elementary mathematical basis of critical-slowing-down indicators.

---

## 18. Why critical slowing down is not a universal crash detector

The OU inference has strict limits.

### 18.1 Noise amplitude

Variance can rise because

\[
\sigma\uparrow
\]

with unchanged \(\kappa\).

### 18.2 Noise color and sampling

Changes in serial dependence of the disturbance process can alter observed autocorrelation.

### 18.3 Oscillatory modes

For a damped oscillator, one coordinate can have a correlation form like

\[
e^{-\kappa\Delta}\cos(\omega\Delta),
\]

so a fixed-lag statistic need not rise monotonically toward one.

### 18.4 Local versus global stability

Fast recovery from small shocks does not imply safety from a sufficiently large shock.

### 18.5 Non-bifurcation tipping

A transition can arise through:

- noise-induced escape;
- threshold crossing;
- rapid parameter change;
- institutional intervention;
- exogenous discontinuity.

### MFSM rule

Critical slowing down is an optional candidate diagnostic, not a privileged core signal. It must compete out of sample against finance-specific variables such as leverage, funding, collateral, liquidity, credit, and exposure networks.

---

# Part VII — Capacity and deadline mechanics

## 19. Three distinct capacities

MFSM separates

\[
\boxed{
R^+
=
\text{remaining same-direction continuation capacity},
}
\]

\[
\boxed{
H
=
\text{financing / collateral / risk headroom},
}
\]

and

\[
\boxed{
R^-
=
\text{opposing absorptive capacity}.
}
\]

Their depletion has different implications:

- \(R^+\downarrow\): continuation may weaken;
- \(H\downarrow\): forced-action thresholds approach;
- \(R^-\downarrow\): an unwind can move prices more violently.

They must not be collapsed into a single “liquidity” or “cash” variable.

---

## 20. Capacity dynamics

A generic capacity equation is

\[
\boxed{
\dot{\mathbf r}_t
=
\mathbf s(\mathbf r_t,\mathbf x_t)
-
\mathbf c(\mathbf x_t,\mathbf r_t),
}
\]

where

- \(\mathbf s\): replenishment / mobilization;
- \(\mathbf c\): consumption / impairment.

The state \(\mathbf r_t\) can include

\[
(R^+,H,R^-).
\]

---

## 21. Time-qualified capacity

Nominal resources matter only if they can be mobilized before forced action.

Define

\[
\tau_{mobilize}
=
\text{time to make resources usable}
\]

and

\[
\tau_{deadline}
=
\text{time before forced action}.
\]

A useful mismatch ratio is

\[
\boxed{
\Psi
=
\frac{\tau_{mobilize}}
{\tau_{deadline}}.
}
\]

Interpretation:

- \(\Psi\ll1\): capacity can probably arrive in time;
- \(\Psi\approx1\): timing becomes binding;
- \(\Psi>1\): nominal resources may be operationally irrelevant to the immediate constraint.

This is a concrete finance-specific form of timescale mismatch.

---

# Part VIII — General stochastic MFSM template

## 22. Market-state dynamics

A general continuous-time representation is

\[
\boxed{
d\mathbf x_t
=
\mathbf f(
\mathbf x_t,
\mathbf r_t,
\mathbf u_t;
\theta_t
)\,dt
+
\Sigma(\mathbf x_t,t)\,d\mathbf W_t.
}
\]

Here:

- \(\mathbf x_t\): interacting activities and market states;
- \(\mathbf r_t\): capacities and buffers;
- \(\mathbf u_t\): control / counterflow states;
- \(\theta_t\): structural parameters;
- \(\Sigma\): state-dependent stochastic disturbance loading.

---

## 23. Delayed control and expectations

A lagged control state can be represented as

\[
\boxed{
T\dot{\mathbf u}_t
=
\mathbf h\left(
\int_0^\infty
K(s)\mathbf x_{t-s}\,ds,
\mathbb E_t[\mathbf x_{t+H}]
\right)
-
\mathbf u_t.
}
\]

This distinguishes:

1. backward-looking memory,

\[
\int_0^\infty K(s)\mathbf x_{t-s}\,ds,
\]

from

2. forward-looking expectations,

\[
\mathbb E_t[\mathbf x_{t+H}].
\]

The expectation term is structurally important in finance because agents can:

- anticipate policy;
- front-run delayed supply;
- anticipate liquidations;
- anticipate other agents;
- change strategy when a model becomes widely known;
- thereby alter the effective coefficients of the system itself.

---

# Part IX — Network propagation

## 24. Economic exposure network

Let

\[
W_t=[w_{ij,t}]
\]

encode economically operative transmission links.

Possible meanings of \(w_{ij}\) include:

- common holdings;
- direct liabilities;
- collateral dependence;
- funding links;
- benchmark coupling;
- dealer hedging links;
- common liquidation channels.

A generic discrete-time propagation model is

\[
\boxed{
\Delta\mathbf x_{t+1}
=
F(\Delta\mathbf x_t)
+
W_t G(\Delta\mathbf x_t).
}
\]

Raw correlation is not a substitute for \(W_t\).

---

## 25. Spectral direction

For a local linear propagation law

\[
\mathbf z_{t+1}
=
P_t\mathbf z_t,
\]

define the spectral radius

\[
\boxed{
\rho(P_t)
=
\max_i|\lambda_i(P_t)|.
}
\]

For this specified linear system:

- \(\rho(P_t)<1\): perturbations decay asymptotically;
- \(\rho(P_t)>1\): at least one propagation mode expands.

This does not imply that more links are always destabilizing. The result depends on weights, buffers, recovery, and the actual propagation law.

---

## 26. Functional diversity

Let \(g_i(s)\) be participant \(i\)'s action as a function of state \(s\).

A conceptual measure of functional diversity is the dispersion of response derivatives:

\[
\boxed{
D_{func}
\propto
\operatorname{Dispersion}_i
\left(
\frac{\partial g_i}{\partial s}
\right).
}
\]

Low functional diversity means nominally different participants react similarly to the same state change.

The dangerous combination is not merely low \(D\), but approximately

\[
\boxed{
D\downarrow
+
\text{forced action}
+
R^-\downarrow
+
W\text{ capable of transmission}.
}
\]

---

# Part X — Thresholds, hysteresis, and hybrid dynamics

## 27. Threshold switching

Many financial constraints are piecewise.

A minimal example is

\[
q(x)
=
\begin{cases}
0, & x>x_c,\\
q_{forced}(x), & x\le x_c.
\end{cases}
\]

Crossing \(x_c\) changes the behavioral law.

Examples:

- margin breach;
- liquidation threshold;
- mandate violation;
- collateral haircut;
- stop-out;
- regulatory-capital threshold.

This can convert voluntary behavior into forced behavior.

---

## 28. Hysteresis

If entry and exit thresholds differ,

\[
x_{enter}\neq x_{exit},
\]

the system has hysteresis.

The same current price can therefore correspond to different future behavior depending on path history.

This is one reason price alone is not a sufficient state variable.

---

## 29. Hybrid-system view

A useful abstraction is a hybrid system with continuous state \(\mathbf x\) and discrete regime \(q\):

\[
\dot{\mathbf x}
=
f_q(\mathbf x),
\]

with guard conditions

\[
g_{q\to q'}(\mathbf x)=0
\]

that trigger regime transitions.

For example:

- normal trading \(\to\) margin stress;
- margin stress \(\to\) forced liquidation;
- normal market making \(\to\) liquidity withdrawal;
- normal operation \(\to\) trading halt.

This is often more faithful than forcing all behavior into one smooth differential equation.

---

# Part XI — Four termination mechanisms

## 30. Fuel exhaustion

\[
R^+\to0.
\]

The reinforcing side loses incremental capacity.

Expected consequence: weakening continuation or stall.

Fuel exhaustion does not by itself imply violent reversal.

---

## 31. Delayed counterflow

\[
I_t\uparrow
\]

after a lag.

Examples can include:

- issuance;
- producer supply;
- arbitrage capital;
- profit taking;
- valuation-sensitive selling;
- hedging.

---

## 32. Gain saturation

\[
\frac{\partial \text{response}}
{\partial \text{stimulus}}
\downarrow.
\]

The same additional stimulus produces less marginal system response.

This is not equivalent to “top formation.” The stimulus must be independently measured before the gain can be estimated.

---

## 33. Threshold unwind

\[
H\to0
\]

and a threshold converts losses into forced same-direction action.

Canonical architecture:

\[
P\downarrow
\rightarrow
H\downarrow
\rightarrow
\text{forced selling}\uparrow
\rightarrow
P\downarrow.
\]

This is structurally different from simple exhaustion.

---

# Part XII — External versus endogenous reinforcement

## 34. Signal-source decomposition

Conceptually separate

\[
S^{ext}
\]

from

\[
S^{end}.
\]

External confirmation can include:

- earnings;
- cash flow;
- adoption;
- physical demand;
- new information.

Endogenous confirmation can include:

- return-induced attention;
- return-induced flows;
- trend following;
- collateral feedback;
- mechanical hedging caused by the prior move.

A conceptual ratio is

\[
\boxed{
E
=
\frac{S^{end}}{S^{ext}}.
}
\]

This is a decomposition target, not a validated scalar market signal.

A rigorous implementation must distinguish:

- information-related price movement;
- mechanical impact;
- persistent order flow;
- anticipation;
- common response to external information.

---

# Part XIII — Adaptive-network foundation: Physarum

## 35. Classic adaptive-tube equations

The classic Physarum network model is useful as a structural example of flow-dependent capacity adaptation.

For edge \(ij\),

\[
\boxed{
Q_{ij}
=
\frac{D_{ij}}{L_{ij}}(p_i-p_j),
}
\]

where:

- \(Q_{ij}\): flow;
- \(D_{ij}\): effective conductivity;
- \(L_{ij}\): tube or edge length;
- \(p_i-p_j\): pressure difference.

For a cylindrical tube under Poiseuille flow,

\[
\boxed{
D_{ij}
=
\frac{\pi a_{ij}^4}{8\eta},
}
\]

where \(a_{ij}\) is radius and \(\eta\) is viscosity.

Adaptive conductance is modeled schematically as

\[
\boxed{
\dot D_{ij}
=
f(|Q_{ij}|)
-
rD_{ij}.
}
\]

Thus

\[
\text{flow}
\rightarrow
\text{capacity adaptation}
\rightarrow
\text{future flow}.
\]

### Allowed MFSM transfer

Use this architecture for:

- adaptive routing;
- flow-dependent liquidity capacity;
- reinforcement and pruning of channels;
- capital-allocation networks.

### Disallowed inference

Do not treat Physarum as a model of:

- strategic expectations;
- valuation;
- leverage;
- investor beliefs;
- speculative reflexivity.

---

# Part XIV — Feed-forward versus feedback antagonism

## 36. Incoherent feed-forward topology

A canonical structure is

\[
A\rightarrow C
\]

and

\[
A\rightarrow B\dashv C.
\]

The same upstream input drives both a fast positive path and an opposing path.

If the direct path is faster, \(C\) can exhibit a pulse.

---

## 37. Delayed feedback topology

A different structure is

\[
C\rightarrow B\dashv C.
\]

Here the current output/state itself creates the eventual antagonist.

These topologies must not be conflated.

### Financial example closer to feed-forward

A valuation shock can simultaneously create:

\[
A\rightarrow\text{immediate buying}
\]

and

\[
A\rightarrow\text{issuance incentive}\rightarrow\text{future supply}.
\]

### Financial example closer to feedback

\[
\text{leveraged appreciation}
\rightarrow
\text{position accumulation}
\rightarrow
\text{margin sensitivity}
\rightarrow
\text{later forced response}.
\]

The important object is causal topology plus gain and lag structure, not the metaphorical label.

---

# Part XV — Trend Strength, Sustainability, and Failure Fragility

## 38. Trend Strength \(T\)

Trend Strength is descriptive.

It should be constructed from observed directional movement, for example:

- multi-horizon return;
- breadth;
- persistence;
- participation;
- directional volume;
- acceleration.

It is not a stability eigenvalue.

---

## 39. Trend Sustainability \(U\)

Conceptually,

\[
U
=
U(
R^+,
S^{ext},
A,
I,
K,
\text{replenishment},
\text{impact}
).
\]

High \(U\) means the continuation-generating process remains economically viable.

No canonical scalar formula is currently justified.

---

## 40. Failure Fragility \(F\)

Conceptually,

\[
F
=
F(
H,
R^-,
L,
W,
D,
K,
\Sigma,
\text{thresholds}
).
\]

High \(F\) means a disturbance can produce disproportionate or propagating consequences.

No canonical scalar formula is currently justified.

---

# Part XVI — Mathematical workflow for applications

## 41. Define the minimal state vector

Choose the smallest economically meaningful

\[
\mathbf X_t.
\]

Do not add variables merely because data are available.

---

## 42. Specify causal arrows

For every proposed arrow, state:

- source;
- target;
- sign;
- mechanism;
- response timescale;
- whether action is voluntary or forced;
- whether the response changes across regimes.

---

## 43. Separate buffers

Estimate or proxy

\[
R^+,\quad H,\quad R^-.
\]

Do not call them all “liquidity.”

---

## 44. Specify memory

Prefer:

- fixed delay only where institutionally defensible;
- first-order lag for a gradual adjustment process;
- general \(K(s)\) where delays are distributed;
- multiple kernels when mechanisms operate on different clocks.

---

## 45. Estimate local dynamics

Estimate or posit

\[
J_t.
\]

Inspect:

- eigenvalues;
- damping rates;
- oscillation frequencies;
- non-normality;
- singular-value transient amplification.

---

## 46. Map propagation topology

Construct \(W_t\) from economically operative links.

Do not substitute raw pairwise return correlation.

---

## 47. Add nonlinear constraints

Represent:

- margin thresholds;
- liquidation rules;
- risk limits;
- mandate constraints;
- hysteresis;
- policy intervention;
- position limits.

---

## 48. Separate disturbance from restoring dynamics

Do not infer weaker stability from higher variance alone.

Model or estimate \(\Sigma_t\) where possible.

---

## 49. Classify termination mechanism

Distinguish

\[
M_1,\ M_2,\ M_3,\ M_4.
\]

Do not label every loss of continuation “exhaustion.”

---

## 50. Validate out of sample

Require:

- locked definitions before the test period;
- real-time data when possible;
- strong benchmark models;
- multiple assets or episodes;
- explicit false-alarm costs;
- mechanism-specific negative controls.

Historical explanation is not enough.

---

# Part XVII — Inferences explicitly rejected

Do not infer automatically that:

1. **Long delay means crash.**  
   Delay interacts with gain, damping, kernel shape, topology, thresholds, and nonlinearities.

2. **Hopf means catastrophic collapse.**  
   A Hopf crossing concerns oscillatory stability. Nonlinear terms determine the resulting dynamics.

3. **Rising variance proves critical slowing down.**  
   Noise amplitude and noise structure can change.

4. **High correlation proves contagion.**  
   Correlation can arise from common information with no direct propagation link.

5. **More connectivity means more fragility.**  
   Network effects are state- and shock-size-dependent.

6. **Diminishing price response means a market top.**  
   The stimulus must be independently identified.

7. **Low \(R^+\) means crash risk.**  
   It may imply only a stall.

8. **Low \(H\) and low \(R^-\) are equivalent.**  
   They correspond to different mechanisms.

9. **A natural equation is automatically a financial equation.**  
   A financial causal counterpart must be independently specified and measured.

---

# Part XVIII — Mathematical research priorities

## 51. State-dependent Jacobian estimation

Can \(J_t\) be estimated from identified shocks, flows, and balance-sheet responses rather than raw correlations?

Candidate methods include:

- local projections;
- structural VARs;
- state-space models;
- regime-switching models;
- event-identified impulse responses;
- local linear models.

---

## 52. Distributed-lag estimation

Can \(K(s)\) be estimated for:

- corporate issuance;
- producer supply;
- collateral mobilization;
- hedging response;
- arbitrage capital;
- liquidity replenishment?

The empirical question is not only the mean lag but the shape of the response-time distribution.

---

## 53. Non-normal amplification

Do apparently stable market states contain large finite-horizon amplification modes?

Estimate

\[
\|e^{J_t h}\|
\]

or discrete-time analogues where plausible.

---

## 54. Threshold-state estimation

Can liquidation, margin, or risk-limit distance be proxied well enough to estimate \(H\)?

---

## 55. Network spectral state

Can exposure-weighted propagation operators improve on raw correlation and concentration measures?

---

## 56. Termination-mechanism classification

Can data distinguish

\[
M_1\text{ through }M_4
\]

before or during transitions?

---

## 57. Expectation feedback

How should

\[
\mathbb E_t[\mathbf x_{t+H}]
\]

enter without making the model observationally unidentifiable?

This is one of the main ways financial systems differ from purely mechanical feedback systems.

---

# Part XIX — Source foundations

The derivations above follow directly from the equations stated in this document. Relevant classical foundations and source-domain references include:

- G. E. Hutchinson, “Circular Causal Systems in Ecology” (1948): https://people.wku.edu/charles.smith/biogeog/HUTC1948.htm
- K. Pyragas, “Continuous control of chaos by self-controlling feedback” (1992): https://privat.ftmc.lt/pyragas/pdffiles/1992/pla92.pdf
- M. B. Elowitz and S. Leibler, “A synthetic oscillatory network of transcriptional regulators” (2000): https://www.nature.com/articles/35002125
- Bak, Tang, and Wiesenfeld, “Self-organized criticality: An explanation of 1/f noise” (1987): https://link.aps.org/doi/10.1103/PhysRevLett.59.381
- Tero et al., adaptive Physarum transport-network work: use the source list in the canonical specification.

For the finance-side evidence and measurement discipline, read Empirical_Finance_Foundations.md.

---

## Final mathematical invariant

The deepest mathematical statement behind MFSM is not:

> delay causes instability.

It is:

> **The response of a feedback system depends jointly on local gain, response-time structure, state-dependent capacity, nonlinear thresholds, network propagation, stochastic disturbance, and the shape of memory.**

Financial reflexivity adds another layer:

\[
\boxed{
\text{agents can alter the effective dynamics because they anticipate the dynamics}.
}
\]

Therefore MFSM should be treated as a **state-dependent dynamical-systems research program**, not a fixed universal equation.
