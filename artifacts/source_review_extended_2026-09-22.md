# Extended Source Review — 2026-09-22

Status: supporting research artifact
Purpose: preserve the source-by-source review that motivated the post-canonical MFSM revisions on shock-conditioned fragility, strategic coordination, term-structured absorptive capacity, constraint sensitivity, controller topology, and measurement error.

## Executive result

The source set supports a deeper formulation of MFSM:

> **Markets should be analyzed by how the current structural state transforms the response law governing the next disturbance.**

The key revision is that fragility should not be treated as a single scalar attached to a trend. A system can be robust to one disturbance and fragile to another; it can also contain latent coordination fragility without any preceding price trend.

The research therefore motivates:

- a latent structural state and explicit observation model;
- fully specified structural interventions rather than shock labels alone;
- a conditional counterfactual path law \(\mathcal P_{t,h}^{\delta}\);
- shock-conditioned consequence \(F_t(\delta,h;\ell,\rho)\);
- structural susceptibility across disturbance amplitude;
- horizon-dependent opposing capacity \(R^-_t(h)\);
- a local constraint-sensitivity Jacobian \(\mathbf\Chi_{B,t}\) plus finite-shock buffer response \(\Delta\mathbf B_t^{\delta}\);
- strategic-complementarity / coordination state \(\Gamma_t\);
- dynamic functional diversity \(D_t\);
- explicit controller topology for opposing mechanisms;
- stronger identification discipline around inferred endogeneity and criticality.

## Source audit

### Diamond–Dybvig / bank-run coordination

Primary link:
- https://www.journals.uchicago.edu/doi/10.1086/261155

Orientation source reviewed earlier:
- https://www.investopedia.com/diamond-dybrig-model-theory-of-bank-runs-6892094

Transfer:
- multiple equilibria and strategic complementarity;
- a system can be fundamentally viable yet fragile because each participant's optimal action depends on expected actions of others;
- fragility can exist without a preceding price trend.

MFSM implication:
- expectations state \(Q_t\) should include a coordination/strategic-complementarity component \(\Gamma_t\);
- trend diagnostics cannot be the only entry point to the model.

Boundary:
- not every crash or liquidation cascade is a bank-run coordination game.

### Filimonov–Sornette, apparent criticality in financial time series

Link:
- https://ideas.repec.org/a/taf/quantf/v15y2015i8p1293-1314.html

Transfer:
- inferred endogeneity can be badly biased by misspecified kernels, outliers, nonstationarity, edge effects, and regime mixing;
- apparent criticality can be an estimation artifact.

MFSM implication:
- distinguish latent structural state from measured proxies:
  \[
  \mathbf Y_t = g(\mathbf Z_t;\psi_t)+\eta_t.
  \]
- estimated amplification \(\hat A_t\), connectivity \(\hat C_t\), or endogeneity are not the latent quantities themselves.

Boundary:
- failure of one Hawkes specification does not imply endogeneity is unmeasurable.

### Kiyotaki–Moore, credit cycles

Link:
- https://msuweb.montclair.edu/~lebelp/KyotakiMooreCreditCyclesJPE1997.pdf

Transfer:
- asset prices can alter collateral capacity and therefore future demand;
- small shocks can be amplified because the price changes the constraint that governs subsequent behavior.

MFSM implication:
- separate current headroom \(H_t\) from the local buffer-sensitivity Jacobian:
  \[
  \mathbf\Chi_{B,t}(h)
  =
  D_{\mathbf z}
  E[
  \mathbf B_{t+h}^{0}
  \mid
  \mathbf Z_t=\mathbf z,\mathcal I_t
  ].
  \]
- for finite interventions, especially near thresholds, use \(\Delta\mathbf B_t^{\delta}\) rather than assuming a derivative remains valid;
- two markets can have equal headroom but very different sensitivity of future headroom to state changes.

### Minsky, financial-instability / financing composition

Link:
- https://www.levyinstitute.org/pubs/wp74.pdf

Transfer:
- financing composition matters, not only leverage quantity;
- extended favorable conditions can change the liability structure toward greater refinancing dependence.

MFSM implication:
- buffer state \(B_t\) should allow composition and maturity structure, not merely scalar leverage;
- state deterioration can occur through liability composition even while prices remain strong.

Boundary:
- Minsky's hedge/speculative/Ponzi categories are not a mechanical crash clock.

### Mangan–Alon, feed-forward-loop motifs

Link:
- https://www.weizmann.ac.il/mcb/alon/sites/mcb.UriAlon/files/structure_and_function_of_the_feed-forward_loop_network_motif.pdf

Transfer:
- controller topology matters;
- coherent and incoherent feed-forward loops have distinct timing functions;
- not every opposing pathway guarantees a simple pulse followed by shutdown.

