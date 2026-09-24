# Experiment 001 timing evidence and diagnostic candidates

Status: diagnostic implementation, 2026-09-24. The primary replay and feature policy remains the original strict rule. No new timing tolerance or model fit is authorized by this document.

## Clock and availability fields

Each raw market record retains its original `received_ns`, `monotonic_ns`, and venue timestamp fields. The recorder now emits `clock_probe` records for the public Binance and Bybit HTTP server-time endpoints, with:

| Field | Meaning |
|---|---|
| `source`, `domain`, `role` | Exchange, `http_server_time`, `server_time` |
| `epoch` | Collector wall/monotonic epoch; increments after a detected wall-clock step |
| `request_start_ns`, `request_start_monotonic_ns` | Local request start |
| `received_ns`, `received_monotonic_ns` | Local response receipt |
| `available_ns` | Probe parsing completion; replay uses the later capture-record availability |
| `server_ns`, `resolution_ns` | Returned server timestamp and its resolution |
| `offset_lower_ns`, `offset_upper_ns` | Interval for server clock minus local clock |
| `status`, `error_type`, `error` | Explicit success or bounded failure diagnostics |

Assuming the returned server timestamp was generated between request start and response receipt, the offset interval is `[server_ns - received_ns - resolution_ns, server_ns - request_start_ns + resolution_ns]`. A local wall/monotonic disagreement above 100 ms during the request invalidates the bound. These intervals include request asymmetry but do not bound absolute UTC error, server clock error, or a WebSocket clock. Probe records are selected only after their capture record is available, in the same epoch and exact timestamp domain, with an explicitly supplied maximum evidence age. No production expiry or drift bound has been selected.

The timestamp roles in the audit are separate: Bybit envelope `ts`, Bybit trade/liquidation item `T`, Binance event `E`, and Binance trade `T`. Ticker and book envelopes remain distinct topics. An HTTP probe cannot qualify any of these WebSocket roles without independent evidence that establishes their clock relationship. Historical captures have no contemporaneous `clock_probe` records and cannot be retroactively certified with today's probes.

The exchanges' own references distinguish these fields: [Bybit orderbook](https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook) calls `ts` system generation time and `cts` matching-engine time; [Bybit trade](https://bybit-exchange.github.io/docs/v5/websocket/public/trade) calls item `T` fill time; [Bybit server time](https://bybit-exchange.github.io/docs/v5/market/time) defines `timeNano` for its HTTP endpoint and warns that endpoint delivery can be delayed. [Binance spot WebSocket](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-streams/~) distinguishes event `E` and trade `T`, while [Binance REST](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general) exposes server time. **Inference from the reviewed references:** none supplies a numerical bound connecting the HTTP clock to every required WebSocket role. Open Web Search engines failed in this session, so the official pages were checked through the web fallback. No Khiip archive was available; these links are source references, not local captures.

## Diagnostic interpretations

For a supported source-domain interval `delta = source clock - local clock`, a source timestamp `s` corresponds to local event time `[s - delta_max, s - delta_min]`. Capture order and receipt availability remain unchanged. A quote is eligible only if its entire possible event interval precedes receipt and its oldest possible age at the decision is at most five seconds. Flow windows use `(left, right]`; a possibly in/out event is `ambiguous`, not a zero contribution. The pure helper for a one-second dwell rejects any start whose latest possible time has not completed the dwell. Full persistence valuation requires a shared-offset/drift model and boundary handling for every reduction; this helper is diagnostic only.

Candidate B indexes quotes, flow messages, and book updates by receipt availability in one local epoch. It changes the measurement from source-event flow to received flow. The audit reports receipt-age quote opportunities and 30-second window membership counts. The feature builder also supports `--timing-candidate receipt_diagnostic`: it calculates quote returns, trade flow, book persistence, depth, ticker fields and pre-trigger scales using receipt time while retaining every source timestamp and the original strict replay diagnostics. It uses the same economics and missingness rules as the strict builder. Every receipt candidate row carries `source_freshness_certified: false`, `primary_eligible: false`, and `model_ready: false`. The candidate does **not** certify delayed source data, full book coverage, liquidation execution value, or a complete feature panel. A source-age rule still needs domain evidence before Candidate B can become primary.

The legacy policy remains reproducible in `Replay` and `CaptureFeatureReplay`: any negative envelope receipt-minus-source lag permanently invalidates the capture's later primary composite; a local clock step does the same. The timing audit reports this behavior separately from Candidate B opportunities. Neither candidate is activated for labels or model rows.

The owner selected preparation of a [versioned receipt-time revision](e001_receipt_time_revision.md). The new `receipt_v1` output uses Candidate B's numeric measurements but adds explicit operational quality states, a protective gross source-lead rejection, and a separate schema/report. It still cannot qualify a primary row because independent UTC and role-specific WebSocket delay evidence are absent. The original 3.3-second clock-error sample is quarantined by the protective guard. The HTTP probes remain diagnostics only.

## Remaining selection gate

The fixed sealed captures provide no WebSocket-domain offset bounds. New HTTP probes record useful local/server-clock diagnostics but do not close that gap. To choose a primary policy, first establish a supported relation for each required WebSocket timestamp role, including validity duration and drift, or explicitly revise Experiment 001 to receipt-time measurements with a defensible delayed-data exclusion rule. Then compare quote, flow, book, and pre-trigger coverage on a short capture with contemporaneous evidence. The historical 3.3-second error must remain rejected.
