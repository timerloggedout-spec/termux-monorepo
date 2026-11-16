# PERFORMANCE-LEDGER (MSM-002 design)

## Authority

Reuse `docs/schemas/model-success-matrix.yaml` — do not invent parallel dimensions.

## Append-only sample (bounded)

```yaml
sample_id: <hash>
observed_at: ISO-8601
head_sha: <when PR-scoped>
role: triage|review|invoke|job:<id>
model_id: <string>
mode: series|parallel|concurrent
dimensions:
  correctness_gate_pass: bool|null
  substantive_review_resolution: bool|null
  duplicate_noise_avoidance: bool|null
  time_to_safe_feedback: number|null   # ms or rank
  cooldown_queue_efficiency: number|null
  resource_cost: number|null           # free-tier units
  coordinated_async_completion: bool|null
provenance:
  capability: string
  evidence_source: string
  decision_schema_version: string
confidence: number  # 0.0 if n==0; ≤0.2 prior-only
```

**Never store** raw issue, PR, or review bodies.

## Aggregation

- Per (role, model_id): n, elo, role_suitability, last_sha, confidence
- Feed MoneyBall / lane short-circuit as **decision support**
- Active weight table updates only under promotion rule (two observe cycles + #192-class ledger + dual-gate PR)

## Confidence rules (existing)

| Condition | Confidence |
|-----------|------------|
| no_samples | 0.0 |
| historic_3l0_prior_only | 0.2 |
| insufficient_samples | report low; do not promote specialist |
