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

The mature MFSM requires one **closed augmented dynamic state**:

\[
\boxed{
\mathcal M_t
=
\{\mathbf Z_t;\mathcal G,\mathcal O\}.
}
\]

Interpretation:

- \(\mathbf Z_t\): the minimal closed latent state required to determine future dynamics;
- \(\mathcal G\): the fixed structural form, including transition equations / kernels, mappings from state to delay-memory and propagation operators, controller architecture, exogenous disturbance law, and parameterization;
- \(\mathcal O\): the true observation mechanism.

"Closed" includes the memory required by the transition law. For a fixed delay \(\tau\), the exact Markov state is a history segment (for example, \(\mathbf Z_{[t-\tau,t]}\)), not merely the instantaneous vector \(\mathbf Z_t\). A general distributed kernel can likewise require a function-valued history state. A finite-dimensional representation is exact only when the chosen kernel admits a finite-dimensional realization, such as the exponential kernel represented by its filter coordinate; otherwise it must be labeled an approximation.

Buffers \(B_t\), expectation / coordination state \(Q_t\), control states, discrete hybrid modes, and any endogenously evolving coefficients/topology are components or measurable projections of \(\mathbf Z_t\). A time-varying object outside \(\mathbf Z_t\) is permitted only when it is predetermined or exogenous with an explicit law in \(\mathcal G\). Thus \(K_t\), \(W_t\), or \(\Sigma_t\) must be functions of the closed state, fixed/predetermined inputs, or governed by explicit exogenous laws. A finite local Jacobian \(J_t\) is derived only for a finite-dimensional realization or labeled approximation; exact fixed-delay linearization is an operator on histories. The termination label \(M_t^{term}\) is a derived prospective classification, not primitive state.

Observed data \(\mathbf Y_t\) need not equal \(\mathbf Z_t\), and an analyst's fitted measurement model need not equal the true observation mechanism.

Useful derived diagnostics include

\[
A,\quad
\{R_k^+\}_k,\quad
H,\quad
R^-_t(h;\delta,\varepsilon,\varphi),\quad
\mathcal A_t^{tr}(h),\quad
\omega(J_t),\quad
\mathbf\Chi_B,\quad
\Delta\mathbf B^{\delta},\quad
N,\quad
\Theta,\quad
\Phi,\quad
C,\quad
D,\quad
\Gamma,\quad
S^{ext},\quad
S^{end},\quad
L.
\]

These are not assumed to enter a universal additive score. \(C\) must be derived from a specified propagation operator rather than treated as a free primitive, \(\Theta\) is a summary of response-time structure rather than a substitute for \(K\), \(L\) is optional derived threshold exposure rather than an independent state variable, and \(\mathcal A_t^{tr}(h)\) / \(\omega(J_t)\) are finite-horizon/local response diagnostics rather than primitive state.

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

The largest possible Euclidean amplification at horizon \(s\) is

\[
G(s)
=
\|e^{Js}\|_2
=
\sigma_{\max}(e^{Js}).
\]

The finite-horizon transient amplification diagnostic is

\[
\boxed{
\mathcal A_t^{tr}(h)
=
\sup_{0\le s\le h}
\|\Phi(t+s,t)\|_2,
}
\]

where \(\Phi(t+s,t)\) is the tangent/state-transition operator along the specified local trajectory. Under a locally frozen linearization,

\[
\Phi(t+s,t)=e^{J_t s}.
\]

Therefore

\[
\Re(\lambda_i)<0
\quad\forall i
\]

does not imply

\[
\mathcal A_t^{tr}(h)\le1.
\]

An instantaneous growth diagnostic for the locally frozen linear system is the numerical abscissa

\[
\boxed{
\omega(J_t)
=
\lambda_{\max}
\left(
\frac{J_t+J_t^\ast}{2}
\right).
}
\]

If \(\omega(J_t)>0\), there exists a perturbation direction with immediate Euclidean growth even when the spectral abscissa is negative.

These quantities are **derived diagnostics**, not new primitive state variables and not universal fragility scores. Their magnitude depends on the chosen coordinates, norm, local model, and horizon.

### Threshold crossing under transient amplification

Let a switching surface be represented locally by a signed distance-like function \(d_j(\mathbf Z)>0\) in the safe region, with failure/forced action when \(d_j\le0\). For a small initial perturbation \(\Delta\mathbf z_0\), the first-order disturbed path is

