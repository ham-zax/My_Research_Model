# MFSM research direction: reassessment of 2026-09-27

Status: owner-approved direction. It supersedes earlier "next step" wording
where the two conflict. It does not revise any frozen protocol or result.

## Summary

The real-market experiments have not failed for lack of features. They could
not answer the edge question at the sample sizes available. The executable
simulation now answers questions in hours. It should decide which real
measurement is worth acquiring and how many events a real test needs, before
more real-data feature work is done.

## Where each strand stands

### Canonical model

- The specification (`Market_Feedback_State_Model_Canonical.md`, about 2,700
  lines) is careful and anti-overclaiming, but most of it is not executable.
- Only the funding, impact and delay core runs:
  - `src/mfsm_reference/` (MFSM-RE-1, deterministic);
  - `src/mfsm_sim/` (MFSM-SIM-1, stochastic).
- The network (W), diversity (D), confirmation (Q) and termination (M) objects
  have no equations or tests.
- Risk: a vocabulary that describes everything and predicts nothing specific.

### Real-market experiments (BTC)

| Experiment | Outcome | Record |
|---|---|---|
| E001, original | Blocked: feed timing bounds and liquidation notional unsupported | `docs/e001_measurement_decision.md` |
| Exploratory hourly BTC | Brier gain 0.000168, unstable; both models lost to a historical-rate forecast | `docs/e001_exploratory_btc_result.md` |
| Free spot-flow screen | Worse than the price-and-volume baseline on reserved 2026 months | `docs/mfsm_free_btc_flow_001_result.md` |
| MFSM-BTC-RESPONSE-1 extraction | Impact coefficient for 19 of 20 events; replenishment for none (the book is only 50 levels deep) | commit `ba7096c`, `docs/mfsm_sim_edge_plan.md` (Parked work) |

The binding constraint is **event count**. We have about 20 usable development
selloffs. In the simulation, per-trade P&L has a standard deviation of about 8
around edges of 1–3. A paired test needs on the order of
`(2 * sd / edge)^2`, roughly 30–250 events, and more for small edges. None of
the real tests could have detected a realistic edge in either direction.

### Simulation (MFSM-SIM-1)

- It gave the first quantitative answer: on development seeds, the state oracle
  earns above costs, so the mechanism can create an edge in its own world.
- It has already exposed one generator artifact: news repriced without trades.
- Its main danger is circularity, because a world built from MFSM's rules can
  flatter MFSM. The guards are:
  - an equal-budget flexible comparator (S5);
  - misspecified test seeds (`ood`) with different rules;
  - the oracle upper bound;
  - a single scoring run on frozen seeds.

### The underlying idea

- Separating forced, reverting selling from permanent information, and
  anticipating liquidation cascades, is established in the literature
  (Brunnermeier and Pedersen) and is actively traded in crypto (liquidation
  maps, open interest, funding).
- If an edge exists, it comes from **better measurement of leverage and flow,
  and speed**. The framework's own contribution is deciding which measurement
  matters and when the answer is `not_identified`.

## Decisions

1. **The simulation is the main line.** Finish the edge question on MFSM-SIM-1
   through one frozen scoring run. See
   [the implementation plan](mfsm_sim_edge_implementation_plan.md).
2. **Two headline outputs:**
   - **value of information**: which hidden quantity carries the edge;
   - **required sample size**: how many real events a test of that edge needs.

   Together these decide whether any real BTC test is feasible.
3. **Real-data feature work is paused** until decision 2 is answered. The likely
   next real-data move is **more events** or **direct leverage measurement**,
   not refined features. Candidates: continuous history instead of
   first-of-month samples, a lower trigger threshold, and open interest,
   liquidation prints or funding.
4. **Canonical model: no new concepts.** Each section is tied to executable code
   or marked untested. The specification converges on what can run. No
   mechanism is added because a symbol lacks an equation (existing rule in
   `docs/mfsm_model_improvement_plan.md`).
5. **First application is risk control, not alpha.** "Do not buy the dip during
   a forced-selling cascade" is easier to validate and useful sooner than a
   standalone trading edge. The simulation reports it as well: S1 buy-dip
   performance with and without an MFSM veto.
6. **Parked:**
   - E001 original (blocked);
   - the BTC top-20 replenishment revision, until value of information says
     replenishment matters.

   Sealed as before: the ETH holdout, and every earlier frozen protocol.

## Working arrangement

- Work happens on `main`. Implementation tasks are executed by coding agents
  from [the implementation plan](mfsm_sim_edge_implementation_plan.md).
- The orchestrator (the owner's primary Claude session) reviews each task and
  decides on anything that the plan marks as an **orchestrator decision**.
