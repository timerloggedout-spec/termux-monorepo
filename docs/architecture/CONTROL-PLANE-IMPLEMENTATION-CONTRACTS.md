# Control-plane implementation contracts

**Status:** implementation contract / design; not a claim that the gateway or live integrations are deployed  
**Parent plan:** [BIUDL Integrated Steering and Evidence Plan](BIUDL-INTEGRATED-STEERING-AND-EVIDENCE-PLAN.md)

## 1. Purpose

Connect Foresight plans to governed, bounded GitHub operations while retaining the repository's existing authorities:

- Foresight owns prioritization and rationale.
- HyperForge coordinates capability selection and collaborator eligibility.
- Workflow Controls invoke existing GitHub Actions and registered operations.
- Admin Web is the authenticated operator surface.
- Admin Graph is a read model over evidence and operational relationships.
- Repository-owned JSONL/receipts and immutable SHA/run/artifact linkage remain the evidence substrate.

This contract does not introduce a second workflow engine, global database, credential store, or source of project state.

## 2. Capability registration

A capability registration describes an operation that already has an owning implementation. It is a contract and discovery record, not permission to execute.

Required fields:

| Field | Meaning |
|---|---|
| `capability_id` | Stable namespaced identifier |
| `version` | Contract version, independently versioned |
| `owner_lane` | Owning component/team |
| `operation` | Existing workflow, API adapter or bounded command |
| `input_schema_ref` / `output_schema_ref` | Versioned contracts |
| `required_scopes` | Least-privilege permission declaration |
| `approval_policy` | Required human/automated approval class |
| `idempotency` | Key scope and duplicate-request behavior |
| `timeout` / `retry_policy` | Bounded execution behavior |
| `evidence_outputs` | Required run, artifact, validation and receipt references |
| `availability` | Observed availability with as-of time; never inferred from registration |

Lifecycle is `DRAFT → REVIEWED → REGISTERED → AVAILABLE/UNAVAILABLE → DEPRECATED`. Registration is not admission, authorization, availability, dispatch or success.

HyperForge may select only a registered capability whose policy, scope, version, dependencies and current availability satisfy the plan. A capability can be registered but unavailable.

## 3. Dispatch request contract

Every request must contain:

- request/event ID and idempotency key;
- plan ID and correlation ID;
- capability ID and exact version;
- repository, ref and immutable source SHA;
- task/issue/PR references;
- requesting actor and execution instance identity;
- input payload validated against the declared schema;
- approval reference when required;
- deadline/timeout and bounded retry policy;
- expected evidence outputs.

Reject requests with missing SHA, unsupported schema, unknown capability, stale approval, insufficient scope, expired deadline, or an idempotency collision with a different payload digest.

A retry with the same idempotency key and same canonical payload returns or links the original operation; it must not create an untracked duplicate side effect. A different payload under the same key is a conflict.

## 4. Authenticated Admin Web gateway

The public/static Tribute dashboard remains a read-only projection. The existing `admin.html` explicitly states that it embeds no credentials and mutates nothing from browser JavaScript. Preserve that behavior.

Privileged operations require a server-side authenticated gateway:

1. Authenticate the operator using an approved identity provider.
2. Resolve actor identity and current role/organization/repository scope.
3. Evaluate policy for the exact action, target, SHA and capability version.
4. Require explicit approval for protected actions.
5. Apply idempotency and request validation.
6. Invoke the owning GitHub API/Actions operation using server-held credentials.
7. Record an append-only request/action/effect receipt.
8. Return a redacted result and evidence links to the browser.

Never put PATs, App private keys, refresh tokens, or other privileged credentials in HTML, JavaScript, local storage, query strings, graph payloads, or client-visible artifacts. Never trust a client-supplied role or approval claim.

### Operation classes

| Class | Examples | Default policy |
|---|---|---|
| Read | inspect refs, issues, PRs, workflow runs, artifacts | authenticated read scope |
| Low-risk write | create intake issue, comment, labels | scoped permission + audit |
| Governed write | assign, edit/close issue, update PR, dispatch workflow | policy + idempotency + explicit approval as configured |
| Protected | merge, publish release, deployment/environment mutation, secrets/policy changes | human approval, branch/environment protection and repository gates |

The gateway must defer to GitHub branch protection, environment protection, required reviews and repository gates; it must not bypass them.