\[
\Delta\mathbf Z_{t+s}
\approx
\Phi(t+s,t)\Delta\mathbf z_0.
\]

A local threshold-crossing condition is therefore

\[
\boxed{
\exists s\in[0,h]:
d_j(\mathbf Z_{t+s}^{0})
+
\nabla d_j(\mathbf Z_{t+s}^{0})^\top
\Phi(t+s,t)
\Delta\mathbf z_0
\le0.
}
\]

This makes the central distinction explicit:

\[
\text{asymptotic stability}
\not\Rightarrow
\text{finite-horizon path safety}.
\]

### MFSM interpretation

A market can be locally mean-reverting in an asymptotic sense and still be capable of large temporary displacement when several response channels align. The danger is strongest when transient amplification is large relative to the distance to financing, liquidity, or behavioral switching surfaces.

Potential financial contributors include:

- common risk constraints;
- dealer inventory feedback;
- hedging flows;
- overlapping liquidations;
- funding stress;
- synchronized volatility targeting.

This is why MFSM should study finite-horizon response paths and threshold crossings, not only long-run equilibrium stability.

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
\tau_y\dot y
=
x-y,
\qquad
\tau_y>0.
\]

Interpretation:

- \(x\): active market or feedback state;
- \(y\): lagging inhibitory / control state;
- \(\tau_y\): adjustment timescale.

The system matrix is

\[
\begin{pmatrix}
a & -b\\
1/\tau_y & -1/\tau_y
\end{pmatrix}.
\]

---

## 11. Characteristic polynomial and stability

The characteristic polynomial is

\[
\boxed{
\tau_y\lambda^2
+
(1-a\tau_y)\lambda
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
a\tau_y-1
\pm
\sqrt{(1-a\tau_y)^2-4\tau_y(b-a)}
}
{2\tau_y}.
}
\]

For \(\tau_y>0\), the Routh-Hurwitz conditions give asymptotic stability exactly when

\[
\boxed{
b>a
}
\]

and

\[
\boxed{
a\tau_y<1.
}
\]

For \(a>0\), the candidate oscillatory boundary is

\[
\tau_y=\frac1a.
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
\tau_y\dot y=x-y
\]

has the consistent-history solution

\[
\boxed{
y(t)
=
\int_0^\infty
\tau_y^{-1}e^{-s/\tau_y}x(t-s)\,ds.
}
\]

Hence the kernel is

\[
\boxed{
K_{\tau_y}(s)
=
\tau_y^{-1}e^{-s/\tau_y},
\qquad
s\ge0.
}
\]

It satisfies

\[
\int_0^\infty K_{\tau_y}(s)\,ds=1
\]

and has mean delay

\[
\int_0^\infty sK_{\tau_y}(s)\,ds=\tau_y.
\]

This turns the lagged control state into an exponentially weighted memory of past activity.
The filter state \(y(t)\), initialized consistently with the past history, is an exact finite-dimensional realization of this exponential kernel. A fixed delay or an arbitrary kernel does not inherit that reduction merely because it has the same mean lag.

---

## 13. Fixed delay and distributed delay are not equivalent

Let the common mean response time be \(\bar\tau\).

A fixed delay corresponds formally to

\[
K(s)=\delta(s-\bar\tau).
\]

An exponential memory with the same mean is

\[
K(s)=\bar\tau^{-1}e^{-s/\bar\tau}.
\]

These kernels have different stability properties.

When \(a=0\):

### Fixed delay

\[
\dot x(t)
=
-bx(t-\bar\tau)
\]

loses stability when

\[
b\bar\tau>\frac{\pi}{2}.
\]

### Exponential-memory lag

\[
\dot x=-by,
\qquad
\bar\tau\dot y=x-y
\]

is asymptotically stable for every finite \(\bar\tau\) when \(b>0\).

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
\frac{\tau_N}{\tau_A},
}
\]

where

- \(\tau_A\): characteristic timescale of amplification;
- \(\tau_N\): characteristic timescale of opposing response.

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
\sigma\,d\beta_t,
\qquad
\kappa>0,
}
\]

where \(\beta_t\) is standard Brownian motion.

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

MFSM separates three economic categories, but the continuation side is mechanism-specific.

For each reinforcing mechanism \(k\),

\[
\boxed{
R_{k,t}^+
=
\text{remaining same-direction continuation capacity of mechanism }k.
}
\]

Headroom is

\[
\boxed{
H
=
\text{financing / collateral / risk headroom},
}
\]

and opposing capacity is

