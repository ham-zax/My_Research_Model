# E001 historical BTC data path — CryptoStruct candidate

Updated: 2026-09-24

## Decision

Keep BTC as the next market for the separate E001-LIQ-OBS-1 study.

Do not treat the short forward capture as the research sample. Its fixed
20,673-second duration and the two-hour episode lockout permit at most three
independent episodes, while the frozen evaluation gate requires 130 eligible
episodes.

Use historical data to solve the sample-size problem while preserving the same
scientific question and the same frozen B4/MFSM feature definitions.

CryptoStruct is the current historical full-depth candidate because its native
day files expose the fields that the liquidity-state study actually needs:

- full Level-2 snapshots and absolute level updates;
- recorder receive time (adapterTs) in nanoseconds;
- venue/exchange time (exchangeTs) where supplied;
- event-id chains for book/trade gap detection;
- aggressor-side trades;
- one normalized schema across venues;
- one instrument per UTC day, with overlap around day boundaries.

This is a data-source decision, not a model result. Original E001 remains
blocked under its original measurement/timing contract, and the separate
liquidity-state study remains observational.

## Why this changes the prior data assessment

The earlier Tardis capacity work failed because the downloaded historical book
did not provide enough price-band coverage for the original 25 bps capacity
quantity, and the later 0.5 bps band was too fragile to act as a literal
capacity measure.

E001-LIQ-OBS-1 deliberately changed the empirical object. It needs the best
50 visible levels per side, their history, observed trade flow and persistent
bid replenishment. It does not interpret displayed depth as a maximum sell
flow that the market can absorb.

CryptoStruct's free Bybit BTCUSDT perpetual sample supports that narrower
observable state directly.

## Free-sample audit performed before any historical model scoring

Source page checked 2026-09-24:

- https://cryptostruct.com/download
- https://cryptostruct.com/skills/cryptostruct-market-data/references/day-file-format.md

Downloaded free sample:

- venue: Bybit perpetual
- instrument: BTCUSDT
- CryptoStruct instrument id: 2449
- nominal day: 2026-09-17
- local audit file: /tmp/cryptostruct-bybit-BTCUSDT-2026-09-17.txt.zst
- compressed size observed locally: about 233 MiB
- decompressed size verified by zstd -t: 1,106,807,478 bytes

The provider's published streaming reader reported:

| Measurement | Result |
|---|---:|
| total events | 5,095,711 |
| book updates | 2,930,693 |
| trade-event batches | 513,174 |
| individual trade fills | 1,708,571 |
| top-of-book events | 1,478,568 |
| mark events | 62,148 |
| index events | 111,120 |
| snapshots | 1 |
| parse errors | 0 |
| book-chain gaps | 0 |
| trade-chain gaps | 0 |
| crossed book states | 0 |
| maximum reconstructed levels | 100 |

A separate one-second replay of the full sample day found:

- sampled seconds: 86,937;
- clean 50 bid + 50 ask levels: 86,937 / 86,937;
- suspect seconds: 0;
- crossed seconds: 0;
- minimum sampled bid levels: 50;
- minimum sampled ask levels: 50.

This is strong measurement-feasibility evidence for the frozen top-50
liquidity definition. It is not prediction evidence. The machine-readable
receipt is [e001_historical_data_candidate_audit.json](../artifacts/e001_historical_data_candidate_audit.json).

### Receipt/exchange timing check

Across the model-relevant sample streams, no record had exchangeTs greater
than adapterTs.

Observed receive-minus-exchange timing on the sample:

| Stream | Records | Mean | Minimum | Maximum |
|---|---:|---:|---:|---:|
| L2 updates | 2,930,693 | 4.924 ms | 1.912 ms | 56.389 ms |
| trade batches | 513,174 | 4.669 ms | 2.796 ms | 60.943 ms |
| BBO | 1,478,568 | 3.667 ms | 1.830 ms | 59.269 ms |
| mark | 62,148 | 2.131 ms | 1.241 ms | 24.011 ms |
| index | 111,120 | 2.117 ms | 1.246 ms | 28.919 ms |

The complete file had one adapterTs regression of about 0.969 seconds, but it
occurred in a funding message (message type 9). The combined model-relevant
book/trade stream (message types 0/1/2) had zero receipt-time regressions in
this sample.

These measurements do not establish a universal source-delay bound for all
days. They only show that this sampled historical recording has a coherent
receive clock for the streams the frozen liquidity feature uses.

## Separate free event-yield check

Before buying L2 days, event incidence can be estimated cheaply from Binance's
official BTCUSDT one-second archive.

For August 2026, the official monthly 1-second ZIP passed the published SHA-256 checksum, contained 2,678,400 rows with zero missing seconds, produced 30 raw -1% / 300s crossings and eight independent events after the fixed two-hour lockout.

