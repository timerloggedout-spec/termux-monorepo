# L3V-PILOT-001 — Provenance-aware context reuse

**Mechanism:** L3V-CONTEXT-REUSE  
**Status:** designed candidate; not admitted to the DoE family; no runs observed.  
**Decision owner:** DoE campaign owner + L3VERAGE mechanism owner.  
**Risk class:** low-risk, reversible, observational.

## Question and falsifiable hypothesis

For a frozen cohort of repository-maintenance tasks that repeatedly require the same project context, does retrieving scoped, freshness-checked, provenance-linked context reduce context reconstruction cost without increasing stale-context defects or reducing task correctness?

Treatment hypothesis: context reuse reduces median context-assembly wall time and measured provider cost while preserving correctness, integration, and regression outcomes.

This is a candidate design, not a result. No baseline, treatment, sample, cost, or outcome has been measured by this document.

## Arms and cohort

- **Control:** the existing task workflow, with no additional L3VERAGE context-reuse intervention.
- **Treatment:** the same task workflow, preceded by retrieval of a frozen, scoped context bundle containing source refs, source SHAs, freshness timestamps, and explicit exclusions.
- **Cohort:** 12 matched task pairs from one predeclared repository-maintenance task class. The DoE owner must freeze the task IDs, complexity band, eligibility rules, and task fingerprints before admission.
- **Assignment:** randomize arm order within each pair. Each pair shares one stable metrics.repetition value and one task_fingerprint.
- **Environment:** pin one environment and record the same environment_fingerprint for both arms of a pair.
- **Configured instances:** record the full treatment.instance stamp and instance_key per arm. Never pool distinct configured instances.

The 12-pair cap is a bounded operational pilot, not a claim of statistical power. Any inferential or generalization claim requires a preregistered power/uncertainty plan from the DoE owner.

## Measures

| Dimension | Metric | Rule |
|---|---|---|
| Primary outcome | independently scored task correctness/completeness, 0–1 | Frozen rubric and independent evaluator; no builder self-score |
| Primary resource | measured provider cost in USD | Use only measured call-level cost aggregated to the arm-run; if absent, cost ratio is not computable |
| Secondary resources | input/output tokens, wall time, human minutes, retries | Report separately with source and units; do not combine unlike units |
| Quality guardrails | deterministic validation, integration, regression, provenance/freshness defects | Any hard-guardrail breach blocks a positive leverage interpretation |
| Context safety | stale-source use, excluded-data exposure, secret exposure | Zero tolerance; stop and preserve the incident evidence |

The exact metric keys, rubric version, minimum correctness threshold, and cost source must be agreed and frozen in the DoE design record before dispatch. No absent metric is imputed.

## Stop and rollback

Stop immediately for secret or excluded-data exposure, stale context that changes a decision, a deterministic regression, or a permission-boundary violation. The intervention is removed by returning to the existing workflow; it does not alter provider routing, production defaults, credentials, or shared system prompts.

## Canonical records and admission

Before any run, the DoE owner must create the campaign design record and admit the campaign under docs/ops/DOE-FAMILY.md. Every dispatched arm run then emits one record conforming to docs/ops/corpus/EXPERIMENT.schema.json and the intake in docs/ops/MVT-ATES-SCORING-INTAKE.md.

Required fields include experiment/cohort/arm identity, baseline and candidate SHAs, suite, configured-instance stamp, terminal status, provenance, confidence, and evidence refs. metrics.repetition, task_fingerprint, environment_fingerprint, ATES fields, and explicitly measured resource metrics support the matched comparison adapter.

The comparison command is read-only:

    python3 scripts/leverage/compare_experiment_records.py <canonical-records.jsonl> \
      --experiment-id <id> --cohort <cohort> \
      --control-arm control --treatment-arm treatment \
      --control-instance-key <control-instance-key> \
      --treatment-instance-key <treatment-instance-key> \
      --outcome-key <frozen-outcome-metric> --outcome-direction higher \
      --cost-key <measured-cost-metric> --cost-unit USD --cost-status measured \
      --min-pairs 12 --guardrail 'quality_floor>=0.95'

Placeholders must be replaced by actual design values; this example is not executable as written. A ratio is not produced when incremental cost is zero/negative, any guardrail fails, or evidence is incomplete.

## Admission checklist

- [ ] Freeze 12 eligible task IDs and pair fingerprints
- [ ] Freeze task rubric, outcome metric key, evaluator identity, and quality floor
- [ ] Freeze measured cost source and units
- [ ] Freeze baseline/candidate refs, suite, environment fingerprint, and configured instances
- [ ] Record randomization and stop/rollback rules in the DoE design
- [ ] Obtain DoE owner admission; commit the design record
- [ ] Execute only after the design is admitted
- [ ] Commit one canonical experiment record per dispatched arm run
- [ ] Independently verify the comparison and evidence before any mechanism lifecycle change

Until all admission fields are supplied and the campaign is admitted, the pilot remains designed, not admitted, experimenting, or validated.
