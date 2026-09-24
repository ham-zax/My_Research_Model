# Experiment 001 continuous BTC capture

Implemented 2026-09-24. This is the next acquisition step after the insufficient [19-day monthly sample scan](../artifacts/e001_monthly_sample_report.md). No model fit or experiment freeze is performed by the collector. ETH remains sealed.

## Access and source choice

**No API key is required.** Binance documents its unauthenticated [market-data-only endpoints](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md); Bybit documents [public topics without authentication](https://bybit-exchange.github.io/docs/v5/ws/connect). Both were reachable from this workspace during the live checks. There are no credential inputs or account/order operations in this implementation.

GitHub projects inspected: [Cryptofeed](https://github.com/bmoscon/cryptofeed) and Bybit's official [pybit](https://github.com/bybit-exchange/pybit). Both are relevant feed connectors. For this fixed three-connection recorder, the implementation uses the smaller [websockets client](https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html), pinned to 17.0.1 in the optional `collect` dependency and lockfile. Original text messages, receipt clocks and collector lifecycle records are retained together. This is an implementation choice, not a claim that the other projects cannot record raw messages. No third-party repository code was copied.

## Recorded inputs

| Source | Subscriptions | Purpose |
|---|---|---|
| Binance spot | `btcusdt@depth@100ms`, `btcusdt@trade` | Spot depth changes with source timestamps, spot trades |
| Binance spot REST | BTCUSDT depth snapshot, 5,000 levels, after each connection begins receiving | Snapshot plus buffered raw deltas for later replay |
| Bybit spot | `orderbook.1.BTCUSDT`, `orderbook.50.BTCUSDT`, `publicTrade.BTCUSDT` | Direct top quotes, depth and trades |
| Bybit linear perpetual | `orderbook.50.BTCUSDT`, `orderbook.1000.BTCUSDT`, `publicTrade.BTCUSDT`, `allLiquidation.BTCUSDT`, `tickers.BTCUSDT` | Fast depth plus deeper coverage, trades, liquidation reports, OI/funding/mark/index fields |

Bybit's [book documentation](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook) defines snapshots, deltas, service resets and cross-sequence ordering. The collector checks that deltas follow a snapshot and IDs increase; it does **not** impose an undocumented +1 rule. Repeated L1 snapshots are expected. The 1,000-level feed is slower than the 50-level feed; the two must remain distinct during replay. Finite depth does not prove complete 25-bps coverage, and RPI orders are excluded by the source.

Binance's [stream contract](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md) defines update ranges `U`/`u` and REST snapshot reconciliation. The recorder detects gaps between incoming depth ranges and reconnects, obtains a fresh snapshot per connection, and retains all inputs. The separate [replay implementation](e001_capture_replay.md) now reconstructs books and checks snapshot alignment and depth coverage. Its first live audit found a local clock offset; those historical captures remain unqualified. A fresh capture after Windows host repair passed the timing gate. A snapshot request's start and receipt times are retained; it cannot be used before receipt.

Bybit's [ticker contract](https://bybit-exchange.github.io/docs/v5/websocket/public/ticker) uses snapshots followed by deltas; omitted fields are unchanged. The recorder requires an initial ticker snapshot and preserves the payload for later stateful reconstruction. Bybit [liquidation messages](https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation) report position side, size and bankruptcy price. The collector preserves those fields without treating bankruptcy price as executed notional. A quiet liquidation channel need not emit a message during a short check.

## Run

**Latest status, 2026-09-24 05:31 UTC:** the restarted development process was no longer running. Its last checkpoint was 03:59:45 UTC, with no clean terminal marker. The [interruption record](../artifacts/e001_capture_interruption_observation.json) preserves the original manifest/checkpoint and verifies the open tail was sealed unchanged as `.unclean`. The old manifest's `running` field is stale. A new [60-second recovery check](../artifacts/e001_capture_recovery_smoke.json) passed integrity, but its [replay](../artifacts/e001_replay_recovery_smoke_results.json) failed the existing timing gate (Bybit median receipt-minus-source -2 ms). Long collection has **not restarted**. The launch details below describe historical runs.

A bounded background recording started at **2026-09-24 00:19:49 UTC**. Run `54dccf2599ba4c6e9394cbc20a660dc8` was subsequently **stopped and sealed** for the approved clock repair; its [integrity audit](../artifacts/e001_capture_before_clock_repair.json) passed, but its original timestamps remain unsuitable for time-qualified replay. The [original launch observation](../artifacts/e001_forward_capture_start.json) is historical.

After host repair and a successful fresh short capture/replay, collection restarted at **2026-09-24 01:06:01 UTC** as run `53d688bfe33349aaab40dc8e7463c802`, PID at launch `10220`. Planned end: **2026-09-25 00:19:44 UTC**, within the original 00:19:49 deadline. The **16 GiB raw-data cap** applies to the same `data/raw/live_btc_development/` directory, including the preserved old run. Current operational files are `collector.pid`, `collector-clock-fixed.log`, the new manifest and `checkpoint.json`. This is a detached process, not an installed restart-on-boot service; it may stop early on a limit, fatal error, interrupt or host shutdown. The [new launch observation](../artifacts/e001_forward_capture_clock_fixed_start.json) confirms initial reception, not a completed-run audit. Check the live process and files before launching another writer.

Verification evidence: [initial live check](../artifacts/e001_capture_initial_smoke.json), [final implementation live check](../artifacts/e001_capture_final_smoke.json), and [post-repair integrity check](../artifacts/e001_capture_clock_fixed_smoke.json) with [replay results](../artifacts/e001_replay_clock_fixed_smoke_results.json). All **90 tests** passed with both `collect` and `test` extras installed.

From the repository root, on Linux (the writer lock uses `fcntl`):

```bash
uv sync --locked --extra collect --extra test
uv run --locked --extra collect python -m mfsm_e001.collect \
  --duration 60 --max-mib 128 --output data/raw/live_btc_check
```

For a fixed 24-hour forward recording, in a terminal/session that remains running:

```bash
uv run --locked --extra collect python -m mfsm_e001.collect \
  --duration 86400 --max-mib 16384 --output data/raw/live_btc_development
```

The second command permits up to 16 GiB of raw segments, including prior runs in that output directory. It stops at the earlier of the fixed duration, storage cap, fatal error or interrupt. It does not remove older observations. Metadata uses additional space. Recording is uncompressed; extrapolate space needs cautiously from measured runs, because activity varies. No background service is installed automatically.

Each run writes a manifest **before opening feeds**, recording the planned duration/end, immutable source subscriptions, code hashes and limits. This prespecifies acquisition, not the eventual scientific train/calibration/test split. A restart records a new period and unknown preceding history; there is no historical backfill or claim that the outage was recovered. Do not select periods or stop recording based on event outcomes.

The command prints the manifest path when finished. Audit that exact run:

```bash
uv run --locked --extra collect python scripts/audit_e001_capture.py \
  data/raw/live_btc_check/RUN_ID.manifest.json \
  --output data/derived/live_btc_check_audit.json
```

Replace `RUN_ID` with the printed identifier. The audit verifies file hashes, byte/record counts, sequential capture IDs and the terminal marker. It reports channel observations, ticker fields, connection errors and missing Binance snapshots. A passed integrity audit establishes storage consistency, not market-data completeness.

## Storage and health behavior

- Original text payloads are stored inside JSONL envelopes with wall-clock nanoseconds, monotonic nanoseconds, connection ID and ordered record ID. These are **application receive timestamps**, not kernel/network-arrival timestamps and not a guarantee of nanosecond accuracy.
- Raw segments rotate near 8 MiB. The writer flushes and fsyncs approximately once per second, and seals segments with SHA-256 sidecars. An abrupt process or machine failure can lose the most recent buffered records; never assume a clean stop after a crash.
- One writer holds an exclusive directory lock. Restart leaves clean segments untouched and seals previous `.open` tails unchanged as `.unclean`, with hashes and explicit recovery metadata. Do not silently feed these tails into training.
- Memory queues have both message-count and 32-MiB serialized-byte limits. Overflow stops the run explicitly; no latest-value overwrite or sampling drops are used.
- Subscription acknowledgements, protocol heartbeat responses, Bybit application pings, snapshot resets, connection attempts/errors/disconnections and local clock steps are recorded. Required depth/ticker topics are checked every 20 seconds for initial observation and 30-second inactivity; this is an operational reconnect policy, not proof of source completeness.
- Reconnects use capped backoff. Five consecutive short/failed connections stop the whole run. Connections rotate before Binance's 24-hour lifetime. SIGINT/SIGTERM drain queued records and seal the run; an interrupt remains distinct from reaching the planned duration.
- Clock changes over 100 ms relative to monotonic time and event-loop delays over 100 ms beyond the one-second watch interval are flagged. Host clock synchronization and exchange-versus-local clock offset still need a separate audit.
- `duration_reached` means the planned timer elapsed, not that every second was usable. Inspect lifecycle records and gaps. The manifest always leaves `feed_completeness_verified` and `model_fitting_enabled` false.

## Next data gate

Book/ticker replay and its timing/depth audit are now [implemented](e001_capture_replay.md). The fresh post-repair capture passed the clock gate; keep auditing the development run and implement the full common perpetual feature panel. Full 25-bps coverage is still incomplete in some 1,000-level book states. Keep the existing approved price/event/label definitions. The fixture-only adapter currently accepts `orderbook.50` and is not the reader for this new capture envelope.

The [live feature builder](e001_live_features.md) now implements supported trade, book, ticker and normalized summaries. The later recovery check shows that passing the first short clock audit did not establish lasting agreement with venue clocks. Resolve the residual clock disagreement under an explicit policy before primary collection resumes; synchronization status alone is not a substitute for recorded-message timing checks.

Longer collection must supply independently eligible episodes and both outcome classes before chronological model development. A successful short feed check is not an event sample or a predictive result.

## Research provenance

Open WebSearch attempts on Startpage and Bing failed (token extraction / HTTP 301); available web search was used as fallback. Known primary URLs were archived through the running Khiip daemon. Capture identifiers:

| Source | Khiip capture ID |
|---|---|
| Cryptofeed repository | `01M38BT0XRQ7AP2BP17EJ3J3PZ` |
| pybit repository | `01M38BT11FB4DQ0W5TW0VKHVRY` |
| Bybit connection contract | `01M38BT0EHJEF0511W7G7DB4CE` |
| Bybit order book | `01M358YH7SM1W1D6W8VZXGFNDG` |
| Bybit ticker | `01M38BT1S2NGJSKWQ5NCXGTZTW` |
| Bybit all-liquidation | `01M37MAHRW17T74XT8R1G5FHWH` |
| Binance streams (GitHub page) | `01M38C2V651D61GNJNYSVBAG66` |
| websockets client | `01M38BT5S0QX0MXAKEKN9VR2SR` |

Captures are stored in the local Khiip vault under `captures/web/`, with provenance/raw artifacts managed by Khiip. Capture of Binance's raw-content URL timed out; the GitHub page capture succeeded. No success is claimed for the timed-out URL.
