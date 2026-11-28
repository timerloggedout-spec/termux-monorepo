# BIUDL Integrated Steering & Evidence Plan

**Status:** committed implementation plan; execution is staged behind existing lane contracts and explicit promotion gates  
**Date:** 2026-11-11  
**Repository:** `timerloggedout-spec/termux-monorepo`  
**Scope:** Unified Foresight → ChronoMancer → HyperForge → Workflow Controls → Admin Web → Admin Graph → independent releases, with Collaborator Management concurrent and FireSight downstream.

## 1. Executive intent

Build one evidence-linked development loop across the existing systems without replacing their sources of truth or creating competing orchestration, identity, workflow, or telemetry platforms.

The compounding sequence is:

1. **Unified Foresight** selects work, records rationale, dependencies, uncertainty, and pinned repository context.
2. **ChronoMancer** steers a workstream's conversation lineage from an optimized historical branch point, carrying forward only relevant, verified resolutions.
3. **HyperForge** coordinates bounded capabilities and eligible collaborators; it does not become a second workflow engine.
4. **Workflow Controls** invoke registered operations through existing GitHub automation.
5. **Admin Web** provides authenticated governance and privileged control through a server-side gateway.
6. **Admin Graph** visualizes live, evidence-backed relationships; it is not authoritative storage.
7. **Independent component releases** make each lane versionable and comparable; the ArchW12.9y integration train pins compatible versions and SHAs.
8. **FireSight** detects operational risk and incidents after the event/evidence substrate exists; findings feed Foresight.

**Collaborator Management is a concurrent cross-cutting lane** for identity projections, qualification/admission, assignment, and lifecycle. It consumes existing identity and execution evidence; it does not replace them.

This is a feedback loop, not a one-way pipeline: Admin Graph and FireSight observations return to Foresight; validated outcomes become ChronoMancer resolution context; release evidence improves capability and collaborator selection.

## 2. Canonical boundaries and sources of truth

| System | Owns | Must not own |
|---|---|---|
| Foresight | prioritization, plan rationale, dependencies, horizon, confidence | execution authorization or dispatch |
| ChronoMancer | historical context selection, branch lineage, verified resolution deltas, working-reference pointer | erasing source history or inventing verified fixes |
| HyperForge | bounded capability coordination and orchestration decisions | duplicate Actions engine or canonical evidence store |
| Workflow Controls | registered operation contracts and existing GitHub workflow invocation | a competing workflow platform |
| Admin Web | authenticated operator control, approvals, policy and audit entry points | credentials in browser code or bypass of repository gates |
| Admin Graph | relationship projection, navigation, staleness and missing-evidence visibility | authoritative persistence or inferred success |
| Collaborator Management | operational roster projection, qualification, admission, assignment and lifecycle | replacement identity, moniker, provider or evidence registries |
| FireSight | operational detection, severity, escalation and incident linkage | unrestricted autonomous repair |
| Release Registry | component versions, compatibility and promotion evidence | one shared version number for unrelated components |
| Repository evidence substrate | append-only records, immutable SHA/run/artifact linkage | inferred outcomes or synthetic values |