MFSM implication:
- attach a **controller topology** to opposing mechanisms:
  \[
  \mathcal C_I \in \{\text{feed-forward, feedback, integral, depletion, saturation, threshold}\}.
  \]

Boundary:
- feed-forward antagonism and delayed feedback are not the same causal graph.

### Brunnermeier–Pedersen, market and funding liquidity

Link:
- https://www.princeton.edu/~markus/research/papers/liquidity.pdf?source=post_page---------------------------

Transfer:
- funding liquidity and market liquidity can reinforce one another;
- margin/loss spirals are state-dependent;
- margins can be stabilizing under some beliefs and conditions.

MFSM implication:
- feedback sign is state-dependent;
- \(H\), \(R^-\), and \(A\) interact nonlinearly.

### Uniswap whitepaper

Link:
- https://app.uniswap.org/whitepaper.pdf

Transfer:
- \(xy=k\) is a contractual reserve invariant;
- external arbitrage links pool price to outside prices;
- averaging/oracle design exposes a robustness-versus-responsiveness tradeoff.

MFSM implication:
- distinguish protocol constraints from equilibrium-restoring forces;
- smoothing/averaging belongs in response-time and measurement design, not as evidence of thermodynamic equivalence.

Boundary:
- \(xy=k\) is not a chemical equilibrium constant and is not itself a positive-feedback engine.

### Milionis et al., Loss-Versus-Rebalancing

Link:
- https://arxiv.org/pdf/2208.06046v2

Transfer:
- passive liquidity provision has an economic carrying cost related to adverse selection / arbitrage and foregone rebalancing;
- available liquidity depends on whether supplying it remains economically viable.

MFSM implication:
- give \(R^-_t\) replenishment and withdrawal economics:
  \[
  \dot R^-_t = \rho^-(\text{fees, spreads, convergence, capital cost}) - c^-(\text{losses, adverse selection, margin, redemptions}).
  \]

### BIS, crypto carry

Link:
- https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf

Transfer:
- carry can reflect leveraged trend-chasing, attention, and scarcity of arbitrage capital;
- high carry contains information about subsequent risk in the studied sample.

MFSM implication:
- crypto carry is a candidate observable that jointly loads on amplification, leverage demand, and limited \(R^-\).

Boundary:
- not a universal deterministic crash threshold.

### Baker–Wurgler, market timing and capital structure

Link:
- https://pages.stern.nyu.edu/~jwurgler/papers/capstruct.pdf

Transfer:
- high market valuations can induce corporate equity issuance.

MFSM implication:
- concrete delayed endogenous counterflow:
  \[
  P\uparrow \rightarrow \text{issuance incentive}\uparrow \rightarrow \text{future supply}\uparrow.
  \]

### Bank of England, money creation

Link:
- https://www.bankofengland.co.uk/-/media/boe/files/quarterly%20bulletin/2014/money-creation-in-the-modern-economy.pdf

Transfer:
- bank lending creates deposits;
- aggregate "cash" is not a conserved stock constraining all buying.

MFSM implication:
- capacity must be actor-, collateral-, balance-sheet-, mandate-, and deadline-specific;
- reject "the market has run out of money" as a generic \(R^+\) story.

### Housing supply and bubbles

Links:
- https://www.nber.org/system/files/working_papers/w14193/w14193.pdf
- https://www.nber.org/papers/w14193
- https://scholar.harvard.edu/files/glaeser/files/housing_supply_and_housing_bubbles.pdf?m=1360041691

Transfer:
- elastic supply can damp price appreciation while causing more construction/overbuilding;
- suppressing one visible variable can shift adjustment into quantity.

MFSM implication:
- robustness must be multidimensional;
- lower price volatility is not automatically lower real-resource fragility.

### NBER w35164, commodity / macro control

Link:
- https://www.nber.org/system/files/working_papers/w35164/w35164.pdf

Transfer:
- optimal control depends on the economic architecture and exposure type;
- one controller is not universal across different "plants."

MFSM implication:
- policy/control variables must be system-specific, not imported as universal stabilizers.

### MIT thermodynamics / Gibbs free energy / chemical equilibrium

Links:
- https://ocw.mit.edu/courses/5-60-thermodynamics-kinetics-spring-2008/resources/lecture-13-gibbs-free-energy/
- https://ocw.mit.edu/courses/5-60-thermodynamics-kinetics-spring-2008/resources/5_60_lecture14/
- https://ocw.mit.edu/courses/5-60-thermodynamics-kinetics-spring-2008/resources/lecture-15-chemical-equilibrium/
- https://ocw.mit.edu/courses/5-60-thermodynamics-kinetics-spring-2008/52946f97fcb18850c32e9d4b8f6bab6a_5_60_lecture15.pdf
- https://ocw.mit.edu/courses/5-60-thermodynamics-kinetics-spring-2008/pages/lecture-notes/

