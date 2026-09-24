# E001: what can be tested without buying historical files

Updated: 2026-09-24 UTC

## Decision

Do not require a paid-data purchase to continue BTC experimentation. Keep the
frozen E001-LIQ-OBS-1 historical top-50 liquidity comparison separate from any
new free trade-flow study. A free-data result can reject or motivate a narrower
trade-flow idea; it cannot validate the frozen book-depth/replenishment claim.

## Verified free inputs

| Source | What it supports | Limit for frozen E001-LIQ-OBS-1 |
|---|---|---|
| [Binance public archive](https://github.com/binance/binance-public-data) | Continuous BTC spot one-second bars and trade files | These files do not contain the two-venue receipt-time midpoint or Bybit perpetual L2 book history. |
| [Bybit public spot archive](https://public.bybit.com/spot/BTCUSDT/) and [perpetual trade archive](https://public.bybit.com/trading/BTCUSDT/) | Continuous price and reported-side trade records; no key needed for the checked files | The checked CSV has exchange trade time, but no recorder receive time or order-book state. |
| [Tardis free CSV samples](https://docs.tardis.dev/downloadable-csv-files/overview) | First-of-month historical spot quotes, L2 updates, and trades | The 42 sampled dates produced 12 history-qualified independent sharp-selloff episodes in the prior event-source audit, below the frozen 130-episode gate. Sampling only first days of months also limits generalization. |
| [CryptoStruct free full-day samples](https://cryptostruct.com/docs/mcp) | Parser and depth-quality verification on one Bybit BTC perpetual day | The current free sample catalog does not provide continuous Bybit BTC perpetual L2 or the exact Binance/Bybit BTCUSDT spot pair for the historical window. |
| Existing public WebSocket collector | Future receipt-time spot and depth observations | The authorized short seed cannot meet the 130-episode gate; a long new capture period would need to be fixed in advance. |

The [free perpetual-trade availability receipt](../artifacts/e001_free_perpetual_trade_availability.json)
compares the existing official-Binance price-proxy ledger with Bybit's public
trade directory. All 283 distinct proxy event days are listed there (428
independent proxy episodes after the two-hour lockout). One 2024-01-01 Bybit
perpetual trade file was downloaded, gzip-checked, hashed, and header-checked.
This is an availability check, not a continuity audit of every file or a model
result. Bybit's [public trade documentation](https://bybit-exchange.github.io/docs/v5/market/recent-trade)
defines `side` as the taker side for its API; archive CSV correspondence still
needs validation before using side as aggressor flow.

A [one-day public/Tardis trade cross-check](../artifacts/e001_free_perp_trade_crosscheck.json)
on 2024-03-01 found 1,330,157 public trades and 1,330,148 Tardis trades.
All 1,330,148 Tardis IDs occurred in the public file; nine IDs occurred only
in the public file. The first 10,000 public IDs all matched Tardis on reported
side, price, and size. This verifies the mapping on one day, while leaving
every other selected day and source-time completeness unverified.

## Recommended no-cost next experiment

Version a separate BTC trade-flow protocol **before** computing labels or model
scores. Use the free multi-year price and perpetual-trade archives to compare a
simple historical-rate forecast, a price-only baseline, and one prespecified
trade-flow addition on chronological holdouts. Define trade timestamp/order,
staleness, gaps, event lockout, labels, feature windows, class minima, and a
conservative cross-venue timestamp-lag sensitivity and causal fee/slippage
benchmark in that protocol. Keep the paid-path acquisition
screen and the ETH holdout untouched.

This can test whether a *trade-flow* signal survives simple baselines across
many free historical days. It cannot measure visible top-50 depth, persistent
bid replenishment, source receipt delay, or executable capacity. If this free
study is weak, buying book data solely to chase its trade-flow effect has poor
motivation; that would not, by itself, disprove the distinct L2 hypothesis.

For the exact frozen historical L2 comparison, the currently verified free
archives are insufficient. Two alternatives remain: acquire the missing
historical spot/L2 files after a read-only quote and explicit spend decision,
or precommit to a long, independently qualified public-feed capture. The
observed Binance proxy rate of 428 episodes over 38 months implies roughly a
year to accumulate 130 episodes **before** quality exclusions if that rate
held in live data; this is a planning estimate, not a promise.
