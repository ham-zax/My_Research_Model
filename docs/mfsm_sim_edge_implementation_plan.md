# MFSM-SIM-EDGE implementation plan for coding agents

Version: `MFSM-SIM-EDGE-IMPL-1`
Date: 2026-09-27
Branch: work directly on `main`. Do not create feature branches.
Orchestrator: the owner's primary Claude session reviews every task before the
next one starts.

The *why* is in [the research direction](mfsm_research_direction_2026-09-27.md)
and [the simulated edge plan](mfsm_sim_edge_plan.md). This document is the *how*:
exact tasks, files, interfaces, tests, acceptance and hand-back rules. Read the
whole of section 0 before touching code.

---

## 0. Context you would otherwise miss

### 0.1 What this project is and is not

- MFSM is a research framework about how a market's structural state (leverage,
  dealer capacity, delayed buyers) changes its response to the next shock.
- **There is no demonstrated real-market edge.** Never write, in code comments,
  docs or commit messages, that the model "has an edge", "works" or "predicts
  BTC". Results from development seeds are *development diagnostics*.
- A synthetic edge is conditional on the simulated world. Every result document
  opens with the claim-boundary table from the simulated edge plan.

### 0.2 Non-negotiable research rules

1. **Seed discipline.**
   - Development seeds are `0 .. 999,999`, and you may use them freely.
   - `test` (`1,000,000+`) and `ood` (`2,000,000+`) seeds are run **once**, and
     only after the orchestrator approves a frozen protocol.
   - `scripts/run_mfsm_sim_edge.py` refuses non-development seeds. Do not remove
     or bypass that guard; task T6 replaces it with a protocol-checked path.
2. **No retuning after scoring.** A change after a test run needs a new protocol
   version and new seeds.
3. **Strategies see only `PublicRow`s** (`tick, mark, volume, signed_volume`).
   Hidden fields (`World`, `WorldLaw`, `Episode.hidden`, `TickRecord` beyond
   `.public`) are for the harness, the oracle (S6) and privileged
   value-of-information variants only, and those must set
   `uses_hidden_state = True`.
4. **Equal budgets.** S4 (MFSM) and S5 (flexible learner) get the same
   development seeds and the same number of tuning configurations. Record the
   count.
5. **Preserve the reductions.** MFSM-SIM-1 must keep reproducing
   `mfsm_reference.economy.step` bit for bit in the declared limit
   (`tests/test_sim_world.py::test_declared_limit_reproduces_reference_economy_exactly`).
   Every new world feature needs a parameter value that switches it off exactly.
6. **Do not touch:**
   - `src/mfsm_reference/` (the frozen reference economy);
   - `src/mfsm_e001/` and any `experiments/*` protocol already frozen;
   - `artifacts/*` receipts;
   - the ETH holdout;
   - `data/raw/`.
7. **Do not edit the canonical model files** (`Market_Feedback_State_Model_Canonical.md`,
   `Mathematical_Foundations.md`, `MFSM_Reference_Economy.md`) unless a task
   says so.

### 0.3 Environment

- WSL2, about 9 GB RAM shared with Windows. **Never run heavy jobs in parallel.**
  One simulation batch or one test suite at a time.
- Python through `uv` only:
  - tests: `uv run pytest -q`; the full suite takes about 10 s and has 281 tests
    at hand-off;
  - scikit-learn is an optional extra, so run with
    `uv run --locked --extra eval python ...`;
  - never `pip install`. If NumPy is approved (T5), add it with `uv add numpy`.
- `data/` is git-ignored. Write development outputs to
  `data/derived/mfsm_sim_edge_dev_<nnnn>/`, and never overwrite an existing
  directory.
- Commit only when the orchestrator asks. End commit messages with the
  repository's co-author line if you are Claude; otherwise follow your own
  harness rules.

### 0.4 Code map (the simulation)