Transfer:
- potentials/gradients can generate directed flows toward equilibrium under stated physical assumptions.

Boundary:
- no established universal Gibbs potential exists for financial markets;
- do not equate \(K_p\), chemical equilibrium, and AMM invariants.

### Investopedia, banks and lending

Link:
- https://www.investopedia.com/articles/investing/022416/why-banks-dont-need-your-money-make-loans.asp

Use:
- secondary explanation of endogenous deposit creation.

Repository rule:
- prefer the Bank of England primary source for canonical claims.

### Danielsson–Shin, endogenous risk

Link:
- https://www.riskresearch.org/files/DanielssonShin2002.pdf

Transfer:
- participant responses to market conditions can generate the risk they are responding to;
- common risk rules can synchronize behavior.

MFSM implication:
- separate exogenous trigger from endogenous amplification;
- large price movement alone does not identify the amplifier.

### Duffie, slow-moving capital

Link:
- https://web.stanford.edu/~duffie/PresidentialAddressApril15NormalFormat.pdf

Transfer:
- stabilizing capital can arrive gradually after a shock;
- prices can overshoot while capital is still mobilizing.

MFSM implication:
- replace a scalar \(R^-_t\) with a horizon-dependent capacity term:
  \[
  R^-_t(h)=\text{opposing capacity able to act by horizon }h.
  \]

### Oil supply response

Links:
- https://econpapers.repec.org/RePEc%3Asae%3Aenejou%3Av%3A40%3Ay%3A2019%3Ai%3A3%3Ap%3A1-30
- https://www.nber.org/system/files/working_papers/w23973/w23973.pdf
- https://ideas.repec.org/p/nbr/nberwo/23973.html
- https://www.rff.org/publications/journal-articles/unconventional-oil-supply-boom-aggregate-price-response-microdata/

Transfer:
- supply response is distributed over time rather than arriving at one fixed lag.

MFSM implication:
- strengthens the use of response kernels \(K(s)\) rather than scalar \(\tau\).

### Federal Reserve, credit-market sentiment

Link:
- https://www.federalreserve.gov/econresdata/feds/2015/files/2015028pap.pdf

Transfer:
- favorable credit pricing is associated with changes in financing composition and future outcomes;
- underwriting / issuer composition can deteriorate during favorable conditions.

MFSM implication:
- "good times" can alter composition and future vulnerability even without immediate visible stress.

Boundary:
- preserve the paper's identification limitations.

### SEC, equity/options market conditions in early 2021

Link:
- https://www.sec.gov/files/staff-report-equity-options-market-struction-conditions-early-2021.pdf

Transfer:
- decompose mechanisms rather than infer from popular narratives;
- short covering occurred, but cannot mechanically explain the whole episode;
- clearing/margin demands are distinct from speculative narratives.

MFSM implication:
- short interest is potential \(R^+\), not proof of squeeze flow;
- event reconstruction should separate fuel, realized flow, and constraint effects.

### Bank of England, anatomy of 2022 gilt crisis

Link:
- https://www.bankofengland.co.uk/working-paper/2023/an-anatomy-of-the-2022-gilt-market-crisis

Transfer:
- unusually strong empirical example of interaction among leverage, collateral deadlines, forced selling, market depth, and intermediary constraints.

MFSM implication:
- strengthens \(H \times R^- \times W\) and deadline mismatch.

### Financial Times gilt / hedge-fund article

Link:
- https://www.ft.com/content/32a59442-54d0-485f-a0e1-3d341cbeda41

Status:
- partially accessible/paywalled.

Repository rule:
- use Bank of England primary research for canonical mechanism claims.

### Bitcoin terminal issuance

Link:
- https://www.investopedia.com/tech/what-happens-bitcoin-after-21-million-mined/

Transfer:
- Bitcoin issuance is protocol-constrained rather than price-elastic like commodity production;
- long-run miner revenue transitions toward transaction fees as subsidy issuance approaches zero.

Boundary:
- rising BTC price does not create a conventional physical-supply antagonist analogous to oil.

### Guardian LDI live coverage

Link:
- https://www.theguardian.com/business/live/2022/oct/10/bank-of-england-pension-fund-support-nobel-economics-stock-markets-recession-business-live

Use:
- contemporaneous chronology/context.

Repository rule:
- later BoE reconstruction should carry greater evidentiary weight.

### Hommes / in 't Veld heterogeneous expectations

Link:
- https://papers.tinbergen.nl/15088.pdf

Transfer:
- strategy selection and relative performance can change behavioral composition endogenously.

MFSM implication:
- functional diversity is dynamic:
  \[
  D_{t+1}=g(D_t,\text{relative performance},\text{flows},\text{constraints}).
  \]
