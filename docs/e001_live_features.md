# Live BTC common feature pipeline

## Scope and status

`E001-live-features-candidate-1` extends the capture replay with **candidate measurements at explicitly supplied decision seconds**. This is the real-capture counterpart to the older fixture feature implementation. It does not select research events, supply labels, fit models, freeze a feature schema, or open ETH. The full common panel remains gated by source semantics and data sufficiency.

Inputs are immutable `E001-capture-v1` segments selected through `CaptureInput`. A live prefix excludes open tails, freezes its file list, and records segment hashes. Every decision is evaluated during receipt-ordered replay; an observation received one nanosecond afterward is unavailable. Original timestamps remain unchanged. The feature builder does not alter the collector or raw input.

## Measurement contract

| Family | Rule and units | Missingness / limit |
|---|---|---|
| Spot reference | Existing equal-weight Binance/Bybit midquotes, each at most five source-event seconds old | Both constituents required; unchanged experiment definition |
| Perpetual book | Bybit `orderbook.1000.BTCUSDT`, separate from the 50-level feed | Full 25-bps bid/ask values require the respective feed boundary to cover the band |
| Trade flows | Bybit linear aggressive buy/sell USDT notional and notional/second over 1/5/15/30/60/300 seconds | Event window `(decision-window, decision]`, actual receipt by decision, uninterrupted acknowledged subscription; zero means no observed events in that operationally valid interval |
| Duplicates | Trade IDs deduplicated within retained flow history; conflicting duplicate identity fails extraction | No invented liquidation identifier or trade/liquidation matching |
| Liquidations | Position `Buy` maps to sell pressure; preserve BTC base quantity separately by pressure side | Bankruptcy price is not execution price. Executed notional and its rate remain null, including quiet periods |
| Gross additions / decreases | Positive/negative absolute-size differences at fixed price levels in the contemporaneous side's 25-bps band, valued at that level's price, divided by window seconds | Initial snapshots are not additions. A newly revealed level beyond the previous feed boundary has unknown previous size, so affected window measurements are missing. Observed decreases are not identified cancellations or executions |
| Persistence | Every positive cohort in `[decision-window, decision]` must finish one source-event second of dwell. Subtract every observed negative change at the same price in `(addition, addition+1s]`; later positive changes do not undo reductions. Require endpoint band membership; divide by the full window | Unfinished dwell is censored. A reset, sequence failure, stale state or missing full band invalidates dependent window features. Aggregate levels do not identify resting orders |
| Current / lagged depth | Full-band USDT notional at decision and each window's lag | No extrapolation through missing/stale book states |
| Ticker state | Snapshot/delta OI in BTC, funding in bps, mark/index divergence in bps | Omitted fields retain their own source/receipt provenance. Reconnect discards state; invalid/nonpositive prices and OI are missing |
| Basis / spread / imbalance | Perpetual midpoint versus independent spot in bps; top spread divided by midpoint in bps; `(bid-depth - ask-depth)/(bid-depth + ask-depth)` | Imbalance needs full coverage on both sides |
| Returns / realized volatility | Simple spot return and square root of the sum of squared one-second log returns for each window | Every grid point including both endpoints required; no gap interpolation |
| OI changes | Percentage and log change over each window | Entire one-second OI path must be valid |

Candidate operational quality limits are explicit: current book and ticker-envelope state must be no more than **five seconds** old; more than **30 seconds** of Bybit source silence breaks flow continuity. Individual unchanged ticker fields keep their original ages and are not forced to update. These are conservative implementation quality gates, not a claim of complete market coverage or a new frozen scientific definition. They must be included in the eventual BTC schema audit before model evaluation.

No cancellation or order-specific execution rate is inferred from aggregate L2 reductions. These named fields remain null with `aggregate_L2_cannot_attribute_removals`. Aggressive trades may include reported and unreported forced liquidations; the sell-pressure interaction is explicitly labelled contaminated.

## Common normalized inputs

For a diagnostic decision `td`, the hypothetical experiment trigger is `t0=td-15s`. Pre-trigger depth and OI medians each require all **1,800 one-second values in `[t0-1800s,t0)`** to be present and positive. Any missing required denominator makes dependent normalized values missing; no fitted replacement is used.

- Divide quote-notional depth, flows and rates by the pre-trigger full bid-depth median. Normalized rates have units `1/second`.
- Divide liquidation **base quantity** by the pre-trigger **base OI** median. This avoids dividing a USDT notional by BTC units.
- Express OI relative to its pre-trigger median, and retain its percentage/log changes.
- Keep returns, volatility, spread, imbalance, funding and basis in their dimensionless/bps forms.
- Preserve raw scale-sensitive measurements only in the separately labelled `raw` diagnostic object.

The capacity proxy is `max(current_bid_depth + 30 * persistent_bid_add_rate_15s, 0.01 * pretrigger_depth_median)`. Its normalized value and low-capacity indicator are shared. Pressure ratios use **30-second** flow notionals, as required by Experiment 001 Section 8.1; the **15-second** window applies to replenishment. `shared` is the B4 base; `mfsm` contains an identical copy plus the contaminated sell-pressure ratio and unavailable liquidation-pressure ratio. Neither output is a fitted model or a final primary feature list.

