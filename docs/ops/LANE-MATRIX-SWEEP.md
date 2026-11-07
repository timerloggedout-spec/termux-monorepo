# Lane-matrix event-driven PR disposition

**Workflow:** `.github/workflows/ops-lane-matrix-sweep.yml`  
**Script:** `scripts/ops/lane_matrix_sweep.py`  
**Board:** `docs/ops/generated/lane-matrix-status.json` + `.md`  
**Trigger:** read-only tests on `pull_request`; inventory writes on `pull_request_target` lifecycle events and master pushes to the workflow, classifier, or policy. No timer, polling, or manual dispatch.

## Authority and scope

This materializes the open-PR disposition view only. It is not the cross-domain
lane×project SSOT. That record is `ops/tracking/tracking.json`, governed by
[REPO-TRACKING](REPO-TRACKING.md). Project/task lifecycle has its own canonical
records, including `docs/agentic/dependency-phases.json` and approvals.

Issue #175 is a preserved historical priority snapshot and has no operational
authority. No issue is a generic hub, database, heartbeat, or dispatch target.

## Demand contract

The workflow reacts to PR lifecycle changes that can affect the board:

- opened, reopened, closed;
- synchronize (head SHA changed);
- ready_for_review, converted_to_draft;
- edited (title/base changes).

The workflow checks out trusted `master` code only. It never checks out or runs
PR-head code. The classifier reads the current open-PR collection, not the
single event payload, so the result converges on current repository state.

Concurrency group `lane-matrix-inventory` uses cancel-in-progress to coalesce
event bursts: newer demand supersedes an in-flight stale materialization. There
is no elapsed-time debounce. A changed PR is eligible immediately.

## Age semantics

Age buckets are descriptive snapshot metadata calculated at `observed_at`.
They never change a PR's disposition and never trigger work. Disposition derives
from structural/evidence conditions (base, draft, mergeability, authorship,
scope, explicit supersession). Dual-gate remains the only promote authority.

This avoids a stale age-driven state transition that would require polling just
to cross 7/20/40-day thresholds. If a future policy needs time-based action,
model it as a specific due event in the owning lifecycle system, not a periodic
full-repository sweep.

## What it does not do

- Merge, rebase, close, or force-push PRs.
- Comment on issues or create heartbeat traffic.
- Dispatch from the ten-minute Quota Dispatch Tree.
- Treat age, file count, or comment volume as promote signals.
- Replace repo-gate + termux-smoke dual-gate.

## Complements

| Surface | Role |
|---|---|
| `docs/ops/LANE-MATRIX.md` | PR-disposition policy |
| `docs/ops/generated/lane-matrix-status.*` | Derived live PR board |
| `docs/ops/REPO-TRACKING.md` + `ops/tracking/tracking.json` | Cross-domain lane×project state |
| `docs/agentic/dependency-phases.json` | Dependency-phase lifecycle source |
| `ops/lane-events` | Append-only execution evidence |
| Desk.html / owning GitHub Issue | Human decisions and exceptions |
| Product PRs | Code / extracts / rebases; dual-gate then promote |

Agent-Identity: lane-matrix-sweep (event-driven)
