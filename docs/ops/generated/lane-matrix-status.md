# Lane matrix status (2026-10-25T05:07:17Z)

- Master: `85393d6cb3a5052b99aabeea01647c4dea78f405`
- Open PRs: **75** (approx from search)
- Oldest: #47 (ancient) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| CANDIDATE | ~20 (prior board) |
| EXTRACT | 1 |
| NEED_EVIDENCE | ~19 |
| SUPERSEDE | ~16 |

| Age bucket | Count |
|------------|------:|
| ancient | 11+ |
| fresh | majority recent |
| stale | 16+ |

## Tip lanes (EXTRACT / CANDIDATE / NEED_EVIDENCE first)

No dual-gate SUCCESS + mergeable PR observed on current tip `85393d6`.
Bases lag (examples: #1624 base 599556ef, #1645 base 683992ec, #1617 base 1bc51a06).

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

**Recon note:** Board restamped from live tip. Prior observation 2026-10-23T17:01:55Z on e60c1698 superseded. Future hourly runs use this baseline for candidate selection. Portability ratchet remains elevated (device_absolute_symlinks 34, tracked_backup_files 102, tracked_session_artifacts 423); next run targets one permanent reduction.
