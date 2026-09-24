# Experiment 001 timing policy comparison: Delivery A

2026-09-24. This is a diagnostic comparison on hash-verified, sealed BTC input. It does not change the primary replay, feature, event, or label definition. No model was fitted and ETH was not read.

## Fixed-input result

| Capture | Grid seconds | Strict valid composite | Strict clock-invalid | Receipt-age quote opportunities | First envelope source ahead of receipt |
|---|---:|---:|---:|---:|---:|
| Original pre-repair smoke | 48 | 0 | 48 | 43 | 3,277.726 ms |
| First post-repair smoke | 63 | 58 | 0 | 58 | none |
| Interrupted run, first 26 sealed segments | 2,264 | 2,226 | 36 | 2,262 | 0.331859 ms |
| Recovery smoke | 63 | 0 | 63 | 58 | 2.218899 ms |
| New 15-second probe smoke | 18 | 0 | 18 | 13 | 9.874649 ms |

The 26-segment prefix ends shortly after the first recurring disagreement. Its 36 invalid seconds are **prefix-only**; this report does not assign a full-run invalidation count to the other 93 sealed segments or the unclean tail. No local `clock_step` record occurred in these five audited inputs. The probe smoke stored one successful Binance and one successful Bybit HTTP time probe; replay accepted both as HTTP-domain evidence. Its first negative WebSocket lag happened before either probe record became available.

The receipt-age column is a **Candidate B opportunity count**, computed from both initialized spot books and quote receipt age at most five seconds in the same local epoch. It does not certify source freshness. In particular, the original 3.3-second clock-error capture still shows 43 receipt-age opportunities, demonstrating that receipt age alone cannot make a period eligible. Thirty-second receipt-window flow and book-update membership diagnostics appear in the JSON audits. Their item totals repeat across overlapping grid windows; they are not unique trade counts, complete persistence values, or model features.

## Feature-level diagnostic comparison

The existing feature builder was extended with `--timing-candidate receipt_diagnostic`. The [feature comparison](e001_receipt_feature_comparison.json) verifies equal input manifests, sealed segment hashes, decision seconds, feature names, code hashes and each compressed output hash before comparing rows. Both variants keep the same book coverage and economic missingness rules. Receipt rows explicitly remain ineligible for model use.

| Input and selected decisions | Strict raw fields available | Receipt raw fields available | Key observation |
|---|---:|---:|---|
| Original clock error, one decision | 0 | 80 | Receipt features can be computed even during the known 3.3-second error; they are not qualified. |
| First post-repair smoke, one decision | 74 | 74 | Four persistence fields differ despite both being clock-valid; this is a measurement change. |
| Recovery smoke, one decision | 0 | 80 | Receipt-time diagnostic retains flow, depth, OI and persistence after strict global invalidation. |
| Interrupted prefix, one decision before failure | 94 | 94 | Six flow/persistence fields differ under the two window clocks. |
| Interrupted prefix, two decisions after failure | 0 each | 91 each | Receipt diagnostic remains ineligible; full-band bid depth and its pre-trigger denominator are still missing. |

The repeated fields in the two clock-valid decisions establish that a receipt-time policy cannot be presented as a harmless repair to the strict code. The sample selection was for timing and history coverage, not based on labels or returns. No event-level model result was calculated.

## Candidate assessment

| Candidate | What the current implementation establishes | Selection result |
|---|---|---|
| A: bounded source time | Pure interval, arrival, worst-case quote age, flow-window membership and dwell-bound helpers are implemented and tested. Capture replay can select causal HTTP probe evidence by domain and epoch. | **Unknown for WebSocket data.** None of the historical captures contain contemporaneous WebSocket-domain offset bounds. The new probe smoke has HTTP evidence only. No defensible source-time corrected composite or feature coverage can be certified. |
| B: receipt-time windows | Quote, flow and persistence diagnostics now use receipt windows without moving information before receipt. Synthetic tests vary receipt timing at a boundary, and fixed inputs have side-by-side feature rows. | **Measurement revision required.** Source-age/backlog exclusion remains unsupported and economics/coverage still leave required features missing. No primary switch is justified. |

The standalone public HTTP probe returned finite offset intervals for both venues, but those requests address `http_server_time`, not Bybit `ts`/`T` or Binance `E`/`T`. Applying the HTTP interval to those WebSocket fields would assume an unverified clock-domain bridge. A later probe also cannot certify an earlier grid decision. The only supported decision now is to keep the strict legacy primary outputs and record timing as unresolved.

## Reproduction and integrity

Run `uv run --locked --extra collect --extra test pytest -q` and `uv run --locked --extra collect python scripts/audit_e001_timing.py MANIFEST --output REPORT`, adding `--sealed-prefix --max-segments 26` for the interrupted run. The machine-readable [comparison manifest](e001_timing_policy_comparison.json) records the exact audit paths, SHA-256 values, and code hashes. Each [original](e001_timing_audit_original.json), [post-repair](e001_timing_audit_clock_fixed.json), [interrupted prefix](e001_timing_audit_recurring_prefix26.json), [recovery](e001_timing_audit_recovery.json), and [probe smoke](e001_timing_audit_probe_smoke.json) audit records the input manifest hash and every sealed segment hash. The [new standalone probe](e001_clock_probe_timing_delivery_a.json) is separate from captured probe evidence and cannot be used retrospectively.

## Next gate

Establish a supported clock relation for each required WebSocket timestamp domain with an expiry and drift rule, or version a receipt-time measurement with an independently justified delayed-data exclusion rule. Then run a short contemporaneous capture through complete quote, flow, book, pre-trigger history, and source-age gates. Until that contract is fixed, do not activate Candidate A or B, restart primary development acquisition, or build research episodes from these diagnostic counts. The original deadline remains 2026-09-25 00:19:49 UTC; no extension has been assumed.
