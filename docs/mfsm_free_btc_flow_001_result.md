# Free historical BTC spot flow screen

Version: `MFSM-FREE-BTC-FLOW-001`<br>
Run date: 2026-09-25 UTC<br>
Status: retrospective observational screen; no trading-edge claim

## Question and frozen boundary

After an independent Binance BTCUSDT spot decline of at least 1% over exactly
300 seconds, does the fraction of 30-second traded quote value classified by
Binance as taker selling improve a 30-minute downside-before-recovery forecast
over price, volatility, total volume, and trade count alone?

The [protocol](../experiments/mfsm_free_btc_flow_001_protocol.json) was written
before this study computed labels or flow scores. It uses official Binance
one-second spot bars from July 2023 through August 2026. A crossing starts a
two-hour lockout. Features end with the bar 15 seconds after the trigger; that
bar is available at `t0+16s`. The future label starts with the next bar and uses
completed one-second closes: a further 1% decline before a 0.75% rise is class
1; an upside hit or neither hit within 30 minutes is class 0. All episodes
require contiguous history and future bars.

The fixed fit period ends in December 2025, and test episodes are in January
through August 2026. Any fit episode whose label matures after the test boundary
is purged. The test months' **price-only** event incidence had been inspected in
earlier acquisition work. This is a retrospective flow test, not a pristine
confirmation sample. No feature, threshold, model, or date was selected after
seeing this run's score.

The source format and availability are documented by the
[official Binance public archive](https://github.com/binance/binance-public-data).
The [result receipt](../artifacts/mfsm_free_btc_flow_001_result.json) pins all
38 source hashes, the earlier source manifest, protocol, code, local episode
ledger, predictions, Python, and scikit-learn versions. The protocol hash is
`9808cd7b019d2a11cbc2d3a2fdd8ba12639078423af1af5570f8618e156f0de4`.

## Measured result

The scan read **100,051,200** one-second bars with **zero gaps**. It found
3,067 raw crossings and 428 episodes after the two-hour lockout. All 428 had
complete feature and label windows. Their trigger timestamps exactly match the
428 accepted entries in the previously saved Binance price-only incidence
scan, an independent check of event construction.

| Fixed measure | Result |
|---|---:|
| Fit episodes (class 1 / class 0) | 344 (97 / 247) |
| Test episodes (class 1 / class 0) | 84 (19 / 65) |
| Test Brier: fit-period historical rate | 0.17814045 |
| Test Brier: price and volume baseline | **0.17764217** |
| Test Brier: same model plus taker-sell fraction | 0.18017092 |
| Test Brier: fixed flexible model with same inputs | 0.18597742 |
| Primary paired Brier improvement, baseline minus flow | **−0.00252876** |
| 95% percentile interval, 5,000 resamples of test calendar months | [−0.00385905, −0.00059699] |

The added flow fraction worsened the frozen logistic forecast in this test.
The paired improvement was negative in seven of eight test months. The month
interval describes uncertainty under a small eight-month block resampling
scheme; 19 positive test outcomes and earlier inspection of price-only event
incidence limit stronger inference. The fixed flexible model also scored worse
than the simple baseline. This result gives **no support for this particular
free spot flow feature**.

It does not test the canonical state or the distinct L2 depth and replenishment
interaction. It uses one venue's aggregated spot bars, has exchange timestamps
only, and has no receipt-time midquotes, perpetual book, executable fills,
fees, slippage, or P&L. The original E001 timing and capacity gates are not
altered. ETH was not accessed.

## Synthetic economy and next decision

The existing [reference timing result](mfsm_reference_timing_result.md) already
checks the proposed mechanism with buying present, late, and disabled. The
[limited-observation result](mfsm_reference_sensitivity_result.md) shows that
identical visible price and dealer inventory can conceal different debt and
produce different responses. Those synthetic checks specify what a future
measurement test must distinguish. They are not empirical wins.

Do not tune this flow screen against the 2026 outcomes or buy book data to
rescue its score. A future test of the depth/replenishment hypothesis requires
its own qualified book history and frozen comparison; a new prospective period
is needed for stronger confirmation. For any synthetic probability exercise,
the initial-state and disturbance distributions must be specified before
generating paths.

Reproduce the local scan and score from the hash-pinned public files:

```bash
uv run --locked --extra eval python scripts/run_mfsm_free_btc_flow.py \
  --output data/derived/mfsm_free_btc_flow_001_repro
uv run --locked --extra eval --extra test pytest -q tests/test_free_btc_flow.py
```

The runner refuses to overwrite an output directory. The local episode ledger
and test predictions are in `data/derived/mfsm_free_btc_flow_001/`; their hashes
are in the tracked result receipt.
