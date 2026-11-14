# Collaborator Management lane contract

**Status:** concurrent lane specification; existing roster/identity sources remain authoritative  
**Parent:** [BIUDL Integrated Steering and Evidence Plan](../architecture/BIUDL-INTEGRATED-STEERING-AND-EVIDENCE-PLAN.md)

## 1. Purpose

Provide a coherent operational view of collaborators across provider, model, agent, GitHub actor, workflow adapter and human identities. Manage qualification, admission, assignment, availability and lifecycle without replacing existing registries.

The lane is a cross-cutting projection and policy adapter. It is not a new identity provider, moniker registry, quota authority, execution engine, or evidence database.

## 2. Canonical source boundaries

| Fact | Authority |
|---|---|
| Display moniker and live trigger | `docs/ops/AGENT-MONIKERS.md` |
| Declared agent/provider adapter and role | `docs/schemas/agent-roster.yaml` plus provider-specific configuration |
| Observed collaborators and capability caveats | `docs/ops/AGENT-TEAM-ROSTER.md`, `docs/ops/PROVIDER-COLLABORATOR-CAPABILITY-MAP.md` |
| Human/agent permissions | `docs/ops/AGENTIC-PERMISSIONS.md` and platform permissions |
| Quota/capacity | owning provider quota source and timestamped observations |
| Execution participation and outcomes | canonical run/receipt/PR/commit/test evidence |
| Cross-domain project state | `ops/tracking/tracking.json` and its declared sources |
| Append-only lane events | `ops/lane-events`; evidence only, not project state |

The provider/collaborator capability map is a dated snapshot, not a live availability assertion. Every derived projection must expose its source and as-of timestamp.

## 3. Identity model

Never conflate these identities:

- `collaborator_id`: stable internal reference for the roster projection;
- `display_name` / `moniker`: human-readable call-sign;
- `github_actor`: GitHub account or App actor;
- `provider_account_id`: provider-side account/tenant identity;
- `model_id`: exact model identifier;
- `adapter_id`: executable integration;
- `execution_instance_id`: configured instance that performed a specific run;
- `human_operator_id`: authenticated human identity.

A shared PAT or GitHub App actor does not prove which model authored an operation. Attribution must use run/session/tool provenance and configured instance evidence. Unknown attribution remains unknown.

## 4. Lifecycle

`DISCOVERED → PROFILED → QUALIFIED → ADMITTED → ACTIVE → EVALUATED → RETAINED | PROMOTED | QUARANTINED | CULLED`.

Transitions are evidence-backed and append-only. Culling is not deletion. A collaborator may be registered but not qualified, admitted but unavailable, available but not dispatched, dispatched but not executed, or executed without a successful task outcome.

### State requirements

| State | Minimum evidence |
|---|---|
| DISCOVERED | source reference and discovery timestamp |
| PROFILED | identity mapping, declared role/capability and provenance |
| QUALIFIED | scope review, trust/security review, required test evidence |
| ADMITTED | explicit policy decision, owner, admitted scope and expiry/review date |
| ACTIVE | current availability/capacity observation and enabled adapter |
| EVALUATED | attributed task cohort and outcome evidence |
| RETAINED | review decision with supporting outcomes |
| PROMOTED | explicit role/scope/version change approval |
| QUARANTINED | reason, severity, containment scope, review owner and release criteria |
| CULLED | decision and preserved provenance/history |

## 5. Qualification and admission

Qualification is capability-specific, not a universal trust badge. Evaluate:

- identity and provenance confidence;
- adapter implementation and version;
- tool schema and permission scope;
- data handling and secret exposure;
- task cohort and bounded responsibilities;
- validation quality and failure behavior;
- availability, quota and provider terms;
- human escalation and rollback path.

Admission must specify permitted roles, repositories, paths/resources, operations, data classes, concurrency, rate limits, expiry, approver and evidence. Missing or stale evidence fails closed for privileged work.

## 6. Assignment interface to HyperForge

HyperForge requests an eligibility decision using task requirements:

```json
{
  "task_id": "task.<id>",
  "repository": "owner/repo",
  "source_sha": "<40-hex SHA>",
  "required_roles": ["implementation"],
  "required_capabilities": ["repo.patch"],
  "allowed_scope": ["src/module/**", "tests/**"],
  "data_classification": "repository-source",
  "deadline": "<UTC>",
  "correlation_id": "corr.<id>"
}
```

The lane returns candidate references and reasons, not an execution command:

```json
{
  "decision": "ELIGIBLE",
  "candidates": [{
    "collaborator_id": "collab.<id>",
    "adapter_id": "<adapter>",
    "capability_refs": ["repo.patch@1"],
    "scope_match": true,
    "availability": "OBSERVED_AVAILABLE",
    "availability_as_of": "<UTC>",
    "evidence_refs": []
  }],
  "rejected": [],
  "policy_version": "<version>"
}
```

Possible decisions: `ELIGIBLE`, `NO_MATCH`, `STALE_EVIDENCE`, `POLICY_DENIED`, `CAPACITY_UNAVAILABLE`, `HUMAN_REVIEW_REQUIRED`. Selection is advisory to HyperForge policy and never itself dispatches work.

## 7. Evaluation and feedback

Measure collaborator performance over matched cohorts and explicit task classes. Preserve:
- accepted/validated outcomes;
- regression and rework;
- time-to-integration;
- duplicate/conflicting actions;
- review findings and disposition;
- human intervention;
- tool/provider failures;
- resource cost and quota;
- attribution confidence;
- sample size and variance.

Quota is capacity, not correctness. A skipped route due to capacity is not a model failure. Do not rank collaborators on raw activity, token volume, comment count, or commit count alone.

## 8. Security and governance

- Least privilege per adapter and task.
- Explicit allowlists for repository/path/operation scope.
- No credential material in profiles or receipts.
- Human approval for protected operations.
- Quarantine disables new assignment but preserves records and permits read-only investigation.
- Expiry and stale evidence make a candidate ineligible until refreshed.
- Human and agent identities remain distinct even when they share infrastructure.

## 9. Acceptance criteria

- Identity dimensions remain distinct and source-linked.
- Every lifecycle transition has actor, timestamp, policy version and evidence references.
- Stale provider maps cannot assert current availability.
- HyperForge receives eligibility, not implicit permission to execute.
- Every execution can be traced to collaborator, adapter and configured instance—or explicitly unattributed.
- Culling/quarantine preserves historical records.
- No duplicate identity, quota, workflow or evidence authority is introduced.

## 10. Initial delivery slices

1. Read-only normalized roster projection with freshness metadata.
2. Identity/adapter reference validation and stale-record report.
3. Lifecycle transition record and admission policy.
4. HyperForge eligibility endpoint/adapter (read-only decision).
5. Execution-receipt ingestion for evaluation.
6. Matched-cohort performance view and review/cull workflow.