## 5. Workflow Controls adapter

Workflow Controls is a registry of existing automation contracts, not a duplicate scheduler or executor. Each entry declares:

- owning workflow file and workflow ID;
- accepted trigger modes and validated input schema;
- minimum permissions;
- concurrency group and cancellation behavior;
- idempotency semantics;
- expected jobs/artifacts/receipts;
- timeout, retry and failure taxonomy;
- source SHA and owning lane.

HyperForge calls the registered operation. The adapter invokes the existing workflow through the authenticated boundary. Workflow status is observed from GitHub; task correctness is determined separately by validation evidence.

## 6. Action-to-effect receipt

A dispatch receipt links request to observed effects:

```yaml
schema_version: "1.0"
receipt_id: "rcpt.<stable-id>"
request_id: "req.<stable-id>"
plan_id: "plan.<stable-id>"
correlation_id: "corr.<stable-id>"
actor:
  id: "<authenticated actor>"
  instance_id: "<configured execution instance>"
capability:
  id: "<capability id>"
  version: "<contract version>"
source:
  repository: "owner/repo"
  ref: "<ref>"
  sha: "<40-hex SHA>"
approval_ref: null
operation:
  workflow_id: "<GitHub workflow id>"
  run_id: null
  attempt: null
  state: "requested"
effects: []
validation:
  state: "unknown"
  refs: []
timestamps:
  requested_at: "<UTC>"
  completed_at: null
```

Receipt states distinguish `REQUESTED`, `ACCEPTED`, `REJECTED`, `QUEUED`, `RUNNING`, `COMPLETED`, `CANCELLED`, `FAILED`, `INTERRUPTED`. Validation is a separate field and can remain `UNKNOWN` after a completed workflow.

Receipts are append-only. Corrections are new linked events; do not rewrite prior execution history.

## 7. Admin Graph read model

Admin Graph consumes evidence and operational feeds and projects relationships:

`plan → collaborator → capability → issue → PR → commit SHA → workflow run → job/step → artifact → validation → component release`.

Each node/edge carries:

- stable entity identity and type;
- source record/reference;
- observed/updated timestamp and freshness policy;
- source SHA where applicable;
- evidence status and confidence;
- lifecycle state;
- unresolved/missing/stale marker.

Graph rules:
- Never infer an edge from name similarity alone.
- Distinguish declared relationship from observed execution and validated outcome.
- A missing edge is displayed as missing, not fabricated.
- A stale feed is visibly stale and cannot authorize dispatch.
- The graph is rebuildable from canonical sources and is not an authority for permissions or state mutation.
- Dispatch controls, if later added, call the authenticated gateway and display the returned receipt; a local graph simulation is never labelled a real dispatch.

## 8. Failure taxonomy

At minimum: `INVALID_INPUT`, `UNKNOWN_CAPABILITY`, `UNREGISTERED_VERSION`, `POLICY_DENIED`, `APPROVAL_REQUIRED`, `APPROVAL_STALE`, `SCOPE_DENIED`, `IDEMPOTENCY_CONFLICT`, `DEPENDENCY_UNAVAILABLE`, `RATE_LIMITED`, `UPSTREAM_REJECTED`, `TIMEOUT`, `CANCELLED`, `INTERRUPTED`, `EXECUTION_FAILED`, `VALIDATION_FAILED`, `EVIDENCE_INCOMPLETE`.

Do not collapse infrastructure unavailability, policy denial, execution failure and task failure into one result.

## 9. Acceptance criteria

- Every operation resolves to one owning implementation and version.
- Requests are schema-validated, SHA-pinned, scoped and idempotent.
- Protected actions fail closed without valid approval.
- No browser artifact contains privileged credentials.
- Every accepted dispatch yields a correlated receipt, including failures.
- Workflow lifecycle and task validation remain separate.
- Graph projections link to source evidence and expose stale/missing data.
- Rebuilding the graph from canonical feeds produces the same relationships.
- No new component becomes a competing project-state or evidence authority.

## 10. Implementation order

1. Capability registry schema and read-only inventory.
2. Workflow Controls adapters for existing, low-risk workflows.
3. Receipt writer and idempotency tests.
4. Server-side authentication/authorization gateway.
5. Admin Web read/write split with explicit policy.
6. Admin Graph evidence projection.
7. Protected operations only after security review and promotion gates.
