# LANE-MATRIX (living SSOT)

**Session:** 2026-09-20 17:20 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master at session start:** `3bf343c7` — help-wanted status refresh 00:12Z  
**Promote this cycle:** #692 squash `f346f1c2` (decision_engines Laya + live commit-slice)

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote when dual-gate is green. Vercel rate-limit is non-gate (proven on #690 and #692).

## Open PR lanes (tip-first)

| PR | Title | Base vs master | Lane | Why |
|----|-------|----------------|------|-----|
| #692 | Laya decision_engines + commit-slice | MERGED `f346f1c2` | DONE | dual-gate SUCCESS; Vercel non-gate squash |
| #691 | session 16:05 PDT | CLOSED/MERGED | DONE | LANE-MATRIX after #690 |
| #689 | Jules audit SSOT + ledger | CLOSED | DONE | landed earlier this session family |
| #688 | refTemplates + Jogyo | CLOSED/MERGED | DONE | structure #692 built on |
| #690 | living LANE-MATRIX 15:17 | MERGED | DONE | prior matrix land |
| #685 | arrhythmic-zero-token-search | stale `0570db31` | OBSERVE | proposal |
| #684 | unify Actions cadence | dirty stale | HOLD | do not auto-merge |
| #682 | ML keep-alive DAG (#175) | stale `0570db31` | WAIT / EXTRACT | keep ML tests+DAG; rebase onto live master |
| #680 | Bolt live_catalog_feed | dirty | OBSERVE | Jules |
| #693 | Linguist CedrLang alloc | dirty vs tip | OBSERVE | Jules |
| #630 | Jules dashboard rich UI | dirty 89-file | EXTRACT | minesweeper |
| #601 / #432 / #549 | ML wholesale family | EXTRACT | #682 is keep-alive |

## Dual-gate contract

1. `repo_gate` / hygiene+portability SUCCESS
2. `termux_smoke` SUCCESS
3. Vercel rate-limits are non-gate
4. Copilot / CodeRabbit / Qodo / Devin = advisory
5. GitLab / Mintlify = non-gate
6. `validate-pull-request` failure is not dual-gate if caused by Vercel/status aggregation

## Issue #175 priority this session

- Keep ML extract path (#682). Do not drop tests or DAG CLI.
- #692 landed Laya as System-1 engine + live GitHub commit-slice in refTemplates eval.
- Do not merge mega PRs for file count.
- Rebase #682 onto live master before promote.
- Help-wanted eval is free-quota cadence, not a merge gate.

## Next cycle

- Rebase #682 ML keep-alive onto post-#692 master.
- Leave #684 HOLD.
- OBSERVE #685/#680/#693; EXTRACT only from #630 minesweeper.
