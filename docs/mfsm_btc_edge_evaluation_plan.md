# Plan to test whether MFSM has a BTC trading edge

Version: `MFSM-BTC-EDGE-PLAN-1`<br>
Date: 2026-09-24<br>
Status: implementation plan; no edge protocol frozen and no edge test run

## Decision this plan will answer

On BTC spot declines defined by the existing
[E001-LIQ-OBS-1 protocol](../experiments/e001_liquidity_observational_protocol.yaml),
does the observable MFSM liquidity interaction improve a **real short-or-flat
decision** after trading costs, compared with simpler decisions made from the
same information?

This tests one operational member of MFSM. It does not identify a counterfactual
market path law, hidden margin headroom, actual liquidation-distance mass, or
the full canonical state. A successful forecast alone is not a trading edge.
The [canonical model plan](mfsm_model_improvement_plan.md) separates mathematical,
mechanistic, predictive, and decision support; this work addresses the last
two using market observations.

The original E001 experiment remains blocked under its original timing and
capacity contract. The earlier [free BTC exploratory result](e001_exploratory_btc_result.md)
tested a different hourly interaction on 19 isolated sample days: a tiny paired
Brier improvement, both fitted models worse than a historical-rate forecast, and
no execution test. Treat those dates and the already inspected liquidity feature
development dates as development material, never as fresh confirmation of this
claim. Keep ETH sealed.

## One candidate decision and its information boundary

Start with the existing, separately versioned BTC liquidity observation:

| Element | Candidate contract to carry into the new protocol |
|---|---|
| Event | First crossing of a -1% five-minute return in the equal-weight Binance/Bybit receipt-time spot midpoint; two-hour episode lockout. |
| Decision | At the existing `t0 + 15 seconds` boundary, after every required feature has arrived and passed quality checks. |
| Forecast | Calibrated probability of the existing 30-minute downside-before-recovery event: spot -1% before +0.75% from the decision reference; neither hit is class 0. |
| Trading instrument | One fixed small size of Bybit BTCUSDT linear perpetual, short or flat. The final protocol must pin the contract, account unit, size and maximum exposure. |
| Exit | On the first of those two spot barriers, or at 30 minutes if neither occurs. A spot trigger leads to a *later* executable perp order after declared processing and routing delay. |
| Feature comparison | Existing eight common observable liquidity summaries for both models; MFSM adds only the two frozen sell-pressure × weak-depth/replenishment combinations. |

The event and feature values above are inherited from E001-LIQ-OBS-1 as a
candidate application boundary. Write a **new versioned edge protocol** before
using them to score trades; do not alter the old protocol or relabel its past
outputs as trading results. A first-passage probability does not by itself
determine expected profit: the execution prices, neither-hit paths, funding,
and costs decide the trade payoff. Select the probability-to-action threshold
using development data only, with the same selection budget for comparison
models. Fix the rule before any confirmation outcomes are examined.

## Implementation order and acceptance gates

### 1. Freeze a claim that can fail

Create `experiments/mfsm_btc_edge_001_protocol.yaml` and a manifest that pins
the event, decision clock, feature and label schemas, instrument, short size,
action threshold selection rule, exit rule, permitted training history, calendar
splits, data-quality exclusions, execution assumptions, comparators, uncertainty
method, and pass/fail criteria. Hash the protocol and source inputs. Inventory
every strategy, feature, threshold, date, and cost variant already tried so the
selection history remains visible.

Use the current E001-LIQ-OBS-1 thresholds unless a **development-only feasibility
check**, documented before the new protocol is frozen, shows that its spot
trigger cannot be connected to causal perp execution. Any changed definition
gets a new name and fresh confirmation period. Do not choose it from the prior
exploratory score or from a profitable backtest.

**Gate:** the protocol and evaluation calendar exist before reading the proposed
confirmation period's labels, predictions, or trade returns. Failure produces
`NOT_FROZEN` and no edge score.

### 2. Qualify a continuous market record

Reuse the existing free Binance/Bybit spot acquisition, event scanner, and
Bybit perpetual book/trade replay where they satisfy the new protocol. Hash raw
files or sealed segments. Record receipt and venue timestamps separately,
continuity epochs, book gaps, stale quotes, spot/perp synchronization,
instrument rules, fee schedule, funding events, and days excluded *before*
feature or payoff scoring. Reject decisions with missing required history or
future path; never fill a missing observation with zero or use a later message
to repair an earlier decision.

The free first-of-month Tardis days, one free CryptoStruct perpetual day, and
the short forward capture can establish software and measurement feasibility;
their small or selected calendar coverage is not a fresh edge test. The
[historical data path](e001_cryptostruct_historical_data.md) already describes a
price-only acquisition screen followed by exact two-venue spot events and then
perpetual L2 windows. It is a candidate acquisition route, not permission to
buy data or evidence of net profit. Keep a continuous free collector for a
prospective confirmation period when practical. Identify the exact missing
field or calendar coverage before requesting any paid data or API key.

The historical acquisition screen is
[`scan_e001_historical_candidates.py`](../scripts/scan_e001_historical_candidates.py):
the frozen development rule retains days at a free composite return of at most
-0.60%, or a Binance-only return of at most -0.50% when the free reference is
missing. A superseded alternate used -0.65%/-0.60%; it has been removed and
must not be recreated or used to define the purchased day set.

**Gate:** a hash-verified, continuous and causal episode ledger with each
decision's information cutoff, book state, future exit path, and exclusion
reason. If coverage is insufficient, report `INSUFFICIENT_DATA`; do not shorten
the horizon or loosen quality rules after seeing performance.

### 3. Check forecasting on past-only splits

