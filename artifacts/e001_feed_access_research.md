# Experiment 001 feed access research

Date: 2026-09-23. Scope: BTCUSDT feed access for Experiment 001. ETH observations remain sealed.

Update: this note records the initial six-feed acquisition. Subsequent work added both spot quote feeds for March, April and May 2025 and implemented the owner-approved provisional midpoint/five-second reference. Read [the current quote audit](e001_spot_reference_audit.md) and [implementation status](e001_implementation_status.md) for the current rule, measurements and next gate. The six-file table below is historical acquisition evidence, not the complete current inventory.

## Result

Tardis normalized CSV is the best current free/low-friction feed candidate for the BTC development pipeline because the downloaded BTCUSDT samples include both exchange event time (`timestamp`) and capture/arrival time (`local_timestamp`) in UTC microseconds. The earlier unauthenticated `datasets.tardis.dev` attempt that returned HTTP 403 was an incomplete access probe: the same sample URLs were successfully downloaded with a browser-like Mozilla `User-Agent`.

This does not make Experiment 001 ready for Milestone 2. The installed data covers one BTCUSDT sample day, 2025-03-01, and Tardis free unauthenticated access is documented as first-day-of-month historical datasets. Full BTC development still needs an approved multi-period data plan, exact split period, and reproducible coverage audit before fitting.

## Primary sources

- Tardis CSV overview: https://docs.tardis.dev/downloadable-csv-files/overview
  - Documents downloadable CSV datasets for tick-level `incremental_book_L2`, `trades`, `derivative_ticker`, and `liquidations`.
  - States first-day-of-month historical datasets are available without an API key.
  - States CSV datasets are exported from collected real-time WebSocket feeds.
  - States row order reflects original capture order.
- Tardis datasets API: https://docs.tardis.dev/downloadable-csv-files/api.md
  - Documents `GET https://datasets.tardis.dev/v1/:exchange/:dataType/:year/:month/:day/:symbol.csv.gz`.
  - States datasets are daily gzip CSVs, split by exchange, data type, and symbol.
  - States datasets are ordered by `local_timestamp`.
  - States unauthenticated access is available for first-day-of-month historical datasets.
  - States Pro and Business responses may include `x-md5`; use file size and gzip decompression success as primary integrity checks for large files.
- Tardis data types: https://docs.tardis.dev/downloadable-csv-files/data-types.md
  - Defines timestamp format as microseconds since epoch, UTC.
  - Defines `local_timestamp` as message arrival timestamp.
  - Defines normalized schemas for `trades`, `incremental_book_L2`, `derivative_ticker`, and `liquidations`.
- Tardis Bybit derivatives details: https://docs.tardis.dev/historical-data-details/bybit
  - States Bybit derivatives historical data is available for linear contracts since 2020-05-28.
  - States historical CSV datasets for first day of each month are downloadable without API key.
  - States Bybit derivatives data format is real-time Bybit WebSocket format plus local timestamps.
  - Lists `publicTrade`, `orderbook.50`, `tickers`, and liquidation channel availability windows; `allLiquidation` is available since 2025-02-25.
- Tardis Bybit spot details: https://docs.tardis.dev/historical-data-details/bybit-spot
  - States Bybit Spot historical data for all currency pairs is available since 2021-12-04.
  - Lists BTCUSDT downloadable samples for `trades`, `incremental_book_L2`, and `quotes`.
  - Lists v5 `publicTrade` and `orderbook.50` availability since 2023-04-05.
- Tardis exchange metadata API:
  - `https://api.tardis.dev/v1/exchanges/bybit`
  - `https://api.tardis.dev/v1/exchanges/bybit-spot`
  - `https://api.tardis.dev/v1/exchanges/binance`
  - `https://api.tardis.dev/v1/exchanges/binance-futures`
  - Queried on 2026-09-23. Current metadata listed BTCUSDT datasets for Bybit spot, Bybit derivatives, Binance spot, and Binance futures.

