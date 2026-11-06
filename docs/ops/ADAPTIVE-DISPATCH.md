# Adaptive dispatch and execution control

**Purpose:** wake the right managed lane when state changes, preserve real
time-based cadence, and keep human authorization separate from agent execution.

## Control-plane boundaries

- Cross-domain lane × project state: `ops/tracking/tracking.json`, rendered by
  `docs/ops/REPO-TRACKING.md`.
- PR disposition: `docs/ops/generated/lane-matrix-status.json` and its Markdown
  projection. It is not the cross-domain SSOT.
- Dependency lifecycle and approvals:
  `docs/agentic/dependency-phases.json` and
  `docs/agentic/phase-approvals.json`.
- Append-only execution evidence: `ops/lane-events`.
- Domain registries remain authoritative within their domains.
- Desk.html and the owning Issue/PR are human decision and exception surfaces.
  No generic issue is a global hub.

Issue #175 is closed and retained only as a historical snapshot. It is not a
state store, command bus, dispatch gate, or current authority.

## Wake model

| Signal | Behavior | Purpose |
|---|---|---|
| PR lifecycle (`pull_request_target`) | Immediate event wake; coalesced per PR | Recompute current open-PR disposition |
| Managed lane completion (`workflow_run` via lane-events recorder) | Immediate event wake | Re-evaluate dependent work and freshness |
| Canonical source-record push | Immediate event wake | Reconcile changed tracking/dependency state |
| Hourly schedule | Cadence clock only | Run hourly and modulo-based 3h/4h/6h/12h slots; recover time-only stale lanes |
| Authorized Issue command | Explicit human force request | Force the managed dispatch fan-out with an auditable receipt |

The Lane Matrix is not part of the Quota Dispatch Tree. It has its own PR
lifecycle trigger and no timer, polling loop, manual dispatch, or six-hour
dependency.

The central dispatcher no longer runs a ten-minute sweep. Its hourly schedule
is the clock for true time cadence. Demand work does not wait for that clock:
PR, lane-completion, and canonical-record events wake the admission tree
immediately. Event wakes do not replay scheduled modulo phase slots.

## Admission and safety

- The decision tree reads current state and active-run pressure before fan-out.
- Per-lane caps and the global managed-run cap apply to normal work.
- A failed pressure read fails closed for gated lanes.
- Staleness-critical lanes retain only their documented preemption behavior.
- Each target workflow keeps its own concurrency, validation, and promotion
  authority.
- Force execution does not merge, approve a PR, write credentials, or bypass
  target-lane gates. Dual-gate remains required for promotion.

## Human force request (Issue HITL)

The currently implemented human force surface is an exact comment on the
owning GitHub Issue:

```text
/quota force all
```

The request is accepted only when all conditions hold:

1. The comment is on an open Issue, not a pull request or closed historical issue.
2. The GitHub sender is a human `OWNER`, `MEMBER`, or `COLLABORATOR`.
3. The comment body matches the command exactly.
4. The immutable comment ID has not already been completed.

The dispatcher checks for a prior receipt marker before force-admitting work.
After the fan-out job succeeds, it writes a receipt to the same Issue with the
authenticated GitHub actor, request comment ID, and dispatcher run URL.
Duplicate webhook deliveries are therefore idempotent. A failed or partial
fan-out does not receive a success receipt; retry behavior remains visible in
the owning Issue and Actions evidence.

Desk.html remains the visual decision surface. It currently does not embed a
GitHub token or directly dispatch workflows. A direct Desk.html action requires
an authenticated server-side adapter; do not add a PAT, App token, or other
credential to browser JavaScript. Until that adapter is verified, use the
authenticated Issue command above.

## Operational invariants

- No generic `workflow_dispatch` surface on the central dispatcher.
- No ten-minute inventory sweep.
- No six-hour Lane Matrix refresh.
- No elapsed-time debounce for demand events.
- No force-all through untrusted comments, PR comments, bot actors, or a
  browser-held credential.
- No automatic merge. Human authorization and dual-gate promotion remain
  separate from agentic execution.