| File | What it holds |
|---|---|
| `src/mfsm_sim/world.py` | `WorldLaw`, `World`, `Holder`, `Draws`, `PublicRow`, `TickRecord`, `mark()`, `step(world, law, draws, trader_order)`. Transition order is documented in `step`: default checks → value/anchor → shock (news, dump) → outside trader → delayed informed trader → noise → holders → publish. |
| `src/mfsm_sim/scenarios.py` | `Priors` (development priors), `sample_episode(seed)`, `draws_for(seed, ticks)`, `run_episode`. Two RNG streams per seed: `mfsm-sim-1/structure/{seed}` and `mfsm-sim-1/draws/{seed}`. **Adding a random draw to the structure stream changes every later draw for every seed**, so append new draws at the end of `sample_episode` and note it in the progress log. |
| `src/mfsm_sim/harness.py` | `TradeSpec`, `crossed`, `execute_trade` (enter, hold `horizon`, unwind; cash P&L after fees), `OracleStrategy` (Monte Carlo over future noise with the true state), `run_paired_episode` (shared prefix, common random numbers). |
| `src/mfsm_sim/strategies.py` | `tape_features`, S0 `Flat`, S1 `BuyDip`, S2 `SellDip`, S3 `FlowRule`. |
| `scripts/run_mfsm_sim_edge.py` | Development batch runner with paired bootstrap intervals. |
| `tests/test_sim_world.py`, `tests/test_sim_harness.py` | Invariants: RE-1 reduction, conservation, determinism, tape isolation, P&L accounting. |

Key facts:
- P&L unit: currency per episode for `TradeSpec.size = 5` units
  (about $500 notional) with 5 bps per leg.
- The trader's own orders move the market; that is intended.
- The informed trader in step 5 is *two-sided* (it sells above value). This was
  added to stop permanent overshoot and is documented in the plan's progress
  log.

### 0.5 Baseline numbers to compare against (development seeds 0–999)

| Strategy | Mean P&L | 95% paired interval vs flat |
|---|---:|---|
| S1 buy dip | +2.02 | [1.33, 2.73] |
| S2 sell dip | −5.36 | [−6.16, −4.61] |
| S3 flow rule | +3.46 | [2.85, 4.09] |
| S6 state oracle (16 rollouts) | +4.90 | [4.32, 5.47] |

These were 799 triggered episodes, and the run took about 85 s. If your
unchanged-code rerun differs, stop and report: something is nondeterministic.

### 0.6 Known traps

- **Look-ahead through the harness.** `run_paired_episode` holds the hidden
  world at the decision tick. Only pass `tape` to public strategies.
- **Float exactness in the RE-1 limit.** Keep the RE-1 expression order for any
  computation reachable in the limit (see `_dislocation`, which uses `expm1`).
  "Close enough" fails the exact test on purpose.
- **Generator artifacts.** If a simple public rule captures most of the oracle
  edge, suspect the generator first (the news-without-trades artifact is the
  example). Report it; do not "fix" it by weakening a strategy.
- **Bootstrap intervals are over episodes**, which are independent seeds. Do not
  bootstrap ticks.
- **Oracle cost.** The oracle's rollouts dominate runtime. Keep 16 rollouts for
  development runs.

---

## 1. How to hand back a task

Reply to the orchestrator with:

1. the files changed and a one-line reason for each;
2. the exact commands run and their tails (tests, runs);
3. the numbers requested by the task, in a table;
4. anything surprising, any rule you were unsure about, and any
   **orchestrator decision** you reached (stop there; do not decide it yourself);
5. confirmation that no non-development seed was run and no frozen file changed.

Append a dated entry to the progress log in `docs/mfsm_sim_edge_plan.md` only
when the orchestrator accepts the task.

---

## 2. Tasks

Tasks are sequential unless marked parallel-safe. Each lists
**orchestrator decisions**: stop and ask at those points.

### T1 — Informed news selling (Phase 2b)

**Goal.** Remove the artifact where news moves the mark only by trade-less
repricing.

**Changes (`world.py`, `scenarios.py`):**
- `WorldLaw.informed_share: float = 0.0` in `[0, 1]`, and
  `WorldLaw.informed_speed: float = 0.0` (units per tick per unit of relative
  overpricing).
- `World.informed: Account`, the informed seller's account. Add it with a
  default so existing constructors keep working, or update every constructor
  and test fixture.
- Anchor rule: after a news jump of size `a`, the anchor absorbs only
  `(1 - informed_share)` of the jump through the existing `anchor_speed` path.
  The informed seller sells `informed_share * informed_speed * max(0, mark/value - 1)`
  units per tick against the dealer, capped by its units, dealer room and
  dealer cash. Place it in the transition **after the scheduled shock and
  before the outside trader**, and document the order.

  Implementation hint: keep two anchor targets. The anchor moves toward
  `value + informed_share * a_remaining`, where `a_remaining` is the part of the
  news not yet sold through. Simpler alternatives are acceptable if they
  conserve accounting and give the exact reduction. Describe your choice.