## Successful sample access method

The six BTCUSDT sample files were downloaded from `datasets.tardis.dev` for 2025-03-01 using the documented datasets path and a Mozilla-style `User-Agent`.

Pattern:

```text
https://datasets.tardis.dev/v1/{exchange}/{dataType}/2025/03/01/BTCUSDT.csv.gz
```

Example:

```text
https://datasets.tardis.dev/v1/bybit/trades/2025/03/01/BTCUSDT.csv.gz
```

Local command support exists in `scripts/fetch_e001_tardis_sample.py`. The script records source URL, retrieval time, file bytes, SHA-256, MD5, source `x-md5` when present, and whether the decompressed header includes `local_timestamp`. The script is a sample acquisition tool only; it does not approve the files for model fitting.

## Installed BTCUSDT samples

Source manifest: `data/raw/tardis/2025-03-01/manifest.json`.

Audit output: `data/derived/e001_tardis_audit_2025-03-01.json`.

All six files are BTCUSDT only, gzip compressed, and include `local_timestamp`.

| File | Rows | Bytes | SHA-256 | Event time range UTC microseconds | Local time range UTC microseconds | Receipt quality notes |
| --- | ---: | ---: | --- | --- | --- | --- |
| `binance_trades_2025-03-01_BTCUSDT.csv.gz` | 3,700,728 | 31,748,449 | `28ede02cd777138a99c73b3263cd2ed658dbc60aa1e47d9844fb7f23023dccfe` | 1740787200184756-1740873599489137 | 1740787200187373-1740873599492402 | 0 missing `local_timestamp`; 0 rows where local time precedes event time; rows in all 24 UTC hours |
| `bybit-spot_trades_2025-03-01_BTCUSDT.csv.gz` | 601,301 | 6,095,257 | `d3be9c72dd827e1c876493595966e534600e67405c388bb0a6ef0a50fc9c6efc` | 1740787200437000-1740873599941000 | 1740787200483830-1740873599979552 | 0 missing `local_timestamp`; 0 rows where local time precedes event time; rows in all 24 UTC hours |
| `bybit_trades_2025-03-01_BTCUSDT.csv.gz` | 1,418,703 | 39,694,407 | `28e3f4cd0e6cfbacbd0424054d424917c349901c7d73d0dc7fd04da69f66d794` | 1740787200062000-1740873599691000 | 1740787200101510-1740873599730443 | 0 missing `local_timestamp`; 0 rows where local time precedes event time; rows in all 24 UTC hours |
| `bybit_incremental_book_L2_2025-03-01_BTCUSDT.csv.gz` | 26,774,896 | 148,641,216 | `a0821cbc171c0e47c1429080783598e81e9d40e2a8b006b490de2eb1dc5d3fd5` | 1740787199833000-1740873599953000 | 1740787200011163-1740873599990215 | 0 missing `local_timestamp`; 0 rows where local time precedes event time; rows in all 24 UTC hours; 100 snapshot rows |
| `bybit_liquidations_2025-03-01_BTCUSDT.csv.gz` | 2,092 | 24,661 | `7fae926819808b32cd08c7d55b8a875a3aec13d28c63cfcdab42971523371e1f` | 1740787470625000-1740871427304000 | 1740787471090427-1740871427591157 | 0 missing `local_timestamp`; 0 rows where local time precedes event time; rows in all 24 UTC hours |
| `bybit_derivative_ticker_2025-03-01_BTCUSDT.csv.gz` | 158,149 | 1,917,955 | `e2fcc444f4d0dd6a9a3b78e7231bade8d35c2286036b74fc3bf73c72b0fe0c32` | 1740787198360000-1740873599159000 | 1740787200254310-1740873599195931 | 0 missing `local_timestamp`; 0 rows where local time precedes event time; rows in all 24 UTC hours; 158,149 nonempty `open_interest` rows |

