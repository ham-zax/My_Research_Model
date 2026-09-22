# MFSM Change Log

This file records material changes to the Market Feedback-State Model so definitions are not silently rewritten after empirical failure.

## 2026-09-22 - Companion foundations added

### Added

- `Mathematical_Foundations.md`
  - exact scalar delayed-feedback stability boundary;
  - crossing-direction derivation;
  - two-state lagged-inhibitor system;
  - distributed-memory kernel formulation;
  - gain-delay and relative-timescale interpretation;
  - Ornstein-Uhlenbeck critical-slowing-down derivation and limits;
  - capacity/deadline mechanics;
  - general stochastic MFSM template;
  - network/spectral formulation;
  - threshold and hybrid-system representation;
  - exact Physarum adaptive-network equations;
  - mathematical workflow and rejected inferences.

- `Empirical_Finance_Foundations.md`
  - finance-native mechanism map;
  - primary/official source list;
  - measurement map for MFSM variables;
  - prespecified test hypotheses;
  - empirical design and validation standards.

- `Research_Protocol.md`
  - mandatory application and extension workflow;
  - evidence labels;
  - falsification requirements;
  - out-of-sample testing requirements;
  - stop conditions for further theorizing;
  - future-LLM output schema.

- `README.md`
  - repository map and usage guidance.

### Canonical model updates

`Market_Feedback_State_Model_Canonical.md` now explicitly delegates:

- exact mathematics to `Mathematical_Foundations.md`;
- finance-side evidence and measurement to `Empirical_Finance_Foundations.md`;
- extension and validation discipline to `Research_Protocol.md`.

### Definitions preserved

The following distinctions remain canonical:

- Trend Strength (T) != Trend Sustainability (U) != Failure Fragility (F);
- continuation fuel (R^+) != headroom (H) != opposing absorptive capacity (R^-);
- fixed delay != distributed memory;
- trend termination by fuel exhaustion != delayed counterflow != gain saturation != threshold unwind;
- correlation != propagation topology;
- natural analogy != financial evidence;
- state diagnosis != validated predictive edge.

### Epistemic status

No change: MFSM remains a research framework, not a validated trading system or universal fragility score.