\[
\boxed{
R^-
=
\text{opposing absorptive capacity}.
}
\]

Their depletion has different implications:

- \(R_{k,t}^+\downarrow\): mechanism \(k\)'s contribution to continuation may weaken;
- \(H\downarrow\): forced-action thresholds approach;
- \(R^-\downarrow\): an unwind can move prices more violently.

Distinct \(R_k^+\) channels must not be summed into one market-wide scalar without a prespecified aggregation rule. None of these categories should be collapsed into a single “liquidity” or “cash” variable.

---

## 20. Capacity dynamics

A generic capacity equation is

\[
\boxed{
\dot{\mathbf r}_t
=
\mathbf s(\mathbf r_t,\mathbf Z_t)
-
\mathbf c(\mathbf Z_t,\mathbf r_t),
}
\]

where

- \(\mathbf s\): replenishment / mobilization;
- \(\mathbf c\): consumption / impairment.

The state \(\mathbf r_t\) can include

\[
(\{R_k^+\}_k,H,R^-).
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

### 21.1 Horizon-, disturbance-, tolerance-, and arrival-profile-dependent opposing capacity

A single \(R^-_t\) is insufficient when stabilizing capital arrives at different speeds or when willingness to absorb depends on the type of shock.

Capacity also depends on **how incoming flow arrives through time**.

Let \(\varphi:[0,h]\to\mathbb R_+\) be a prespecified normalized incoming-flow profile,

\[
\int_0^h \varphi(s)\,ds=1,
\]

so total incoming flow \(q\) arrives at rate \(q\varphi(s)\). The profile \(\varphi\) is the **stress-flow schedule whose absorptive capacity is being measured**; it is distinct from any temporal intervention profile already contained in \(\delta\). Let \(\mathfrak d_{t,h}(\delta,q\varphi)\) be the named adverse-consequence metric under intervention \(\delta\) and that flow schedule.

Define the operational object by the largest flow scale for which **all smaller scales remain within tolerance**:

\[
\boxed{
R^-_t(h;\delta,\varepsilon,\varphi)
=
\sup
\left\{
q\ge0:
\mathfrak d_{t,h}(\delta,q'\varphi)
\le\varepsilon
\;\;
\forall q'\in[0,q]
\right\}.
}
\]

If the consequence metric is monotone in \(q\), this reduces to the simpler threshold condition at \(q\) itself.

The tolerance \(\varepsilon\) must be attached to a specified consequence metric. For market-microstructure applications, a common choice is a maximum adverse price displacement \(\varepsilon_P\). For broader stress applications, \(\varepsilon\) can refer to a prespecified path-loss or threshold criterion.

If the research question concerns a class \(\Phi\) of plausible arrival schedules rather than one profile, a conservative capacity can be defined as

\[
\boxed{
R^-_t(h;\delta,\varepsilon,\Phi)
=
\inf_{\varphi\in\Phi}
R^-_t(h;\delta,\varepsilon,\varphi).
}
\]

This definition makes explicit that liquidity quantity and absorptive capacity are not the same object, and that the same total notional can imply different capacity requirements when it arrives instantaneously versus gradually.

When \(\varphi\) is fixed by design, \(R^-_t(h;\delta,\varepsilon)\) is acceptable shorthand. When tolerance and profile are fixed, \(R^-_t(h;\delta)\) is acceptable shorthand. When disturbance, tolerance, and profile are all fixed, \(R^-_t(h)\) is acceptable shorthand.

If horizons are compared under a **compatible standardized arrival convention** and usable capacity only accumulates with time, longer horizons may admit weakly greater capacity. There is no generic monotonicity theorem when changing \(h\) also changes the incoming-flow schedule, toxicity, state, or willingness to absorb risk.

The relevant mismatch is not "eventual buyers exist." It is whether enough \(R^-_t(h;\delta,\varepsilon,\varphi)\) becomes usable before the forced-action horizon for the specified arrival profile without breaching the prespecified consequence tolerance.

### 21.2 Constraint sensitivity and finite-shock buffer response

Current headroom and state sensitivity are distinct. The matrix form below assumes an exact finite-dimensional realization or a labeled finite-dimensional approximation.

Let

\[
\mathbf B_t\in\mathbb R^m,
\qquad
\mathbf Z_t\in\mathbb R^n.
\]

The local constraint-sensitivity object is the Jacobian

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
\right]
\in\mathbb R^{m\times n}.
}
\]

