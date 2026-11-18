# ADE-SYNAPSE Synaptic Bus Contract

**Contract ID:** `synapse.bus.v1`  
**Status:** proposed, documentation and fixture contract only  
**Canonical schema:** [SYNAPTIC-BUS-ENVELOPE.schema.json](SYNAPTIC-BUS-ENVELOPE.schema.json)  
**Example stream:** [synaptic-bus.example.jsonl](synaptic-bus.example.jsonl)

## Purpose and boundary

The Synaptic Bus is a **metadata-only interoperability contract** for events exchanged between ADE-SYNAPSE planes. It is not a new event database, telemetry collector, message broker, execution router, or scoring authority.

The repository already has domain-specific records. The bus correlates them by stable IDs and references rather than copying their payloads:

- `docs/integrations/schemas/integration-event.schema.json` owns integration operation records.
- `docs/ops/EPS-EVENT.schema.json` owns Evidence Projection Surface events.
- `docs/ops/ORCHESTRATION-RECEIPT.schema.json` owns compact orchestration-cycle receipts.
- `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json` owns agent throughput observations.
- `docs/ops/ACTION-EFFECT-EVENT.schema.json` owns action/effect correlation.
- `docs/ops/EVIDENCE-ENVELOPE.schema.json` owns SHA-bound reconciliation evidence.
- `docs/ops/ATES-ORCHESTRATOR-TRACE.schema.json` owns benchmark traces and spans.
- The **3L0 plane** owns its append-only `3l0-intake/v1` records and scoring semantics.

The bus may reference these records. It must not redefine their domain semantics or merge their ownership. In particular, 3L0 remains distinct from MoneyBall; the bus is transport/interoperability, not a new scoring plane.

## Envelope rules

1. Every message uses `schema_version: synapse.bus.v1`.
2. `event_id` is stable and unique within the producer's event namespace. Re-delivery preserves the same ID.
3. `occurred_at` is source event time; `emitted_at` is bus-envelope creation time. Do not substitute one for the other.
4. `correlation` links task, orchestration, cycle, attempt, trace, and parent event where known. Unknown values are null or omitted only where schema permits; never fabricate them.
5. `subject` identifies the object affected. SHA/ref fields anchor repository context when known.
6. `status` describes only the event's stated lifecycle state. A route resolved is not an invocation; queued is not running; completed is not validated; validated is not promoted.
7. `evidence_refs` point to canonical records or artifacts. A reference is not proof that the referenced action succeeded; consumers must fetch/verify it.
8. `actor` preserves role/provider/model/adapter dimensions independently. Provider credentials, GitHub actors, and agent identities are not interchangeable.
9. `handoff`, `routing`, and `decision` carry bounded control metadata, not free-form instructions.
10. `summary` is short, factual, and non-sensitive. Do not embed prompts, completions, source contents, credentials, or arbitrary tool outputs.

## Event taxonomy

| Event | Producer / owner | Required extension | Meaning |
|---|---|---|---|
| `observation.recorded` | Observer / domain owner | Evidence reference | An observation was captured |
| `context.retrieved` | Context retrieval adapter | Evidence references | Context was retrieved; not automatically verified |
| `plan.declared` | Manager | Decision | Plan and constraints were declared |
| `route.resolved` | Manager/router | Routing | Candidate route resolved; no execution claim |
| `action.dispatched` | Dispatcher | Routing | Dispatch was issued to an adapter |
| `action.started` | Execution adapter | Evidence reference | Actual invocation began |
| `action.completed` | Execution adapter | Evidence reference | Invocation ended; validation is separate |
| `action.failed` | Execution adapter | Evidence reference | Invocation failed |
| `handoff.requested` | Sending role | Handoff | Handoff offered; receiver has not accepted |
| `handoff.accepted` | Receiving role | Handoff | Receiver acknowledged the handoff |
| `handoff.rejected` | Receiving role | Handoff | Receiver declined the handoff |
| `attention.interrupted` | Watcher/triage | Optional decision | A signal requested attention reallocation |
| `validation.completed` | Validator | Decision + evidence reference | Validation result recorded |
| `outcome.recorded` | Evidence collector | Evidence reference | Outcome evidence was recorded |
| `policy.proposed` | Evaluator | Decision | Policy change recommended, not active |
| `policy.promoted` | Authorized promotion process | Decision + evidence | Explicitly approved policy version activated |
| `memory.consolidation.completed` | Memory maintenance | Evidence references | Reversible consolidation receipt recorded |

