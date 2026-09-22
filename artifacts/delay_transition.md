The strongest defensible analogy is feedback with different response times, not a universal law that growth inevitably outruns inhibition. Delay, feedback gain, resource replenishment, network structure, noise, and expectations jointly determine stability.

Exact scalar result — independently derived and checked against the delay-stability literature.

For

z
˙
 (t)=az(t)−bz(t−τ),0≤a<b,
with constant coefficients, τ≥0, and a continuous initial history on [−τ,0], the characteristic equation is

λ−a+be 
−λτ
 =0.
At a purely imaginary root λ=iω,

a=bcos(ωτ),ω=bsin(ωτ).
Consequently the first stability boundary is

ω 
c
​
 = 
b 
2
 −a 
2
 
​
 ,τ 
c
​
 = 
b 
2
 −a 
2
 
​
 
arccos(a/b)
​
 .
​
 
The equilibrium is exponentially stable for 0≤τ<τ 
c
​
 , loses exponential stability at τ 
c
​
 , and is unstable for τ>τ 
c
​
 . At the first crossing,

ℜ 
dτ
dλ
​
 = 
(1−aτ 
c
​
 ) 
2
 +(ω 
c
​
 τ 
c
​
 ) 
2
 
ω 
c
2
​
 
​
 >0.
For a=0, the condition becomes bτ<π/2. Thus the meaningful quantity combines delay and response strength; delay alone has units and cannot define universal danger.

Qualification: this linear system does not produce a bounded attracting limit cycle. A Hopf bifurcation in an underlying nonlinear model requires additional smoothness and nondegeneracy conditions; nonlinear terms determine whether emerging cycles are stable or unstable. The scalar stability classification agrees with Nishiguchi’s proof of Hayes’ theorem.

A useful two-state alternative — independently derived.

Let x represent activity and y its lagging inhibitory signal:

x
˙
 =ax−by,T 
y
˙
​
 =x−y,T>0.
Its characteristic polynomial and eigenvalues are

Tλ 
2
 +(1−aT)λ+(b−a)=0,
λ 
±
​
 = 
2T
aT−1± 
(1−aT) 
2
 −4T(b−a)
​
 
​
 .
The equilibrium is asymptotically stable exactly when

b>a,aT<1.
For a>0, the candidate Hopf boundary is T=1/a, with frequency  
a(b−a)
​
 .

Crucially, this filter corresponds to an exponentially distributed memory:

y(t)=∫ 
0
∞
​
 T 
−1
 e 
−s/T
 x(t−s)ds
when the filter and past history are consistent. If a=0, it remains stable for every finite T, whereas a fixed delay of the same mean destabilizes when bT>π/2. Therefore, even equal mean response times can produce different stability outcomes. For suitable systems, deliberately designed delayed feedback can also stabilize an unstable periodic orbit; see Pyragas’ original control paper. This does not imply that adding arbitrary delay improves control.

Representative mechanisms across domains.

Domain	Defensible mechanism and evidence	Important limit
Population regulation	Delayed density dependence:  
N
˙
 =rN[1−N(t−τ)/K]. Linearizing about N=K gives  
z
˙
 =−rz(t−τ), hence local exponential stability for rτ<π/2. Hutchinson, Circular Causal Systems in Ecology.	This is a particular delayed logistic model, not a universal population equation.
Predator–prey interactions	Explicit prey and predator populations create response lags even in ordinary differential equations. Classical Lotka–Volterra equations have neutrally stable closed orbits; adding resource limitation and saturating consumption changes stability. Hutchinson discusses the distinction between idealized interaction cycles and natural observations in the same original essay.	A phase lag between prey and predator is not evidence of a discrete time delay. Cycles alone do not identify their cause.
Endocrine regulation	Constant CRH stimulation produced ultradian ACTH/glucocorticoid oscillations in experimental work supporting a peripheral pituitary–adrenal oscillator. Biosynthesis and feedback introduce response times. Walker et al., 2012.	Physiological oscillations can be functional. Oscillation is not synonymous with regulatory failure or crisis.
Gene regulation	The synthetic repressilator links three transcriptional repressors in a negative-feedback ring and produces noisy oscillations in individual bacteria. Elowitz and Leibler, 2000.	Multistage transcription, translation and degradation can supply phase lag without a literal fixed-delay term.
Chemical oscillation	The Oregonator reduces the Belousov reaction mechanism to three intermediates and demonstrates stable limit-cycle behavior. Autocatalytic production and restoration of inhibition are mechanistically identifiable. Field and Noyes, 1974, original paper text.	These are nonlinear reaction-rate equations maintained away from equilibrium, not evidence that every expanding system must crash.
Power-grid control	Delayed decentralized frequency-based control can introduce instabilities; topology and averaging of measurements alter stability. In studied network motifs, sufficiently long measurement averaging improved stability. Schäfer et al., 2016.	Averaging duration and pure transport/reaction delay are different quantities. Stability also depends on inertia, damping, coupling and controller gain.
Epidemics and behavior	A delayed prevalence-dependent contact reduction can generate several epidemic waves without seasonal forcing. The model modifies transmission as β[1−r(I(t−τ)/N)]SI/N. Mahmud et al., 2025.	This is a modeling result, not proof of the cause of observed waves. Their wave count is nonmonotonic in delay: both very short and very long delays can yield a single wave.
Early-warning signals: the precise inference and its limits.