- strategy success can manufacture crowding.

### Yi–Huang–Simon–Doyle, integral feedback in bacterial chemotaxis

Link:
- https://www.pnas.org/doi/pdf/10.1073/pnas.97.9.4649

Transfer:
- integral feedback is a distinct controller topology capable of robust adaptation under specified closed-loop conditions.

MFSM implication:
- ask whether a financial stabilizer reacts to current deviation, accumulated deviation, or a threshold.

Boundary:
- market mean reversion is not automatically integral control.

### Robert May, complexity and stability

Link:
- https://www.nature.com/articles/238413a0

Transfer:
- local stability is about the spectrum of the interaction matrix, not raw component count.

Boundary:
- May's random-matrix assumptions do not justify "more financial connectivity always means less stability."

### Carlson–Doyle, Highly Optimized Tolerance

Link:
- https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevLett.84.2529/fulltext

Transfer:
- systems can be highly robust to familiar disturbances and highly fragile to unanticipated ones;
- robustness and fragility coexist.

MFSM implication:
- replace scalar fragility with disturbance-specific path-response analysis;
- distinguish shock-conditioned consequence
  \[
  F_t(\delta,h;\ell,\rho)
  \]
  from structural susceptibility across intervention amplitude.

### AMOC article

Link:
- https://www.theguardian.com/environment/2025/feb/26/total-collapse-of-vital-atlantic-currents-unlikely-this-century-study-finds

Transfer:
- severe functional degradation can occur without a formal "total collapse."

MFSM implication:
- do not define failure only as a bifurcation or complete systemic collapse;
- large degradation within the same nominal regime matters.

Boundary:
- secondary source; do not use for quantitative climate claims inside MFSM.

### Heemeijer et al. / positive vs negative expectations feedback

Link:
- https://pure.uva.nl/ws/files/4138569/56651_286737.pdf

Transfer:
- experimental evidence that the **sign of expectations feedback** changes aggregate behavior: positive-feedback environments generate qualitatively different aggregate dynamics from negative-feedback environments.

MFSM implication:
- sign of expectations feedback belongs in \(Q_t\) / \(J_t\), not only in realized momentum.

### Harvard DASH UUID

Link:
- https://dash.harvard.edu/bitstreams/7312037c-57df-6bd4-e053-0100007fdf3b/download

Status:
- document identity could not be established reliably during review.

Repository rule:
- do not infer or cite a finding until the document is identified.

## Model-level conclusions

The source set supports the following revisions:

1. **Broaden the invariant question.**
   From "How is the current trend changing the response to the next disturbance?" to:
   > **How is the current structural state changing the system's response law for the next disturbance?**

2. **Distinguish disturbance class from structural intervention.**
   A label such as funding withdrawal or run risk must be instantiated by target, amplitude, direction, onset, temporal profile, and any stochastic component.

3. **Use a counterfactual path law as the theoretical response object.**
   \[
   \mathcal P_{t,h}^{\delta}
   =
   \mathcal L(
   \mathbf Z_{[t,t+h]}^{\delta}
   \mid
   \mathcal I_t
   ).
   \]
   Terminal expected state is only one derived projection.

4. **Define shock-conditioned consequence through explicit loss and severity functionals.**
   \[
   F_t(\delta,h;\ell,\rho)
   =
   \rho_{\mathcal P_{t,h}^{\delta}}
   [
   \ell(\mathbf Z_{[t,t+h]}^{\delta})
   ].
   \]

5. **Separate shock consequence from structural susceptibility.**
   Study
   \[
   a\mapsto F_t(\delta(c,a),h;\ell,\rho)
   \]
   and critical disturbance amplitudes rather than comparing consequences under arbitrarily different shock magnitudes.

6. **Make opposing capacity horizon-dependent.**
   \[
   R^-_t(h).
   \]

7. **Separate headroom, local sensitivity, and finite-shock buffer response.**
   \[
   H_t,
   \qquad
   \mathbf\Chi_{B,t}(h),
   \qquad
   \Delta\mathbf B_t^{\delta}(s).
   \]

8. **Represent strategic complementarity explicitly.**
   \[
   \Gamma_t
   \]
   within the expectations/coordination state.

9. **Make functional diversity evolutionary.**
   \[
   D_{t+1}=g(D_t,\text{relative strategy performance},\text{flows},\text{constraints}).
   \]

10. **Represent opposing mechanisms by topology as well as magnitude.**
    \[
    \mathcal C_I.
    \]

11. **Add an observation model.**
    \[
    Y_t=g(Z_t;\psi_t)+\eta_t.
    \]

12. **Do not interpret robustness to common shocks as generic safety.**
    Validation should include disturbance-class, amplitude, and horizon holdouts where feasible.
