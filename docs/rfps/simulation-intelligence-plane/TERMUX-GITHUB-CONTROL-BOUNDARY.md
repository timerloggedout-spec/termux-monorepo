# Termux ↔ GitHub Control Boundary

**Contract:** SIP-TERMUX-GITHUB-BOUNDARY-001  
**Status:** proposed clarification; no runtime implementation implied

## 1. Canonical interpretation

Termux is the local, offline-capable operator controller for GitHub surfaces. It is not the Simulation Intelligence Plane's hosted backend, always-on service, remote worker, scheduler, or simulation execution environment.

"Offline-capable" describes the controller's local operating model: it can inspect and prepare work from locally available repository state and cached evidence while disconnected. GitHub mutations and fresh remote observations necessarily wait until connectivity and authorization are available. The controller must never represent a queued local intent as a completed GitHub action.

Termux controls GitHub surfaces; it does not host the workloads those surfaces dispatch.

## 2. Responsibility split

| Surface | Responsibility |
|---|---|
| Termux local controller | Operator interface; local repository/worktree inspection; local plans and drafts; offline cache; queued intents; explicit sync; GitHub API orchestration; polling; evidence download and local indexing |
| GitHub repository | Canonical remote source for branches, commits, issues, pull requests, labels, releases, and repository metadata |
| GitHub Actions / remote runner | Executes CI, validation, scheduled automation, and explicitly dispatched remote jobs |
| External simulation worker | Executes OASIS or another admitted engine in a separately provisioned, bounded environment |
| QUE / Workflow Contract | Existing admission, dispatch authority, dependency planning and workflow semantics |
| DoE / ATES / CEEL | Existing experiment, evaluation, trace and normalized-event/evidence authorities |
| SHE / Tribute / Observatory | Read-only projections of canonical records and evidence |

Termux may initiate or monitor a GitHub Actions run through authorized GitHub APIs. The run executes on its configured remote runner, not inside Termux. A local Termux command that launches a local test is a separate, explicitly local operation and must be labeled as such.

## 3. Offline and synchronization semantics

1. **Read:** use the local checkout/cache when disconnected; label its commit SHA and cache freshness. Do not claim it represents current GitHub state.
2. **Plan:** allow local drafts and proposed operations to be prepared without network access.
3. **Queue:** persist intended remote operations locally with operation ID, target repository/ref, expected base SHA, payload digest, creation time and required authorization class.
4. **Reconcile:** after reconnecting, fetch current remote state before applying a queued mutation. Reject or require operator resolution when the expected base/ref has drifted.
5. **Apply:** perform only explicitly authorized, idempotent or deduplicated GitHub operations. Record the GitHub response and resulting object/commit/run identifiers.
6. **Observe:** poll remote Actions/jobs and retrieve logs/artifacts as evidence. A dispatch acknowledgement is not a successful run.
7. **Recover:** retries must use operation identity and current remote state; never blindly replay non-idempotent mutations.

A local queued intent is pending_sync, not dispatched, merged, completed, or verified.

## 4. Simulation execution boundary

The SIP adapter is a workload adapter and evidence contract. Its runtime must be placed on a declared execution host selected through the existing QUE / Workflow Contract path. Initial CI and contract tests should use the deterministic offline fake engine. A real OASIS pilot, if later admitted, runs in a bounded remote worker or other explicitly provisioned environment.

- Termux may prepare a scenario, inspect manifests, request an authorized dispatch, monitor the remote run and collect its evidence.
- GitHub Actions may perform repository-native validation and orchestration steps on GitHub-hosted runners.
- A simulation engine runs only where its runtime, dependencies, resource limits, persistence and secrets are explicitly provisioned.
- No design may assume a persistent Termux daemon, inbound tunnel, always-on phone, or Termux-hosted API.
- No ordinary CI job may install or invoke paid/live model providers by implication.

## 5. Evidence and provenance

Every remote operation and run receipt should retain, where applicable:

- repository full name and canonical GitHub object URL;
- local checkout SHA and remote base/head SHA;
- operation ID and request/payload digest;
- GitHub workflow/run ID, attempt, job IDs and conclusion;
- execution host/runner identity and workflow revision;
- scenario/experiment IDs and digests, engine/adapter versions, seed and resource budget;
- artifact identifiers and content digests;
- timestamps, sync state, errors and retry lineage.

Distinguish at least: local_only, pending_sync, submitted, remote_running, remote_completed, evidence_collected, verified, rejected, and needs_reconciliation. These are controller/evidence states, not a replacement for QUE or SIP's canonical run lifecycle.

## 6. Security and authority

- Local credentials remain in the operator's approved local secret store; never commit them or place them in simulation manifests, logs or artifacts.
- Use least-privilege GitHub permissions and separate read operations from mutation scopes.
- Issue/comment/PR text and repository content are untrusted input, not executable controller instructions.
- Destructive actions, merges, permission changes, deployments and external side effects require their existing explicit authorization gates.
- A local operator command or successful API response does not bypass branch protection, required reviews, QUE admission or repository policy.
- Remote artifacts are untrusted until integrity and provenance checks pass.

## 7. Non-goals

This contract does not introduce a second scheduler, event bus, repository registry, provider router, experiment registry, or control plane. It does not make Termux a cloud worker, expose a public API from the device, or authorize automatic merge/promotion. Existing GitHub, QUE, WFC, DoE, ATES and CEEL authorities remain in force.

## 8. Acceptance checks

- Disconnected mode can inspect cached state and prepare a local intent without claiming a remote mutation.
- Reconnect detects remote SHA drift before applying a queued write.
- Duplicate sync attempts do not create duplicate remote effects.
- Dispatch acknowledgement and workflow success are represented as distinct states.
- Workflow logs/artifacts are linked to the exact repository SHA, run ID and attempt.
- A simulation dispatch targets a declared remote execution host; no Termux daemon or device tunnel is required.
- Offline fake-engine tests run without network, secrets, provider calls or package installation.
