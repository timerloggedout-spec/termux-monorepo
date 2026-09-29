# LANE-MATRIX (policy SSOT)

This file is **durable policy**, not a live dashboard.

**Open the live board:** [lane-matrix-status.md](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/lane-matrix-status.md) · [JSON](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/lane-matrix-status.json) · [sweep workflow](https://github.com/timerloggedout-spec/termux-monorepo/actions/workflows/ops-lane-matrix-sweep.yml)

Live inventory on disk: [`docs/ops/generated/lane-matrix-status.md`](generated/lane-matrix-status.md)  
Writer: `.github/workflows/ops-lane-matrix-sweep.yml` + `scripts/ops/lane_matrix_sweep.py`  
Priority issue: #175 is a **hub**, not a comment stream.  
Credentials: #184 names-only.

Do **not** open `ops/session-lane-matrix-*` PRs to restamp this file.  
Do **not** post a recon comment on #175 every session.  
Git history is a ledger. The generated artifact is the board. **Open that artifact.** Do not keep a pulse PR open to “hold the matrix open.”

## What belongs where

| Artifact | Role | How it changes |
|----------|------|----------------|
| This file | Dual-gate, mega-merge, Vercel, dirty-block rules | Rare policy PR |
| `docs/ops/generated/lane-matrix-status.*` | Open-PR inventory + lane counts | Sweep commits to master (observer) |
| Issue #175 | Durable operator intent | Edit the issue body when intent changes; no pulse comments |
| Product PRs | Code / extracts / rebases | Dual-gate then promote |
| Session chat | Human recon | Stays in chat; not a merge candidate |

## Dual-gate contract (promote authority)

1. `hygiene + portability gate` / `repo gate` SUCCESS on **this** SHA
2. `agentic termux smoke` / `termux smoke` SUCCESS on **this** SHA
3. Vercel rate-limits are **non-gate** (#772)
4. Copilot / CodeRabbit / Qodo / Devin = advisory only
5. Age, file count, and comment volume are context only
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
| SUPERSEDE | Session pulse, bot-only, or ancient no-auto |

HOLD / WAIT / OBSERVE are **invalid parking**. Gate outputs remain ALLOW | BLOCK | NEED_EVIDENCE.

## Session recon is not a PR

A timestamped rewrite of who is dirty / superseded is stale before CI finishes.

Agents must:

- **Read** generated status + live GitHub API for current SHA
- **Write** product or durable policy only
- **Close** leftover `ops(session): … LANE-MATRIX` PRs as not-planned / superseded
- **Never** treat HOLD / OBSERVE / WAIT as idle parking when product work exists

Sweep classifies session-record titles as **SUPERSEDE**, not dual-gate WAIT.

## Known durable lanes (update only when the fact is durable)

- #48 remainder EXTRACT; core already on master via #805. Dirty vs `master-staging` is a hard block. Do not retarget.
- #809 / #806 need rebase onto live `master` before any promote attempt.
- #69 superseded by #784. #810 / #812 are historical pulses.
- #772 documents Vercel mergeable_state noise.
- #814 landed the board-vs-ledger policy.
- #184 names-only credential inventory. Do not paste secret values.

Agent-Identity: Grok (Administrator)
