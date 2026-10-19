# Automated Telemetry Audit Contract

**Status:** implementation contract for ATES and Help-Wanted outcome accounting.

## Non-negotiable rule

Audits are part of automated telemetry, not an occasional manual cleanup. Every eligible source workflow must produce either a validated evidence receipt or an explicit skip/partial receipt. Absence of a metric is never converted to zero, success, or inferred attribution.

## ATES observation outcomes

Every observer execution must end in one of these machine-readable outcomes:

- `emitted`: sanitized events and metrics were produced from observed evidence.
- `partial`: some source evidence was unavailable; available evidence is retained and missing fields remain null/absent.
- `skipped`: metadata collection could not safely produce metrics; a skip receipt records source run, attempt, SHA, workflow, reason, timestamp, and artifact outcome.
- `failed`: the observer itself failed unexpectedly; failure must remain visible as a failed check and incident.

Rate limits are `deferred`, not evidence of zero work. Retry policies must honor reset/retry metadata where available and avoid immediate retry storms. Missing optional task-boundary artifacts are an attribution-quality gap, not grounds to fabricate task identity.

## Incident deduplication

Use an incident key composed from:

`repository + observer workflow + source SHA + normalized failure fingerprint`

A source run ID and attempt are child observations, not the sole incident identity. Keep all affected runs linked beneath one incident. Emit a new notification only when the normalized incident is new, materially changes, or passes an explicit reminder cooldown. Never discard run-level evidence merely because the incident is deduplicated.

## Help-Wanted candidate and tribute audit

Discovery rank is not claim authorization. Every candidate should expose its score components, evidence gaps, observation timestamp, and candidate-only state. Unobserved repository health, language fit, and competing-PR absence earn no positive points.

The outcome ledger must maintain separate counts and canonical IDs for:

1. discovered candidate;
2. eligibility checked;
3. stake/claim opened;
4. implementation delta observed;
5. validation passed;
6. upstream accepted/merged;
7. realized effect independently evidenced.

A stake or public comment is never a completed solution. Acceptance, validation, and realization require linked evidence and explicit provenance. Classifiers may self-assess, but their own confidence is not independent ground truth.

## Required telemetry fields

Each audit record should carry schema version, canonical record/incident ID, source repository, workflow/run/attempt, source SHA, timestamp, actor or attribution method, evidence references/hashes, state transition, reason, confidence, missing-evidence list, and validator identity. Keep raw prompts, completions, credentials, private payloads, and secrets out of this evidence plane.

## Regression gates

- Missing optional evidence produces a partial/skipped receipt, not invented metrics.
- Rate-limit and unmapped-workflow paths are classified explicitly.
- Unknown ranking signals earn zero points.
- Repeated unchanged incident fingerprints do not generate repeated notifications.
- Every claimed success resolves to a canonical upstream PR and stage-specific evidence.
- Aggregate dashboard totals equal the deduplicated ledger at each lifecycle stage.
- Classifier calibration is evaluated against independent labels and reported with abstentions and false-positive/false-nudge rates.

## Operational limitation

The current changes add explicit ATES skip receipts and evidence-honest Help-Wanted ranking. They do not yet implement persistent cross-run incident deduplication or a full historical tribute reconciliation; those remain follow-on acceptance gates and must not be described as complete until code and tests land.
