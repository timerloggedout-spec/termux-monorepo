# LANE-MATRIX (PR-disposition policy SSOT)

This file is durable policy for the **open pull-request disposition view**. It is
not the global lane×project state store and it is not an operator-intent issue.

**Live PR board:** [lane-matrix-status.md](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/lane-matrix-status.md) · [JSON](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/lane-matrix-status.json) · [event workflow](https://github.com/timerloggedout-spec/termux-monorepo/actions/workflows/ops-lane-matrix-sweep.yml)

**Cross-domain lane×project SSOT:** [REPO-TRACKING](REPO-TRACKING.md), canonical feed
`ops/tracking/tracking.json`, generated human board `ops/tracking/tracking.md`,
and dashboard projection `apps/tribute-dashboard/data/tracking-feed.json`.
Project/task lifecycle remains in its domain records, including
`docs/agentic/dependency-phases.json` and `docs/agentic/phase-approvals.json`.
The append-only `ops/lane-events` ledger is execution evidence, not project state.

Live PR disposition writer: `.github/workflows/ops-lane-matrix-sweep.yml` +
`scripts/ops/lane_matrix_sweep.py`. It is triggered by pull-request lifecycle events and master pushes to the
policy/classifier; there is no cron, ten-minute poll, six-hour sweep, manual
dispatch, or comment heartbeat. Bursts are coalesced by concurrency cancellation; each
materialization reads the current open-PR set and writes only when its generated
artifact changes.

**Issue #175 is retired from operational authority.** It is a preserved historical
priority snapshot, not a live hub, database, dispatch target, or source of truth.
Human decisions belong in Desk.html or the specific GitHub Issue/PR that owns the
decision. No issue is used as a generic state container.

Do **not** open `ops/session-lane-matrix-*` PRs to restamp this file.
Git history is the audit ledger. The generated PR board is a derived view.

## Dual-gate contract (promote authority)

1. `hygiene + portability gate` / `repo gate` SUCCESS on **this** SHA
2. `agentic termux smoke` / `termux smoke` SUCCESS on **this** SHA
3. Vercel rate-limits are **non-gate** (#772)
4. Copilot / CodeRabbit / Qodo / Devin = advisory only
5. Age, file count, and comment volume are context only; age never changes lane state
6. Mega-merge is allowed when dual-gate SUCCESS **and** mergeable on the candidate SHA
7. CodeRabbit ~100-file limit is advisory review capacity, not a promote ban
8. `mergeable_state=dirty` or a merge conflict **blocks** promote until rebase/re-extract
9. Dual-gate SUCCESS on an older head does not authorize a newer SHA
10. Combined commit status is not dual-gate; bind the named jobs

## Lane vocabulary (sweep v2)

| Lane | Meaning |
|------|---------|
| EXTRACT | Re-cut onto live master; do not wholesale-merge |
| CANDIDATE | On master; dual-gate may promote if green |
| NEED_EVIDENCE | Wrong-base / draft / dirty — missing rebase or checks |
| SUPERSEDE | Session-record artifact, bot-only artifact, or explicitly superseded item |

HOLD / WAIT / OBSERVE are **invalid parking**. Gate outputs remain ALLOW | BLOCK | NEED_EVIDENCE.

## Session recon is not a PR

A timestamped rewrite of who is dirty / superseded is stale before CI finishes.

Agents must:

- **Read** generated status + live GitHub API for current SHA
- **Write** product or durable policy only
- **Close** leftover `ops(session): … LANE-MATRIX` PRs as not-planned / superseded
- **Never** treat HOLD / OBSERVE / WAIT as idle parking when product work exists

Event-driven classifier marks session-record titles **SUPERSEDE**. Age buckets are snapshot metadata only; crossing an age threshold never changes disposition.

## Known durable lanes (update only when the fact is durable)

- #48 remainder EXTRACT; core already on master via #805. Dirty vs `master-staging` is a hard block. Do not retarget.
- #809 / #806 need rebase onto live `master` before any promote attempt.
- #69 superseded by #784. #810 / #812 are historical pulses.
- #772 documents Vercel mergeable_state noise.
- #814 landed the board-vs-ledger policy.
- #184 names-only credential inventory. Do not paste secret values.

Agent-Identity: Grok (Administrator)
