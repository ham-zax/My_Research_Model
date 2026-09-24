# E001 visible-capacity audit

Status: **INSUFFICIENT_INDEPENDENT_EPISODES**

## Result

The audit cannot measure the specified 25 bps capacity proxy on the downloaded data.

- All 22 predefined sharp-selloff crossings were used. No event or threshold was selected after viewing the outcome.
- The eight December 1 crossings occur only six to eight minutes after the daily file begins, so their required 30 minute pretrigger histories are unavailable.
- The 14 February 1 and March 1 crossings have pretrigger history, but none has complete 25 bps bid coverage at every required second.
- Across those 14 events, the minimum per second bid coverage within each 30 minute history ranges from 0.718 to 1.198 bps. The largest coverage seen in any of those histories is 5.278 bps, still far below 25 bps.
- Zero crossings and zero independent episodes therefore have a valid capacity measurement. The predeclared minimum for descriptive rank correlations is five independent episodes, so no correlation was computed.

This is a useful negative measurement result. The downloaded normalized Bybit book files are suitable for top of book reconstruction and trade flow, but they do not contain enough simultaneous visible depth to reconstruct the existing 25 bps capacity definition.

## What this does and does not show

The result shows a data and measurement mismatch. It does not show that the capacity idea fails, and it provides no evidence of predictive or trading edge. No model was fitted and no thresholds were tuned.

The current proxy can be tested only with archived BTCUSDT perpetual L2 that continuously covers at least 25 bps on the bid side, includes receipt timestamps and snapshots or sequence recovery, and spans at least 30 minutes before each predefined event. The existing Bybit trade files are usable for the 30 second aggressive sell-flow outcomes.

Changing the band to the available 1–5 bps would define a different proxy and requires a separately versioned protocol before looking at its result.

## Reproduce

```bash
uv run --locked python scripts/audit_e001_capacity.py \
  --output data/derived/e001_capacity_audit_REPRO
```

The full event rows and manifest are preserved in `data/derived/e001_capacity_audit_003/`. The tracked summary is `artifacts/e001_capacity_audit_results.json`.
