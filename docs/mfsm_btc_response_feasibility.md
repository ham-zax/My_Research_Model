# MFSM BTC observable-response feasibility result

Version: `MFSM-BTC-RESPONSE-1-feasibility-result-1`
Date: 2026-09-27
Status: **DEVELOPMENT_FEASIBLE_NOT_VALIDATION_READY**

Protocol revision `1.1` clarified the last eligible pre-trigger bin and the
audit's failed-gate wording before any response-feature extraction. The corrected
audit still finds 32 complete-input dates and 20 accepted candidate events;
the field/calendar gate result is unchanged.

Frozen development-feasibility protocol:
`experiments/mfsm_btc_response_001_protocol.json`

Tracked receipt:
`artifacts/mfsm_btc_response_feasibility_result.json`

## Why this experiment exists

The synthetic observability work showed that public price history can narrow some response ambiguity, but it cannot generally recover hidden debt/headroom, and anonymous total volume added no discrimination in the frozen example.

The empirical continuation therefore does **not** try to estimate the hidden MFSM state. It asks a narrower question: whether the market's *observable recent response behavior* contains incremental information about how the next large BTC shock develops.

The new development protocol prespecifies two descriptive, public response summaries computed strictly before the trigger:

- `pretrigger_sell_impact_beta_5s`: the observed five-second midpoint response associated with normalized net aggressive sell pressure;
- `pretrigger_bid_replenishment_beta_5s`: the observed persistent bid-addition response following the same normalized sell pressure.

They are observational response coefficients, not causal structural parameters.
Both use five-second pressure bins anchored at trigger minus 30 minutes. Pressure
trades belong to `(bin_start, bin_end]` by local receipt time. Replenishment
uses `(bin_end, bin_end + 5s]`, including a book update at its endpoint, so an
eligible bin must satisfy `bin_end + 5s < trigger`. The pressure bin ending at
`trigger - 5s` is excluded; the last eligible one ends at `trigger - 10s`, and
its replenishment ends at `trigger - 5s`. This is a specification rule; this
audit did not extract either feature.

## Read-only feasibility audit

The audit inspected only local file presence, gzip CSV headers, and the already-existing **spot-only** candidate-event ledger. It deliberately did not replay the perpetual L2 histories.

Measured local coverage:

| Quantity | Result |
|---|---:|
| Tardis first-of-month sample directories | 42 |
| Dates with both spot quote feeds + Bybit perp L2 + Bybit perp trades | **32** |
| Required-file header failures | **0** |
| Complete-input span | 2023-05-01 to 2026-09-01 |
| Spot crossings on complete-input dates | **90** |
| Two-hour-lockout accepted candidate events | **20** |
| UTC weeks containing accepted candidates | **16** |

Thus the fields required to construct both proposed response measurements already exist locally on a nontrivial development sample.

These are **not** 20 response-feature-eligible episodes yet. That would require replaying each event's L2/trade history and checking continuity, resets, valid depth, and the minimum number of response bins. This milestone intentionally stops before that step.

## What was not done

This audit did not:

- compute either response coefficient;
- inspect new event labels;
- fit or score a model;
- compute P&L;
- replay L2 outcomes;
- buy or download paid data;
- access ETH.

The existing first-of-month sample has also been used in earlier development work, so it cannot serve as fresh confirmation even if the new features are computable.

## Data-route decision

The cheapest current route is to use the existing Tardis files only for **outcome-blind feature engineering and feasibility**.

A second possible route is Binance historical futures L2. Binance's official documentation describes tick-by-tick `T_DEPTH` and BTCUSDT approximately one-second/20-level `S_DEPTH`, but says access requires a Futures account and a whitelisted API key; `T_DEPTH` may contain gaps and `S_DEPTH` has some missing data. This route is therefore treated as **access-gated**, not assumed free, and was not used here.

CryptoStruct remains a paid route and is not authorized.

The public live collector already supports the needed book/trade messages, but its previous acquisition window expired. Any prospective confirmation period must be fixed in advance before a new launch.

## Decision

The observable-response direction survives its first empirical gate:

**the required measurements are field-feasible with data already present, so no purchase is needed to implement and debug them.**

The next step is now narrower and concrete:

1. replay only the development-only candidate histories;
2. compute the two pretrigger response coefficients without reading labels;
3. report availability, exclusions, and feature distributions;
4. freeze neutral same-information comparator summaries;
5. freeze a genuinely fresh evaluation calendar;
6. only then enable model scoring.

A failure at steps 1–3 should change or reject the measurement definition before any predictive result exists. A successful development extraction still does not establish MFSM prediction or trading edge.

## Integrity

- Protocol SHA-256: `79d07c191eac9a506815ecaf641927f482f3495afff540987cc2946d306f0a5b`
- Audit runner SHA-256: `0d1dc56aa6eefd27c9c342ed3d8187cc2c6eb3756fe483909b44cbf30c23b791`
- Full derived result SHA-256: `c4fd72139d509a4b63d7d8ae3c5e8d644caea705ece16ef9ed5a5e93a7cf71f4`