For an exact delay model, replace the current vector with the history state \(\boldsymbol\phi_t\in\mathcal X\), such as \(\mathcal X=C([-\tau,0];\mathbb R^n)\). Where the conditional expectation is Fréchet differentiable in that history, its initial-state sensitivity is an operator in \(\mathcal L(\mathcal X,\mathbb R^m)\), and the intervention projection applies the operator to the induced history perturbation. It is not generally an \(m\times n\) matrix.

\(\mathbf\Chi_{B,t}(h)\) is specifically an **initial-state sensitivity**.

If a small intervention acts solely through an instantaneous displacement of the initial state, define

\[
\mathbf v_{\delta}
=
D_{\delta}\mathbf Z_t[\dot\delta].
\]

Then the chain rule gives

\[
\boldsymbol\chi_{B,t}^{\delta}(h)
=
\mathbf\Chi_{B,t}(h)\mathbf v_{\delta}.
\]

For a general intervention on a parameter, constraint, transition kernel, or temporal forcing, the appropriate local object is the direct intervention derivative

\[
D_{\delta}
\,
\mathbb E[
\mathbf B_{t+h}^{\delta}
\mid
\mathcal I_t
][\dot\delta].
\]

Only when the intervention factors entirely through an initial-state displacement does that derivative reduce to \(\mathbf\Chi_B\mathbf v_{\delta}\).

For a finite intervention, especially near a threshold or regime switch, local derivatives are only approximations. Define instead

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

Two systems with identical current \(H_t\) can therefore have different shock responses because their future buffers respond differently to the same state perturbation or structural intervention.

This is the mathematical slot for collateral feedback such as price \(\rightarrow\) borrowing capacity \(\rightarrow\) demand.

---

# Part VIII — General stochastic MFSM template

## 22. Closed market-state dynamics

For applications whose specified memory has a finite-dimensional realization, a continuous-time representation uses a **closed augmented state**:

\[
\boxed{
d\mathbf Z_t
=
\mathbf f_{\mathcal G}
\left(
\mathbf Z_t,
\mathbb E_t[\mathbf Z_{t+h_e}]
\right)dt
+
\Sigma(\mathbf Z_t,t)d\boldsymbol\beta_t,
}
\]

where \(\boldsymbol\beta_t\) is Brownian motion and \(h_e\) is an expectation horizon.

Capacities \(\mathbf r_t\), control / counterflow states \(\mathbf u_t\), coordination states, and discrete hybrid modes that evolve independently are coordinates of \(\mathbf Z_t\). If an application writes separate evolution equations for them, those equations are part of the structural transition law \(\mathcal G\).

This stochastic differential equation is a finite-dimensional template, not an exact representation of every delay model above. Under a fixed delay, two paths with the same current \(\mathbf Z_t\) but different past segments can have different next derivatives. Use the history segment as the state for an exact delay model, or state the finite-memory approximation and its validation. The ordinary finite matrix \(J_t\), \(e^{J_t s}\), and its eigenvalues apply to the finite-dimensional realization or approximation; an exact fixed-delay model uses its history-state evolution and characteristic roots. The conditional expectation term also needs an expectation-formation rule in \(\mathcal G\) before this template defines a transition law.

### 22.1 True observation mechanism and analyst measurement model

The structural state should not be identified with its proxy.

Conceptually, the true data-generating observation mechanism is the conditional law

\[
\boxed{
p_*(\mathbf Y_t\mid\mathbf Z_t).
}
\]

An additive-noise representation

\[
\mathbf Y_t
=
g_*(\mathbf Z_t)
+
\boldsymbol\eta_t
\]

is only one special case.

The analyst does not know \(p_*\) exactly and instead uses one or more candidate probabilistic measurement models

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

A structural conclusion should therefore state whether it is robust across a **prespecified finite set** of reasonable measurement specifications. This is essential when estimating endogeneity, branching ratios, headroom, crowding, or network state. Misspecified kernels, regime mixtures, edge effects, nonstationarity, or proxy error can produce apparent structure that is not present in the latent system.

### 22.2 Structural intervention operator and counterfactual path laws

A disturbance class \(c\) is not yet a mathematical intervention. The tuple

\[
\boxed{
\delta
=
(c,V,a,d,t_0,p,\nu)
}
\]

is a required **descriptor**, where \(V\) is the target, \(a\ge0\) the amplitude, \(d\) the direction, \(t_0\) the onset, \(p(s)\) the time profile, and \(\nu\) any stochastic component.

