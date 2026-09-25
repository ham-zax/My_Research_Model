# Codex handoff — E001 historical BTC data path

Updated: 2026-09-25

Repository: /home/hamza/repo/My_Research_Model
Branch: feat/e001-milestone1
HEAD at handoff: f8ee1e32346a9c13e0c70d176a0b7c50cb964a3c
Remote relation at handoff: branch ahead of origin by 3 commits

Recent committed base:
- af37bd1 feat: wire E001 liquidity replay into dataset pipeline
- b60c1eb feat: freeze E001 liquidity observational protocol
- f8ee1e3 docs: classify liquidity capture as qualification seed

## Continuation result after this handoff

The later continuation resolved the candidate-screen conflict against the frozen
calibration receipt and observational protocol. `scan_e001_historical_candidates.py`
is authoritative: free two-venue return <= -0.60%, Binance-only fallback <=
-0.50% only when the free reference is unavailable, and no screening lockout.
The superseded -0.65%/-0.60% scanner was removed.

The already-completed July 2023-August 2026 frozen scan contains 748 candidate
UTC days and 775 paid-spot seed/support days, with 100,051,200 Binance seconds,
zero Binance gaps, and 92.841298% valid free-reference seconds. The acquisition
manifest is `artifacts/e001_historical_spot_acquisition_manifest.json`, SHA-256
`164d309e9ff3bcbfd4f45aa4a092e7d61bbf925de7127cf99ef007bfd284fef6`.
It records 12 early candidate/support days before Bybit spot catalog coverage.

A read-only CryptoStruct quote then found all 1,526 purchasable Binance/Bybit
spot instrument-days available, with zero missing, for EUR 1,526 total. The
quote receipt is `artifacts/e001_historical_spot_price_quote.json`, SHA-256
`1df9de3fb59d0da3abaefc324d2fbac35906f216a54ae7105b60b7c5f743c17a`.
No checkout, paid download, model fit, L2 outcome inspection, or ETH access was
performed. The next paid step requires explicit spending authorization; after
spot acquisition, rebuild the exact receipt-time two-venue trigger before any
perpetual L2 purchase or model fit.

## Mission

Continue the separate BTC liquidity-state study E001-LIQ-OBS-1 using historical data.

Do not change markets.
Do not reopen the original literal "absorption capacity" claim.
Do not treat Binance-only or free-trade screens as the final research trigger.
Do not open ETH; ETH remains sealed.
Do not fit a real B4/MFSM model until the frozen historical quality/sufficiency gates pass.

The scientific question remains:

After an independent BTC spot decline crosses -1% over exactly five minutes,
do prespecified interactions between observed sell pressure and contemporaneous
visible liquidity state improve 30-minute downside-before-recovery probability
beyond a flexible model receiving the identical primitive liquidity summaries?

## Frozen E001-LIQ-OBS feature contract

Shared B4/MFSM features:
1. top_bid_relative
2. top_ask_relative
3. imbalance
4. spread_bps
5. buy_relative_total_depth_30s
6. sell_relative_total_depth_30s
7. gross_trade_relative_total_depth_30s
8. persistent_bid_add_relative_15s

MFSM-only deterministic additions:
- sell_pressure_x_inverse_bid_depth
- sell_pressure_x_inverse_replenishment

Do not add another feature family because a historical vendor exposes more fields.

Final event/label contract remains:
- equal-weight Binance Spot + Bybit Spot receipt-time midpoint
- exact 300-second return
- crossing <= -1%
- two-hour lockout
- decision t0 + 15s
- primary 30-minute first-passage label:
  lower -1%, upper +0.75%
- secondary horizon 120 minutes

The acquisition screen is only for deciding which historical files to buy.
It must never become this final trigger.

## Why historical BTC is now viable

The earlier short live capture cannot solve sample size:
20,673 seconds with a 7,200-second lockout permits at most three independent
episodes, while the frozen evaluation gate requires at least 130 eligible
episodes.

Historical feasibility is now established.

Official Binance BTCUSDT 1-second archive scan:
- period: 2023-07 through 2026-08
- 38 consecutive months
- 100,051,200 one-second rows
- zero one-second gaps
- 3,067 raw -1% / 300s crossings
- 428 independent episodes after the fixed two-hour lockout
- 283 distinct accepted-event UTC days

By year:
- 2023 Jul-Dec: 50 accepted
- 2024: 200
- 2025: 94
- 2026 Jan-Aug: 84

This is acquisition-planning evidence only because it uses Binance one-second close.

Tracked scanner:
scripts/scan_e001_binance_event_yield.py

