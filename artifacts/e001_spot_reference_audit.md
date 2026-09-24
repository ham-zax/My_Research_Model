# BTC spot reference: measured coverage and better validity checks

Date: 2026-09-23. Candidate experiment: `e001-v1.2`. Raw schema: `E001-raw-candidate-2`. Label schema: `E001-label-v3`. Status: BTC data-quality and episode-feasibility result; no fitted model or predictive score.

## Finding

The approved equal-weight Binance/Bybit spot midpoint with a five-second quote-age cap has usable grid coverage in the three sampled days. Five seconds is a provisional measurement choice, not an empirically optimal setting. A better eventual validity test checks reconstructed source books, sequence continuity, disconnects, resynchronization and capture progress. An unchanged top quote and a stopped feed can both produce no quote update; a time cap alone cannot distinguish them.

The earlier claim that 62% last-trade coverage categorically prevents reliable labels was too strong. It establishes substantial exclusions in that one sample. The correct next checks are contiguous required label paths, exclusions near stress and enough actual triggered episodes. A first barrier hit can make a label valid before the full 30 minutes; conversely, a small percentage of missing seconds can invalidate many long paths.

## Fixed audit and observations

Dates were fixed to the first three consecutive monthly samples beginning with the already acquired March day: 2025-03-01, 2025-04-01 and 2025-05-01. The fixed protocol is [e001_quote_audit_protocol.md](../experiments/e001_quote_audit_protocol.md). Each source is BTCUSDT only, with original exchange and collector receipt timestamps. Quote states follow receipt/capture order, including when exchange timestamps regress. Both sources are required; invalid new states do not reuse an older quote.

| UTC day | Valid seconds, 5s cap | Grid coverage | Complete 30-minute windows | Accepted selloff events |
| --- | ---: | ---: | ---: | ---: |
| 2025-03-01 | 86,386 / 86,400 | 99.9838% | 77,238 | 0 |
| 2025-04-01 | 86,399 / 86,400 | 99.9988% | 84,599 | 0 |
| 2025-05-01 | 86,399 / 86,400 | 99.9988% | 84,599 | 0 |

A complete window includes its starting price and all subsequent one-second prices for 30 minutes: 1,801 points. There are 84,600 possible such windows inside a day. Window counts above are data continuity diagnostics at all possible starts, not independent episodes or model observations. The first grid second lacks an already received quote; March also has 13 Bybit quote-age exclusions.

The unchanged event threshold is a crossing to a five-minute return at or below -1%. **No accepted event occurred in these three sampled days**, so there are zero episode labels to fit or score. This is neither evidence of predictive success nor evidence of predictive failure.

| Quote-age cap | March complete windows | April complete windows | May complete windows |
| --- | ---: | ---: | ---: |
| 1 second | 0 | 7,545 | 3,868 |
| 2 seconds | 4,931 | 35,053 | 42,349 |
| 5 seconds, approved candidate | 77,238 | 84,599 | 84,599 |
| 10 seconds, diagnostic only | 84,599 | 84,599 | 84,599 |

On five-second-valid grids, the 99th percentile of cross-venue midpoint disagreement was 4.35, 2.41 and 1.85 basis points respectively; maxima were 8.03, 11.04 and 8.48 basis points. These are diagnostics, not grounds for an unannounced exclusion filter. The quote-age 99th percentile was at most 0.586 seconds for Binance and 1.651 seconds for Bybit across these days. A five-second limit therefore permits occasional older quotes; it does not mean all prices are delayed by five seconds.

## Why the better approach needs more evidence

[Tardis quote documentation](https://docs.tardis.dev/downloadable-csv-files/data-types.md#quotes) says these quotes are reconstructed from L2 and emitted when the top of book changes. The [CSV API documentation](https://docs.tardis.dev/downloadable-csv-files/api.md) states disconnect events are omitted. The [data FAQ](https://docs.tardis.dev/faq/data.md) explains that exchange timestamps can regress while capture timestamps determine file order. These primary sources were archived through the running Khiip daemon on 2026-09-23 as `captures/web/untitled-9.md`, `untitled-10.md`, and `untitled-11.md`.

The preferred next source includes raw spot book updates and connection/reset markers for **both** venues, so unchanged quotes can be retained only while the source book is demonstrably synchronized. It also needs an explicit maximum transport/processing delay rule and local collector clock audit. Receipt timestamps here refer to the provider's collection infrastructure, not guaranteed availability at a future trader's machine. No available quote file proves the absence of every missed update.

Keep the two-source arithmetic average simple for this candidate. Adding a third audited venue and a median could limit the effect of one bad source, but introduces source eligibility and outage decisions; that is a later prespecified comparison, not an automatic improvement. Avoid volume- or volatility-dependent weights without evidence because they can change the reference during stress.

## Reproduction and next gate

```bash
uv sync --locked --extra test
python3 scripts/fetch_e001_tardis_sample.py --date 2025-03-01 --profile spot-quotes
python3 scripts/fetch_e001_tardis_sample.py --date 2025-04-01 --profile spot-quotes
python3 scripts/fetch_e001_tardis_sample.py --date 2025-05-01 --profile spot-quotes
uv run --locked python scripts/e001_quote_audit.py
uv run --locked pytest -q
```

The tracked [machine-readable results](e001_quote_audit_results.json) contain actual source hashes, metrics and empty episode ledgers. Ignored per-second quote provenance is saved in `data/derived/e001_quote_grid_YYYY-MM-DD.jsonl.gz`; the original trade feasibility artifact remains in `data/derived/e001_spot_feasibility_2025-03-01.json`. The March sample additionally contains audited Bybit perpetual trades, L2, liquidation and derivative ticker feeds. April and May downloads contain only spot quotes.

Next gate: obtain a prespecified BTC development period with enough independent triggered episodes and the required contemporaneous feeds; complete feed-health, liquidation valuation and feature audits before matched chronological model fitting. Sparse free monthly samples do not establish that coverage during stress is adequate. No account was created, paid archive purchased, model fitted, freeze tag created or ETH observation opened.
