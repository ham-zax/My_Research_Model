# Plan: simulate whether MFSM reasoning can produce a trading edge

Version: `MFSM-SIM-EDGE-PLAN-1`
Date: 2026-09-27
Status: Phases 1–2 built and tested on development seeds; no protocol frozen; no test-seed result

## Progress log

**2026-09-27: Phases 1–2 built (development only).**

- `src/mfsm_sim/world.py`: MFSM-SIM-1 transition. It reproduces
  `mfsm_reference.economy.step` exactly in the declared limit on nine reference
  and sensitivity scenarios (`tests/test_sim_world.py`).
- One deviation from the first draft: the delayed informed trader is two-sided.
  It sells its holdings when the mark is above value. Without this, delayed buying
  overshot permanently once `q_ref > 0`. In the RE-1 limit the mark never exceeds
  value, so the reduction is unchanged.
- `src/mfsm_sim/scenarios.py` (priors, seeded episodes), `harness.py` (paired
  execution, state oracle), `strategies.py` (S0–S3), and
  `scripts/run_mfsm_sim_edge.py` (development seeds only). 38 new tests pass;
  the full suite passes (281).
- **Development diagnostic, seeds 0–999, 799 triggered episodes**, P&L per episode
  for a 5-unit (~$500) position after 5 bps per leg; 95% paired bootstrap
  interval against flat:

  | Strategy | Mean P&L | Against flat |
  |---|---:|---|
  | S1 buy dip | +2.02 | [1.33, 2.73] |
  | S2 sell dip | −5.36 | [−6.16, −4.61] |
  | S3 flow rule (untuned) | +3.46 | [2.85, 4.09] |
  | S6 state oracle | +4.90 | [4.32, 5.47] |

  Q1 on development seeds: an edge above costs exists in this world.
- **Design flaw found before building S4.** S3 captures about 70% of the oracle
  edge because in MFSM-SIM-1 news moves the mark through trade-less quote
  repricing (the anchor), while forced and exogenous selling moves it through
  trades. Net sell flow per unit of decline therefore nearly reveals the
  scenario. Real news also arrives with heavy informed and stop-driven selling.
  Before S4, add **informed news selling**: a declared, randomly drawn share of
  each news move is transmitted by informed sell orders against the dealer, and
  the rest by repricing. Otherwise the S4-versus-S3 comparison measures an
  artifact of the generator. This addition must also reduce to the current member
  when the informed share is zero.

## Next steps (ordered)

Direction: [research direction 2026-09-27](mfsm_research_direction_2026-09-27.md). Agent-executable detail for each step: [implementation plan](mfsm_sim_edge_implementation_plan.md) (T1 = step 1, T2 = step 3, T3 = step 4, T4 = risk-control view, T5 = step 5, T6 = step 6, T7 = step 7 plus sample size, T8 = step 8).

Each step ends with tests passing and a short entry in the progress log. Only
development seeds are used until step 6 freezes the protocol.

1. **Informed news selling (Phase 2b).** Add `informed_share` in `[0, 1]` to
   `WorldLaw`, drawn per episode from a declared prior (development default
   `U(0.3, 0.9)`). After a news jump, an informed seller holding a declared
   inventory sells toward the new value against the dealer. Its desired size is
   `informed_share * informed_speed * (1 - value/mark)` units per tick, and it
   stops when the mark reaches value. The anchor absorbs only the remaining
   `1 - informed_share` of the jump. Tests: `informed_share = 0` reproduces the
   current member bit for bit; conservation holds; and a news episode now shows
   net selling comparable to a liquidity episode of the same size. The
   `noise` account keeps its role; the informed seller is a new account.
2. **Re-baseline on development seeds.** Rerun `run_mfsm_sim_edge.py` on
   seeds 0–999 and record S0–S3 and S6. Expected: S3's share of the oracle edge
   falls well below 70%. If the oracle edge falls to or below costs, record that,
   and apply the stopping rule before any retuning.