Existing canonical foundations remain in force:
- `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md`: repository-owned JSONL/receipts and immutable Git SHA/run linkage; OpenTelemetry is an interoperability boundary; missing evidence is null, not zero.
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md`: Scout → candidate → experiment → telemetry → review → admission → synthesis.
- `docs/ops/LANE-MATRIX.md`: PR disposition policy only; cross-domain lane/project state remains in REPO-TRACKING and its canonical feed.
- `docs/ops/DOE-FAMILY.md` and `docs/ops/corpus/EXPERIMENT.schema.json`: campaign/run evidence and configured-instance identity.

No new global database is introduced by this plan.

## 3. Shared event and evidence envelope

Every cross-lane transition SHOULD carry the following logical envelope. Implementations may map it into existing JSONL, workflow artifacts, issue/PR references, and EXPERIMENT records; do not create a second evidence authority.

```json
{
  "schema_version": "1.0",
  "event_id": "evt.<stable-id>",
  "event_type": "plan.created",
  "occurred_at": "<UTC ISO-8601>",
  "correlation": {
    "plan_id": "plan.<stable-id>",
    "correlation_id": "corr.<stable-id>",
    "parent_event_id": null
  },
  "source": {
    "component_id": "foresight",
    "component_version": "<semver>",
    "repository": "timerloggedout-spec/termux-monorepo",
    "ref": "master",
    "commit_sha": "<40-hex SHA>"
  },
  "subject": {
    "capability_id": null,
    "collaborator_id": null,
    "task_id": null,
    "issue_ref": null,
    "pull_request_ref": null
  },
  "decision": {
    "state": "proposed",
    "approval_ref": null
  },
  "evidence": {
    "status": "observed",
    "refs": [],
    "digests": []
  },
  "outcome": {
    "state": "unknown",
    "validation_ref": null,
    "attribution_confidence": null
  }
}
```

Lifecycle states are distinct and must not be collapsed:
`PLANNED → APPROVED → DISPATCHED → COMMITTED → EXECUTED → VALIDATED → PROMOTED → MONITORED`.
A transition requires its own evidence. A queued workflow is not an execution; a completed workflow is not task correctness; a commit is not promotion.

## 4. ChronoMancer: single-workstream steering contract

### 4.1 Governing behavior

ChronoMancer is a steering mechanism for one evolving workstream/session lineage. It:
1. preserves the original conversation and all historical messages;
2. identifies the best prior assistant branch point for the next production-code continuation;
3. extracts resolved errors/issues only when their correction is supported by verification evidence;
4. attaches compact, relevant resolution context to a new branch;
5. makes the resulting branch the current optimized working reference;
6. sends later failures back through the same resolution and steering loop.

The underlying conversation API may create a new physical session ID. The lineage remains one conceptual workstream with explicit parent/child ancestry.

### 4.2 Resolution Dangle record

A Resolution Dangle is a compact, addressable knowledge unit extracted from an error or issue and its verified resolution. It is not a dangling TODO and not a free-form memory.

Minimum logical record:

```yaml
schema_version: "1.0"
dangle_id: "dang.<stable-id>"
workstream_id: "work.<stable-id>"
origin:
  session_id: "<origin-session>"
  message_range: ["<start-message-id>", "<end-message-id>"]
  issue_ref: null
problem:
  summary: "<concise failure>"
  error_signature: "<stable normalized signature or null>"
  root_cause: "<evidence-supported cause or null>"
resolution:
  status: "verified" # verified | unresolved | superseded
  correction: "<concise corrective knowledge>"
  patch_ref: "commit:<40-hex-sha>"
  validation:
    status: "PASS" # PASS | FAIL | UNKNOWN
    test_refs: []
    run_ref: null
    validated_sha: "<40-hex-sha or null>"
steering:
  target_message_id: "<historical assistant message>"
  context_delta: "<minimal instruction/context to carry forward>"
  relevance: "high" # high | medium | low
lineage:
  parent_dangle_ids: []
  supersedes: []
  evidence_refs: []