Derived report:
data/derived/e001_binance_event_yield_2023-07_to_2026-08.json
SHA-256 recorded in artifacts/e001_historical_data_candidate_audit.json.

## CryptoStruct source findings

CryptoStruct is the current historical full-depth source candidate.

Required instruments:
- Binance Spot BTCUSDT: CryptoStruct 67838, catalog since 2023-03
- Bybit Spot BTCUSDT.spot: CryptoStruct 2000, catalog since 2023-07
- Bybit BTCUSDT linear perpetual: CryptoStruct 2449, catalog since 2023-07

Common advertised window begins 2023-07.

Free sample actually audited:
- Bybit perpetual BTCUSDT
- instrument 2449
- nominal day 2026-09-17
- downloaded from /api/download/sample/2449/2026-09-17
- SHA-256:
  4b90e9d6d93d8792fff6a71689b7800157a8028e45782edb8df27e91f922c561

Sample structural audit:
- 5,095,711 events
- 2,930,693 L2 updates
- 1,708,571 individual trade fills
- 1,478,568 BBO events
- one snapshot
- zero parse errors
- zero book-chain gaps
- zero trade-chain gaps
- zero crossed-book states
- up to 100 reconstructed levels

One-second top-50 replay:
- 86,937 sampled seconds
- 86,937 / 86,937 had clean 50 bid + 50 ask levels
- zero suspect seconds
- zero crossed seconds

Timing audit on model-relevant streams:
- no exchangeTs > adapterTs records
- combined message types 0/1/2 had zero adapterTs regressions
- one whole-file adapterTs regression existed in funding message type 9 only

Approx receive-minus-exchange means:
- L2 update ~4.924 ms
- trade batch ~4.669 ms
- BBO ~3.667 ms

This is measurement-feasibility evidence, not model evidence.

## CryptoStruct adapter

New/staged file:
src/mfsm_e001/cryptostruct.py

Purpose:
CryptoStruct snapshot/update/trade stream
-> existing reconstructed state/trade contract
-> decision_liquidity_state()
-> liquidity_model_features()

Important invariants:
- preserve file/capture order; never sort historical events by timestamp
- reject model-relevant adapterTs regressions
- snapshots reset book state
- event-id chain gaps invalidate dependent state
- instrument ERROR state clears book observations and recent trade flow
- no message strictly after t0+15s may enter the decision feature
- keep output primary_eligible=false and model_ready=false
- no fitting

A fixed engineering probe at 2026-09-17 00:45:00 UTC produced:
- ready feature vector
- all 8 shared features
- exactly the 2 frozen MFSM extras
- zero book-chain gaps
- zero trade-chain gaps
- zero source-clock leads
- no label/model score

The probe was rerun after fixing a one-message lookahead bug and reconnect/error
history handling.

## Price-only acquisition-screen research

Do not buy every historical L2 day first.

Intended purchase sequence:
1. use free price/trade archives to select conservative candidate UTC days
2. buy CryptoStruct Binance Spot + Bybit Spot only for those candidate days
   plus deterministic boundary support
3. rebuild the exact receipt-time two-venue -1% trigger and two-hour lockout
4. only then buy Bybit perpetual 2449 L2 for finalized exact event windows
5. acquire any extra spot boundary day required for finalized 120-minute labels
6. do not fit until >=130 eligible episodes and all frozen quality gates pass

This is much cheaper than buying perpetual L2 for every screening day.

## Free second venue discovered

Bybit public BTCUSDT spot trade archives are available without credentials:
https://public.bybit.com/spot/BTCUSDT/

Daily files exist through the common window, e.g.
BTCUSDT_YYYY-MM-DD.csv.gz

Monthly files also exist:
BTCUSDT-YYYY-MM.csv.gz

Schema observed:
id,timestamp,price,volume,side,rpi

The repo already had a parser:
src/mfsm_e001/public_archive.py::read_bybit_spot_gzip

The existing development parser/data were used only to calibrate an acquisition
screen, not to fit a model.

## Acquisition-screen calibration evidence

Artifact currently present:
artifacts/e001_historical_screen_calibration.json

This artifact is important and should be treated as the latest intended
candidate-day calibration unless the current working-tree author shows a newer
authoritative decision.

Development calibration inputs:
- 38 first-of-month quote-grid days, 2023-07-01 through 2026-08-01
- 3,283,131 valid receipt-time quote-composite seconds
- 3,115,456 valid free Binance+Bybit trade-composite seconds
- free-reference coverage ~94.893%
- 2,972,750 valid five-minute comparison pairs