3. **Richer public tape features.** Extend `tape_features` with causal
   summaries a real desk could see: return path shape (depth and speed of the
   decline, the last-tick bounce), volume acceleration, sell-flow persistence
   across ticks, realized volatility before the trigger, and the pre-trigger
   impact per unit of flow (the synthetic analogue of the BTC sell-impact
   coefficient). S3 and S5 both use these, so neither strategy gets a
   private advantage.
4. **S5 flexible comparator.** Gradient boosting (`scikit-learn`, already an
   optional `eval` dependency) on the step 3 features. The target is forward P&L
   sign, with a no-trade band. Fit on seeds 0–4,999 with 5-fold cross-validation
   by seed; the threshold is chosen on seeds 5,000–9,999.
5. **S4 MFSM trader (Phase 3).**
   - a bootstrap particle filter over hidden structure and state, using the
     MFSM-SIM-1 transition with a declared observation-noise band on the mark
     and volume;
   - a forward valuation of buy, sell and flat per particle, reusing
     `execute_trade`;
   - it acts only if the expected P&L exceeds the declared margin, and reports
     `not_identified` when the posterior disagrees on the sign;
   - it gets the same development seeds and tuning budget as S5;
   - pure Python first; NumPy only if a 1,000-episode development run takes
     more than about 30 minutes;
   - tests: the posterior concentrates on the truth with a noise-free tape, stays
     diffuse for observationally equivalent candidates, and never reads hidden
     fields.
6. **Freeze and score `mfsm_sim_edge_001`.** Write the protocol JSON:
   - priors, the informed-share prior, trade spec, strategy settings and
     metrics;
   - seed ranges: `test` 1,000,000–1,001,999; `ood` 2,000,000–2,001,999 with
     hyperbolic impact, longer buyer delays, a higher news share and reversed
     holder order, all unknown to S4;
   - remove the development-only guard in the runner only for the frozen
     protocol.

   Run once, write the receipt with hashes, and publish
   `docs/mfsm_sim_edge_001_result.md` answering Q1–Q3 and Q5 against the frozen
   edge criterion.
7. **Value of information and capacity (Phase 4, protocol `002`).** Give S4 one
   privileged input at a time and sweep size and fees. This ranks which hidden
   quantity is worth measuring and gives the break-even cost.
8. **Bring it back (Phase 5).** Map the step 7 ranking to BTC observables. Then
   decide whether to resume the parked BTC top-20 replenishment revision, or to
   pursue a different measurement (open interest, liquidation prints, or the
   basis), and update the canonical known-weaknesses section with any confirmed
   limitation.

Not planned yet: crowding with several MFSM traders (Phase 6), which happens
only if step 6 finds an edge.

## Why this plan exists

The executable reference economy, [MFSM-RE-1](../MFSM_Reference_Economy.md), is a
deterministic, fully observed stress calculator. It answers "given this exact
balance sheet and this shock, what path follows?" It cannot answer "does
reasoning in MFSM terms make money?", for four reasons:

1. **No randomness.** One initial state gives one path. There is nothing to
   forecast and no distribution of profits to average.
2. **The value anchor is known.** Every mark satisfies `p <= v`, and the delayed
   buyer pushes the mark back toward `v`. "Buy any discount to `v`" therefore wins
   by construction. An edge measured there would be an artifact.
3. **No outside decision maker.** Nobody observes the public tape, chooses an
   action, pays costs, and books profit and loss.
4. **One holder and one shock.** A cascade needs many positions with different
   liquidation distances. That distribution is exactly what MFSM claims matters.

The synthetic observability work
([mark only](mfsm_reference_observability_result.md),
[public history](mfsm_reference_public_history_result.md)) already showed the
core difficulty: public prices only partly identify the hidden debt and impact
law, and in the frozen catalog anonymous volume added nothing.

## The edge question, stated in MFSM terms

> After a sharp public price decline, can a trader who sees only public data
> estimate how much of the decline is **forced, reverting selling** and how much
> is **permanent information**, well enough to profit after costs?

