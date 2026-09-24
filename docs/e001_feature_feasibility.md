# E001 selected BTC feature feasibility

Updated 2026-09-24. This audit covers **six diagnostic decision seconds in four fixed captures**, not every second of the continuous acquisition and not six eligible research episodes. The source counts and hashes are in `data/derived/e001_readiness_003/result.json` and its manifest. The 26-segment development prefix excludes later segments and its unclean tail.

| Field or family | Economic meaning and units | Present source and measured status | B4/MFSM use |
|---|---|---|---|
| Spot midpoint | Equal-weight Binance/Bybit BTC spot midquote, USDT/BTC | Receipt-grid values can be constructed when both quotes are fresh; absolute source-age certification is absent | Event and label reference, not a neutral depth input |
| Full 25-bps bid/ask depth | Visible Bybit perpetual liquidity, USDT | `orderbook.1000.BTCUSDT`; each side needs known full-band coverage; depth denominator missing at all 6 selected decisions | Relative shared depth and capacity need a complete pre-trigger median |
| Persistent bid additions | Observed additions surviving one-second dwell, USDT/s | Aggregate L2 with coverage, initialization and gap rules; some short windows have measured values, not a complete primary panel | Shared replenishment/capacity input when valid |
| Aggressive sell flow | Taker sell trade value, USDT over 30 seconds | Public Bybit trade stream; may overlap liquidation activity | Shared normalized flow; MFSM sell ratio is explicitly contaminated |
| OI and pre-trigger median | Open interest, BTC | Bybit ticker field with per-field age; complete 1,800-second OI scale at 3 of 6 selected decisions | Shared relative OI features when valid |
| Liquidation size | Reported position liquidation size, BTC | Bybit all-liquidation messages; measured base size can be zero during a complete observed interval | Diagnostic base-quantity feature, distinct from missing quote notional |
| Liquidation executed value | Actual forced execution notional, USDT | Public liquidation price is bankruptcy price; no independently supported execution valuation in the selected source | Required liquidation-pressure interaction unavailable at all 6 decisions |
| Cancellations and executions | Separate removed resting liquidity by cause, USDT/s | Aggregate L2 reduction cannot identify cause | Unavailable diagnostic columns; never impute zero |

The fixed runner reports **6/6 missing pre-trigger depth scales**, **3/6 missing OI scales**, **6/6 missing liquidation-pressure ratios**, and **6/6 incomplete full common panels**. These counts are measured at selected diagnostic decisions; they do not establish a population rate. The earlier 119-segment and post-warm-up audits in the [live feature contract](e001_live_features.md) show why initialization, clock validity and full-band depth coverage must be tracked independently.

The current real comparison has **no frozen supported feature list**. A narrower observable comparison would remove or redefine liquidation-pressure and other unsupported interactions, give B4 and MFSM the same neutral shared inputs, and narrow the claim. That is a material scientific contract change to decide before looking at model scores. The synthetic model fixture uses invented `depth_relative` and `interaction` columns solely to test the evaluator.