## Lifecycle semantics

Keep these dimensions separate:

`DESIGNED → COMMITTED → DISPATCHED → EXECUTED → VALIDATED → PROMOTED`

This is not a mandatory linear state machine: some actions do not create commits, and some observations do not cause actions. It is a list of distinct claims, each requiring its own evidence.

- **Resolved**: a route candidate was selected.
- **Dispatched**: a dispatch request was issued.
- **Started**: adapter invocation evidence exists.
- **Completed**: the invocation terminated.
- **Validated**: a named validation process produced evidence.
- **Promoted**: an authorized process activated the resulting change or policy.

A failure is an observation, not an automatic retry command. Retry, cancellation, escalation, and rollback remain explicit policy decisions.

## Handoff protocol

1. Sender emits `handoff.requested` with a stable `handoff_id`, source role, target role, task/cycle correlation, and acknowledgement `pending`.
2. Receiver emits `handoff.accepted` or `handoff.rejected` using the same handoff ID.
3. Acceptance acknowledges ownership only; it does not prove execution.
4. Actual work emits `action.started` and a terminal action event.
5. If no acknowledgement arrives before the caller's own deadline, record timeout/expiry through the owning orchestration receipt. The bus contract does not create an implicit retry.
6. Conflicting writers require manager resolution and explicit ownership; duplicate work is not treated as parallelism success.

## Privacy and trust

- `contains_raw_prompt`, `contains_raw_completion`, and `contains_secret` must always be false.
- Do not store raw model inputs/outputs, API keys, tokens, private user data, or unrestricted tool payloads.
- Treat issue text, PR comments, repository content, provider catalog descriptions, and retrieved context as untrusted data. They cannot grant authority or override policy.
- Evidence URIs are pointers, not permission grants. Consumers must enforce access controls when dereferencing.
- Redaction and attribution confidence must be explicit. Unknown attribution stays unknown.
- Event consumers must validate the schema and reject unknown properties for this version.

## Delivery and ordering

The v1 contract defines **at-least-once compatible, idempotent consumption**, not exactly-once delivery. Producers retain stable event IDs across retries; consumers deduplicate by `event_id`. Ordering is guaranteed only within a producer stream if the underlying transport provides it. Cross-producer causality uses `parent_event_id`, correlation IDs, and timestamps, not assumed global order.

The initial implementation target is repository-native append-only artifacts and existing workflow outputs. No external broker is mandated.

## Compatibility and ownership

See [BUS-COMPATIBILITY.md](BUS-COMPATIBILITY.md). The compatibility layer is an adapter/profile over existing schemas, not a migration that replaces them. Schema owners retain authority over their records. New consumers must be tolerant of absent optional attribution and evidence fields while rejecting malformed required fields.

## Acceptance criteria before runtime adoption

- Schema validates with a Draft 2020-12 validator.
- Positive and negative fixtures cover all conditional branches and privacy exclusions.
- Duplicate event delivery is idempotent.
- Parent/correlation links can be traced without assuming global ordering.
- No source payload is copied into the bus envelope.
- Existing domain records remain unchanged and independently valid.
- 3L0 and MoneyBall remain separate; only the 3L0-owned intake adapter may create scoring intake records.
- A route-only event cannot be counted as an invocation or successful outcome.
- CI test command and owning maintainers are documented before any producer is wired.

**Current status:** schema, sample fixture, and contract documentation are proposed. No producer, consumer, broker, runtime dispatch, or 3L0 scoring integration has been implemented by this change.