This is the canonical distinction between a liquidity dislocation and a
benchmark change (reference proposition P5: a permanent value decline need not
reverse; liquidity recovery restores at most the new value). If this cannot be
estimated from public data in a world built on MFSM's own mechanism, a real-market
MFSM edge built on it is implausible. If it can, the simulation tells us
**which hidden quantities carry the edge**, and therefore which real
measurements are worth acquiring.

## What a simulated edge would and would not mean

| A positive result means | It does not mean |
|---|---|
| In worlds generated by the declared law and priors, a public-data MFSM trader beats flat, naive and flexible same-information traders after the declared costs on frozen test seeds. | BTC or any real market behaves like the simulator. |
| The listed hidden quantities have a measurable value of information. | The simulator's parameter ranges are calibrated. |
| The edge survives the declared misspecification set. | It survives every misspecification. |

A negative result is equally useful. It may show that the mechanism cannot
create an edge net of costs, that public data cannot recover it, or that a
generic pattern learner captures it without structural reasoning. Each outcome
narrows what the real BTC work should measure.

## The simulated world: MFSM-SIM-1

A new member in `src/mfsm_sim/`. It extends MFSM-RE-1 and does not edit it.
Every addition has a **limiting case that reproduces MFSM-RE-1 exactly**, and a
regression test enforces that reduction.

### State and actors

| Actor / object | Rule | Hidden from the trader? | Reduces to RE-1 when |
|---|---|---|---|
| Fundamental value `v_t` | Random walk `v_t = v_{t-1} exp(sigma_v * eps_t)` plus a scheduled permanent news jump `-a` at the shock tick | Yes | `sigma_v = 0`, no news |
| Dealer quote anchor `u_t` | Moves toward `v_t`: `u_t = u_{t-1} + eta (v_t - u_{t-1})`; news is absorbed gradually, not instantly | Yes | `eta = 1` |
| Dealer | Mark `p = u_t exp(-lambda (q_D - q_ref))` (exponential) or the hyperbolic analogue; finite cash, inventory in `[0, Q]` | Inventory, cash, `lambda`, curve: yes | `q_ref = 0` |
| Holders `i = 1..N` | Each has cash, units and debt `B_i`; each runs the RE-1 restore-target sale and margin deadline independently | Yes (debt distribution is the key hidden object) | `N = 1` |
| Delayed buyer | RE-1 rule with dislocation measured against `v_t` (the informed slow capital); finite cash; delay kernel | Yes | unchanged |
| Noise traders | Each tick, signed order `n_t ~ Normal(0, sigma_n)` units, filled against the dealer through the same execution integrals, capped by inventory, room and a large noise cash/unit pool | Their flow is part of the tape, not labeled | `sigma_n = 0` |
| Exogenous distressed seller | Optional dump of `X` units at the shock tick, value unchanged | Yes | `X = 0` |
| Outside trader | Starts with cash `C0` and units `U0`; a "short" sells from `U0`, and exits restore `U0`; no negative holdings | Is the observer | absent |

`q_ref > 0` gives the dealer two-sided inventory, so noise buying is possible.
This deliberately drops RE-1's `p <= v` property. That property is one reason
dip-buying was trivially profitable.

### Shock scenarios

Each episode draws one scenario, with the scenario hidden:

| Scenario | News jump `a` | Cascade potential (holder leverage) | Exogenous dump | Expected post-shock drift |
|---|---|---|---|---|
| `NEWS` | large | low | 0 | none; the drop is permanent |
| `NEWS_CASCADE` | moderate | high | 0 | partial reversion of the cascade part only |
| `LIQUIDITY` | 0 | medium to high | `X > 0` | reversion as the delayed buyer arrives, if the deadline allows |
| `NULL` | 0 | any | 0 | none (noise-only crossings) |

News size, holder leverage, dealer capital, buyer speed, delay, `eta` and
`lambda` are drawn independently from declared priors. The **reverting
fraction** of the decline varies continuously across episodes. The `NULL`
scenario ensures that false triggers from noise alone exist.

### Transition order within a tick

Extending RE-1's ordering. Each rule is declared, and alternatives are
sensitivity checks, not silent choices:

