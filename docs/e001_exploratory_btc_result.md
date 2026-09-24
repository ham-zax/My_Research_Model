# Separate exploratory BTC result (E001-OBS-1)

Run date: 2026-09-24 UTC. This is the owner-selected free receipt-time observational test. It answers a narrower question than the original shock-triggered E001. The [frozen protocol](../experiments/e001_observational_exploratory_protocol.yaml), [full result with paired predictions](../artifacts/e001_observational_btc_result.json), and [provenance manifest](../artifacts/e001_observational_btc_manifest.json) are tracked. The local episode ledger is `data/derived/e001_observational_002/episodes.jsonl` and can be regenerated from the source data.

## Question and data

At each scheduled UTC hour 02:00–22:00 on 19 **nonconsecutive first-of-month days** from March 2025 through September 2026, does one sell-pressure × spread interaction improve a calibrated 30-minute downside-first forecast over a matched baseline? The seven baseline inputs are five-minute spot return and realized volatility, current spot spread and cross-venue disagreement, five-minute Bybit perpetual open-interest change, mark/index basis, and observed Bybit sell trade notional divided by current OI notional. MFSM receives those identical seven inputs plus the one interaction. Both models use the same pinned histogram boosting family, two-candidate tuning grid and disjoint calibration periods.

The spot reference is the equal-weight Binance/Bybit spot midquote on a one-second local-receipt grid, with each quote at most five seconds old. Decisions are scheduled hourly; they are **not** shock events. The first-passage label starts strictly after the decision, uses a 30-minute horizon and **−0.5% downside / +0.375% upside** barriers. Neither-by-horizon is class 0. These barriers differ from original E001. The source files are free [Tardis first-of-month CSV samples](https://docs.tardis.dev/downloadable-csv-files); no API key was used. The actual file hashes for each date are in the manifest.

## Predeclared split and measured result

The dates, decisions, feature list, barriers, two calendar folds, minimum row counts and primary paired Brier metric were written before any model score. The first run and the final input-validation rerun produced identical `result.json` bytes.

| Measure | Result |
|---|---:|
| Scheduled decisions | 399 |
| Eligible decisions | 375 |
| Eligible downside-first / recovery-first / neither | 41 / 66 / 268 |
| Exclusions (reasons can overlap) | 20 label-price gaps; 6 feature-history gaps |
| Paired held-out decisions | 126 across 7 sample days |
| Held-out downside-first outcomes | 18 |
| Baseline Brier | 0.13207137 |
| MFSM Brier | 0.13190346 |
| Primary improvement, baseline minus MFSM | **+0.00016791** |

Fold 1 tested March–May 2026: 58 eligible decisions, 6 downside-first outcomes, and **−0.00005077** Brier improvement. Fold 2 tested June–September 2026: 68 eligible decisions, 12 downside-first outcomes, and **+0.00035444** improvement. The earlier fit/calibration/validation blocks and exact episode IDs are recorded in the result. One calibration block contained only four positive outcomes; scikit-learn warned about its default five-way internal split. The frozen estimator and separate calibration periods remained unchanged; this warning is evidence of sample fragility, not a reason to tune the run after seeing its score.

Two **post-score descriptive checks**, excluded from the primary metric, limit the interpretation. A constant forecast using only each fold's earlier *fit-period* positive rate scored Brier **0.12661880** on the same 126 held-out decisions, better than either fitted model. The paired MFSM improvement becomes **−0.00087670** if June 2026 is omitted, and **+0.00111814** if September 2026 is omitted. The tiny positive aggregate is therefore sensitive to one sampled day. These checks are diagnostic comparisons; they were not used to select features, barriers, dates, or candidates.

**Conclusion:** this run does **not** demonstrate a useful predictive edge, let alone net trading profit. It only tests one interaction under a sparse observational design. It does not validate the original E001 liquidation mechanism, a simulation of real stock or crypto market dynamics, causal effects, or execution quality. Both fitted models scored worse than a simple earlier-history prior in this sample.

## Measurement limits

- The 19 sample days are isolated first days of months. The held-out result covers only seven days, and a first-of-month effect cannot be ruled out.
- Tardis `local_timestamp` orders observed arrival at its collector. These files do not provide an independently audited per-message venue source-age bound, cross-feed completeness certificate, or the original E001 timing qualification. The code rejects missing spot prices before a first barrier hit and hashes every used source file; it cannot prove a silent feed dropout did not occur.
- The flow is **observed ordinary sell trades**, not execution-valued liquidation notional. This study does not use L2 depth or liquidation messages, even though those files were also downloaded.
- Brier is a forecast-quality metric. There is no order placement, fee, slippage, market-impact or capacity model here. A lower Brier score alone would not establish a tradable edge.
- The original E001 real run stays `BLOCKED_TIMING` with zero eligible primary rows. Its strict and receipt-policy diagnostic outputs are separate from this study; ETH remains sealed.

## Reproduce and next decision

For a fresh checkout, fetch `--profile all` for each of the 19 dates in the protocol with `scripts/fetch_e001_tardis_sample.py`; the free Tardis first-of-month samples do not need a key. Then run:

```bash
uv run --locked --extra collect --extra eval python scripts/run_e001_exploratory.py \
  --output data/derived/e001_observational_REPRO
uv run --locked --extra collect --extra eval --extra test pytest -q
```

Use a new output name because the runner refuses to overwrite a prior receipt. The pinned protocol SHA-256 is `64b598d73d1bb02c25a00c031894167157dd9f11ed94f459b2f9d22aa8913c1d`; the final result SHA-256 is `16c162ae892d43d81938f098b968052bf92203544caab7e4f7c729c113a8f8bc`, the local episode ledger SHA-256 is `02f0d7aa110c3808c5d5be13983abb2e86fdb2ea1d47023a671ac6b3f20d0f39`, and the final manifest SHA-256 is `803e2815f6457836472278a07f1e9aca40e670c43b88ecc4bc4ce13674a1d4b2`.

The next useful observational test needs a **new versioned protocol before scoring**: continuous independent days, recorded feed continuity, a simple historical-rate comparator in the primary evaluation, and a causal fee/slippage benchmark if the claim is trading edge. The existing public Binance/Bybit live feeds need no key; continuous *historical* Tardis dates outside the free samples require a [subscription/API key](https://docs.tardis.dev/faq/billing-and-subscriptions). A subscription supplies more observational data, but it does not repair the original E001 per-role source-age or liquidation-valuation gaps. Do not retrofit this run's rules based on its score.
