# Actions quota consolidation (planning lanes), 2026-10-19

Recon source: read-only pass over master c9d923a (help-wanted, SHE, cadence, lane matrix, merge promotion).

## Changed in this PR (cron only, no logic changes)
| Workflow | Before | After | Runs/day saved | Why safe |
|---|---|---|---|---|
| `help-wanted-scout.yml` | `17 */2` (12/day) | `17 */4` (6/day) | 6 | `help-wanted-execute.yml` (`41 */4`) re-runs the scout inline for both labels; standalone scout now lands 24 min before each execute |
| `help-wanted-status-refresh.yml` | `7 *` (24/day) | `7 */6` (4/day) | 20 | `workflow_run` on execute, followup and scout already refreshes after every change |
| `merge-promotion-queue-v3.yml` | `7,37 *` (48/day) | `7 *` (24/day) | 24 | 9 `workflow_run` triggers still fire it; same workflow id kept (no new ghost id) |

About 50 scheduled runs a day fewer, before counting the `workflow_run` chains each one starts.

## Found, intentionally NOT changed
- `merge-promotion-queue.yml` and `-v2.yml` are already dispatch-only (they hold no cron). Deleting them would be destructive, so they stay.
- Generated JSON pushed to master by `help-wanted-followup`, `help-wanted-status-refresh`, `cadence-lead-lag` and `ops-lane-matrix-sweep`. `apps/help-wanted-dashboard/matrix.html`, `help-wanted-dashboard-deploy.yml` and `tribute-vercel-prod.yml` read those files from master, so moving them to a side branch would break the dashboards. Next step after the `lane_events` ledger (#1277) has data: have the dashboards read the ledger, then stop the pushes.
- The inline re-scout in `help-wanted-execute.yml` could reuse the standalone scout's catalog artifact when it is under 3h old. That's a logic change, left for a follow-up.