Let the pre-intervention latent-state law be

\[
\mu_t
=
\mathcal L(
\mathbf Z_t
\mid
\mathcal I_{t^-}
).
\]

The mathematical intervention acts on the full counterfactual specification:

\[
\boxed{
\mathfrak I_{\delta}:
(\mu_t,\mathcal G)
\longmapsto
(\mu_t^{\delta},\mathcal G^{\delta}).
}
\]

A pure state-setting / jump intervention may change \(\mu_t\) while leaving \(\mathcal G\) fixed. A structural intervention changes the transition system. A hybrid intervention may change both.

For each application, state the exact initial-state law, equation, transition kernel, parameter, constraint, jump rule, or forcing term modified; the amplitude units; the law of \(\nu\); its coupling to baseline exogenous noise; and the timing convention.

The intervention should act on a causally upstream structural variable. Endogenous outcomes such as a run, cascade, or liquidation wave are responses, not interventions.

Let \(\mathbf Z^{\delta}\) denote the potential closed-state path generated by \((\mu_t^{\delta},\mathcal G^{\delta})\), and \(\mathbf Z^0\) the no-intervention baseline generated by \((\mu_t,\mathcal G)\).

Let \(\mathcal I_t\) denote the information available at time \(t\). If \(\mathbf Z_t\) is latent, conditioning on \(\mathcal I_t\) integrates over state-estimation uncertainty rather than assuming \(\mathbf Z_t\) is observed exactly. Define the theoretical primitive

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

The baseline law is

\[
\mathcal P_{t,h}^{0}
=
\mathcal L
\left(
\mathbf Z_{[t,t+h]}^{0}
\mid
\mathcal I_t
\right).
\]

The mean causal response is only one projection:

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

Because expectation is linear, this difference is defined from the two marginal potential-outcome expectations. By contrast, the **distribution** of the pathwise difference \(\mathbf Z^{\delta}-\mathbf Z^0\) requires a structural coupling of the two potential paths, for example through shared exogenous noise. Two marginal path laws alone do not identify that joint counterfactual distribution.

The full path law is a theoretical object. Empirical work may target only decision-relevant projections such as threshold probabilities, maximum adverse excursion, cascade size, tail loss, and recovery probability.

---

## 23. Delayed control and expectations

If \(\mathbf u_t\) is a control / counterflow coordinate of the closed state, a lagged response equation can be represented as

\[
\boxed{
\tau_u\dot{\mathbf u}_t
=
\mathbf h\left(
\int_0^\infty
K(s)\mathbf Z_{t-s}\,ds,
\mathbb E_t[\mathbf Z_{t+h_e}]
\right)
-
\mathbf u_t,
}
\]

where \(\tau_u>0\) is the control-adjustment timescale and \(h_e\) is an expectation horizon.

This distinguishes:

1. backward-looking memory,

\[
\int_0^\infty K(s)\mathbf Z_{t-s}\,ds,
\]

from

2. forward-looking expectations,

\[
\mathbb E_t[\mathbf Z_{t+h_e}].
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
\Delta\mathbf Z_{t+1}
=
F(\Delta\mathbf Z_t)
+
W_t G(\Delta\mathbf Z_t).
}
\]

Raw correlation is not a substitute for \(W_t\).

---

## 25. Spectral direction

For a **fixed time-invariant** linear propagation law

\[
\mathbf z_{n+1}
=
P\mathbf z_n,
\]

define the spectral radius

\[
\boxed{
\rho(P)
=
\max_i|\lambda_i(P)|.
}
\]

For this specified fixed linear system:

- \(\rho(P)<1\): perturbations decay asymptotically;
- \(\rho(P)>1\): at least one propagation mode expands.

The boundary \(\rho(P)=1\) is conditional on this fixed linear iteration.

For a time-varying sequence

\[
\mathbf z_{n+1}=P_n\mathbf z_n,
\]

the individual conditions \(\rho(P_n)<1\) do **not** in general imply that

\[
P_{n-1}\cdots P_1P_0
\]

decays. Products of individually stable noncommuting matrices can transiently or asymptotically amplify. A pointwise \(\rho(P_n)\) should therefore be interpreted only as a locally frozen / one-step diagnostic unless stronger contractivity, common-Lyapunov, joint-spectral-radius, or direct product-growth conditions are established.

Neither the fixed-matrix boundary nor a locally frozen spectral diagnostic is a universal financial-system cascade threshold once the operator changes with the state, losses saturate, institutions switch regimes, defaults truncate exposures, or policy/intermediation changes the propagation law.

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

