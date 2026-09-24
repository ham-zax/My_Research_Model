# Experiment 001 implementation status

Updated 2026-09-24. Branch: `feat/e001-milestone1`; starting revision `02436fb`. Existing README and plan edits were retained. No implementation commit or freeze tag has been created. This ledger supersedes earlier statements that Tardis samples could not be downloaded.

## Current result

The owner-approved spot midpoint/five-second candidate has now been scanned across **19 isolated first-of-month days, March 2025 through September 2026**. All 38 quote files were acquired and verified; no date failed. Overall grid coverage is **99.98069%**. There are **22 observed crossings, 18 nominal lockout exclusions and four nominal labelled episodes** (one downside-first, two recovery-first, one neither). Only **two** have eligibility supported by the conservative missing-history audit; both are binary-negative outcomes on March 1, 2026. This cannot support chronological model training, calibration and evaluation. **No model was fitted and no predictive score exists.**

Current result: [monthly sample report](e001_monthly_sample_report.md), with [machine-readable evidence](e001_monthly_sample_results.json). The original three-day audit remains preserved in `artifacts/e001_spot_reference_audit.md` and `artifacts/e001_quote_audit_results.json`.

The next acquisition implementation is now available: [continuous BTC recorder](../docs/e001_continuous_capture.md). All three public connections were reached without credentials. The initial 60-second live check captured every requested topic, including a liquidation message; its [integrity audit](e001_capture_initial_smoke.json) is preserved. These checks are software/data-access evidence, not eligible model-training periods. A separate [receipt-ordered replay](../docs/e001_capture_replay.md) now reconstructs books and ticker state with explicit clock, sequence and depth-coverage gates. The full common feature panel remains unfinished.

The final implementation passed a separate 45-second live check: **5,209 WebSocket messages**, a Binance REST depth snapshot, all three connections, six transport heartbeat responses and no connection errors. Its [integrity audit](e001_capture_final_smoke.json) includes code hashes matching the final collector. The quiet liquidation channel emitted no event in this final interval; the initial check verified that channel with an observed event. Ticker payloads included OI, funding, mark and index fields.

The original forward run `54dccf2599ba4c6e9394cbc20a660dc8` was **stopped and sealed** after replay and public clock probes exposed approximately 3.3 seconds of local clock lag. Its [integrity audit](e001_capture_before_clock_repair.json) passed with 150,615 records and zero queued unwritten records. Historical timestamps remain unchanged and unqualified for the primary grid. Chrony ran with clock control disabled (`-x`); the owner repaired Windows host time.

Fresh verification reported synchronized Windows service status and [exchange offset bounds containing zero](e001_clock_probe_host_fixed.json). A new 60-second capture passed [integrity](e001_capture_clock_fixed_smoke.json) and [replay](e001_replay_clock_fixed_smoke_results.json): 7,195 WebSocket messages, 58 valid composite seconds out of 63 including startup/shutdown, and no clock-review or sequence-gap diagnostics. The 1,000-level perpetual book still lacked full bid-band coverage for six of 59 initialized seconds; incomplete full-band values remain missing.

Development capture restarted at **2026-09-24 01:06:01 UTC**, run `53d688bfe33349aaab40dc8e7463c802`, PID at launch `10220`. Planned stop is **2026-09-25 00:19:44 UTC**, within the original 00:19:49 deadline. The 16 GiB directory-wide raw cap includes the preserved interrupted run. Output: `data/raw/live_btc_development/`; log: `collector-clock-fixed.log`. The [new launch receipt](e001_forward_capture_clock_fixed_start.json) verified all three sources, a Binance snapshot, a current checkpoint and code hashes matching the successful fresh capture. Verify live status from the process, checkpoint and manifest before resuming work. The outage remains unknown history, and this is not a completed development dataset yet.

Candidate versions are `e001-v1.2`, `E001-raw-candidate-2`, `E001-features-candidate-2`, and `E001-label-v3`. The manifest remains pending with null resolved hashes and dates; ETH observations remain unopened. The next agent must not interpret the candidate version names as existing Git tags or a completed freeze.

## Implemented paths

