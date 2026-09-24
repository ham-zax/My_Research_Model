# Experiment 001 data readiness audit

Date: 2026-09-23. Scope: Milestone 1 preparation and BTC spot-reference feasibility. Evidence about an API's current fields is **not** evidence that an identical historical archive exists or preserves local receipt times.

## Current state

- No raw BTC research dataset or existing executable pipeline was present at the start of this milestone. A bounded public BTC **spot-trade sample** for 2023-10-01 has since been downloaded into ignored `data/raw/2023-10-01/`; it is insufficient for the full experiment.
- No ETH market records were opened.
- Receipt-timestamped Tardis BTC samples are now installed: eight feeds on 2025-03-01, plus Binance/Bybit spot quotes on 2025-04-01 and 2025-05-01. The three-day quote audit produced zero eligible events. Full model evaluation remains blocked by sample sufficiency, feed-health evidence, liquidation valuation and unfinished feature/model code. See `e001_spot_reference_audit.md` for the current measured result.
- The [freeze manifest](../experiments/Experiment_001_Freeze_Manifest.yaml) remains pending. Do not fill its release fields during this milestone.

## Source inspection

| Venue / candidate | Verified current semantics | Historical evidence and decision |
| --- | --- | --- |
| Bybit V5 BTCUSDT spot and linear perpetual | [Public trades](https://bybit-exchange.github.io/docs/v5/websocket/public/trade): `S` is taker side, `v` size, `p` trade price, `T` fill time, `i` trade ID. A message can contain multiple trades with the same sequence. [Orderbook](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook): snapshot resets the book, deltas set absolute level size, zero deletes, `u` is update ID and `seq` orders messages. Spot and linear book streams are documented. [All Liquidation](https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation): `S=Buy` denotes a liquidated long, `v` executed size, `p` bankruptcy price; the stream is pushed every 500 ms and covers USDT, USDC and inverse contracts. [Open interest](https://bybit-exchange.github.io/docs/v5/market/open-interest): linear BTCUSDT units are BTC; historical API intervals start at 5 minutes, and delivery may lag in severe volatility. [Funding history](https://bybit-exchange.github.io/docs/v5/market/history-fund-rate) is documented. | Current field definitions support a **candidate** Bybit adapter for BTCUSDT spot/linear. They do not prove complete historical L2, liquidation, receipt timestamps, or 1–60 second OI observations. A Bybit archive and contract-version record are required before real feature extraction. Do not infer executed liquidation notional by multiplying size by bankruptcy price. |
| Binance BTCUSDT spot and USDT-margined perpetual | Tardis BTC spot trades and quotes now provide receipt-timestamped samples; the quote midpoint is supported by the provisional spot reference. | Spot quote parser approved for the candidate feasibility audit. Binance perpetual field, depth-sequence, liquidation sampling and full historical coverage remain unaudited. |
| OKX BTC spot and perpetual | Candidate venue named in the experiment, but no field-level or historical archive was verified in this audit. | Excluded from the initial adapter. Add only after its own evidence and mapping. |

## Free public spot archives now installed

The [official Binance public-data repository](https://github.com/binance/binance-public-data) documents daily spot trade CSV archives, source columns, checksum companions, and the change to microsecond spot timestamps from 2025-01-01 onward. The 2023-10-01 sample uses milliseconds. The [Bybit public directory](https://public.bybit.com/spot/BTCUSDT/) exposes daily gzipped BTCUSDT spot CSV files. The local files are excluded from Git and may be reproduced from these URLs:

| File | Source URL | SHA-256 | Parsed records | Event-time range (UTC epoch ms) |
| --- | --- | --- | ---: | --- |
| `data/raw/2023-10-01/binance-btcusdt-spot-trades.zip` | `https://data.binance.vision/data/spot/daily/trades/BTCUSDT/BTCUSDT-trades-2023-10-01.zip` | `afcd135830251d10117343740f7a87134cd3f84bc81ef858468cc84cd9609710` | 883,593 | 1696118400000–1696204799999 |
| `data/raw/2023-10-01/bybit-btcusdt-spot.csv.gz` | `https://public.bybit.com/spot/BTCUSDT/BTCUSDT_2023-10-01.csv.gz` | `1839e975392b13b9cb4ab7a95464adfef7c9b763d12aefc9fcb6c5c91c35789c` | 140,577 | 1696118403019–1696204798240 |

The Binance digest matched its downloaded `.CHECKSUM` companion. The Bybit digest is a local integrity record; no independently published checksum was verified. Both parsed files contain **zero receipt timestamps**. The public archive reader preserves that fact as `received_ms=None`. See `src/mfsm_e001/public_archive.py` for the narrow parsers and their tests. A [third-party downloader](https://github.com/flowdrivenml/bybit-history-downloader) documents public Bybit L2 downloads, but it was inspected only as a candidate; its code was not installed or run and historical content/schema have not been verified here.

From the repository root, `python3 scripts/fetch_e001_public_spot.py` retrieves or verifies exactly these two files. `uv sync --locked --extra test` installs the test environment, and `uv run --locked python -m mfsm_e001.cli audit-public --binance data/raw/2023-10-01/binance-btcusdt-spot-trades.zip --bybit data/raw/2023-10-01/bybit-btcusdt-spot.csv.gz --output data/derived/e001_public_audit.json` reproduces the counts, hashes and event-time ranges. The audit command does **not** build events or claim historical availability at a trading decision time.

The Bybit documents above were retrieved live on 2026-09-23 and archived through Khiip under `captures/web/` in the local vault. The original documents are the cited source of field semantics; the capture is a provenance record. Binance's redirected page did not expose substantive feed details to the retrieval tools, and the OKX search did not produce a verified source. Those gaps remain unknown rather than being filled by assumptions.

## Tardis normalized CSV candidate

Tardis is now the most concrete candidate for a point-in-time BTC feed. Its downloadable CSV overview says CSV datasets include tick-level L2, trades, derivative tickers and liquidations; first-day-of-month historical datasets are available without an API key; exports come from collected real-time WebSocket feeds; and row order reflects original capture order. Its datasets API says files are daily gzip CSVs split by exchange, data type and symbol, ordered by `local_timestamp`, with `local_timestamp` serving as the receipt-time field. Its data-type documentation defines timestamps as UTC microseconds and lists these normalized schemas:

| Tardis data type | Required audit columns |
| --- | --- |
| `trades` | `exchange`, `symbol`, `timestamp`, `local_timestamp`, `id`, `side`, `price`, `amount` |
| `incremental_book_L2` | `exchange`, `symbol`, `timestamp`, `local_timestamp`, `is_snapshot`, `side`, `price`, `amount` |
| `derivative_ticker` | `exchange`, `symbol`, `timestamp`, `local_timestamp`, `funding_timestamp`, `funding_rate`, `predicted_funding_rate`, `open_interest`, `last_price`, `index_price`, `mark_price` |
| `liquidations` | `exchange`, `symbol`, `timestamp`, `local_timestamp`, `id`, `side`, `price`, `amount` |

Tardis Bybit Spot documentation states all spot pairs are available since 2021-12-04 and includes BTCUSDT spot sample links for `trades`, `incremental_book_L2`, and `quotes`. It also lists v5 `publicTrade` and `orderbook.50` availability since 2023-04-05. Tardis Bybit Derivatives documentation states linear contract coverage since 2020-05-28, lists BTCUSDT in the exchange metadata API with `trades`, `incremental_book_L2`, `derivative_ticker`, and `liquidations`, and states `allLiquidation` is available since 2025-02-25.

Verified Tardis sources, retrieved live on 2026-09-23:

- https://docs.tardis.dev/downloadable-csv-files/overview
- https://docs.tardis.dev/downloadable-csv-files/api.md
- https://docs.tardis.dev/downloadable-csv-files/data-types.md
- https://docs.tardis.dev/historical-data-details/bybit
- https://docs.tardis.dev/historical-data-details/bybit-spot
- `https://api.tardis.dev/v1/exchanges/bybit`, `bybit-spot`, `binance`, and `binance-futures` were queried to verify current BTCUSDT dataset symbols and data types.

Repository support added: `src/mfsm_e001/public_archive.py` audits local Tardis normalized `.csv.gz` files for BTCUSDT only, validates the required columns above, preserves `timestamp` and `local_timestamp` in microseconds, records SHA-256, and rejects ETH rows. The CLI command is:

```bash
uv run --locked python -m mfsm_e001.cli audit-tardis \
  --file data/raw/tardis/bybit_trades_YYYY-MM-DD_BTCUSDT.csv.gz \
  --data-type trades \
  --exchange bybit \
  --symbol BTCUSDT \
  --output data/derived/e001_tardis_trades_audit.json
```

The first access probe returned HTTP 403/404, but the documented sample URLs downloaded successfully with a Mozilla-style User-Agent. `scripts/fetch_e001_tardis_sample.py` records source URLs, byte sizes and hashes; `scripts/audit_e001_tardis_sample.py` audited the March feeds. That day has 26,774,896 Bybit L2 rows, 1,418,703 perpetual trade rows, 2,092 liquidation rows and 158,149 derivative ticker rows with nonempty OI, in addition to spot feeds. Every audited row has a local timestamp and none precedes its exchange timestamp. This does not establish a sufficient development sample or complete feed continuity.

## Input-family decision table

| Family | Status for synthetic fixture | Status for real BTC research |
| --- | --- | --- |
| Independent spot reference | Midquote rule specified below | Tardis spot quotes with receipt times on three sample days; 99.98%+ valid seconds with five-second age cap; zero eligible events |
| Perpetual trades and aggressor side | Synthetic normalizer | One Tardis Bybit BTCUSDT day installed; full-period contract and duplicate policy remain to be finalized |
| L2 snapshots, deltas, and sequence continuity | Synthetic reconstruction | One normalized Bybit day installed; snapshot semantics documented, raw sequence/disconnect evidence and 25 bps band coverage still require validation |
| Liquidation sell size and notional | Synthetic base size only | One normalized Bybit day installed. Tardis side denotes liquidation pressure; price preserves exchange semantics. Executed notional valuation and trade de-duplication remain unresolved |
| OI, funding, basis, mark/index | Synthetic availability metadata only | One derivative-ticker day contains OI, upcoming funding rate, mark and index with receipt times. This is a WebSocket archive, distinct from the five-minute REST OI history. Full feature windows and historical field semantics remain to be implemented |
| Venue status, outages, contract changes | Synthetic validity markers | Historical archive, timestamp and contract metadata missing |

## Approved candidate spot reference

On 2026-09-23 the owner approved equal-weight Binance/Bybit BTCUSDT spot midquotes with a five-second maximum source-event age. Each source must be received by the integer UTC grid boundary, have positive finite prices and displayed sizes, and have bid strictly below ask. Preserve microsecond event/receipt precision and capture order; a newer invalid quote invalidates that source instead of falling back to an older valid state. Both venues are required. `experiments/e001_data_schema.yaml` and Experiment 001 Section 4 own the exact rule.

This advances the candidate to `e001-v1.2`, raw schema `E001-raw-candidate-2`, and label schema `E001-label-v3`. The prior last-trade/one-second rule and its feasibility result are retained as historical artifacts. The change was approved before model fitting; the freeze manifest remains pending.

[The current audit](e001_spot_reference_audit.md) compares quote-age limits, continuous 30-minute paths, spreads and venue disagreement across three preselected monthly samples. Quote CSVs omit disconnect messages and update only when the top of book changes. The five-second rule is therefore provisional, and a synchronized full-book/feed-health approach remains preferable when its required metadata are available.

## Remaining owner decisions and access

1. Obtain or collect a prespecified BTC development period with enough independent selloff episodes and contemporaneous required feeds. Installed monthly samples verify parsers and timing, but the three quote days have zero eligible events. Keep source files BTC-only; no ETH or mixed-asset observations have been opened.
2. Establish historical field-version dates, coverage, gaps, permission/cost terms, and receipt timestamps for each source. Live API docs cannot settle these.
3. Decide and version how executed liquidation notional is measured when feed `p` is a bankruptcy price. Until then the adapter exposes base size and marks liquidation notional unavailable.
4. Confirm whether a common BTC/ETH primary feature panel exists before freeze. An unavailable field must follow the spec's missingness rule, not be silently imputed.

The receipt-aware spot feasibility path is now implemented. Full feature and matched-model work must satisfy the remaining data gates before a predictive result is reported.

The bounded secondary capacity comparison is fixed in `experiments/e001_capacity_diagnostic.md`; it is not a substitute for the missing L2 archive or for the primary E001 evaluation.