At quote-composite <= -1%:
- 1,506 shock seconds
- 1,444 had a valid free trade composite
- free-reference coverage ~95.883%

Dangerous one-sided error:
free trade composite minus receipt-time quote composite
- worst observed: +35.248 bps
- free return: -69.515 bps
- quote composite return: -104.762 bps
- date: 2024-05-01

Shock-second recall when free reference existed:
- -0.90% screen: 98.338%
- -0.85%: 99.377%
- -0.80%: 99.723%
- -0.75%: 99.931%
- -0.70%: 99.931%
- -0.65%: 100%
- -0.60%: 100%

Day-level development check:
- 14 days had actual quote-composite <= -1%
- Binance -0.60% selected 20 days, missed 0 final days
- free trade composite -0.65% selected 19 days, missed 0
- free trade composite -0.60% selected 21 days, missed 0

The calibration artifact currently freezes a MORE CONSERVATIVE rule:
- primary free two-venue trade-composite threshold: <= -0.60%
- missing-free-reference fallback: Binance-only <= -0.50%
- no screening lockout

Reason for no screening lockout:
a widened proxy event must never suppress a later true -1% research event.

This rule is acquisition-only and is not claimed to have guaranteed zero false
negatives outside the development data.

## Candidate-screen conflict recorded at handoff (resolved above)

At the handoff there were two candidate-day screen scripts in the working tree:

1. scripts/scan_e001_historical_candidates.py
   - appears to implement the calibration artifact's frozen conservative rule:
     free threshold -0.60%
     fallback -0.50%
     no screening lockout
   - also appears to add deterministic previous-day support when a signal occurs
     early enough that prior lockout/300s history can cross the UTC boundary

2. scripts/scan_e001_free_spot_candidate_days.py
   - created during the later exploration
   - currently uses:
     free threshold -0.65%
     fallback -0.60%
   - this is LESS conservative than the calibration artifact's frozen rule

Do not merge these thresholds mechanically.

The -0.65/-0.60 scanner was started over 2023-07..2026-08 and then explicitly
stopped as superseded after discovering the calibration artifact's frozen
-0.60/-0.50 rule. Its result should not be treated as authoritative.

Preferred next action:
inspect scripts/scan_e001_historical_candidates.py against
artifacts/e001_historical_screen_calibration.json and
experiments/e001_liquidity_observational_protocol.yaml.
If it faithfully implements the frozen -0.60/-0.50 acquisition rule and
boundary logic, use that script and retire/remove the superseded alternative
only if doing so will not overwrite another agent's active work.

## Git state recorded at handoff — historical snapshot

At handoff:
branch feat/e001-milestone1 is ahead of origin by 3 commits.

Current status:
A  artifacts/e001_historical_data_candidate_audit.json
M  artifacts/e001_implementation_status.md
AM docs/e001_cryptostruct_historical_data.md
MM docs/e001_next_implementation_plan.md
MM experiments/e001_liquidity_observational_protocol.yaml
A  scripts/scan_e001_binance_event_yield.py
A  src/mfsm_e001/cryptostruct.py
M  src/mfsm_e001/liquidity_live.py
M  tests/test_replay.py
?? artifacts/e001_historical_screen_calibration.json
?? scripts/scan_e001_free_spot_candidate_days.py
?? scripts/scan_e001_historical_candidates.py

There are staged AND unstaged edits.

Do not run git reset, restore, add -A, commit -a, or otherwise normalize the
index blindly. Reconcile staged/unstaged provenance first.

Notably:
- src/mfsm_e001/liquidity_live.py has staged receipt-order changes
- tests/test_replay.py has staged test additions
- artifacts/e001_historical_screen_calibration.json and
  scripts/scan_e001_historical_candidates.py appeared during concurrent work

Treat these as potentially another active agent's changes until provenance is
clear. Preserve them.

No commit for the historical-data wave has been made yet.

## Live BTC forward capture

Do not confuse the historical work with the independent forward qualification
capture.

Latest checked process:
PID 2504994
command:
.venv/bin/python3 -m mfsm_e001.collect --duration 20673 --max-mib 16384 --output data/raw/live_btc_development

Latest checked state at handoff:
- process alive
- elapsed ~2h38m

Run id:
9c4ee7b3301742aabf31377f5d2c894c

Role:
measurement/feed-quality qualification seed only.

Because of the 7,200-second lockout, the full fixed-duration run can contain at
most three independent episodes. It can never satisfy the 130-episode
evaluation gate.

Do not stop/restart or extend this collector based on outcomes unless the user
explicitly authorizes it.

## What is already documented

Primary historical decision record:
docs/e001_cryptostruct_historical_data.md