The elementary calculation is a locally stationary Ornstein–Uhlenbeck approximation:

dZ=−κZdt+σdW 
t
​
 ,κ>0.
It gives

Var(Z)= 
2κ
σ 
2
 
​
 ,Corr[Z(t),Z(t+Δ)]=e 
−κΔ
 ,t 
recovery
​
 =1/κ.
With fixed noise strength and sufficiently slow parameter change, decreasing restoring rate κ therefore increases variance, persistence and recovery time. This is the basis for critical-slowing-down indicators.

There is experimental support, not just analogy: replicated Daphnia populations undergoing controlled deterioration showed warning statistics before a transcritical bifurcation. However, baseline/reference populations materially improved interpretation. Drake and Griffen, 2010. A disease-emergence study also trained warning models on simulations and evaluated them on several epidemiological datasets; this supports application-specific usefulness, not universal forecasting. Brett and Rohani, 2020.

The main caveats are:

Changing variance need not mean weakening stability. In the displayed formula, greater σ increases variance with unchanged κ. Changing noise color can change autocorrelation. Trends, measurement changes, sampling and detrending also matter.

Hopf warnings differ from a zero-frequency tipping point. An oscillatory mode has a decaying envelope and oscillating correlations. For an isotropic two-dimensional linear oscillator, one coordinate has autocorrelation e 
−κΔ
 cos(ωΔ); a fixed lag statistic need not rise toward one.

Local resilience is not global basin safety. A system can recover rapidly from small disturbances yet escape under a sufficiently large shock.

Retrospective selection biases warnings. Selecting only trajectories that later crashed can create apparent warning patterns even when transitions occurred by chance. Boettiger and Hastings, Early warning signals and the prosecutor’s fallacy.

Not all tipping involves loss of local stability. Noise can cause escape from an existing basin; sufficiently rapid external change can cause failure to track an attractor without a bifurcation of the frozen system. Such mechanisms need not supply the familiar critical-slowing-down warning. Ashwin et al., Tipping points in open systems.

Hence “warning statistic increased” is evidence to compare against alternative models and out-of-sample false-alarm rates—not an identified mechanism or crash date.

Self-organized criticality is a separate hypothesis.

The original sandpile construction concerns driven, spatially interacting threshold systems that organize into a critical state with avalanches across scales. It is not another name for delayed negative feedback, an oscillation, or a saddle-node bifurcation. Bak, Tang and Wiesenfeld, 1987.

Heavy tails, apparent power laws or bursts do not identify SOC. As a concrete counterexample, thresholded stochastic processes can yield apparently scale-free event statistics without the proposed critical mechanism. Touboul and Destexhe, 2010. Finance-specific SOC claims require evidence about the driving, redistribution, dissipation, scaling and competing generative models.

A better formal template for the analogy.

Treat the following as a proposed modeling framework, not an established universal law:

dx 
t
​
 
r
˙
  
t
​
 
T 
u
˙
  
t
​
 
​
  
=f(x 
t
​
 ,r 
t
​
 ,u 
t
​
 ;θ 
t
​
 )dt+Σ(x 
t
​
 ,t)dW 
t
​
 ,
=s(r 
t
​
 )−c(x 
t
​
 ,r 
t
​
 ),
=h(∫ 
0
∞
​
 K(s)x 
t−s
​
 ds, E 
t
​
 [x 
t+H
​
 ])−u 
t
​
 .
​
 
Here x contains interacting activities, r finite resources or buffers, u inhibitory/control responses, and K a specified memory kernel. Omit components unsupported by the application.

This improves on  
x
˙
 =A(x)R−I(x(t−τ)) by making resource depletion, response dynamics and noise explicit. In finance, the expectation term flags a major difference: agents can anticipate policy and one another, change strategies, and alter effective coefficients. That is a modeling distinction, not a claim that natural systems never anticipate or adapt.

Linearization should determine whether the relevant failure is a real eigenvalue crossing, an oscillatory crossing, transient amplification, or none of these. Nonlinear basin analysis and explicit constraints are then needed to study large shocks and failure. The analogy generates candidate mechanisms; identifying a financial mechanism still requires financial data and institutional detail.