Functional diversity can itself evolve. A generic composition law is

\[
\boxed{
D_{t+1}
=
g_D(D_t,\pi_t,\mathbf f_t,\mathbf c_t),
}
\]

where \(\pi_t\) denotes relative strategy performance, \(\mathbf f_t\) capital flows, and \(\mathbf c_t\) constraints. This allows successful strategies to attract capital and endogenously reduce diversity.

### 26.1 Strategic complementarity

Some amplification arises because one participant's best action depends directly on the expected actions of others.

A local conceptual measure is

\[
\boxed{
\Gamma_t
\sim
\frac{\partial a_i^*}
{\partial \bar a_{-i}}.
}
\]

Positive \(\Gamma_t\) represents strategic complementarity: withdrawal can make withdrawal optimal, refusal to roll funding can make refusal optimal, and selling can make selling rational even before price feedback is the dominant channel.

No universal numerical instability boundary follows from the symbol alone. A condition such as \(\Gamma=1\) is meaningful only inside a specified best-response / coordination mapping with the relevant normalization and regularity assumptions.

This is distinct from \(A_t\), which summarizes endogenous state/flow amplification.

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

Fuel exhaustion is mechanism-specific. For one or more previously active reinforcing channels,

\[
R_{k,t}^+\to0
\]

or becomes too small to sustain its prior contribution.

The reinforcing side loses incremental capacity through those channels.

Expected consequence: weakening continuation or stall.

Exhaustion of one channel does not imply that every continuation mechanism is exhausted, and fuel exhaustion does not by itself imply violent reversal.

---

## 31. Delayed counterflow

\[
N_t\uparrow
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

### 37.1 Controller topology

MFSM should retain the topology of the opposing mechanism, not only its scalar magnitude. A useful categorical object is

\[
\boxed{
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
}
\]

These mechanisms have different state and timing implications.

For example, integral feedback responds to accumulated error:

\[
u_I(t)
=
k_I
\int_0^t e(s)\,ds,
\]

whereas threshold control changes the behavioral law only after a guard condition is crossed. An observed mean-reverting market process should not be labeled "integral control" unless the institutional mechanism actually integrates an error-like quantity.

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

# Part XV — Trend Strength, Sustainability, Shock Consequence, and Structural Susceptibility

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
\{R_k^+\}_k,
S^{ext},
A,
N,
K,
\text{replenishment},
\text{impact}
).
\]

High \(U\) means the continuation-generating process remains economically viable.

No canonical scalar formula is currently justified.

---

## 40. Shock-conditioned consequence and structural susceptibility

The path law \(\mathcal P_{t,h}^{\delta}\) is the theoretical response object. Practical questions are posed through functionals of that law.

### 40.1 Absolute and incremental path losses

An **absolute stressed loss** has type

\[
\ell_{\mathrm{abs}}:
\mathbf Z_{[t,t+h]}
\longrightarrow
\overline{\mathbb R},
\]

and maps the intervention path into a loss, damage, or failure statistic.

Examples include

\[
\ell_{\mathrm{abs}}
=
\mathbf 1
\{
\tau_{\mathrm{liquidation}}\le h
\},
\]

\[
\ell_{\mathrm{abs}}
=
\max_{0\le s\le h}
\mathrm{Drawdown}(\mathbf Z_{t+s}),
\]

or cascade size.

An **incremental causal path loss** instead has type

\[
\ell_{\Delta}:
(\mathbf Z^{\delta}_{[t,t+h]},\mathbf Z^0_{[t,t+h]})
\longrightarrow
\overline{\mathbb R}.
\]

Its distribution is not determined by the two marginal path laws alone; a joint structural coupling of \(\mathbf Z^{\delta}\) and \(\mathbf Z^0\) must be stated explicitly.

All loss functionals used inside a severity object must be oriented so that **larger means worse**. Resilience quantities such as probability of recovery should either be reported separately or converted to a loss orientation such as probability of failure to recover.

### 40.2 Risk / severity functional

Let \(\rho\) summarize uncertainty in a **loss-oriented scalar**. Examples include:

- expectation;
- probability that loss exceeds a threshold;
- quantile;
- Value-at-Risk;
- expected shortfall.

Define the absolute stressed consequence

