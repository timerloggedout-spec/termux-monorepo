# Automated Telemetry Audit Contract

**Status:** implementation contract for ATES and Help-Wanted outcome accounting.

## Non-negotiable rule

Audits are part of automated telemetry, not an occasional manual cleanup. Every eligible source workflow must produce either a validated evidence receipt or an explicit skip/partial receipt. Absence of a metric is never converted to zero, success, or inferred attribution.

## ATES observation outcomes

Every observer execution must end in one of these machine-readable outcomes:

- `emitted`: sanitized events and metrics were produced from observed evidence.
- `partial`: some source evidence was unavailable; available evidence is retained and missing fields remain null/absent.
- `skipped`: metadata collection intentionally did not produce metrics (for example, an unmapped workflow); the receipt records source run, attempt, SHA, workflow, reason, timestamp, and artifact outcome.
- `deferred`: rate limiting prevented collection; retry after the provider's reset window rather than interpreting the event as zero work.
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

## Automated tribute audit operation

The hourly Help-Wanted status refresh now invokes `scripts/ci/help_wanted_tribute_audit.py`. It performs a bounded, rotating read-only sample of upstream tribute PRs, checks PR state, changed-file evidence, solution-proof markers, and GitHub check runs, and writes:
- `docs/ops/generated/help-wanted-tribute-audit.json`;
- a `tribute_audit` projection into the generated status JSON and dashboard data.

The live batch is intentionally capped at 25 PRs per refresh to limit API pressure. The window rotates hourly, and the generated report retains the latest known audit per currently listed PR across refreshes. `audited_pr_count` is cumulative coverage, `audited_this_run_count` is the current batch, and `not_audited_count` is the remaining gap. Cached stages are last-observed evidence, not current-state guarantees. A deferred/failed/unknown refresh preserves the last known stage while recording `last_attempt_status`, `last_attempt_at`, and `last_attempt_evidence_gaps`; the status counts describe the latest attempt, not necessarily the stage's freshness. Changed-file and check-run responses are checked for truncation, and incomplete pages cannot establish a validated solution. Rate limits and missing/truncated check/file data are recorded as unknown/partial, not success. A merged PR is counted as accepted, never as realized effect.

Independent realized-effect receipts are ingested from `docs/ops/help-wanted-realization-evidence.jsonl`; see `docs/ops/HELP-WANTED-REALIZATION-EVIDENCE.md` for the schema and attestation rules. A valid record requires a separate verifier, explicit independence attestation, HTTPS effect and verification links, a timestamp, method, and evidence summary. The checker validates structure and identity separation; it does not treat the JSON assertion itself as proof.

## Operational limitations

Automated skip/partial receipts, cross-run incident notification deduplication, evidence-honest candidate ranking, feedback-first nudge suppression, and sampled upstream tribute auditing are now wired into the PR implementation. Full historical reconciliation of every claimed tribute and a fully populated, user-filterable canonical queue remain outstanding; neither should be described as complete until the historical ledger has been traversed and the public dashboard exposes the stage-separated counts.


## Receipt-count semantics

The generated status builder classifies each receipt as `actioned`, `skipped`, or `failed`. A skip is an observed no-op, not successful work. The public dashboard displays these operational counts separately from audited `validated_solution`, `accepted`, and `realized effect` stages. The latter two are not interchangeable: acceptance does not prove downstream realization.