The reproducible scanner was then run over the full common candidate window,
July 2023 through August 2026. All 38 monthly archives passed their published
checksums. Across 100,051,200 one-second rows there were zero gaps, 3,067 raw
-1% / 300s crossings and 428 accepted two-hour-lockout episodes. The accepted
proxy episodes were distributed as 50 in 2023 (July-December), 200 in 2024,
94 in 2025 and 84 through August 2026. Thirty-seven of 38 months contained at
least one accepted episode; the median was nine per month. The 428 episodes
occurred on 283 distinct UTC days.

This materially changes the feasibility assessment: the frozen 130-episode
minimum is achievable within the available historical era before L2/data-quality
exclusions. Event scarcity is no longer the primary blocker. The 428 proxy
episodes fell on 283 event days; adding only the preceding/following UTC files
needed by the fixed two-hour lockout and 120-minute label horizon expands the
exact-threshold lower-bound set to 330 instrument-days. At three required
CryptoStruct instruments per selected UTC day, that is 990 instrument-day
files before any wider acquisition screen is applied. This is a planning lower
bound, not a purchase instruction.

This remains only an acquisition-planning proxy because it uses Binance
one-second close, not the frozen equal-weight Binance/Bybit receipt-time
midpoint. It must never be used as the final E001-LIQ-OBS trigger ledger.

The reproducible scanner is scripts/scan_e001_binance_event_yield.py.

## Intended historical acquisition design

### 1. Estimate event incidence for free

Scan consecutive official Binance BTCUSDT one-second months over the candidate
historical range. Record raw threshold crossings, accepted events after the
fixed two-hour lockout, missing/gap seconds, and month/regime concentration.

This decides whether the 130-episode design is feasible and approximately how
much calendar history is needed. It does not select model features or evaluate
MFSM.

### 2. Freeze the paid-data acquisition rule before reading L2 outcomes

Do not buy or inspect deep historical book days one by one according to whether
a previous day looks favorable.

Before the paid acquisition wave, write and hash a deterministic candidate-day rule using price-only information. The rule must include enough margin around the final -1% / 5m threshold that a Binance-only screening approximation does not systematically omit events that would cross under the final Binance+Bybit midpoint. Candidate-day selection must retain every threshold-crossing UTC day and must not apply the two-hour episode lockout at the screening stage. The real two-hour lockout is applied only after the final two-venue trigger is rebuilt; using the wider screen's lockout could suppress a later true -1% event and omit its required data day.

The acquisition screen is now frozen in [e001_historical_screen_calibration.json](../artifacts/e001_historical_screen_calibration.json), before any new paid CryptoStruct L2 outcome/model inspection. Simply purchasing only days where Binance itself crosses exactly -1% could miss final composite events. The broader development quote grids showed a dangerous one-sided Binance-only error of 31.981 bps at a true composite shock, while a free equal-weight Binance-close / latest-Bybit-trade proxy reduced the development shock-screen error enough that a -0.60% free-reference threshold captured all 14 development days containing a quote-composite -1% condition. The free trade proxy covered 95.88% of the 1,506 quote-composite shock seconds; where it is unavailable, the frozen fallback retains a day when Binance alone is <= -0.50% over five minutes. The screen applies no two-hour lockout. It is only a data-acquisition filter and can never become the final research trigger.

The frozen screen is deliberately conservative: primary condition = any valid five-minute free-reference return <= -0.60%; missing-reference fallback = Binance-only return <= -0.50%. The final trigger remains the paid receipt-time Binance+Bybit spot midpoint crossing <= -1% with the fixed two-hour lockout. A separate audit of the first 92 sealed segments of the current forward capture produced 7,481 valid simultaneous spot seconds and 7,163 valid five-minute return comparisons, with at most 2.516 bps absolute Binance-versus-composite return difference. The continuous result is reassuring but too short to replace the broader development calibration.

### 3. Acquire only the market data required for frozen candidate days

Acquisition is staged to avoid paying for perpetual L2 before the exact spot event ledger exists. First buy only the two spot instruments for frozen screen days. Rebuild the exact receipt-time two-venue trigger and fixed two-hour lockout. Only then buy the Bybit perpetual file for finalized exact event windows. This keeps L2 selection independent of liquidity outcomes and materially reduces unnecessary paid files.

For each selected UTC event day, the preferred historical inputs are:

- Binance Spot BTCUSDT, CryptoStruct instrument 67838: independent spot constituent; catalog coverage from 2023-03-01;
- Bybit Spot BTCUSDT.spot, CryptoStruct instrument 2000: independent spot constituent; catalog coverage from 2023-07-18;
- Bybit BTCUSDT perpetual, CryptoStruct instrument 2449: full L2 + aggressor trades for liquidity state; catalog coverage from 2023-07-18, with a nine-day gap from 2024-02-29 through 2024-03-08.