\[
\boxed{
F_t^{\mathrm{abs}}(\delta,h;\ell_{\mathrm{abs}},\rho)
=
\rho_{\mathcal P_{t,h}^{\delta}}
\left[
\ell_{\mathrm{abs}}
\left(
\mathbf Z_{[t,t+h]}^{\delta}
\right)
\right].
}
\]

An incremental causal consequence may be defined only after specifying a joint coupling \(\Pi_{t,h}^{\delta,0}\) of the two potential paths:

\[
\boxed{
F_t^{\Delta}
=
\rho_{\Pi_{t,h}^{\delta,0}}
\left[
\ell_{\Delta}
\left(
\mathbf Z^{\delta}_{[t,t+h]},
\mathbf Z^{0}_{[t,t+h]}
\right)
\right].
}
\]

This is not a universal fragility scalar. It is conditional on the current information/state, the structural intervention operator, the horizon, the loss definition, the severity functional, and—when incremental pathwise effects are used—the coupling assumption.

When later sections write \(F_t\) without a superscript, they mean the absolute stressed consequence unless explicitly stated otherwise.

### 40.3 Derived response statistics

Useful projections include:

\[
\Pr(
\tau_{\mathrm{liquidation}}
\le h
\mid
\delta,\mathcal I_t
),
\]

\[
\mathbb E[
\mathrm{MAE}_{0:h}
\mid
\delta,\mathcal I_t
],
\]

\[
\Pr(
S_{\mathrm{cascade}}>s
\mid
\delta,\mathcal I_t
),
\]

and

\[
\Pr(
\tau_R\le h
\mid
\delta,\mathcal I_t
).
\]

If recovery time is used, the recovery set must be defined explicitly. It may be:

- a neighborhood of the no-intervention counterfactual;
- a post-shock viable region;
- restored headroom / liquidity conditions;
- a specified equilibrium manifold.

Because some paths may not recover within the horizon, \(\Pr(\tau_R\le h)\) or truncated / conditional recovery time can be more stable than an unconditional \(\mathbb E[\tau_R]\).

### 40.4 Structural susceptibility

A system can have a large consequence only because the imposed intervention is large. Structural susceptibility instead asks how rapidly consequence rises as intervention amplitude increases.

For disturbance class \(c\), define an intervention family \(\delta(c,a)\), where \(a\ge0\) is amplitude in **prespecified economic units**. The susceptibility profile is

\[
\boxed{
\mathfrak S_t(c,h;\ell,\rho)
:
a
\longmapsto
F_t^{\mathrm{abs}}(\delta(c,a),h;\ell_{\mathrm{abs}},\rho).
}
\]

Because slopes are coordinate-dependent, cross-system comparisons require the same amplitude convention or a prespecified dimensionless normalization

\[
\tilde a
=
\frac{a}{a_{\mathrm{ref}}(c)}.
\]

A comparable local susceptibility measure is then

\[
\frac{\partial F_t}{\partial \tilde a},
\]

when the derivative exists.

For a failure criterion with probability threshold \(q\), define

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

Small \(a_q^*\) means relatively little disturbance is required to push the system into the specified failure region.

Here \(\ell^*\) is the prespecified failure threshold associated with the chosen path-loss functional. A Highly Optimized Tolerance style interpretation follows naturally: low consequence or high resilience for one disturbance family does not imply resilience to another.

---

# Part XVI — Mathematical workflow for applications

## 41. Define the minimal state vector

Choose the smallest economically meaningful latent structural state

\[
\mathbf Z_t.
\]

Specify the closed augmented state, including the required history for exact delay or general-memory dynamics, and distinguish the unknown true observation mechanism \(\mathbf Y_t=g_*(\mathbf Z_t)+\boldsymbol\eta_t\) from the analyst's candidate measurement models \(g^{(m)}(\cdot;\psi^{(m)})\). State whether any finite-memory representation is exact or approximate. Do not add state variables merely because data are available.

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
\{R^+_{k,t}\}_{k\in\mathcal K},\quad H,\quad R^-_t(h;\delta,\varepsilon,\varphi).
\]

Do not call them all “liquidity,” and do not treat realized absorption as identical to prospective capacity. State the consequence metric attached to \(\varepsilon\) and the incoming-flow profile \(\varphi\).

---

## 44. Specify memory

Prefer:

- fixed delay only where institutionally defensible;
- first-order lag for a gradual adjustment process;
- general \(K(s)\) where delays are distributed;
- multiple kernels when mechanisms operate on different clocks.

---

## 45. Estimate local dynamics

For a specified finite-dimensional realization or labeled approximation, estimate or posit

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

