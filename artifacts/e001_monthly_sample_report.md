# BTC monthly sample feasibility result

Fixed scan: **2025-03-01 through 2026-09-01**, first day of each month only. These are 19 isolated days, not continuous monthly coverage. The calendar and unchanged event rule are recorded in [the scan protocol](../experiments/e001_monthly_scan_protocol.md).

## Result

Completed **19/19 days**; acquisition/audit failures: **0**. Found **22 observable threshold crossings**, of which **18** were suppressed by the nominal two-hour lockout, leaving **4 nominal episodes** on **3 days**.

Nominal valid label counts: `{'downside-first': 1, 'recovery-first': 2, 'neither-by-horizon': 1}`. Missing-path or sample-boundary label exclusions: **0**. Additional nominal labels excluded by uncertain episode history: **2**. Valid labels whose lockout eligibility is supported by observed history: `{'neither-by-horizon': 1, 'recovery-first': 1}`.

The approved five-second midpoint rule gives **1,641,283/1,641,600 valid seconds (99.98069%)** across completed days. This measures quote availability and freshness; it does not verify feed connectivity.

**No model was fitted.** This scan has 4 nominal episodes, 1 nominal downside-positive labels and 0 history-qualified downside-positive labels. It cannot support the prescribed chronological training, calibration and held-out comparison. The spot scan also does not supply the complete perpetual feature panel. It establishes data-pipeline feasibility, not predictive skill or realistic trading performance.

## Every sampled day

Complete 30-minute windows require 1,801 consecutive valid one-second grid points. They overlap and are not independent training observations.

| Date | Valid seconds / 86,400 | Valid % | Complete 30m windows | Crossings | Nominal episodes | History-qualified valid labels |
|---|---:|---:|---:|---:|---:|---:|
| 2025-03-01 | 86,386 | 99.98380 | 77,238 | 0 | 0 | 0 |
| 2025-04-01 | 86,399 | 99.99884 | 84,599 | 0 | 0 | 0 |
| 2025-05-01 | 86,399 | 99.99884 | 84,599 | 0 | 0 | 0 |
| 2025-06-01 | 86,398 | 99.99769 | 82,798 | 0 | 0 | 0 |
| 2025-07-01 | 86,395 | 99.99421 | 82,673 | 0 | 0 | 0 |
| 2025-08-01 | 86,389 | 99.98727 | 82,789 | 0 | 0 | 0 |
| 2025-09-01 | 86,397 | 99.99653 | 84,597 | 0 | 0 | 0 |
| 2025-10-01 | 86,398 | 99.99769 | 84,598 | 0 | 0 | 0 |
| 2025-11-01 | 86,399 | 99.99884 | 84,599 | 0 | 0 | 0 |
| 2025-12-01 | 86,399 | 99.99884 | 84,599 | 8 | 1 | 0 |
| 2026-01-01 | 86,399 | 99.99884 | 84,599 | 0 | 0 | 0 |
| 2026-02-01 | 86,362 | 99.95602 | 80,962 | 6 | 1 | 0 |
| 2026-03-01 | 86,398 | 99.99769 | 84,598 | 8 | 2 | 2 |
| 2026-04-01 | 86,399 | 99.99884 | 84,599 | 0 | 0 | 0 |
| 2026-05-01 | 86,351 | 99.94329 | 61,976 | 0 | 0 | 0 |
| 2026-06-01 | 86,396 | 99.99537 | 80,996 | 0 | 0 | 0 |
| 2026-07-01 | 86,396 | 99.99537 | 84,596 | 0 | 0 | 0 |
| 2026-08-01 | 86,273 | 99.85301 | 36,196 | 0 | 0 | 0 |
| 2026-09-01 | 86,350 | 99.94213 | 56,348 | 0 | 0 | 0 |

## Nominal episode ledger

| Trigger (UTC) | Outcome | History status |
|---|---|---|
| 2025-12-01T00:06:06+00:00 | downside-first | ambiguous_lockout_history |
| 2026-02-01T23:06:40+00:00 | recovery-first | ambiguous_lockout_history |
| 2026-03-01T16:48:28+00:00 | neither-by-horizon | accepted_with_observed_lockout |
| 2026-03-01T22:36:40+00:00 | recovery-first | accepted_with_observed_lockout |

## Missing history and remaining limitations

Each sample begins without the preceding day's episode state. The history audit tracks all possible prior lockout states and treats unavailable trigger comparisons as potential unseen crossings. A nominal event is history-qualified only when every retained state permits it. Ambiguity is conservative; it is not evidence that a hidden event actually happened. An arbitrary two-hour burn-in alone is insufficient because an early ambiguous event can shift later lockouts.

Missing price comparisons can hide crossings, so the observed crossing count is not an estimate of all real episodes. Valid labels use the first observed barrier hit or the full 30-minute horizon; any missing price before resolution invalidates a label. The full primary horizon must fit inside the sampled day even for an early hit.

These first-of-month days omit most calendar time and cannot represent continuous market regimes. Quote age does not establish sequence continuity, disconnect status or usable book depth. No execution costs, fills or predictive performance were measured.

## Next implementation handoff

1. Keep this sample set as an ingestion and label regression fixture. Do not relax the event threshold or tune quote age to manufacture more labels.
2. Implement a BTC-only continuous collector for the two spot references plus Bybit perpetual trades, book, liquidation and derivative-state feeds. Persist raw messages, local receipt timestamps, connection/reset/sequence evidence and source versions. Use bounded storage and restartable checkpoints; define the forward observation period before inspecting its outcomes. A longer existing archive is an alternative only if its provenance and missingness can be established.
3. Verify synchronized book reconstruction and full 25-bps depth support, resolve liquidation notional semantics, then implement the remaining neutral/B4/MFSM feature windows. Do not substitute bankruptcy prices for execution prices.
4. Reassess independent episode counts, both classes and chronological blocks on that continuous period before constructing training/calibration/test splits. Keep model fitting disabled until the data and common-feature gates are met. ETH remains sealed and the freeze manifest remains pending.

## Reproduce and provenance

```bash
uv sync --locked --extra test
uv run --locked python scripts/e001_monthly_scan.py --download --workers 2
uv run --locked python scripts/e001_monthly_report.py
uv run --locked pytest -q
```

[Machine-readable results](e001_monthly_sample_results.json) retain all source hashes, per-day coverage and age/spread/disagreement diagnostics, all crossings and labels, history classifications, pipeline hashes and grid hashes. Source URLs and download receipts are retained locally in `data/raw/tardis/DATE/manifest.json`; raw data and derived grids are ignored by Git. The earlier three-day audit remains unchanged. A failed date is retained as a failure in the scan, never silently recorded as zero events.
