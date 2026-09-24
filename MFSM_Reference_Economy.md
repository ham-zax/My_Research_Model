# MFSM reference economy: constrained liquidation and delayed buying

Version: `MFSM-RE-1`
Date: 2026-09-24
Status: fully specified deterministic theoretical example; no empirical calibration

This is one restricted member of the model family in
[the canonical specification](Market_Feedback_State_Model_Canonical.md).
It makes the funding/impact/delay mechanism executable. It does not claim a
complete market, a new financial mechanism, an estimated causal effect, or an
edge. Its deterministic path law is a point mass conditional on the initial
state and parameters. Probabilities require an additional justified distribution.

## 1. Boundary, units, and assumptions

There is one asset and three trading roles: a leveraged long holder L, a dealer D,
and a delayed buyer S. Quantities are asset units; cash, debt, and headroom are
currency units; prices are currency per asset unit. One tick is a declared
abstract decision interval, with no claim that it is an exchange second.

L has a fixed debt B >= 0, owed to a passive lender outside the trading system.
The matching loan receivable is recorded at the boundary. Principal, interest,
and funding access do not change during this finite horizon. Sale proceeds stay
in L's collateral cash account. There is no new borrowing, shorting, interest,
fee, dividend, or default settlement within the modeled horizon.

The public reservation-value benchmark v > 0 is constant after the initial
intervention. It is an assumed exogenous input, not a claim that fundamental value
is observable in real markets. The buyer treats v as its valuation and follows
the rule below; rational expectations and optimal behavior are not assumed.

Parameters are fixed: inventory impact lambda >= 0 (inverse asset units), dealer
inventory ceiling Q >= 0, maintenance ratio 0 < m < 1, restoration ratio
m < m_R < 1, buyer response kappa >= 0 (asset units per tick), signal delay
tau >= 0 (integer ticks), and margin deadline d_max >= 1 (integer ticks).

An initial state supplies nonnegative finite cash c_i and holdings q_i for each
role, with q_D <= Q, the last at most tau observed dislocations, the consecutive
breach count, and the mode. Missing *initial* signal prehistory is explicitly zero
in the synthetic examples. Real missing data must not inherit this assumption.

## 2. State, observation, and valuation

The closed state consists of the tick, the three cash/holding pairs, the bounded
signal queue, consecutive margin-breach count, and hybrid mode. The fixed debt
and parameters belong to the structural law. There is no evolving object outside
this state without an explicit rule. A finite tick queue realizes the stated
discrete delay exactly.

The dealer's marginal reservation curve sets the mark:

\[
p(q_D)=v e^{-\lambda q_D}.
\]

L's equity and maintenance headroom are derived:

\[
E_L=c_L+p q_L-B,\qquad H_L=c_L+(1-m)p q_L-B.
\]

Dealer/buyer cash and inventory limits are primitive constraints. H is derived
from the balance sheet; response-qualified R-minus is derived from entire paths.
They are not independent reservoirs. A dollar received by L is paid by D; a
dollar replenishing D through a buyer trade is paid by S.

For this theoretical reference the observation law is exact: Y_n = Z_n, and the
initial state is known. This is a deliberate idealization, not an estimator for
hidden real-world positions. The benchmark is also known to these model agents.

## 3. Self-financing execution

A holder sale f >= 0 to D traverses the reservation curve. Starting at mark p,
its total proceeds are

\[
A_p(f)=\begin{cases}
p(1-e^{-\lambda f})/\lambda,&\lambda>0,\\
pf,&\lambda=0.
\end{cases}
\]

Transfer f units from L to D and A_p(f) currency from D to L. The new mark is
p exp(-lambda f). No order is executed entirely at the old marginal quote.

A buyer purchase b >= 0 from D reverses traversal of the same curve:

\[
C_p(b)=\begin{cases}
p(e^{\lambda b}-1)/\lambda,&\lambda>0,\\
pb,&\lambda=0.
\end{cases}
\]

Transfer b units from D to S and C_p(b) currency from S to D. The new mark is
p exp(lambda b). Because b <= q_D, the price cannot exceed v. At unchanged v,
an exact reverse traversal has the same total payment; the impact rule alone
does not give a free round-trip gain.

For cash C, the maximum affordable buyer quantity is log(1+lambda C/p)/lambda.
The maximum quantity D can acquire is -log(1-lambda C/p)/lambda when
lambda C < p, and is cash-unconstrained when lambda C >= p; finite seller
inventory and Q still bind. At lambda=0 both limits are C/p. These are inverses
of the execution integrals, not estimates from displayed depth.

## 4. One complete transition

Every step uses this ordering. Cash/quantity limits always apply to the updated
accounts, so a resource cannot be spent twice in the tick.

1. A terminal mode is absorbing. If initial marked equity is negative, enter
   `DEFAULT` immediately, retaining assets, cash, and debt as recorded.
2. Observe the current dislocation g_n = 1 - p_n/v. Read g_(n-tau) from the queue;
   when tau=0 use g_n. Set desired buyer quantity to kappa g_(n-tau).
