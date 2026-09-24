# Canonical reference economy implementation plan

> **For agentic workers:** This is the completed implementation record for MFSM-RE-1. Preserve unrelated staged work.

**Goal:** Make the canonical MFSM contract restrictive and supply one complete, inspectable reference economy.

**Architecture:** Preserve the general framework and its existing state categories. Add a deterministic one-asset economy with three trading roles, conserved transaction cash/inventory, a fixed loan, constrained dealer execution, delayed buying, and explicit margin/default rules. Derive capacities and response conditions from the primitive state.

**Tech Stack:** Markdown mathematics; dependency-free Python; pytest.

**Spec:** The owner-approved six-point canonical revision in the conversation, implemented concretely in `MFSM_Reference_Economy.md`.

## Global constraints

- This is a theoretical reference member of the model family, with no fitted parameters or market validation.
- No new canonical state category; instantiate existing positions, funding, control history, and hybrid modes.
- Preserve all experimental protocols, data, running collectors, historical receipts, and unrelated staged changes.
- Separate mathematical completeness, causal support, predictive usefulness, and decision usefulness.
- Preserve uncertainty and explicit non-identification; no default probability from a deterministic path.

## Review focus

- Cash or inventory created by execution or reused across simultaneous capacities.
- Delayed signals accidentally using future observations or arriving before their declared tick.
- Default/margin failure silently forgiven or treated as successful recovery.
- Sale impact worsening headroom despite an apparent reduction in exposure.
- A reference-value decline mistaken for a reversible liquidity dislocation.

## Tasks

- [x] Write the full reference economy: domain, state, execution integrals, ordering, delay, margin target, failure rules, interventions, observation mechanism, proofs, and limits.
- [x] Write behavioral tests for accounting, finite budgets, delay, default absorption, the no-impact limit, headroom sensitivity, and permanent repricing. Run them before adding the implementation.
- [x] Implement `src/mfsm_reference/economy.py` and a synthetic demonstration runner.
- [x] Revise the canonical and companion specifications; link the reference and record the version in README/changelog.
- [x] Review equations against implementation, run the full suite, validate local links and the final diff.

Verification: `uv run --locked pytest -q` returned 194 passed; the reference
runner produced a no-buyer stationary discount, buyer recovery to the new
benchmark, and a strong-impact default under its synthetic parameters.

## Decisions

The reference uses a long holder and a cash-only dealer/buyer. Short squeezes, networks, strategic learning, default settlement, and stochastic calibration remain outside this member's declared domain. The buyer uses a fixed delayed valuation rule. A maintenance breach triggers liquidation toward a higher target margin, preventing an implicit assumption of instantaneous exact restoration. Insolvency and an expired margin deadline terminate the modeled path without inventing settlement liquidity.
