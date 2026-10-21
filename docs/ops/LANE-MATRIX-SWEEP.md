# Lane-matrix recursive sweep

**Workflow:** `.github/workflows/ops-lane-matrix-sweep.yml`
**Script:** `scripts/ops/lane_matrix_sweep.py`
**Board:** `docs/ops/generated/lane-matrix-status.json` + `.md`
**Schedule:** `11 */6 * * *` + `workflow_dispatch`

## What it does

1. Lists open PRs.
2. Age-buckets and classifies lanes, including **SUPERSEDE** for session-pulse titles.
3. Writes generated board files and may commit them to `master`.
4. Does **not** comment on #175 unless explicitly dispatched with `comment_175=true`.

## What it does *not* do

- Merge, rebase, or force-push.
- Open session-pulse PRs.
- Treat age or file-count as a promote signal.
- Replace dual-gate.
- Turn #175 into a heartbeat stream.

## Complements

| Surface | Role |
|---------|------|
| `docs/ops/LANE-MATRIX.md` | Durable policy |
| generated status | Live board |
| `merge-promotion-queue.yml` | Dual-gate candidate inventory |
| Product PRs | The only promote objects |

Agent-Identity: Grok (Administrator)