1. Terminal and default checks per holder (RE-1 step 1, per holder).
2. Value update, then quote-anchor update.
3. Scheduled shock actions (news jump applies to `v`; dump executes).
4. Outside trader's order, decided from the tape **up to the previous tick**.
5. Delayed buyer order (RE-1 step 3).
6. Noise order.
7. Holder margin processing in fixed index order (RE-1 steps 4–6 per holder).
   The ordering is an assumption; reversed and randomized orders are
   sensitivity variants.
8. Publish the tape row for this tick; append signals; advance.

### Public tape (what the trader may see)

| Map | Contents per tick |
|---|---|
| `T1` | End-of-tick mark |
| `T2` | `T1` plus total executed units |
| `T3` | `T2` plus signed aggressor volume (buys minus sells against the dealer) |

Everything else is hidden. The harness hands the strategy **only** a tape
object truncated at the decision tick; a test proves that later rows and hidden
fields are unreachable.

### Accounting invariants (tests, not results)

- Total cash and total units across all accounts are conserved every tick,
  including noise, dumper and outside trader.
- No account goes negative; `0 <= q_D <= Q`.
- Seeded determinism: the same seed gives a byte-identical path.
- RE-1 reduction: with `N = 1`, `sigma_v = sigma_n = 0`, `eta = 1`,
  `q_ref = 0`, no trader and no dump, every path equals `mfsm_reference.economy.step`
  exactly on the existing reference and sensitivity scenarios.
- Paired runs: the same seed with and without the outside trader differs only
  through the trader's own orders (common random numbers).

## The trading problem

- **Trigger:** first tick where the public mark's return over `W` ticks is at or
  below `-x` (default `W = 5`, `x = 2%`), mirroring the BTC event rule. A lockout
  gives one trigger per episode.
- **Decision:** at `trigger + delta` ticks, choose `BUY s`, `SELL s` or `FLAT`.
- **Exit:** unwind at `decision + H` ticks (default `H = 30`). A second variant
  uses symmetric barriers.
- **Execution:** entry and exit trade against the dealer through the same curves,
  so the trader pays its own impact and moves the world. A proportional fee
  `c` bps is charged on both legs.
- **P&L:** final cash minus initial cash after restoring `U0` units. No
  mark-to-model profits.

## Strategies compared on identical episodes

| ID | Strategy | Information | Purpose |
|---|---|---|---|
| S0 | Flat | none | zero baseline |
| S1 | Always buy the triggered dip | tape | naive contrarian |
| S2 | Always sell the triggered dip | tape | naive momentum |
| S3 | Rule on drop speed and volume (for example, fast decline on high volume means buy) | tape | hand heuristic |
| S4 | **MFSM model-based trader** | tape + declared prior | the object under test |
| S5 | Flexible same-information learner (gradient boosting on tape features) | tape | fair comparator |
| S6 | Oracle with the hidden scenario and parameters | hidden state | upper bound on available edge |

**S4 in detail.** A particle filter over the hidden world uses the declared
MFSM-SIM-1 transition as its own model. Each particle holds hidden parameters
and state. Particles propagate with their own noise draws and are weighted by
the likelihood of the observed tape under a small declared observation-noise
band. At the decision tick, each particle is simulated forward under each
action. S4 chooses the action with the highest expected P&L net of costs, and
trades only if that exceeds a declared margin. It also reports the posterior
reverting fraction and whether the posterior is too diffuse to act
(`not_identified`, per the canonical output rule). The filter prior is
declared separately from the generator prior, so misspecification can be
tested.

**S5 and S4 get the same tuning budget** on development seeds. S5 is the test
MFSM must pass: if a generic learner using the same tape does as well, the
structural reasoning adds nothing in this world. That is still a finding.

## Data splits, seeds and freezing

| Split | Use | Rule |
|---|---|---|
| `dev` seeds | Build, debug, tune thresholds and S5 hyperparameters | Unlimited looks |
| `test` seeds | One scoring run per frozen protocol | Scored once; any change afterwards creates a new protocol version |
| `ood` seeds | Generator priors and law shifted relative to S4's prior | Scored once, alongside `test` |