## Output and reproduction

Each `features.jsonl.gz` row carries decision time, hypothetical trigger time, latest consumed input availability, raw diagnostics, pre-trigger scales, shared/MFSM inputs, ticker provenance, missing reasons and explicit readiness flags. Decimal values serialize as strings. Gzip output is deterministic. `report.json` records code/input/output hashes, exact requested decision seconds, available-feature counts and remaining limitations.

```bash
uv run --locked python scripts/build_e001_capture_features.py \
  data/raw/live_btc_clock_fixed_smoke/094532e21b2946268a5d829746463ee7.manifest.json \
  --decision-second 1790211890 \
  --output data/derived/e001_features_clock_fixed_smoke

uv run --locked --extra collect --extra test pytest -q
```

For an ongoing run add `--sealed-prefix --max-segments N`, using an explicit frozen segment count and a decision inside that prefix. The command verifies every selected segment even if all requested decisions occur earlier. Unsupported decisions fail; the CLI does not shift them to a convenient observation.

### Receipt-time diagnostic

Add `--timing-candidate receipt_diagnostic` and use a separate output directory to measure quotes, flows and book dwell in receipt time. This produces schema `E001-live-features-receipt-diagnostic-1`. Source timestamps remain in the payload and provenance. Every row states `source_freshness_certified: false`, `primary_eligible: false`, and `model_ready: false`; a local clock step makes subsequent numeric values unavailable. The default `legacy` mode retains the strict source-time definition. See the [timing contract](e001_timing_contract.md) and [paired real-capture comparison](../artifacts/e001_receipt_feature_comparison.json). The receipt candidate changes values even when the strict clock is valid and is not an approved experiment feature schema.

The prepared `--timing-candidate receipt_v1` mode writes the separate `E001-live-features-receipt-candidate-1` schema with the same receipt-time numeric features and an explicit `timing_quality` gate on each row. Its [revision contract](e001_receipt_time_revision.md) defines receipt quote age, source-lead quarantine, initialization/history checks and the unresolved independent UTC/WebSocket delay requirements. The [fixed-input result](../artifacts/e001_receipt_policy_gate_results.json) records all rows as ineligible. The receipt grid and synthetic episode/label builder now exist, but real primary event extraction remains gated by timing and feature qualification.

## Verification and initial measured results

The full suite now passes **145 tests** with `--extra eval`, including receipt-time policy, dataset and matched evaluator regressions. A separate reviewer identified the 30-second pressure-window mismatch, unknown prior sizes at newly revealed feed boundaries, and multiple additions sharing the inclusive left endpoint. All three were reproduced with failing tests and corrected. The endpoint issue was treated as a correctness defect because it changes the specified persistence sum, despite being uncommon.

The longer live capture also exposed flow messages whose source timestamps exceeded local receipt. The feature replay records those as clock failures and leaves all subsequent numeric features missing, rather than aborting and losing the audit report. Original observations remain unchanged; malformed economic fields still raise errors. Regression tests cover disagreement in both envelope and individual trade timestamps.

The post-clock-repair smoke capture produced one diagnostic row with **67 available raw measurements**; its [feature report](../artifacts/e001_features_clock_fixed_smoke_results.json) retains hashes and missing reasons. A fixed first-12-segment development prefix produced **four clock-valid diagnostic rows**. In that [prefix report](../artifacts/e001_features_forward_prefix_results.json), 30-second aggressive-sell flow and OI were available in all four rows; current full bid depth was available in three, but 15-second bid-persistence was unavailable in all four because its required history failed coverage/validity checks. None of these early decisions had a complete pre-trigger depth scale. These are implementation/data-quality observations, not eligible research episodes or predictive scores.

A [119-segment audit](../artifacts/e001_features_extended_prefix_results.json), excluding the unclean tail, evaluated three later diagnostic decisions. One was clock-valid with 100 available raw measurements, including bid-persistence; the two after the first recurring clock failure had every numeric feature missing. None supplied a valid pre-trigger depth denominator. The earliest decision's pre-trigger interval includes initial feed warm-up, so it also lacks a complete OI denominator. The report preserves full segment and code hashes; no missing denominator was replaced with a fitted constant.

A separate [post-warm-up check](../artifacts/e001_features_pretrigger_audit_results.json), at decision second 1790213822 using the first 24 sealed segments, verified the full 30-minute OI denominator: **59,225.673 BTC**, with decision OI **0.4369% above** that median. It produced 94 available raw measurements and valid bid-persistence, while the pre-trigger depth denominator remained unavailable. This distinguishes initial warm-up from the persistent full-band depth limitation. No model was fitted.

## Remaining research gates

1. Audit full capture continuity, band coverage, field ages and available pre-trigger scales over sufficient BTC data. A successful diagnostic row is not an eligible event.
2. Resolve independent liquidation valuation or explicitly revise the scientific feature contract before any fitting. Do not substitute bankruptcy-price notional.
3. Finalize the supported common feature list and quality rules; verify documentary ETH schema support without inspecting ETH observations.
4. Join eligible trigger/label ledgers to these decision-time features, preserving unknown lockout history and unavailable labels. Then assess sample sufficiency and chronological evaluation readiness.