Protocol:
experiments/e001_liquidity_observational_protocol.yaml

Implementation status:
artifacts/e001_implementation_status.md

Next implementation plan:
docs/e001_next_implementation_plan.md

Machine-readable source/sample audit:
artifacts/e001_historical_data_candidate_audit.json

Screen calibration:
artifacts/e001_historical_screen_calibration.json

## What the handoff intended to do next (historical)

1. Reconcile the candidate-screen conflict.
   - compare scripts/scan_e001_historical_candidates.py with the frozen
     calibration artifact and protocol
   - keep the frozen conservative -0.60% free / -0.50% fallback rule
   - no screening lockout
   - preserve explicit missingness

2. Run the frozen candidate-day scanner over 2023-07 through 2026-08.
   Expected output should include:
   - immutable source hashes
   - free-reference coverage
   - candidate UTC days
   - deterministic prior-day support where required
   - no labels
   - no L2 outcomes
   - no model fitting

3. Inspect the resulting candidate-day count and acquisition cost only.
   Do not inspect future L2 outcomes or use model scores to change the screen.

4. Freeze/hash the resulting candidate-day acquisition manifest before any
   paid CryptoStruct acquisition.

5. Verify CryptoStruct paid availability for:
   - 67838 Binance Spot
   - 2000 Bybit Spot
   on every selected day/support day.

6. Acquire paid spot files first, not perpetual L2 first.

7. Implement/finish a historical spot adapter that reconstructs latest
   causally available receipt-time Binance+Bybit midquotes across UTC-day
   boundaries and produces the exact final trigger ledger.

8. Apply the frozen exact:
   - -1%/300s crossing
   - 2h lockout
   - t0+15s decision
   - label windows

9. Only after exact event times are fixed, acquire Bybit perpetual 2449 full
   L2/trades for the required event windows/days.

10. Feed those files through src/mfsm_e001/cryptostruct.py and the existing
    liquidity-state functions. Do not invent new features.

11. Add a historical readiness/sufficiency gate before removing any real-fit
    guard:
    - source hashes/manifest fixed
    - receipt ordering/gap epochs valid
    - full 30m history
    - full label maturity
    - >=130 independent eligible episodes
    - required classes/splits available

12. Only then enable the existing frozen chronological B4 versus MFSM
    evaluation.

## Model/evaluation gate that must remain closed

Frozen learner:
sklearn HistGradientBoostingClassifier
scikit-learn 1.8.0
sigmoid calibration with FrozenEstimator
seed 1001
early_stopping false
l2_regularization 0.1
preset model-size candidates only

Frozen walk-forward:
- initial fit 50 episodes
- calibration 20
- inner validation 20
- outer test 20
- at least two full outer test blocks
- minimum 130 eligible episodes
- both classes required in fit/calibration

Primary metric:
B4 calibrated Brier - MFSM calibrated Brier

Diagnostic reference comparator:
constant earlier fit-block positive rate

Do not use a favorable score to redefine features, events, thresholds,
candidate days, or acquisition duration.

## Claim boundaries

Even a future positive B4-vs-MFSM result would establish only:
the prespecified liquidity-state interactions add out-of-sample predictive
information on this BTC observational design.

It would NOT by itself establish:
- literal market absorption capacity
- a causal liquidation effect
- source-age certification beyond recorded receipt semantics
- original E001 confirmation
- trading profitability

Trading-edge claims require a separate frozen execution-cost protocol including
fees, spread/slippage, latency, fill assumptions, impact/capacity, signal rule,
entry/exit timing and fresh evaluation data.

## Validation already performed in this wave

Performed:
- CryptoStruct sample zstd integrity
- provider-reader structural/deep stats
- one-second top-50 reconstruction audit
- receipt/exchange lag audit
- model-stream receipt monotonicity audit
- Python compile checks for the new adapter/scanners
- direct frozen feature-vector probes
- git diff --check
- checksum-verified 38-month Binance incidence scan
- development price-reference calibration described above

No full test suite was intentionally run in this continuation.

There is currently a staged tests/test_replay.py modification from concurrent
work. Do not assume test execution is authorized merely because that change
exists.

## Immediate safe resume command pattern

First inspect:
git status --short --branch
git diff --cached
git diff

Then inspect:
artifacts/e001_historical_screen_calibration.json
scripts/scan_e001_historical_candidates.py
experiments/e001_liquidity_observational_protocol.yaml

Resolve only the candidate-screen contract mismatch.

Do not start paid downloads until the candidate-day rule/output is frozen and
hashed.

Do not touch ETH.
Do not fit a model yet.
