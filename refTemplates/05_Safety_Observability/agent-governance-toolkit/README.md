# Agent Governance Toolkit / Agent Control Specification Pattern

**Category:** `05_Safety_Observability`  
**Disposition:** concept-adaptation candidate · metadata-first

## Source

See `SOURCE.txt`. Pin an immutable source revision before reproducible experiments.

## Pattern to extract

- Express agent controls as a portable policy contract.
- Place policy checkpoints at input, model, state, tool and output boundaries.
- Produce auditable policy decisions and enforcement evidence.
- Compare embedded policy enforcement with managed enforcement as distinct deployment patterns.

## Repository adaptation

Map the policy contract onto existing repository-owned tool boundaries, event envelopes and safety checks. Start with one existing policy and implement a parallel, shadow-mode evaluator. Compare policy decisions before enabling enforcement.

## Measures

Policy coverage, decision parity, bypass resistance, false positives, false negatives, audit completeness, latency and maintenance effort.

## Ownership

CEEL owns concept extraction and experiment evidence. The designated licensing duty owner handles licensing disposition separately.
