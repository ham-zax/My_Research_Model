# BTC capture replay and data-quality gate

Implemented and verified on 2026-09-24. This layer reads `E001-capture-v1` and produces `E001-replay-v1` one-second state grids. It does not fit models or supply the complete B4/MFSM feature panel.

## Measured result

The frozen first **seven sealed segments** of forward run `54dccf2599ba4c6e9394cbc20a660dc8` contain 58,715,949 bytes and span **771 grid seconds**, from 2026-09-24 00:19:50 through 00:32:40 UTC as recorded by the local clock. The open tail was excluded. [Machine-readable evidence](../artifacts/e001_replay_prefix_results.json) records every input hash and the exact code versions.

| Reconstructed stream | Initialized grid seconds | Full bid-side 25-bps band | Full ask-side 25-bps band |
|---|---:|---:|---:|
| Binance spot depth | 769 | 769 | 769 |
| Bybit perpetual 50 levels | 770 | 0 | 0 |
| Bybit perpetual 1,000 levels | 770 | 575 | 770 |

The required OI/funding/mark/index/next-funding fields were known in reconstructed ticker state for 770 seconds. These are **sequence/state reconstruction measurements**, not time-qualified model inputs. The 50-level book does not cover the requested band, and even 1,000 levels provide incomplete bid coverage in part of this interval. The output retains observed partial sums separately and sets a full-band notional to null when coverage is missing. Reported coverage refers to the displayed feed and excludes RPI/hidden liquidity.

**Valid primary spot-composite seconds: zero.** Receipt clocks lagged the venue event clocks. Median local-receipt minus event time was -3,296 ms for Binance, -3,332 ms for Bybit perpetual and -3,331 ms for Bybit spot. The [closed final smoke capture](../artifacts/e001_replay_smoke_results.json) has the same timing problem. Earlier capture integrity success remains valid, but did not establish clock validity.

## Clock diagnosis and host repair

Public server-time probes independently placed exchange clocks more than 3.29 seconds ahead of the local wall clock. [Probe evidence](../artifacts/e001_clock_probe_verified.json) preserves request/response bounds and raw responses. Bounds assume a fresh server timestamp generated during the request and make no symmetric-latency assumption; they do not prove the server clock's absolute UTC accuracy.

A local `chronyc tracking` check then reported **3.377450228 seconds slow of NTP time**. `timedatectl` simultaneously reported `NTP=yes` and `NTPSynchronized=yes`. The environment is WSL2; `systemd-timesyncd` was unavailable. Further inspection found Chrony running with `-x`, which disables system-clock control and explains the owner's `sudo chronyc makestep` returning `500 Failure`. Other Chrony readings used the Hyper-V PHC reference; agreement with that reference alone did not establish external clock accuracy. Full initial diagnostic output was saved under `data/derived/e001_chrony_tracking.txt` and `data/derived/e001_chrony_sources.txt`.

The replay retains original timestamps and sequence-reconstructed state but blocks the primary price grid after clock disagreement. No offset is fitted to market outcomes, no historical timestamps are rewritten, and no negative-lag state becomes a valid model row. A clock step or future source timestamp marks the rest of that replay run as needing clock review; successful host correction requires a fresh capture session before declaring timing repaired.

The owner approved stopping, sealing, correcting time and restarting through the original deadline. The original run was sealed with status `interrupted`: **150,615 records**, zero queued unwritten records, and a passed [integrity audit](../artifacts/e001_capture_before_clock_repair.json). Its timestamps remain unchanged. An initial elevated Windows resync returned exit code zero while service status still reported unsynchronized; it was not accepted as proof of repair.

The owner subsequently repaired Windows Time from Windows. Fresh checks from this workspace reported leap indicator 0, stratum 2, source `time.google.com,0x1` and last sync error 0. Three public probes per exchange all bracketed zero offset; the [new probe evidence](../artifacts/e001_clock_probe_host_fixed.json) no longer shows the earlier 3.3-second offset. These request bounds are not proof of microsecond UTC accuracy or long-term stability.

## Fresh capture after host repair

Run `094532e21b2946268a5d829746463ee7` completed its fixed 60-second recording with **7,524 records**, **7,195 WebSocket messages**, all three sources, one Binance REST snapshot and no connection errors or clock-step records. The quiet liquidation topic emitted no event. Its [integrity audit](../artifacts/e001_capture_clock_fixed_smoke.json) passed.

The [fresh replay](../artifacts/e001_replay_clock_fixed_smoke_results.json) produced **58 valid composite seconds out of 63 grid seconds**; the five exclusions were initial connection/snapshot availability and shutdown. There were no clock-review failures or sequence-gap diagnostics. Minimum receipt-minus-source lag buckets were **63 ms for Binance** and **19 ms for both Bybit streams**; median buckets were 67 ms and 21 ms respectively. This verifies the short observed interval, not future clock stability or sub-millisecond UTC accuracy.

Required ticker fields were known for 59 seconds. The Bybit 1,000-level perpetual book covered the full bid-side 25-bps band for **53 of 59 initialized seconds**, and the ask band for 59. The 50-level book covered neither full band. Partial depth remains explicitly missing for full-band features. No 30-minute windows or model results can come from this short check.

