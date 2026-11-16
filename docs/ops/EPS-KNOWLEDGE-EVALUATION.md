# EPS Knowledge Evaluation

## Goal

Measure whether telemetry improves repository knowledge work before investing heavily in custom visualization.

## Baselines

1. GitHub/Git-only source inspection.
2. Existing ledger/evidence artifacts.
3. EPS normalized events.
4. EPS + ML/Hex/Grafana derived views.
5. EPS + visualization (secondary experiment).

## Tasks

Use reproducible repository questions:

- What happened to a specific PR and why?
- Which agent/provider/action produced an observed effect?
- Can the event be traced to an exact SHA/run/attempt?
- Where did retries, stalls, conflicts, or provider-state interruptions occur?
- Is a metric complete, partial, stale, or unverified?
- Which observations can be safely joined without multiplying denominators?
- Can an anomaly discovered visually be recovered from source evidence?

## Measures

Do not collapse these into a single opaque score.

- evidence retrieval accuracy;
- provenance reconstruction accuracy;
- time-to-answer;
- missing-evidence detection;
- false attribution rate;
- stale-data detection;
- duplicate/replay resistance;
- context consumed;
- human intervention;
- downstream reducer agreement.

An optional experimental **Knowledge Yield** can be reported as useful, evidence-backed discoveries per unit of analyst time/context. It is a research metric, not a governance score.

## Acceptance

EPS is useful when it measurably reduces evidence-retrieval work without increasing false attribution or hiding incomplete coverage.

A visualization experiment only advances when the same evidence tasks remain reproducible without the visualization.