The common advertised coverage window starts on 2023-07-18, excluding the
perpetual gap. The [2026-09-24 catalog receipt](../artifacts/e001_cryptostruct_catalog_coverage.json)
records the keyless `get_coverage` responses for all three instrument IDs.
The frozen July 2023-August 2026 screen retained 748 candidate UTC days and 775
spot seed/support days. The [frozen acquisition manifest](../artifacts/e001_historical_spot_acquisition_manifest.json)
flags 12 early days before Bybit spot coverage, where no two-venue event can be
certified. A subsequent [read-only price/availability quote](../artifacts/e001_historical_spot_price_quote.json)
found all 1,526 purchasable Binance/Bybit spot instrument-days available with
zero missing at a quoted total of EUR 1,526. No checkout or paid download was
created.

Acquire adjacent UTC files whenever the required 30-minute pre-trigger history,
two-hour lockout history, or 120-minute secondary label window crosses a day
boundary.

CryptoStruct currently advertises instrument-day pricing rather than requiring
a bulk subscription. Price and availability must be rechecked before purchase;
do not treat the present website price as a permanent contract.

### 4. Rebuild the real trigger after acquisition

The price-only Binance screening event is not the research event.

After the two spot source files are available, rebuild the frozen spot reference
from the latest causally available Binance and Bybit spot midquotes and apply:

- exact 300-second point-to-point return;
- <= -1% crossing;
- two-hour episode lockout;
- decision at t0 + 15s;
- 30-minute primary first-passage label;
- 120-minute secondary horizon.

Only this rebuilt ledger can enter the E001-LIQ-OBS dataset.

### 5. Keep the existing feature definition unchanged

The historical adapter must translate the source into the existing
decision_liquidity_state() contract. It must not create a new MFSM feature
family merely because another source has more fields.

Both B4 and MFSM keep the same eight shared features:

1. top bid depth / own 30-minute median;
2. top ask depth / own 30-minute median;
3. book imbalance;
4. spread in bps;
5. 30-second buy flow / historical visible depth;
6. 30-second sell flow / historical visible depth;
7. 30-second gross trade flow / historical visible depth;
8. 15-second persistent bid replenishment / historical bid depth.

MFSM adds only the two already frozen deterministic interactions:

- sell pressure / relative bid depth;
- sell pressure / (1 + relative persistent replenishment).

### 6. Keep the model gate closed

No real B4/MFSM fitting is enabled merely because historical data becomes
available.

The existing gate still requires:

- a frozen historical source/acquisition manifest;
- hash-verified source files;
- valid receipt ordering for model-relevant streams;
- reconstructable gap-free book state or explicit invalid epochs;
- complete feature/label windows;
- at least 130 eligible independent episodes;
- both classes in required fit/calibration partitions;
- the frozen chronological walk-forward design.

## Adapter implementation started

src/mfsm_e001/cryptostruct.py is the first source adapter.

Its intended role is deliberately narrow:

CryptoStruct snapshot/update/trade stream
-> existing reconstructed top-level state/trade-flow contract
-> existing decision_liquidity_state()
-> existing liquidity_model_features().

It rejects model-relevant receipt-time regressions rather than sorting
historical events, treats snapshots as book resets, checks event-id chains,
reconstructs absolute level updates, applies the contract multiplier to
quantity, and keeps the returned row diagnostic/model-ineligible.

A fixed 00:45 UTC engineering probe on 2026-09-17 replayed the free sample to
00:45:15 UTC and produced a ready feature vector with all eight frozen shared
features and exactly the two frozen MFSM additions. The adapter observed zero
book-chain gaps, zero trade-chain gaps and zero source-clock leads on that
probe. This result was re-run after enforcing a strict no-message-after-decision
cutoff. The timestamp was chosen only to exercise the measurement path; it was
not selected as a market event and no label or model score was computed.

This preserves the scientific definition while changing only the data adapter.

## What remains unsolved

Before CryptoStruct can become an evaluation source, still verify:

1. exact Binance Spot and Bybit Spot instrument ids and historical availability
   on the same selected days;
2. spot-book/BBO semantics needed for the two-venue midpoint;
3. multi-day overlap trimming and event-id deduplication at UTC boundaries;
4. chain-gap and receipt-order quality over all purchased days, not one sample;
5. source hashes and immutable acquisition manifest;
6. candidate-day screen after the multi-year free incidence scan;
7. complete cross-day prehistory/label handling;
8. sufficient independent episodes/classes for the frozen evaluation design.

Liquidation messages are not required by E001-LIQ-OBS-1. Their bankruptcy
price and ambiguous side semantics must not be promoted into execution
notional merely because CryptoStruct exposes the messages.

## Interpretation

The historical-data blocker has moved from:

"no credible reconstructable top-level history identified"

to:

"credible candidate identified and one free full-day perpetual sample passed
the initial structural/timing/depth audit."

That is meaningful progress, but not yet a completed research dataset or a
predictive result.
