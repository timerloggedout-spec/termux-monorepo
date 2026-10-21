# Agent Evidence Contract

## Purpose

Provide one vendor-neutral execution evidence contract for MCP/A2A interoperability,
OpenTelemetry projection, evaluation, provenance, and manager tournaments.

The canonical event is an exportable JSON/JSONL record. Vendor dashboards and
adapters are projections only.

## Required event envelope

- schema_version
- event_id
- run_id
- event_type
- occurred_at (UTC ISO-8601)
- agent_id
- manager_id when applicable
- parent_event_id when applicable
- task_id
- provider when applicable
- model when applicable
- tool_name for tool events
- protocol: mcp, a2a, local, or other
- status
- attributes containing only allowlisted metadata

Payloads, prompts, completions, secrets, credentials, and arbitrary messages are
not admitted to the canonical evidence plane.

## Event vocabulary

Minimum interoperable vocabulary:

- agent.invoke
- agent.plan
- workflow.invoke
- tool.execute
- mcp.session
- mcp.operation
- a2a.delegate
- a2a.result
- evaluation.judgement
- provenance.snapshot
- environment.snapshot
- artifact.produced

These map naturally to OpenTelemetry GenAI/agent conventions without making
OpenTelemetry the storage contract.

## Evidence states

DISPATCHED, QUEUED, and IN_PROGRESS describe runtime state only.
EXECUTED requires an observed effect. VALIDATED requires evidence that the effect
satisfies the declared contract. PROMOTED is a separate lifecycle state.

## Attribution

GitHub identity is not agent identity. Attribution preserves workflow run/job/step,
triggering event, issue/PR, SHA/ref, timestamps, provider/model telemetry,
session/export provenance, and attribution confidence.

## Lock-in rule

Every adapter must permit export of canonical JSONL. A system that can display an
event but cannot export raw evidence is evidence-lock-in and cannot become the
canonical store.