After these checks, development recording restarted as a **new run**, `53d688bfe33349aaab40dc8e7463c802`, in `data/raw/live_btc_development/` at **2026-09-24 01:06:01 UTC**. Its planned end is **2026-09-25 00:19:44 UTC**, five seconds before the original deadline to allow launch overhead. PID at launch: `10220`. The directory-wide **16 GiB** raw cap includes the preserved interrupted run. The [launch receipt](../artifacts/e001_forward_capture_clock_fixed_start.json) verifies all three sources, a Binance snapshot, fresh checkpoint and code hashes matching the successful smoke capture. It is a start observation, not proof of a completed development dataset. The outage remains an unknown-history interval.

## Replay contract

- Read immutable, hash-verified segments in global capture-record order. Verify segment numbering, record IDs, counts and schema. Reject out-of-scope assets/topics. A normal completed-run replay requires its terminal marker; an explicit sealed-prefix replay makes no claim of a complete run.
- Freeze the input file list at startup. `--max-segments N` reproduces the same initial prefix while the recorder continues. Open or unclean tails are never consumed. Grids use deterministic gzip encoding and exact Decimal arithmetic for price/size calculations.
- Start each connection with empty state. Disconnects and connection errors invalidate its books and ticker. Old-connection messages cannot revive state. Deltas without a snapshot remain unusable.
- Buffer Binance depth changes until the REST snapshot is received; discard already-covered ranges and require the next range to bridge its update ID. Gaps require a fresh snapshot/connection. A snapshot alone has no exchange event timestamp, so it cannot establish a fresh spot quote. Delayed REST results are applied at their position in capture order, never backdated.
- Reconstruct each Bybit depth stream separately. Snapshots replace state; deltas set absolute quantities and zero deletes a level. Trim to that stream's top N. Check monotonic update IDs/cross-sequences without assuming +1 increments.
- Keep Binance's initial snapshot price boundaries fixed: sparse later updates outside them do not establish knowledge of all intervening levels. Bybit coverage is bounded by the reconstructed current top N. Check each side of the 25-bps band independently.
- Merge ticker deltas into an initial snapshot. Omitted fields retain both value and their own prior observation timestamps. A new snapshot clears old fields; a reconnect clears all ticker state.
- Refresh a derived quote's age only when its best price or size changes. Repeated identical L1 snapshots and deep-only Binance changes do not extend quote freshness. Keep equal venue weights, both-venue requirements and the approved five-second maximum source age. This is a conservative capture-to-quote adapter, not a retuning of the event rule.
- Emit only grid boundaries supported by consumed receipts; never extrapolate past the last selected record. Raw book state can be reconstructed despite clock disagreement, but it is marked separately from receipt-clock validity. Source-age and clock checks must pass before the primary composite is populated.

The Binance reconciliation follows its [official stream contract](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md). Bybit snapshot/delta semantics and ticker field retention follow its [book](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook) and [ticker](https://bybit-exchange.github.io/docs/v5/websocket/public/ticker) contracts. The previous capture research note records their Khiip archives.

## Reproduce

```bash
uv run --locked python scripts/replay_e001_capture.py \
  data/raw/live_btc_clock_fixed_smoke/094532e21b2946268a5d829746463ee7.manifest.json \
  --output data/derived/e001_replay_clock_fixed_smoke

uv run --locked python scripts/replay_e001_capture.py \
  data/raw/live_btc_final/23b5d4a3f0614020a96bbb58344c725a.manifest.json \
  --output data/derived/e001_replay_final_smoke

uv run --locked python scripts/replay_e001_capture.py \
  data/raw/live_btc_development/54dccf2599ba4c6e9394cbc20a660dc8.manifest.json \
  --sealed-prefix --max-segments 7 \
  --output data/derived/e001_replay_forward_prefix

uv run --locked python scripts/probe_e001_clock.py --samples 3 \
  --output data/derived/e001_clock_probe.json

uv run --locked --extra collect --extra test pytest -q
```

Outputs are `grid.jsonl.gz` and `report.json`. The grid includes quote validity, observed/full-band depth, per-field ticker provenance and a false model-readiness flag. The report includes input/code/output hashes, diagnostics and a source-clock lag histogram. Tests: **90 passed**, including causal snapshot availability, exact nanosecond boundaries, disconnect resets, gap rejection, missing ticker fields, finite-depth coverage, clock gating and deterministic replay.

The public clock endpoints are documented by [Bybit](https://bybit-exchange.github.io/docs/v5/market/time) and [Binance](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md). Khiip capture IDs are `01M38D988Z4MQQ4ZGPXG4GDMPK` and `01M38DGWQ2DHMCFJNT0H7TTTEX`. Capture of the Binance developer-site page failed with an upstream extraction error; the GitHub documentation capture succeeded.

## Remaining implementation

Clock validity passed the fresh short session. Continue auditing the new development run, then build receipt-aware trade/liquidation windows, persistent book additions, the full pre-trigger depth history and neutral feature transforms from this replay. Do not route the new capture envelope directly into the fixture adapter, infer full depth from partial books, or value liquidations at bankruptcy prices. Keep model fitting disabled until the common feature panel and independently eligible development sample are sufficient.