- `Priors`: `informed_share=(0.3, 0.9)` and `informed_speed=(200.0, 800.0)`,
  drawn **at the end** of `sample_episode`. The informed account starts with
  enough units to sell the full move (for example, 200 units, 0 cash).

**Tests (`tests/test_sim_world.py`):**
- `informed_share = 0` reproduces the pre-T1 path bit for bit on several seeds.
  Capture the pre-T1 records in the test by constructing the law with the
  feature off; do not store fixtures from old code.
- Conservation including the new account.
- A synthetic news episode with `informed_share = 0.8` shows net sell volume
  within a factor of 3 of a liquidity dump of similar price impact.
- The RE-1 reduction test still passes unchanged.

**Run.** Development seeds 0–999 and a table as in section 0.5, plus S3's share
of the oracle edge.

**Acceptance.** All tests pass. S3's share of the oracle edge falls clearly
below the 70% baseline.

**Orchestrator decisions:**
- if the oracle edge falls to or below about 1.0 (near costs);
- if S3 still captures 60% or more of the oracle edge;
- if you want different prior ranges than specified.

### T2 — Richer public features (parallel-safe with T3 design, not with T3 runs)

**Changes (`strategies.py`).** Extend `tape_features` with causal summaries
computed only from `tape`:
- decline depth and speed (worst one-tick return in the window, number of down
  ticks);
- last-tick bounce;
- volume acceleration (last 2 ticks against the rest of the window);
- sell-flow persistence (fraction of window ticks with net selling);
- pre-trigger realized volatility over 30 ticks;
- **pre-trigger impact per unit flow**: regression slope of one-tick return on
  signed volume over the 30 ticks before the window (the synthetic analogue of
  the BTC sell-impact coefficient).

Keep existing keys unchanged; S3 depends on `flow_per_drop`.

**Tests.** Each feature matches a hand-computed value on a small constructed
tape. Features must be finite when volume is zero. Truncating the tape after
the decision row does not change them.

**Acceptance.** Tests pass; no strategy behaviour changed (rerun section 0.5
numbers: identical).

### T3 — S5 flexible comparator

**Changes.** `strategies.py`: `class FlexibleLearner(Strategy)`,
`name = "S5_flexible"`, which wraps a fitted scikit-learn model. New module
`src/mfsm_sim/learning.py`:
- `collect_training_rows(seeds)` runs `run_paired_episode` with S1 only, to get
  the decision tape and forward outcome. Store features from `tape_features`
  and a label equal to the S1 P&L. S2's P&L is roughly its negative minus costs,
  but compute both rather than assume it.
- `fit(rows, config)` uses `HistGradientBoostingRegressor` to predict S1 P&L and
  S2 P&L separately. The action is the argmax of {0, predicted S1, predicted S2},
  with a no-trade margin.
- Seeds: fit on development seeds 10,000–14,999; choose the margin and
  hyperparameters on 15,000–19,999; report on 0–999 (the standard development
  batch). Cap tuning at **12 configurations**; that number becomes S4's budget.

Run with `uv run --locked --extra eval ...`. scikit-learn must stay an optional
import: the world and harness modules must not import it.

**Tests.** Determinism with a fixed `random_state`; `decide` uses only the tape;
the fitted model object is not given `Episode.hidden`.

**Acceptance.** Section 0.5 table plus an S5 row, with paired intervals against
S3 and S6.

**Orchestrator decision:** if S5 is at or above 90% of the oracle, suspect a
remaining artifact.

### T4 — Risk-control view (small; parallel-safe after T3)

Add to the runner a derived strategy `S1_vetoed_by_<X>`: buy the dip unless
strategy X would sell or stay flat. Report it for X = S3 and S5 (S4 after T5).
This is the "don't buy the dip in a cascade" application: mean P&L, CVaR 5% and
worst episode against plain S1.

### T5 — S4 MFSM trader (Phase 3)

**Design.** New module `src/mfsm_sim/filter.py`:
- **Particles:** a hidden-structure draw from a declared prior *identical in
  form* to `Priors` (initially the same ranges; `ood` later breaks this), plus
  its own `World`.
- **Initialization:** the filter does not know the pre-shock history of the
  hidden state. Start particles at tick 0 from prior draws and run them through
  the observed tape with their own noise draws (bootstrap filter).