## 49. Derive termination mechanism prospectively

Using only information available before the realized transition, distinguish or assign probabilities over

\[
M_1,\ M_2,\ M_3,\ M_4.
\]

Do not label every loss of continuation “exhaustion,” and do not treat a hindsight label as a primitive state variable.

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

7. **Low capacity in one \(R_{k,t}^+\) channel means crash risk.**
   It may imply only weakening or exhaustion of that continuation mechanism.

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
\mathbb E_t[\mathbf Z_{t+h_e}]
\]

enter without making the model observationally unidentifiable?

This is one of the main ways financial systems differ from purely mechanical feedback systems.

## 58. Counterfactual path-response estimation

Can the model estimate decision-relevant functionals of

\[
\mathcal P_{t,h}^{\delta}
\]

for intervention operators with prespecified descriptors, amplitude units, and paths rather than fitting one generic "fragility" state?

Priority intervention families include:

- funding withdrawal;
- margin increase;
- redemption;
- volatility shock;
- collateral haircut;
- supply shock;
- policy shock;
- coordination / rollover disturbances instantiated through upstream variables.

Where possible, evaluation should include disturbance-class, amplitude, and horizon holdouts rather than only date holdouts.

## 59. Measurement-model robustness

Can latent-state estimates survive plausible alternatives for

\[
g(\cdot;\psi_t)
\]

and the assumed noise / kernel structure?

Any estimate of endogenous amplification, criticality, crowding, or network state should be stress-tested for:

- kernel misspecification;
- nonstationarity;
- outliers;
- edge effects;
- regime mixtures;
- sampling frequency;
- proxy error.

---

# Part XIX — Source foundations

The derivations above follow directly from the equations stated in this document. Relevant classical foundations and source-domain references include:

- G. E. Hutchinson, “Circular Causal Systems in Ecology” (1948): https://people.wku.edu/charles.smith/biogeog/HUTC1948.htm
- K. Pyragas, “Continuous control of chaos by self-controlling feedback” (1992): https://privat.ftmc.lt/pyragas/pdffiles/1992/pla92.pdf
- M. B. Elowitz and S. Leibler, “A synthetic oscillatory network of transcriptional regulators” (2000): https://www.nature.com/articles/35002125
- Bak, Tang, and Wiesenfeld, “Self-organized criticality: An explanation of 1/f noise” (1987): https://link.aps.org/doi/10.1103/PhysRevLett.59.381
- Tero et al., adaptive Physarum transport-network work: use the source list in the canonical specification.
- Mangan and Alon, feed-forward-loop network motifs: https://www.weizmann.ac.il/mcb/alon/sites/mcb.UriAlon/files/structure_and_function_of_the_feed-forward_loop_network_motif.pdf
- Yi, Huang, Simon, and Doyle, integral feedback in bacterial chemotaxis: https://www.pnas.org/doi/pdf/10.1073/pnas.97.9.4649
- Carlson and Doyle, Highly Optimized Tolerance: https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.84.2529/fulltext
- Trefethen, Trefethen, Reddy, and Driscoll, “Hydrodynamic Stability Without Eigenvalues” (1993), for non-normal transient growth and pseudospectral motivation: https://doi.org/10.1126/science.261.5121.578
- P. J. Schmid, “Nonmodal Stability Theory” (2007), for finite-time/nonmodal growth, numerical range, and numerical-abscissa diagnostics: https://doi.org/10.1146/annurev.fluid.38.050304.092139

For finance-side evidence, measurement discipline, and the empirical motivation for \(R^-_t(h;\delta,\varepsilon,\varphi)\), \(\mathbf\Chi_B\), \(\Delta\mathbf B^{\delta}\), \(\Gamma_t\), the intervention/path-law layer, and the observation/identification layer, read Empirical_Finance_Foundations.md.

---

## Final mathematical invariant

The deepest mathematical statement behind MFSM is not:

> delay causes instability.

It is:

> **The response of a feedback system depends jointly on local gain, response-time structure, state-dependent capacity and capacity sensitivity, nonlinear thresholds, network propagation, strategic coordination, stochastic disturbance, and the shape of memory. Robustness is conditional on the disturbance being considered.**

Financial reflexivity adds another layer:

\[
\boxed{
\text{agents can alter the effective dynamics because they anticipate the dynamics}.
}
\]

Therefore MFSM should be treated as a **state-dependent dynamical-systems research program**, not a fixed universal equation.
