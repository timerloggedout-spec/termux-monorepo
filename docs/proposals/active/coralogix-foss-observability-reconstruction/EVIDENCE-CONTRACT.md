# Canonical Observability Evidence Contract

## Envelope

Required: schema_version, event_id, event_type, occurred_at, producer, repository, ref, commit_sha, evidence_status.

Workflow correlation: workflow_run_id, run_attempt, job_id, task_id, lane, ssot_path, environment_fingerprint.

Experiment/request correlation when applicable: experiment_id, variant_id, assignment_source, assignment_version, request_id, trace_id, provider_id, model_id, endpoint_id.

Outcome/usage fields when observed: outcome, validation_status, latency_ms, input_tokens, output_tokens, retry_count, cost_observed, artifact_digest.

## Event types

workflow.lifecycle, task.lifecycle, agent.invocation, tool.invocation, model.request, model.response, evaluation.result, profile.artifact, action.effect, promotion.decision.

## Evidence semantics

- Preserve producer-reported state and timestamp.
- Distinguish observed, documented, inferred, and independently reproduced evidence.
- Represent unavailable fields as null with a reason/status.
- Preserve source SHA, schema version, provider/version, and artifact digest.
- Retries create attempt observations and retain parent correlation.
- Corrections append a new record and preserve the prior event.

## Privacy defaults

Exclude credentials, authorization headers, raw prompts/completions, private context, raw request/response bodies, and unredacted errors. Use explicit allowlists for additional fields. Test redaction with synthetic secret fixtures.

## Metric cardinality

Use bounded labels such as event type, provider family, outcome class, and lane. Keep request ID, trace ID, commit SHA, workflow run ID, task ID, and experiment ID in trace/event records and indexed attributes.

## Compatibility

Adapters declare supported schema versions and preserve canonical event digest. Provider-specific fields use a namespaced object. Schema changes require fixtures and a compatibility note.