Reuse the existing E001 liquidity feature definitions and matched B4/MFSM
classifier implementation. Include a historical-rate forecast as a formal
comparator from the beginning, because it beat both fitted models in the prior
exploratory sample. Also include a flexible model that receives the same raw
feature history and a simple predeclared momentum/volatility/liquidity rule.
Give comparison models the same decision rows, fit history, calibration method,
and tuning budget where their architectures permit it. Fit transformations,
calibration, and action thresholds using only observations whose full label
horizon ended before the next fit.

Set chronological development and untouched confirmation blocks before model
scores. Use development data to estimate whether there are enough independent
events and calendar weeks to detect an economically meaningful effect with a
usefully narrow interval. Freeze the resulting sample and precision requirement;
the E001 130-episode gate is a **forecast experiment minimum**, not a proof of
trading power. Avoid random row splits, especially when episodes or regimes
cluster by day.

**Gate:** emit paired, out-of-sample probabilities, Brier score, calibration,
coverage, split IDs and class counts. Failure to beat the historical-rate and
same-information comparators limits the predictive claim, even if one pairwise
MFSM comparison is slightly positive.

### 4. Replay an executable short-or-flat decision

For each eligible event, every model chooses short or flat using its own
development-selected threshold. Flat earns zero *trade* P&L and stays in the
denominator. Simulate a short sale into available perp bids after the declared
decision/routing delay, then a buyback into asks after the first eligible exit
signal and its delay. Walk available depth for the fixed size when L2 supports
it. Use actual exchange fees and funding cash flows from the applicable period,
including an event crossing a funding timestamp. Report the result in both
currency per fixed size and basis points of traded notional.

The executable fill prices already include bid/ask spread and walked-book
impact; do not subtract either a second time. Add explicit fees and funding.
If only top-of-book or trade prices exist, label the calculation an execution
**proxy**, stress the missing slippage, and withhold a strong edge claim until
prospective order or sufficiently complete replay evidence supports the fill
assumptions. Account for rejected, missed, and stale orders; no fill means no
invented position. The position and capital convention is the same for every
model and is fixed before scoring.

**Gate:** the replay is deterministic from the frozen inputs, records every
order/exit and its causal timestamps, and reconciles trade cash flows. Test
late signals, gaps, barrier ties, funding boundaries, no fills, and terminal
exits with small hand-checkable fixtures.

### 5. Evaluate the claim and stop at the evidence level reached

The primary economic quantity is mean **net** P&L per eligible independent
episode, including flat decisions as zero, for the fixed size. Compare MFSM
against flat and against the strongest comparator selected using development
data alone. Declare both tests before confirmation. Estimate uncertainty by
resampling calendar blocks, not individual seconds or overlapping trades;
pin the block unit, algorithm, seed and minimum number of blocks before scoring.
Report total P&L, drawdown, exposure, turnover, costs, fill rate, forecast
quality, and performance by predeclared calendar segment. Report every attempted
configuration, including failures. Use a prespecified worse-fill/cost case as
a sensitivity check.

| Status | Required interpretation |
|---|---|
| `EDGE_SUPPORTED_FOR_TESTED_POLICY` | On untouched confirmation data, both the lower uncertainty bounds for MFSM net P&L versus flat and for its incremental net P&L versus the development-selected comparator exceed zero; coverage and execution gates pass; the predeclared cost stress does not reverse the point estimate. This is evidence limited to the named instrument, size, dates and execution assumptions. |
| `PREDICTIVE_ONLY` | The frozen forecast improves appropriately matched prediction scores, but the net decision test does not pass. |
| `STRATEGY_EDGE_NOT_MFSM_SPECIFIC` | A short-or-flat rule passes its absolute net test, but the MFSM version does not improve over the same-information comparator. |
| `NO_EDGE_DETECTED` | Adequate confirmation data and execution evidence give a nonpositive or materially inferior result under the frozen rule. |
| `INCONCLUSIVE` | Too few independent blocks, wide intervals, missing fills/fees, unstable feed quality, or failed timing/measurement gates prevent a reliable call. |

An interval crossing zero means `INCONCLUSIVE` rather than proof that the true
edge is zero. A positive backtest, even one passing these gates, is evidence
under its specified conditions rather than mathematical proof of perpetual
profit. Multiple unreported trials would weaken that evidence.

### 6. Confirm prospectively before any live-capital claim

After the historical protocol and code are sealed, publish each prediction,
intended action, data-quality state and expected order time to an append-only
local log **before** its outcome. Reconcile the paper order against the actual
subsequent book and venue rules. Select a fixed start/end period and minimum
precision requirement in advance; do not extend collection because the result
is close to passing. A separate, explicitly authorized small live trial would
be needed to measure actual fills and operational failure rates.

## Files and first executable milestone

Implement this without editing the canonical theory or retrofitting an E001
result. Likely new files are the edge protocol, an execution replay module and
runner, fixtures for timing/fills, and an immutable result/manifest writer. Reuse
`src/mfsm_e001` only through stable event, feature, label and evaluation
functions; keep an adapter if the edge protocol needs a distinct output schema.

The **first milestone** is a protocol draft plus a read-only feasibility report:
count candidate episodes and independent calendar blocks; list which spot,
perp L2, fee and funding fields are present; identify where fill assumptions
cannot yet be checked. It should not fit a model or print P&L. Once that report
passes, freeze the protocol and calendar, implement the replay with fixtures,
then evaluate development and confirmation in that order. Every terminal run
must retain exact code/protocol/input hashes and the reason for any gate failure.

The next coding agent should begin by reading this plan, the frozen
[liquidity observation contract](../experiments/e001_liquidity_observational_protocol.yaml),
the [earlier exploratory result](e001_exploratory_btc_result.md), and the
[historical source decision](e001_cryptostruct_historical_data.md). It should
inspect the current Git index before editing and preserve unrelated work.