## Header samples

Observed decompressed headers match the Tardis normalized schemas:

```text
exchange,symbol,timestamp,local_timestamp,id,side,price,amount
exchange,symbol,timestamp,local_timestamp,is_snapshot,side,price,amount
exchange,symbol,timestamp,local_timestamp,funding_timestamp,funding_rate,predicted_funding_rate,open_interest,last_price,index_price,mark_price
```

For trades and liquidations, `side` is the normalized taker or liquidation side field from Tardis, not the raw Bybit V5 `S` field. Do not mix the normalized CSV semantics with the exchange-native adapter without an explicit mapping note.

## Coverage against E001 feed needs

| E001 feed need | Current Tardis sample coverage | Remaining limit |
| --- | --- | --- |
| Two-venue BTC spot composite with receipt time | Binance BTCUSDT trades and Bybit Spot BTCUSDT trades include `timestamp` and `local_timestamp` across all 24 hours on 2025-03-01 | One sample day only; need full BTC development period and final composite construction tests |
| Bybit BTCUSDT perpetual trades with receipt time | Bybit BTCUSDT derivative trades include `timestamp`, `local_timestamp`, side, price, amount, id | One sample day only; need de-duplication and row-order policy frozen |
| Bybit BTCUSDT L2 book with receipt time | Bybit BTCUSDT `incremental_book_L2` includes updates and 100 snapshot rows with `local_timestamp` | Need book reconstruction continuity checks and handling of restarts/snapshots before feature extraction |
| Bybit BTCUSDT liquidations with receipt time | Bybit BTCUSDT normalized liquidation CSV includes 2,092 rows with `local_timestamp` | Need confirm normalized `side`, `price`, and `amount` economics for liquidation pressure; do not reuse raw Bybit bankruptcy-price assumptions blindly |
| OI, funding, mark, index | Bybit BTCUSDT `derivative_ticker` has `funding_timestamp`, `funding_rate`, `open_interest`, `last_price`, `index_price`, `mark_price`; all 158,149 rows have nonempty open interest in this sample | Need full-period availability and exact point-in-time feature rules |
| Venue status / disconnect evidence | Not covered by normalized CSV samples | Tardis docs state disconnect events are not included in CSV datasets; raw HTTP API or normalized replay with disconnect messages is needed if venue-status features are required |

## Practical limits and decisions

- The installed Tardis files support BTC-only feed feasibility and parser validation. They do not support a real model result.
- First-day-of-month free samples are useful for pipeline tests and schema audits, but they cannot replace a prespecified development sample.
- Use `local_timestamp` as receipt/availability time for point-in-time feature gating when using Tardis normalized CSV.
- Use row position as the tie-breaker when needed because Tardis documents CSV row order as original capture order.
- Do not access ETH samples until the Experiment 001 BTC gate and holdout protocol allow it.
- Do not treat Tardis normalized liquidation semantics as identical to raw Bybit V5 liquidation semantics without source-backed mapping.
- If full-period Tardis data is purchased or accessed with an API key, preserve raw `.csv.gz` files, manifests, hashes, exact source URLs, and audit outputs before any feature extraction.

## Original proposed next step (superseded by quote audit)

The initial next-step proposal below used trades for the spot reference. The later owner-approved quote definition supersedes item 1; follow the current implementation status before proceeding. The remaining derivative-feed work is still a software exercise until data gates are met:

1. Read Binance and Bybit Spot trades into a one-second composite using `local_timestamp` gating.
2. Reconstruct Bybit L2 book state from `incremental_book_L2`, discarding state at snapshot resets.
3. Join Bybit perpetual trades, liquidations, and derivative ticker rows by decision-time availability.
4. Produce a sample-day episode/feature table labelled clearly as `tardis_sample_day_software_check`.

Keep `build-real` gated for the actual E001 evaluation until a full BTC development dataset and source-coverage report exist.
