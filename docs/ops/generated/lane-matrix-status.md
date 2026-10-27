# Lane matrix status (2026-10-27T18:10:00Z)

- Master: `ff90a60461b232c2390b1fa4293262c8c2ab6614`
- Open PRs: **~80** (observer budget; exact count from live list)
- Oldest: #47 (ancient)

| Lane | Count |
|------|------:|
| CANDIDATE | pending live classify |
| EXTRACT | 1 |
| NEED_EVIDENCE | pending |
| SUPERSEDE | pending |

| Age bucket | Count |
|------------|------:|
| ancient | ~12 |
| fresh | majority recent |
| mid | few |
| stale | some |

## Tip lanes (EXTRACT / CANDIDATE / NEED_EVIDENCE first)

| PR | Days | Lane | Reasons | Title |
|---:|-----:|------|---------|-------|
| #1852 | 0.0 | CANDIDATE | dual-gate SUCCESS on tip, mergeable_state=unstable | chore(recon): refresh pinned free-provider research |
| #1694 | 0.7 | NEED_EVIDENCE | base lagging tip, mergeable_state=unstable | fix(help-wanted): preserve historical audit coverage on partial refreshes |

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

Recon session 2026-10-27 18:10Z: current tip ff90a604. No dual-gate SUCCESS + mergeable_state=clean on live tip observed. #1852 dual-gate green (hygiene 40556611885 success, termux-smoke 40556616034 success) but unstable. Portability ratchet continues (recent .bak retirement). Free-tier lanes active per PARTNERS.md. Next: rebase lagging high-signal PRs onto tip for dual-gate reconfirm.