A JSON protocol (`experiments/mfsm_sim_edge_001_protocol.json`) freezes the
priors, scenario mix, costs, sizes, trigger, strategy settings, seed ranges and
metrics before `test` or `ood` runs. The runner writes a receipt with protocol,
code and result SHA-256 hashes, following the existing `run_mfsm_reference_*`
convention.

## Metrics

Per strategy on each split:

- mean P&L per episode and per trade, net of costs; standard deviation; trade rate;
- hit rate; 5% conditional value at risk; worst episode;
- **paired** mean difference against S0, S1, S5 and S6 on the same episodes, with
  a bootstrap interval over episodes (episodes are independent draws);
- capture ratio = S4 edge / S6 edge;
- S4 calibration: predicted versus realized reverting fraction and forward return;
- results stratified by the hidden scenario (reported after scoring, never used
  by the strategy).

**Simulated-edge criterion (frozen before test):** S4's paired mean P&L exceeds
max(S0, S1, S2, S3, S5), with the 95% bootstrap interval above zero after costs,
on `test`. The same sign must hold on `ood`. Anything less is reported as no
simulated edge for that configuration.

## What will be investigated

| # | Question | How | What an answer changes |
|---|---|---|---|
| Q1 | Does any edge exist at all in this world? | S6 oracle P&L versus costs | If oracle edge is at or below costs, the world or mechanism cannot yield an edge; stop and revise the world, not the trader |
| Q2 | How much of the available edge can public data recover? | S4 capture ratio on `T1`/`T2`/`T3` | Quantifies the observability gap found in the earlier synthetic checks |
| Q3 | Does structural reasoning beat pattern learning? | S4 versus S5, paired | If tied, MFSM's contribution is interpretation and robustness, not raw forecast |
| Q4 | Which hidden quantity is worth observing? | Give S4 one privileged input at a time (holder debt near threshold, dealer inventory, buyer cash/delay, news flag) and measure the edge gain | Ranks real measurements: liquidation-level data, open interest, book depth or replenishment, flow |
| Q5 | Is the edge robust to a wrong model? | `ood`: hyperbolic impact, distributed delay, different news share, reversed holder ordering, all unknown to S4 | Separates a real structural edge from overfitting to the generator |
| Q6 | How big can the trade be? | Edge versus size `s` and fee `c`; break-even cost | Capacity and cost ceiling, the first check before any real deployment talk |
| Q7 | Does the edge disappear when copied? | Several S4 traders in the same world (optional stage) | Reflexivity: MFSM traders become part of the buyer capacity they forecast |
| Q8 | What must the real BTC test measure? | Map each Q4 winner to a BTC observable | Replaces a blind data search with a targeted one |

Q8 mapping candidates (to be confirmed by Q4, not assumed):

| Simulated hidden quantity | Candidate BTC observable |
|---|---|
| Impact coefficient `lambda` | pre-trigger sell-impact coefficient (MFSM-BTC-RESPONSE-1) |
| Buyer speed and delay | bid replenishment after sell pressure |
| Holder debt distribution | open interest changes, liquidation prints, funding |
| News versus liquidity | cross-venue and spot-perpetual basis behaviour, trade-size mix |

## Phases, deliverables and acceptance

### Phase 1 — World generator (MFSM-SIM-1) — done

Files: `src/mfsm_sim/__init__.py`, `src/mfsm_sim/world.py`,
`tests/test_sim_world.py`, and a synthetic-member section appended to this plan
or a new `MFSM_Sim_Economy.md`.

Acceptance: all accounting invariants pass; exact RE-1 reduction on the existing
reference and sensitivity scenarios; seeded determinism; the four scenarios
produce qualitatively distinct average post-shock drifts on a small `dev` batch
(a sanity check, not a result).

### Phase 2 — Tape, harness, baselines and oracle — done

Files (the tape is `PublicRow` in `world.py`; no separate `tape.py`): `src/mfsm_sim/harness.py`,
`src/mfsm_sim/strategies.py`, `tests/test_sim_harness.py`,
`scripts/run_mfsm_sim_edge.py`.

