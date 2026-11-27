# Evidence Contract — Existing Schema Composition

## Decision

Use the repository's existing evidence schemas as a composed contract. This proposal introduces no parallel canonical event schema.

## Existing owners

| Contract | Canonical path | Responsibility |
|---|---|---|
| Agent execution event | docs/research/AGENT-EVIDENCE.schema.json | Agent/task/run identity, event type, protocol, lifecycle status, allowlisted attributes |
| Provider integration event | docs/integrations/schemas/integration-event.schema.json | Integration identity, repository/SHA/PR/workflow/request IDs, execution, outcome, artifacts, validation, provenance, privacy |
| SHA-bound reconciliation evidence | docs/ops/EVIDENCE-ENVELOPE.schema.json | Experiment/source identity, commit and baseline SHA, observed time, status/outcome, provenance, confidence |
| Agent evidence semantics | docs/research/AGENT-EVIDENCE-CONTRACT.md | Event vocabulary, status semantics, attribution, canonical export rules |
| Adapter behavior | docs/integrations/ADAPTER-CONTRACT.md | Idempotency, redaction, scopes, retries, schema validation, promotion |

## Existing telemetry ingestion

scripts/telemetry_ingest/ingest.py reads scripts/telemetry_ingest/sources.json and emits independent Provenance and HindSight outputs plus an ingest receipt. Extend the manifest and owning extractors when new source surfaces require ingestion. Preserve the separate sink semantics and existing coverage tests.

## OpenTelemetry mapping

config/agent_stack_integrations.json already records otel-core as ADOPT. The entry defines agent invocation and MCP admission inputs, OTLP-compatible export, canonical JSONL receipts, and version pinning. Provider adapters translate the existing canonical events into OTLP signals and preserve source event IDs/digests.

## Correlation mapping

- Agent/task/run/parent-event identity maps to AGENT-EVIDENCE.
- Repository, commit SHA, PR, workflow run, provider request ID, execution state, artifact refs, validation, and provider attribution map to integration-event.
- Experiment ID, source identity, baseline SHA, confidence, and reconciliation status map to EVIDENCE-ENVELOPE.
- Trace/span context, run attempt, variant assignment, endpoint identity, and token/latency measurements require an explicit versioned extension to the owning schema when the current fields cannot express them. Add compatibility fixtures and retain prior schema versions.

## Privacy and cardinality

Apply the existing adapter contract's privacy rules and schema constraints. Exclude credentials, authorization headers, prompts, completions, private context, and raw request/response bodies by default. Keep high-cardinality request/trace/SHA/run IDs in events and traces; use bounded metric dimensions.

## Promotion

Validate mappings against existing JSON Schemas and sanitized fixtures. Preserve source SHA, provider/version, artifact digests, idempotency keys, and evidence status. Keep dashboards and provider persistence observational; canonical JSONL/receipts and repository-owned reducers retain authority.
