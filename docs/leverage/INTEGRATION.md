# L3VERAGE measurement integration contract

**Status:** implemented as a read-only comparison adapter over existing records.  
**Authority:** DoE family, ATES intake, 3L0/MoneyBall, and the canonical evidence envelope retain their existing ownership.

## Data flow

    Mechanism definition + preregistered design
                      |
                      v
             DoE family campaign record
             docs/ops/corpus/EXPERIMENT.schema.json
                      |
                      v
             ATES / MVT run observation
             docs/ops/MVT-ATES-SCORING-INTAKE.md
                      |
                      v
          canonical evidence + immutable refs
          docs/ops/EVIDENCE-ENVELOPE.schema.json
                      |
              +-------+--------+
              v                v
       3L0 actor scoring   MoneyBall PR/economics
              |                |
              +-------+--------+
                      v
           L3VERAGE comparison projection
           scripts/leverage/compare_experiment_records.py

L3VERAGE does not write to any upstream record, alter routing, or create a second telemetry ledger. The comparison command reads committed DoE experiment JSONL and emits a disposable JSON projection to stdout.

## Canonical contracts and exact mappings

| L3VERAGE need | Existing contract | Integration rule |
|---|---|---|
| Campaign, cohort, arm, baseline/candidate | docs/ops/corpus/EXPERIMENT.schema.json | One record per dispatched arm run; experiment_id, cohort, treatment.arm, baseline_sha, candidate_sha, suite remain canonical |
| Configured execution identity | treatment.instance.instance_key and scripts/doe/instance_key.py | Compare exact configured-instance keys; never aggregate by model name alone |
| Execution outcome and ATES trace | docs/ops/MVT-ATES-SCORING-INTAKE.md and docs/ops/ATES-ORCHESTRATOR-TRACE.schema.json | Consume ates_outcome, deterministic_score, judge_score, net_score, trace_id, task_fingerprint, and environment_fingerprint only when actually present |
| Usage and cost | EXPERIMENT usage{} plus metrics{}; MoneyBall 3l0.moneyball.v1 | Preserve measured/estimated/activity-only/not-established distinctions; never synthesize zeros or combine unlike units |
| Provenance | docs/ops/EVIDENCE-ENVELOPE.schema.json | Retain immutable refs and source SHA; do not copy payloads into the mechanism catalog |
| Actor/endpoint scoring | docs/ops/3L0-PLANE.md | 3L0 remains the actor/provider/configured-instance scoring plane |
| PR and economic scoring | docs/ops/HEX-MONEYBALL-INTEGRATION.md | MoneyBall remains separate; its run/attempt/provider-call/outcome/decision grains must not be flattened or conflated |

The DoE family rule is controlling: MVT and ATES are nested components of DoE for roll-up counting, while each surface retains its own record home. Cross-surface use is citation-only. L3VERAGE is not counted as an additional experiment or telemetry plane.

## Comparison adapter

Run from a repository checkout:

    python3 scripts/leverage/compare_experiment_records.py experiments/doe/<campaign>/records/<records>.jsonl \
      --experiment-id <experiment-id> \
      --cohort <cohort-id> \
      --control-arm <control-arm> \
      --treatment-arm <treatment-arm> \
      --control-instance-key <64-hex-instance-key> \
      --treatment-instance-key <64-hex-instance-key> \
      --outcome-key <numeric-metrics-key> \
      --outcome-direction higher \
      --cost-key <numeric-resource-metrics-key> \
      --cost-unit <unit> \
      --min-pairs <preregistered-count> \
      --guardrail <quality-metric>">=<minimum>

The adapter fails closed when either selected arm has no matching records for the explicit configured-instance key; a run is not terminal; a metric is missing/non-numeric; cost is negative; selected arms differ in suite, baseline SHA, candidate SHA, or matched repetition set; a repetition lacks matching non-empty task and environment fingerprints; repetitions are duplicated; or the preregistered minimum pair count is not met.

The adapter reports means, oriented outcome delta, incremental cost, guardrail results, and the ratio only when its denominator is positive and guardrails hold. A zero/negative denominator or failed guardrail yields a null ratio with a reason. The selected metric and unit are explicit command inputs; no hidden conversion or weighted composite is applied.

Its output explicitly says descriptive comparison only and promotion_authorized false. It never edits the mechanism catalog. A DoE owner and the existing proposal/promotion authorities decide whether any result supports validation or promotion.

## Scoring and privacy rules

- Quality and correctness remain hard constraints; speed and cost cannot compensate for a failed guardrail.
- judge_score is eligible only from an evaluator instance distinct from the builder instance, per ATES intake.
- Preserve provider/model, role, prompt/tool hashes, and instance_key only where the canonical record provides them.
- Missing values stay missing. activity_only and not_established usage values are not consumption.
- Do not export prompts, completions, tool payloads, secrets, or arbitrary log text.
- Keep 3L0 and MoneyBall records separate. L3VERAGE may compare cited outputs but cannot rewrite their scores.