Acceptance: strategy code receives only the truncated public tape (a test
attempts to read future or hidden fields and fails); P&L equals the
cash-accounting change; paired runs share random numbers; S0–S3 and S6 run on a
`dev` batch. **First checkpoint: answer Q1 on `dev`.** If the oracle edge is not
above costs, revise the world priors with a documented reason before building
S4.

### Phase 3 — MFSM trader and flexible comparator

Files: `src/mfsm_sim/filter.py` (particle filter and forward valuation),
S4 and S5 in `strategies.py`, tests for filter correctness. The tests check that
the posterior concentrates on the truth when the tape is noise-free and the
prior contains the truth, and stays diffuse when candidates are observationally
equivalent, matching the earlier `not_identified` results.

Performance: vectorize particles with NumPy (added with `uv add numpy`) if the
pure-Python filter is too slow. The target is under 30 minutes for a full
`test` run on this machine. Respect the ~9 GB shared RAM: no parallel heavy jobs.

Acceptance: S4 and S5 tuned on `dev` only; then **freeze
`mfsm_sim_edge_001_protocol.json`**; one `test` + `ood` run; receipt and
result document `docs/mfsm_sim_edge_001_result.md` answering Q1–Q3 and Q5.

### Phase 4 — Value of information and capacity

Q4 and Q6 as a second frozen protocol (`002`), scored on fresh seeds. The
result document ranks hidden quantities by edge gain and gives break-even costs.

### Phase 5 — Bring the answer back to the model and to BTC

Update the [model improvement plan](mfsm_model_improvement_plan.md), the
canonical known-weaknesses section if a limitation is confirmed, and the
[BTC edge plan](mfsm_btc_edge_evaluation_plan.md) with the Q8 mapping. Decide
which real measurement to pursue next, with the simulated value of information
as the justification.

### Optional Phase 6 — Crowding

Q7 with several S4 traders. Only if Phase 3 finds an edge.

## Stopping rules

- Q1 negative after one documented prior revision: stop. Report that this
  mechanism does not yield an edge net of costs in its own world.
- S4 no better than S5 on `test`: report it. Keep S4 only if it wins on `ood`
  (robustness), and say so explicitly.
- Edge on `test` but not `ood`: the edge depends on knowing the generator.
  Report it as fragile, and do not carry it to BTC as a claim.
- Never retune after seeing `test` or `ood`. A new idea needs a new protocol
  version and new seeds.

## Risks and how the plan handles them

| Risk | Mitigation |
|---|---|
| Building a world where MFSM wins by construction | S5 comparator with equal budget; `ood` misspecification; oracle bound reported; `NULL` scenario; `p <= v` removed |
| Look-ahead leakage into the strategy | Truncated tape object and a test for it |
| Trader's own impact ignored | Trades execute against the dealer through the same curves; paired no-trader runs measure the footprint |
| Tuning on the test set | Seed splits frozen in the protocol and receipt hashes |
| Slow simulation | NumPy vectorization; modest `N` holders; cap particle count; profile on `dev` first |
| Over-reading a synthetic result | Every result document leads with the claim-boundary table above |

## Parked work (not abandoned)

- **MFSM-BTC-RESPONSE-1 top-20 revision.** The corrected extraction
  (`data/derived/mfsm_btc_response_features_001_top50guard/`) still gives zero
  replenishment values. The archived Bybit book is exactly 50 levels deep, so
  existing deeper bids enter the credited top 50 and are indistinguishable from
  new bids. On 2023-05-01, of about 109,000 such entries, about 1,800 entered at
  rank 20 or better. The proposed fix is protocol revision 1.2, crediting the top
  20 levels for both coefficients, then a rerun. The uncommitted guard fix in
  `src/mfsm_e001/capacity_audit.py` and `liquidity_state.py`, with its tests,
  is correct in principle and still pending commit. Phase 4's Q4 result should
  decide whether replenishment is worth finishing.