created_at: "<UTC ISO-8601>"
```

Rules:
- `verified` requires a concrete patch/commit reference and passing validation bound to the same SHA. Otherwise status remains `unresolved` or `UNKNOWN`.
- Never turn an assistant assertion, green workflow alone, or unverified patch into a verified dangle.
- Preserve source message, issue, patch, run, test, and SHA references.
- Supersession is additive: retain the prior dangle and link the replacement.
- Duplicate resolutions may be deduplicated only when their causal/problem identity and validated correction are equivalent; retain all provenance references.
- Context capsules are summaries with expandable evidence pointers, not replacements for source history.

### 4.3 Steering algorithm and safety

1. Load the requested workstream's own session lineage and account scope.
2. Select validation evidence scoped to that session/workstream; never use another session's latest account-level success as its timestamp.
3. Identify candidate historical assistant messages preceding the validated milestone.
4. Reject a candidate if required tools/files/context were not yet available; walk backward only within the same lineage.
5. Rank eligible verified dangles by task relevance, causal confidence, validation strength, and freshness. This ranking is a heuristic, not a substitute for hard constraints.
6. Assemble the smallest context capsule that preserves current task, active constraints, production-code state, relevant verified dangles, and unresolved blockers.
7. Create a branch with explicit parent session/message, dangle IDs, source SHA, context digest, and correlation ID.
8. Record the branch and make it the working reference only after branch creation succeeds.
9. Compare continuation outcomes and preserve failed/unknown outcomes as evidence.

No secrets, credentials, or private token values are copied into dangles or injected context. Unresolved errors remain visible with uncertainty. Historical detail remains retrievable.

### 4.4 Known implementation gaps to close

The inspected implementation in `harmony_hub/workspace/agent/chronomancer.py` has a correctness defect: `find_best_fork_point(session_id, account)` selects the latest validated `run_history` row by account only, then applies its timestamp to the requested session's messages. It must be scoped to the requested session/workstream and handle missing/ambiguous timestamps deterministically.

The spec describes validated-state injection, but the inspected `execute_fork()` path branches and logs a row without implementing the full explicit verified-state context capsule. Implement that as a separately tested assembly/injection seam.

The existing `run_history` fork row records the new session ID, but does not fully preserve parent session/message, dangle IDs, injected-summary digest, or a durable working-reference pointer. Additive lineage evidence is required; do not rewrite historical rows.

### 4.5 Existing DOE gate — mandatory

The existing campaign `experiments/doe/cb-1-chronomancer-emission/` is preregistered as **design-only**. Its README and DESIGN.json explicitly say **DISPATCH ∅ until doe-expert approves**, constrain both competing arms to exactly:
- `scripts/doe/chronomancer_emitter.py`
- `tests/test_chronomancer_emitter.py`

The emitter contract is read-only over `run_history`, deterministic, schema-valid against `docs/ops/corpus/EXPERIMENT.schema.json`, with exact fork/continuation pairing and source DB immutability. Do not dispatch either arm, widen its allowed paths, alter its acceptance criteria, or silently implement the competing-build task outside that campaign. Obtain the campaign's explicit approval and run its pre-registered arms/acceptance as written. The broader ChronoMancer runtime changes in §4.4 are a separate, explicitly scoped follow-on lane and must not be smuggled into cb-1.

## 5. Concurrent Collaborator Management lane

Collaborator Management is built concurrently and exposed to HyperForge through a narrow eligibility/assignment contract.

Lifecycle:
`DISCOVERED → PROFILED → QUALIFIED → ADMITTED → ACTIVE → EVALUATED → RETAINED | PROMOTED | QUARANTINED | CULLED`.

Keep these facts separate:
- registered ≠ qualified;
- qualified ≠ admitted;
- admitted ≠ available;
- available ≠ dispatched;
- dispatched ≠ executed;
- executed ≠ successful.

Identity/moniker/provider/model/configuration remain in their existing canonical registries. The manager stores lifecycle decisions and operational projections with source references and freshness. Admission requires declared scope, provenance, policy result, and evidence; culling preserves identity and history.

HyperForge asks this lane for eligible collaborators and capability compatibility. Workflow Controls remain the execution boundary. Execution receipts flow back to Collaborator Management for evaluation.

## 6. Implementation waves

### Wave 0 — plan and contract alignment (this PR)
- Record ownership, lifecycle, shared event envelope, ChronoMancer steering contract, dangle record, campaign gate, and release strategy.
- No live dispatch, credentials, or production authority is granted by this plan.

### Wave 1 — evidence-linked planning and ChronoMancer foundation
- Pin every plan to repository/ref/SHA, issue/task, rationale, dependencies, confidence, and evidence references.
- Fix session-scoped validation lookup and deterministic timestamp handling.
- Define and validate Resolution Dangle schema; implement append-only ledger/index.
- Implement verified-state context capsule with deterministic budget selection and provenance digest.
- Record branch parentage, selected dangles, context digest, and working-reference transition.
- Add fixtures for cross-session contamination, unresolved/superseded dangles, duplicate resolution, missing timestamps, budget pressure, and branch failure.
- Keep the DOE emitter campaign isolated behind its own approval and allowed-path rules.

### Wave 2 — bounded capability coordination and workflow execution
- Register capabilities with stable ID/version, input/output schema, scope, required approvals, owning workflow, idempotency behavior, failure states, and evidence outputs.
- HyperForge resolves an eligible collaborator + capability; it does not run a shadow Actions engine.
- Workflow Controls invoke existing GitHub automation with correlation/idempotency keys.
- Persist action→effect receipts with request, actor/instance, approval, run/job/step, artifact, validation and outcome references.
- Enforce approval before privileged actions; fail closed on missing policy/evidence.

### Wave 3 — authenticated control plane and live relationship graph
- Admin Web uses a server-side authenticated control gateway; browser code contains no PATs or privileged credentials.
- Gateway enforces identity, authorization, capability scope, approvals, idempotency, audit receipts, and bounded GitHub API operations.
- Keep read-only/static surfaces read-only; no simulated graph action may be presented as dispatched.
- Admin Graph consumes repository evidence and GitHub operational feeds; show stale/missing/unverified edges explicitly.
- Graph model: plan → collaborator → capability → issue → PR → commit SHA → workflow run → artifact → validation → release.

### Wave 4 — FireSight operational early warning
- Consume canonical run/evidence events and operational feeds.
- Detect failed gates, repeated retries, stale approvals, missing receipts, broken dependencies, anomalous failure rates, and unvalidated production changes.
- Emit findings with severity, confidence, affected entity refs, evidence refs, owner/escalation target, and deduplication key.
- Findings route to operator review and Foresight reprioritization. No autonomous repair or promotion.

### Wave 5 — independent releases and integration train
Independent version/release families:
- `foresight-vX.Y.Z`
- `chronomancer-vX.Y.Z`
- `hyperforge-vX.Y.Z`
- `workflow-controls-vX.Y.Z`
- `admin-web-vX.Y.Z`
- `admin-graph-vX.Y.Z`
- `collaborator-management-vX.Y.Z`
- `firesight-vX.Y.Z`
- `termux-cockpit-vX.Y.Z`

Each release declares source SHA, schema/contract versions, dependencies, compatibility, tests, security review, known limitations, and evidence. The ArchW12.9y integration train pins exact component versions/SHAs and runs cross-component contract tests. It does not replace component release identities.

Comparisons use the same frozen fixtures/cohorts, environment, acceptance criteria, and evidence schema. Do not compare unmatched runs or silently pool configured instances.

## 7. First end-to-end acceptance slice

Given a pinned issue and repository SHA, the system can:
1. explain why Foresight selected the work and expose its dependencies/uncertainty;
2. reconstruct the correct ChronoMancer workstream lineage;
3. attach only verified, relevant Resolution Dangles;
4. identify an admitted collaborator and authorized capability;
5. dispatch only through the registered existing GitHub workflow contract;
6. trace the action to run/job/step/artifact and validation;
7. preserve append-only receipts and make the relationship graph navigable;
8. return operational findings and measured outcome to Foresight;
9. package each changed component under its independent version with integration compatibility evidence.

**Pass condition:** every transition is attributable to the same correlation/plan lineage and immutable source SHA; missing evidence is explicit; no stage claims success on the basis of activity alone.

## 8. Security, governance, and non-goals

- No tokens, credentials, secrets, or private user data in source, event records, graph payloads, dangles, or artifacts.
- No privileged operation from static browser JavaScript.
- No bypass of required repository gates, approvals, branch protections, or existing campaign dispatch approval.
- No silent rewriting/deletion of historical evidence.
- No autonomous repair, merge, release promotion, or production deployment in this plan.
- No duplicate workflow engine, collaborator identity store, telemetry database, or graph database as a new source of truth.
- No fabricated metrics, timestamps, validation, actor identity, or success states.
- Human/operator promotion remains explicit.

## 9. Delivery tracking

| Deliverable | Completion evidence | State at plan commit |
|---|---|---|
| Integrated architecture and ownership contract | this document | committed |
| Resolution Dangle contract | this document; formal schema + validator still required | specified |
| ChronoMancer session-scope correction | code + regression tests | not implemented |
| Verified context capsule and branch lineage | code + deterministic fixtures | not implemented |
| cb-1 DOE emitter | approved arm PRs + A1–A6 acceptance | design-only; dispatch blocked pending doe-expert approval |
| Collaborator Management adapter | lifecycle contract + integration tests | specified; concurrent lane |
| HyperForge/Workflow Controls event handoff | action/effect receipts + end-to-end tests | not implemented |
| Admin Web authenticated gateway | authz/security tests + audit evidence | not implemented |
| Admin Graph live evidence projection | live-source freshness and provenance tests | not implemented |
| FireSight | detector fixtures + escalation evidence | deferred until substrate |
| Independent releases + ArchW12.9y pinset | release manifests + compatibility suite | not implemented |

## 10. Promotion gates

1. **Contract gate:** schema validation, ownership and scope checks pass.
2. **Correctness gate:** deterministic unit/integration tests pass on the candidate SHA.
3. **Evidence gate:** source SHA, run, artifact, actor/instance and validation lineage are complete or explicitly unknown.
4. **Security gate:** authorization, secret handling, idempotency, and approval tests pass.
5. **Reproducibility gate:** frozen fixtures can be replayed in a pinned environment.
6. **Comparative gate:** competing implementations use the same preregistered cohort and acceptance criteria.
7. **Promotion gate:** required repository gates pass on the exact candidate SHA and an authorized operator explicitly promotes.

A successful plan commit is not evidence that any implementation wave or promotion gate has passed.
