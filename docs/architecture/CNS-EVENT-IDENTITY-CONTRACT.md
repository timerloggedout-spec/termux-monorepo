# CNS Event and Identity Contract

**Status:** Proposed integration contract, version 1  
**Purpose:** Correlate existing canonical records across CNS organs while preserving each event family's owner.

## 1. Identity dimensions

The shared trace view correlates the following dimensions where supplied by authoritative sources:

| Dimension | Meaning | Source-of-truth rule |
|---|---|---|
| `repository` | Repository full name | GitHub repository identity |
| `source_sha` | Exact source revision | Git commit SHA |
| `task_id` | Work item identity | Existing task / issue / queue owner |
| `scope_id` | Authorized work scope | Proposal and scope registry |
| `orchestration_id` | Manager-run coordination identity | Existing orchestration record |
| `cycle_id` | Repeated manager or workflow cycle | Existing cycle record |
| `attempt_id` | A single attempt | Existing attempt / run-attempt record |
| `agent_id` | Collaborator or agent identity | Agent roster / invocation record |
| `provider_id` | Provider identity | Provider catalog |
| `model_id` | Exact model identity/version | Provider catalog snapshot |
| `adapter_id` | Actual execution adapter | Adapter registry and invocation evidence |
| `run_id` | Workflow or execution run | GitHub Actions or native runner |
| `artifact_id` | Immutable output reference | Artifact owner |
| `outcome_id` | Confirmed outcome record | Outcome ledger / task owner |

## 2. Correlation envelope

The following is a CNS projection contract. It maps existing event IDs and references; it does not establish a new canonical event database.

```json
{
  "schema": "cns-correlation/v1",
  "event_ref": {
    "system": "canonical-owner",
    "id": "native-event-id",
    "uri": "https://..."
  },
  "correlation": {
    "task_id": "native-task-id",
    "scope_id": "native-scope-id",
    "orchestration_id": "native-orchestration-id",
    "cycle_id": "native-cycle-id",
    "attempt_id": "native-attempt-id",
    "parent_event_ref": "native-event-reference"
  },
  "actor": {
    "agent_id": "native-agent-id",
    "provider_id": "native-provider-id",
    "model_id": "native-model-id",
    "adapter_id": "native-adapter-id"
  },
  "execution": {
    "repository": "owner/name",
    "source_sha": "full-git-sha",
    "run_id": "native-run-id",
    "run_attempt": 1
  },
  "result": {
    "artifact_id": "native-artifact-id",
    "outcome_id": "native-outcome-id",
    "status": "observed-native-status"
  },
  "provenance": {
    "evidence_class": "verified",
    "observed_at": "2026-11-20T00:00:00Z",
    "source_uri": "https://..."
  }
}
```

## 3. Mapping and identity rules

- Preserve native identifiers and source URIs.
- Use exact Git SHA, workflow run ID, and run attempt when available.
- Keep provider, model, agent, role, and adapter as separate dimensions.
- Keep declared routes separate from actual invocations.
- Keep workflow completion separate from task outcome.
- Preserve the event-family owner for append, correction, and lifecycle transitions.
- Treat missing identity dimensions as `NOT_ESTABLISHED`.
- Classify correlation confidence as verified, derived, inferred, or candidate.
- Promote derived correlations only when deterministic source fields support the join.
- Store metadata references and bounded summaries according to the owning source's privacy contract.

## 4. Event lifecycle projection

The CNS trace may display these stages when their native owners provide evidence:

`planned → admitted → context_selected → reasoned → routed → dispatched → invoked → completed → validated → outcome_confirmed → scored → learned`

Each stage is independently observed. The projection records gaps and out-of-order events as reconciliation findings. A stage label does not manufacture an event.

## 5. Synaptic Bus relationship

PR #5637 proposes ADE-SYNAPSE / Synaptic Bus v1. CNS correlation fields should map to that envelope through a compatibility adapter after its contract is reviewed and promoted. The Synaptic Bus remains an interoperability surface; ATES, Action-Effect, Orchestration Receipts, 3L0, MoneyBall, and other existing event owners retain their records.

## 6. Acceptance tests

- Same task with multiple attempts retains distinct attempt identities.
- Same provider with multiple models retains distinct model identities.
- Same model called through multiple adapters retains adapter identity.
- Re-run of a workflow retains run-attempt identity.
- Missing fields remain explicitly unknown.
- Correlation across unrelated source SHAs is rejected or marked candidate.
- Duplicate event delivery resolves idempotently to the native event reference.
- Projection preserves source URI, observation time, and evidence classification.