3. Fill that buyer order up to current dealer inventory and buyer affordability.
   Update both accounts and the mark using C_p. This models capital that arrives
   before this tick's margin processing. No future observation enters the order.
4. Recompute L's equity and maintenance headroom at the new mark. If H_L < 0,
   request a sale toward the higher restoration ratio, using this mark:

   \[
   f^*=\min\left(q_L,
   \frac{[B-c_L-(1-m_R)pq_L]_+}{m_R p}\right).
   \]

   If H_L >= 0, request zero. This is a specified mechanical sizing rule that
   ignores its own subsequent impact; it is not an optimal liquidation policy.
5. Fill f* up to D's remaining inventory room and cash affordability. Transfer
   assets/cash using A_p and recompute the mark, equity, and headroom.
6. Negative final equity enters `DEFAULT`. Otherwise, negative headroom increments
   the consecutive breach count. Reaching d_max enters `MARGIN_FAILURE`; before d_max,
   use `MARGIN`. Nonnegative headroom resets the count to zero and mode to `NORMAL`.
7. Append the *start-of-tick* g_n to the bounded queue and advance the tick.

An initial insolvency cannot be rescued after default by a delayed buyer. A
margin failure is an unmet requirement, not necessarily negative equity.
Terminal accounts are retained; no debt write-off or recovery value is invented.
Loss functionals must include the terminal failure. An absorbing mark after
failure is a bookkeeping convention, not a forecast of subsequent market prices.

The implementation uses currency tolerance 1e-9 by default for equity/headroom
comparisons, and clips roundoff-sized negative transaction cash to zero.
The theoretical inequalities above use exact arithmetic. The executable rejects
nonfinite inputs, invalid ratios/delays, and lambda Q > 100 to avoid extreme
floating-point exponents. That numerical-domain restriction is not economics.

## 5. Interventions and outputs

A reference-value shock replaces v_0 with v_0-a, where 0 <= a < v_0, before the
first tick. Portfolios and the existing signal history are identical to baseline;
the state is revalued under the changed benchmark. A margin-rule shock changes
m and m_R before the first tick, subject to their admissible domain. The parameter
change, amplitude units, and baseline must be named. A cascade is an output.

For these deterministic paired paths, initial state and all unmodified parameters
are shared. There is no unreported noise coupling. A finite comparison can report:

- margin/default failure by tick h;
- minimum headroom, maximum discount to the scenario's v, and peak dealer inventory;
- total forced sales and first restoration of maintenance headroom;
- the separate distance from the old benchmark v_0.

Restoring margin and restoring a prior price are different events. Neither should
be silently substituted for the other or for liquidation of all obligations.

R-minus is obtained only after specifying a supported incoming-flow intervention,
its profile, the horizon, and a consequence tolerance, then solving the resulting
paths as in canonical section 7.3. This implementation does not label Q, cash/p,
or a scenario's realized purchases as prospective R-minus; it does not implement
an arbitrary stress-flow intervention or calculate R-minus numerically.

## 6. Derived propositions and their boundaries

### P1. Transaction accounting and bounded liquidation

Every internal trade gives one account precisely the cash/asset change removed
from another. Therefore total cash and asset units of L+D+S are conserved before
and at termination, up to numerical roundoff. L never buys, so cumulative forced
sales cannot exceed its initial holding. D never borrows, S never borrows, and
0 <= q_D <= Q. Marked wealth is not conserved: with total quantity M,
total marked trading equity is total cash + pM - B and changes with p.

These are model invariants. A violation is a mathematical/implementation defect,
not contrary empirical evidence about a market.

### P2. The no-impact limit restores margin when the trade can be funded

If lambda=0, initial E_L >= 0, H_L < 0, and D can fund and hold the requested sale,
then f* <= q_L and the filled sale reaches the restoration target exactly.
At the same price H_L rises by m p f. Since m_R > m, any remaining position has
positive maintenance headroom. This claim excludes binding dealer constraints.

### P3. A small forced sale can worsen headroom

Holding v fixed and starting just before L's execution, after sale f:

\[
H(f)=c_L+A_p(f)+(1-m)p e^{-\lambda f}(q_L-f)-B.
\]

Therefore

\[
H'(0)=p\{m-\lambda(1-m)q_L\}.
\]

A sufficiently small positive sale **reduces** headroom if
lambda(1-m)q_L > m. The exposure reduction is outweighed by the mark loss on
remaining holdings. This is a local result for the declared inventory curve and
execution convention; it is not a global cascade threshold or a universal score.
Actual sales are bounded by cash, inventory, and the termination rules.

### P4. Delayed buying can relieve constraints, but exhaustion need not rebound

At fixed v a buyer fill b > 0 raises the mark and L's headroom by
(1-m)q_L(p_after-p_before), while replenishing D's cash and inventory room.
It cannot lower L's immediate headroom under these assumptions. This does not
prove that changing delay or buyer aggressiveness monotonically improves every
entire path, because later forced orders and terminal timing can change.