- **Weighting:** Gaussian likelihood of each observed `PublicRow` given the
  particle's own published row, with declared bands (development defaults: mark
  0.05% relative, volume 1.0 unit, signed volume 1.0 unit). Resample
  systematically when the effective sample size falls below N/2.
- **Decision:** at the decision tick, for each surviving particle and each
  action in {buy, sell}, run `execute_trade` over K fresh future draws.
  Expected P&L is the weighted mean. Act if the best exceeds the declared margin.
  Report `not_identified` (act flat) if the weighted probability that buying
  beats selling lies in `[0.35, 0.65]`.
- **Budget:** N particles and K rollouts are tuning parameters within the
  12-configuration budget. Start with N = 200 and K = 4.

**Performance.** Pure Python first. Measure the time per decision on 50
development episodes. If a 1,000-episode run is projected above about 30
minutes, stop: **orchestrator decision** on NumPy vectorization or a smaller N.

**Tests (`tests/test_sim_filter.py`):**
- Noise-free tape, prior containing the true structure: the posterior mass on
  the true scenario is at least 0.8.
- Two structures that produce identical tapes: the posterior stays split and
  the decision is `not_identified`.
- `decide` never receives `World`: the strategy's public interface takes only
  `tape`. The filter uses only its own simulated worlds.
- Deterministic under a fixed seed.

**Acceptance.** Section 0.5 table with S4 and S5 rows, paired intervals S4–S3,
S4–S5 and S4–S6, and the capture ratio S4/S6.

### T6 — Freeze and score `mfsm_sim_edge_001` (orchestrator-gated)

1. Draft `experiments/mfsm_sim_edge_001_protocol.json`:
   - priors and the trade spec;
   - every strategy's frozen settings, including fitted-model hyperparameters
     and training seed ranges;
   - `test` seeds 1,000,000–1,001,999;
   - `ood` seeds 2,000,000–2,001,999 with the generator changed to a hyperbolic
     curve, buyer delay `(4, 12)`, scenario weights `(0.45, 0.25, 0.2, 0.1)` and
     reversed holder order (S4 keeps its original prior);
   - metrics and the edge criterion from the plan.

   **Stop for orchestrator approval.**
2. After approval, the runner verifies the protocol's SHA-256 and runs `test`
   and `ood` once. It writes a receipt to
   `artifacts/mfsm_sim_edge_001_result.json` with the protocol, code and result
   hashes (follow `scripts/run_mfsm_reference_public_history.py`).
3. Write `docs/mfsm_sim_edge_001_result.md`: the claim boundary first, then Q1,
   Q2, Q3 and Q5 answers, the tables, and the limits.

Reversed holder order and the hyperbolic curve for `ood` may need new
`WorldLaw` switches. Add them with exact-off defaults and tests *before*
drafting the protocol.

### T7 — Value of information and sample size (Phase 4, protocol `002`)

- **Value of information:** S4 variants each receiving one privileged hidden
  input: the scenario flag; holder margin distances; dealer inventory; buyer
  speed and delay; impact coefficient. Edge gain against plain S4 with paired
  intervals.
- **Capacity:** S4 P&L against size {1, 5, 10, 25} and fee {0, 5, 10, 20} bps;
  the break-even fee.
- **Sample size (headline output):** for each strategy and value-of-information
  variant, the number of independent events needed for the paired interval
  against flat to exclude zero with 80% power:
  `n ≈ (1.96 + 0.84)^2 * var(diff) / mean(diff)^2`, from the scored seeds. Also
  report it at the real-market trigger frequency. **Orchestrator input needed**
  for the real event rate; the current BTC development sample gives about 20
  events.

Frozen like T6, on fresh seeds (`test` 3,000,000+, `ood` 4,000,000+).

### T8 — Bring it back (orchestrator-led)

The orchestrator maps the T7 ranking to BTC observables and decides the next
real-data action. Candidates: resume the top-20 replenishment revision (parked
in the simulated edge plan), a continuous history or lower-threshold event set,
or open interest and liquidation data. Agents may be asked to draft protocols.

---

## 3. Suggested agent prompt (copy for each task)

> You are working in `/home/hamza/repo/My_Research_Model` on branch `main`.
> Read `docs/mfsm_sim_edge_implementation_plan.md` section 0 fully, then do
> task **T<n>** exactly as written. Do not run non-development seeds, edit frozen
> files, or commit. Stop at any "orchestrator decision" and report. When done,
> hand back using section 1.