- `data.py`: synthetic BTC Bybit V5 trade/liquidation/L2 adapter, receipt timestamps, duplicate checks, side/unit rules and gap markers.
- `events.py`, `labels.py`: one-second trigger crossings, two-hour lockout, 15-second decision delay and barrier labels with missingness reasons. Label availability cannot precede the grid time where an outcome becomes observable.
- `features.py`: fixture book reconstruction, depth, persistent additions, causal flow windows and shared B4/MFSM components. Full neutral feature coverage and matched models remain unfinished.
- `public_archive.py`, `cli.py`: BTC archive and Tardis CSV audits; fixture output; real model build remains gated.
- `tardis_spot.py`, `scripts/e001_spot_feasibility.py`: retained legacy last-trade/one-second feasibility probe, labelled with its original raw candidate version.
- `spot_quotes.py`, `scripts/e001_quote_audit.py`: current quote midpoint reference, exact microsecond availability, capture-order states, invalid-quote handling, age/continuity/spread/disagreement diagnostics, per-second provenance, and sample episode/label ledgers.
- `scripts/fetch_e001_tardis_sample.py`: BTC-only first-of-month downloads; `--profile spot-quotes` restricts acquisition to two spot quote files. `scripts/audit_e001_tardis_sample.py` records full-file coverage.
- `experiments/e001_quote_audit_protocol.md`: fixed data-quality sensitivity panel. The primary five-second candidate was approved before its episode extraction. No outcome or prediction score selected the age limit.
- `experiments/e001_monthly_scan_protocol.md`, `scripts/e001_monthly_scan.py`: fixed 19-date scan, source/code hash validation, per-day checkpoints and explicit failures.
- `sampling.py`, `scripts/e001_monthly_report.py`: conservative possible-lockout history audit, distinguishing nominal labels from history-qualified labels; tracked coverage, crossing and label evidence plus implementation handoff.
- `collect.py`, `capture_store.py`, `capture_health.py`: BTC-only public recorder with original payloads, application receipt clocks, fixed-duration manifests, bounded queues/storage, segment hashes, crash-tail preservation, reconnect/heartbeat and sequence diagnostics. Optional pinned `collect` dependency.
- `scripts/audit_e001_capture.py`: completed-run integrity audit, per-topic counts, ticker-field inventory and missing Binance snapshot diagnostics. Does not certify source completeness.
- `replay.py`, `scripts/replay_e001_capture.py`: hash-verified closed captures or frozen sealed prefixes; Binance snapshot/range reconciliation, separate Bybit depth books, ticker-delta provenance, conservative quote freshness, finite-band coverage and clock gating. Outputs deterministic one-second grids and reports; no model fit.
- `scripts/probe_e001_clock.py`: bounded public exchange-time probes with original responses and local-step checks; never changes clocks or historical timestamps.

## Installed data

- Original event-time-only Binance and Bybit BTC spot trade archives for 2023-10-01 remain in ignored `data/raw/2023-10-01/`.
- Tardis 2025-03-01 BTCUSDT: Binance and Bybit spot trades/quotes, Bybit perpetual trades, L2, liquidations, derivative ticker. March audits found 26,774,896 L2 rows, 1,418,703 perpetual trades, 2,092 liquidation rows and 158,149 derivative-ticker rows. All audited rows had local timestamps and none preceded exchange time.
- Tardis first-of-month samples 2025-04-01 through 2026-09-01: two BTC spot quote files per day only. Together with March 2025, these are 19 nonconsecutive days, not 19 months of continuous observations.
- Raw sources and SHA-256 values are recorded under `data/raw/tardis/DATE/manifest.json`; the tracked monthly results retain all 38 quote-file hashes. Direct access succeeded using a Mozilla-style User-Agent after initial 403/404 probes failed.

## Reproduce

```bash
uv sync --locked --extra test
python3 scripts/fetch_e001_tardis_sample.py --date 2025-03-01
python3 scripts/audit_e001_tardis_sample.py --date 2025-03-01
python3 scripts/fetch_e001_tardis_sample.py --date 2025-04-01 --profile spot-quotes
python3 scripts/fetch_e001_tardis_sample.py --date 2025-05-01 --profile spot-quotes
uv run --locked python scripts/e001_quote_audit.py
uv run --locked python scripts/e001_monthly_scan.py --download --workers 2
uv run --locked python scripts/e001_monthly_report.py
uv run --locked pytest -q
```

Observed verification: full suite **90 passed** using `uv run --locked --extra collect --extra test pytest -q`. Nineteen replay tests cover receipt boundaries, snapshot alignment, book gaps/resets, ticker provenance, finite-depth coverage, clock gating and deterministic output. Twelve capture tests include actual local WebSocket disconnect/reconnect, complete queue draining, corrupt segment rejection, sequence gaps, snapshot resets, byte/count queue limits, total storage budgets and unclean restart preservation. Prior quote tests cover microsecond arrival at a grid boundary, exact five-second expiry, newer invalid quotes, timestamp regressions in capture order, unavailable future quotes, and invalid prices/sizes. Six history tests cover unknown prior-day state, exact lockout expiry, ambiguity after early events and gaps inside/outside confirmed lockouts. The 19-day scan completed; report generation verified source/checkpoint hashes, grid coverage and matching crossing ledgers. Original fixture/event/label/book/holdout tests still pass. `git diff --check` passed.

## Remaining gates and next eligible work

1. Audit the new forward run after it stops, then replay its exact manifest. For interim inspection, freeze sealed segments explicitly; do not consume its open tail. The short live checks are not a replacement for the missing development dataset. No paid access or account creation has been needed. The completed monthly sample scan supplies only two history-qualified labels, both negative, and cannot support model development.
2. Use the implemented book/ticker replay to audit receipt clocks, missing intervals and 25-bps depth coverage across the development period. Build the full pre-trigger depth history and observed-persistence features while preserving null full-band values when the feed is too shallow. Quote age and transport heartbeats alone do not prove source completeness.
3. Resolve liquidation notional without interpreting Bybit bankruptcy price as execution price; preserve normalized Tardis side semantics and the trade/liquidation contamination flag. Implement remaining OI/funding/basis/mark/index feature windows and the full common feature panel.
4. Finalize chronological BTC splits, model selection and calibration, then implement/fill the matched B4/MFSM evaluation from the approved plan. No synthetic or sparse-sample result can pass the BTC development gate.

The better long-term spot rule uses a synchronized reconstructed book with explicit source-health evidence. The approved five-second midpoint is a documented provisional rule for available quote archives. Preserve both facts when resuming. Do not expand to stocks, trading execution or ETH confirmation under the current data evidence.