If buyer response or buyer cash is zero, the dealer's inventory cannot fall. With v fixed,
the mark cannot rise. Once forced sales stop, it remains where it is. Thus seller
exhaustion alone creates no rebound in this economy.

With zero prehistory and q_D initially zero, the first possible nonzero buyer
signal comes from the start of tick 1 after a sale at tick 0. Its earliest action
is tick 1+tau. If a breach persists after every tick and d_max <= 1+tau, the deadline
terminates the path before that action. This is a timing statement with those
initial conditions, not a universal delay/deadline risk ratio.

### P5. A permanent benchmark decline need not reverse

Because q_D >= 0, p <= v at every active state. If v is permanently reduced below
v_0, even complete removal of the inventory discount restores at most v, not v_0.
Recovery of liquidity does not reverse the specified information change.

### P6. The transition is well defined in its stated domain

For finite nonnegative accounts, v > 0, admissible ratios, and finite Q, marks are
positive and both execution integrals are continuous and increasing. Their cash
limits are unique. The ordered min/cap operations select one fill at each stage;
the signal queue, deadline update, and default precedence select one next state.
Nonnegative holdings/cash and the inventory bound are preserved. Thus induction
gives a unique finite-horizon path, with terminal modes absorbing. No equilibrium
selection or unspecified conditional expectation remains in this member.

This proof concerns exact arithmetic. The tests also check representative
floating-point paths; they are not a machine proof over every possible input.

## 7. What this member does and does not identify

The reference instantiates M4 (threshold-driven selling) and M2 (delayed buying)
using existing canonical state categories. It does not identify these mechanisms
from prices alone. Other action rules can produce similar prices.

It omits short positions, endogenous lending terms, strategic anticipation,
information asymmetry, networks, entry/exit, and post-default settlement. The
dealer curve and buyer rule are assumptions, not optimization results. It is a
restricted long-side stress economy, not a simulator of a named exchange.

For real use, observation and structural uncertainty need explicit laws or
admissible sets. A response range over a stated parameter/model set is a
scenario range, not automatically a confidence interval. If admissible models
disagree on the sign of an effect, the structural conclusion is not identified.

## 8. Reproduce the mathematical examples

Implementation: [economy.py](src/mfsm_reference/economy.py).
Checks: [test_reference_economy.py](tests/test_reference_economy.py).

```bash
uv run --locked python scripts/run_mfsm_reference_economy.py
uv run --locked pytest -q tests/test_reference_economy.py
```

The runner prints synthetic scenarios with chosen, uncalibrated parameters.
No real prices, experiment labels, fitted probabilities, or trading returns enter
the calculation. The analytic propositions above carry their own assumptions.

Financial precedent: [Brunnermeier and Pedersen, Market Liquidity and Funding
Liquidity](https://www.princeton.edu/~markus/research/papers/liquidity.pdf) motivates
the interaction of funding constraints and liquidity. The equations and sequencing
in this reference are our declared simplification, not their estimated model.

## 9. Structural variants and incomplete observation

The [MFSM-RE-SENS-1 protocol](docs/mfsm_reference_sensitivity_protocol.md) and
[result](docs/mfsm_reference_sensitivity_result.md) extend this reference in
three controlled ways: a hyperbolic impact curve, fixed-lot forced selling, and
a finite distributed buyer delay. They also replace the idealized exact
observation `Y=Z` with a limited map for a non-identification example. The
default implementation remains the exponential, restoration-target, pure-delay
member above.

For the hyperbolic member, `p(q_D)=v/(1+lambda*q_D)`. Starting at inventory `q`,
selling `f` asset units to the dealer pays
`v/lambda * log((1+lambda*(q+f))/(1+lambda*q))` and buying `b` units from the
dealer costs `v/lambda * log((1+lambda*q)/(1+lambda*(q-b)))`. The continuous
limit at zero impact is `v` times the traded quantity. Fixed-lot selling requests
up to a declared number of units when headroom is negative; cash, inventory,
holdings, and the original termination rules still cap execution. A delay kernel
uses a normalized weighted sum of available start-of-tick dislocations, with
zero synthetic prehistory as specified in the protocol.

For any differentiable decreasing mark curve whose execution proceeds equal
the integral of its marginal mark, the local headroom response at dealer
inventory `q_D` is

\[
H'(0)=m p(q_D)+(1-m)q_L p'(q_D).
\]

Both curves have `p(0)=v` and `p'(0)=-lambda*v`, so they share the local
headroom slope at zero inventory. They need not agree for a finite sale or away
from zero inventory. The synthetic comparison shows such a finite difference;
it does not select the correct curve for any exchange.

Under limited observation, the same pre-shock mark, benchmark, and dealer
inventory can conceal different holder debt and therefore different forced-sale
responses. The reference's exact-observation uniqueness proposition applies
only when the full initial state and law are supplied. It cannot be promoted
to an observer's unique forecast from a price snapshot.
