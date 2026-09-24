# E001 near-touch capacity experiment

Run date: 2026-09-24 UTC. Status: **INSUFFICIENT_INDEPENDENT_EPISODES**.

This is a separately versioned observational experiment. It does not alter or rescue the original 25 bps E001 capacity proxy.

## What was fixed before outcomes

The [discovery protocol](../experiments/e001_shallow_capacity_discovery_protocol.yaml) fixed 42 first-of-month days from April 2023 through September 2026, the original −1%/five-minute spot trigger, receipt-time two-venue midquote, two-hour lockout, and a proposed 0.5 bps near-touch bid band. Discovery read spot quotes only and calculated no labels, L2 capacity, or forward trade outcomes.

Discovery found 90 crossings and 20 nominal episodes. The existing conservative missing-history audit qualified 12 independent episodes across nine dates. Their exact event-source hash was then frozen in the [capacity protocol](../experiments/e001_shallow_capacity_protocol.yaml) before any new L2 or trade outcome was read. The protocol also fixed the 15-second persistent-addition window, one-second dwell, 30-minute pretrigger depth scale, 30-second outcome, 25 bps midpoint breach, and minimum of five valid independent episodes for descriptive rank correlations.

The 0.5 bps band was chosen from coverage diagnostics only. The earlier 25 bps run had stopped before outcomes and found at least 0.718 bps of book span in its later event histories. No shallow result selected the band.

## Result

Only **5 of 90 crossings** had a complete near-touch capacity measurement. Only **2 of 12 history-qualified independent episodes** were valid, below the fixed minimum of five. No rank correlation was computed and no model was fitted.

Exclusions were:

- 59 crossings with at least one zero-depth second inside the 0.5 bps midpoint band during the 30-minute scale history. This occurs when the bid is farther than 0.5 bps below the midpoint, including spreads wider than one basis point.
- 17 crossings with invalid or stale pretrigger book state.
- 9 crossings with incomplete 15-second replenishment history.

Both valid independent events were right-censored no-breach observations:

| Trigger UTC | Capacity proxy | Observed sell flow, next 30s | Sell/capacity | 30s midpoint return |
|---|---:|---:|---:|---:|
| 2023-09-01 17:27:29 | 72,846.58 USDT | 10,773,495.37 USDT | 147.89× | +16.84 bps |
| 2024-03-01 21:03:16 | 1,330,087.50 USDT | 2,116,321.14 USDT | 1.59× | +4.40 bps |

Because neither midpoint fell 25 bps, the sell-flow values are lower bounds on observed gross sell flow without a breach. Simultaneous buy flow, hidden liquidity, cancellations, cross-venue activity, and trade aggregation prevent interpreting these ratios as literal causal capacity.

## Conclusion

The 0.5 bps midpoint-band definition is too fragile for this dataset. It is empty during ordinary spread widening and leaves too few independent measurements. The two surviving rows also show that gross aggressive sell volume can greatly exceed the displayed proxy while price rises, so the proxy should not be described as a direct absorption limit.

Do not try another band on these same outcomes. A future version should replace the capacity claim with an explicitly observable liquidity-state feature, such as fixed top-level depth and replenishment normalized by its own historical scale, and evaluate it only on fresh dates or a prespecified continuous archive.

## Reproduce

```bash
uv run --locked python scripts/discover_e001_shallow_capacity_events.py \
  --download --workers 2 --output data/derived/e001_shallow_event_discovery_REPRO

uv run --locked python scripts/finalize_e001_shallow_event_source.py \
  --discovery data/derived/e001_shallow_event_discovery_REPRO/result.json \
  --output data/derived/e001_shallow_event_source_REPRO

# Update a copied protocol with the reproduced event-source hash before this step.
uv run --locked python scripts/audit_e001_capacity.py \
  --protocol experiments/e001_shallow_capacity_protocol.yaml \
  --workers 3 --output data/derived/e001_shallow_capacity_audit_REPRO
```

The complete 90-event result, all 16 day-level source hash pairs, report, and manifest are preserved in `data/derived/e001_shallow_capacity_audit_001/`. The concise tracked receipt is [e001_shallow_capacity_result.json](../artifacts/e001_shallow_capacity_result.json).
