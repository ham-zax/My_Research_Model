# E001 BTC capacity diagnostic: prespecified secondary comparison

Date: 2026-09-23. Status: design only; no real BTC book or outcome rows have been inspected. This diagnostic cannot change the primary E001 endpoint, MFSM/B4 feature definitions, model gate, or ETH confirmation rule.

## Three capacity inputs

For each otherwise eligible BTC episode and each audited venue, compute these values at the same decision time from the same complete L2 history. Use the local mid, the 25 bps bid band, the 15-second lookback `(t_d - 15s, t_d]`, the 30-second capacity horizon, and the existing one-percent pre-trigger depth floor.

1. **Depth alone:** `D_exec(t_d)`, the immediately executable bid notional in band.
2. **Published proxy:** `max(D_exec(t_d) + 30 * q_persist(t_d), floor)`, where `q_persist` is exactly the cohort-and-one-second-dwell estimator in Experiment 001 Section 8.2.
3. **Net-displayed alternative:** `max(D_exec(t_d) + 30 * q_net(t_d), floor)`, with

   `q_net(t_d) = max(0, sum_{p in B(t_d)} p * (size_p(t_d) - size_p(t_d-15s))) / 15`.

   `B(t_d)` is the fixed set of bid prices within 25 bps below the local mid at `t_d`; missing levels have size zero. Reconstruct `size_p` with the audited snapshot/delta rules. This nets repeated additions and removals at each price. A removal may be a cancellation or execution; aggregate L2 cannot tell which. The alternative therefore measures **net displayed growth**, not true cancellation or future executable capacity.

## Eligibility and scoring

Use only BTC episodes with a valid primary 30-minute label, complete causal input history for both endpoints, a valid book without gap or reset throughout the 15-second interval, positive pre-trigger 30-minute depth median, and all three values present for the same venue. Missingness excludes the episode from this paired diagnostic only and is counted by reason. The full Experiment 001 primary sample remains governed by its own rule.

Fit three otherwise identical BTC-only, chronologically trained calibrated models on the same eligible episodes and neutral controls; expose only the respective capacity input to each diagnostic arm. Keep folds, tuning budget, missingness handling, calibration, and scoring rows identical. Score the same binary `Y_30m` with paired out-of-sample Brier differences: published-minus-depth and net-minus-depth, where a positive value means depth alone had lower loss. Report means and UTC-week bootstrap intervals, coverage and exclusion counts. Do not choose a winner to alter the confirmatory model; any replacement requires a new versioned experiment specification and another untouched test.

This diagnostic tests whether recent displayed growth adds information beyond current depth. It cannot show that the same quote capital remains available against future sell flow. The synthetic churn case in `tests/test_features.py` demonstrates the published proxy's potential overstatement without asserting a measured market bias.
