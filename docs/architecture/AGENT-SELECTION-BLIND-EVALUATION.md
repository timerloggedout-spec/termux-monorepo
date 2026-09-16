# Blind Agent Selection & Evaluation

## Purpose

Agent selection should minimize identity, provider-brand, and reputation bias when those attributes are not relevant to the task. This document defines a **double-blind-style evaluation layer**, not a claim that GitHub or an LLM evaluation can achieve perfect statistical blindness.

## Core principle

Separate **treatment identity** from **evaluation identity**.

```text
REAL TREATMENT
(provider, model, prompt, manager, cohort, sequence)
        │
        │ deterministic opaque assignment ID
        ▼
BLIND TREATMENT
(candidate A/B/C…, sanitized context)
        │
        ▼
EXECUTION
        │
        ▼
EVIDENCE
(output + tests + logs + artifacts)
        │
        ▼
BLIND EVALUATION
(correctness / completeness / regression / task outcome)
        │
        ▼
UNBLIND
        │
        ▼
MONEYBALL / 3L0
```

## Two blindness layers

### Selection blinding

When scientifically appropriate, the manager receives opaque candidate IDs rather than provider/model names before treatment assignment. The assignment service retains the protected mapping.

### Evaluation blinding

Reviewers/evaluators receive outputs and objective evidence without provider/model identity whenever feasible. Prompts and task context must also be normalized so the evaluator cannot infer identity from unnecessary metadata.

Unblinding is performed only after the evaluation record is frozen, or earlier when safety, debugging, quota, or operational intervention requires it; such exceptions must be recorded.

## What must remain attributable

Blindness must never destroy provenance. Store protected mappings sufficient to reconstruct:

`experiment_id → treatment_id → provider/model → prompt → manager → cohort → sequencing → request → SHA/run → job/step → logs/artifacts → evaluator → outcome`.

The identity mapping is access-controlled/separately stored where the implementation supports it. Public reports may expose aggregate results without exposing unnecessary provider identity.

## Scientific safeguards

- Randomize treatment assignment where randomization is appropriate.
- Use stable cohorts and predeclare factors/levels when feasible.
- Prefer objective tests and reproducible scoring over subjective preference.
- Replicate promising results before promotion.
- Record missingness, failures, cooldowns, unavailable treatments, and evaluator uncertainty.
- Distinguish task correctness from latency, cost/quota, and availability.
- Use paired comparisons when the same task can be evaluated across treatments.
- Avoid leakage through provider-specific formatting, tool names, model signatures, or response metadata.
- Never hide safety-critical information from an evaluator who needs it.

## Bias checks

Blind evaluation is one control, not proof of unbiased selection. After unblinding, compare:

- blinded versus unblinded reviewer scores;
- evaluator agreement;
- outcome distributions by provider/model;
- prompt/cohort imbalance;
- selection and attrition effects;
- regression and replication rates.

If identity can be inferred reliably, record the trial as **partially blinded** rather than claiming double-blind status.

## Relationship to MoneyBall / 3L0

MoneyBall/3L0 consumes **evidence records**, not brand reputation. Identity can be revealed after evaluation so the system can learn which provider/model treatment generated the result. Historical reputation may be a feature only when explicitly justified as a factor under test.

## Relationship to BIUDL

Blind evaluation belongs in `VALIDATE`; its findings enter `LEARN` and modify the next `BROAD` baseline.

```text
BROAD → INTEGRATE → VALIDATE → DEVELOP → LEARN → BROAD
                         │
                         └─ blind/paired evaluation where appropriate
```

## Related sources

- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.mmd`
- `docs/ops/SCOUT-ROSTER.md`
- `docs/ops/SCOUT-MISSIONS.md`
- `.agents/skills/multivariate-doe/SKILL.md`
- `.agents/skills/evidence-led-monorepo-ops/SKILL.md`
- `.agents/skills/review-loop/SKILL.md`
