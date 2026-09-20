# LANE-MATRIX (living SSOT)

**Session:** 2026-09-20 15:17 PDT  
**Agent-Identity:** Grok (Administrator)  
**Live master:** `fbfdb5a0` — `ops(help-wanted): live status refresh 2026-09-20T21:29Z`  
**Prior skill snapshot:** `0570db31` (superseded on tip by Actions help-wanted refresh).

Rewrite this file every admin session. Copilot is optional peer, not a promote gate. Size ≠ quality. Promote only when dual-gate is green (`repo_gate` + `termux_smoke`). `mergeable_state=unstable` is WAIT, not merge.

## Open PR lanes (tip-first)

| PR | Title | Base SHA vs master | Lane | Why |
|----|-------|--------------------|------|-----|
| #689 | Jules audit SSOT + merged-branch ledger | tip-aligned `fbfdb5a0` | WAIT | unstable; 2-file docs; checks still settling |
| #688 | refTemplates + Jogyo + recovery | tip-aligned `fbfdb5a0` | WAIT | hygiene/portability + CodeQL + smoke SUCCESS; mergeable still unstable |
| #687 | living LANE-MATRIX + Copilot demote | stale `0570db31` | HOLD-REBASE | superseded by this session file; rebase or close after #690 lands |
| #686 | skills record 13:00 PDT | stale `0570db31` | WAIT | session-record only |
| #685 | arrhythmic-zero-token-search | stale `0570db31` | OBSERVE | proposal surface |
| #684 | unify Actions cadence | dirty stale `502583d2` | HOLD | cadence rewrite; do not auto-merge |
| #682 | ML keep-alive DAG (#175) | stale `0570db31` | WAIT / EXTRACT | 130 files; keep ML; rebase onto `fbfdb5a0` before promote |
| #680 | Bolt live_catalog_feed | dirty | OBSERVE | Jules bolt |
| #679 | Sentinel telemetry symlink | dirty | OBSERVE | security-shaped; do not squash blindly |
| #673 / #672 | skills + help-wanted dashboard | stale `9538f4a3` | HOLD | rebase debt |
| #671 | BIFROST-006 codespace | stale | OBSERVE | docs |
| #649 | Jules consolidate audit | dirty stale | OBSERVE | minesweeper vs #689 |
| #648 / #647 / #641 | skills + graph | dirty stale | HOLD | do not merge stale session records |
| #639 | mermaid-cli no-sandbox | stale | OBSERVE | CI fix |
| #630 | Jules dashboard rich UI | dirty 89-file class | EXTRACT | minesweeper |
| #620 | Linguist CedrLang | stale | OBSERVE | |
| #619 / #616 / #607 | old session records | stale | HOLD | close after living matrix lands |
| #618 | Agentic-Agile docs | stale | OBSERVE | |
| #617 | proposal registry gate | stale | OBSERVE | |
| #608 | ledger SyntaxError | stale | OBSERVE | |
| #605 | Paper2Agent | stale | OBSERVE | |
| #601 / #432 family | ML wholesale | EXTRACT | keep extract-only; #682 is the keep-alive |

## Dual-gate contract

1. `repo_gate` SUCCESS
2. `termux_smoke` SUCCESS
3. No required-check failure on head SHA
4. Copilot / CodeRabbit / Qodo / Devin = advisory
5. Vercel / GitLab / Mintlify = non-gate

## Issue #175 priority this session

- Keep ML pipeline extract path (#682) alive; do not drop tests or DAG CLI.
- Land living LANE-MATRIX on master (this file) so WAIT cycles have an SSOT on tip.
- Do not merge mega PRs solely because file count is high.
- Rebase #682 onto `fbfdb5a0` next cycle if dual-gate stays green after rebase.
- Foreign-repo help-wanted eval remains a free-quota cadence, not a merge gate.

## Peer routing

See `docs/ops/PEER-REVIEW-ROUTING.md` when present. Copilot is optional. Human / OPERATOR merge decision uses dual-gate only.

## Next cycle (adaptive-wait disjoint work)

- Comment #175 with this matrix snapshot.
- Watch #688/#689 required checks; promote only if mergeable leaves `unstable`.
- Close superseded session-record PRs after this PR merges.
- Leave #684 HOLD until cadence diff is reviewed against live workflows on `fbfdb5a0`.
