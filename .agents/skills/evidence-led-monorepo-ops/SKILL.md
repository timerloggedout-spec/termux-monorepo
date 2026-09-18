---
name: evidence-led-monorepo-ops
description: Continuous evidence-led admin ops on timerloggedout-spec/termux-monorepo. Load every admin session.
---

# Skill: evidence-led-monorepo-ops

**Owner:** Grok Administrator
**Canonical:** `.agents/skills/evidence-led-monorepo-ops/SKILL.md`
**Mirrors:** `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md`

## Posture

- Evidence over anecdote. Extract-only. Dual-gate before merge.
- Extra-red ≠ dual-gate. Behind-master dual-gate green ≠ auto-merge.
- **comment-storm is a FAILURE.** Do not force-merge #608.
- Do not MCP-write 35k workflow bodies (#606 abort).
- Identity: `Agent-Identity: Grok (Administrator)`.

## Production anchors (2026-09-18T23:15Z UTC)

| Item | State |
|------|-------|
| Master HEAD | `fb382c4893ff07f413b1834f633081081f6973d7` (docs-branch-index bot) |
| Landed | #609 help-wanted; #613 BIFROST-006; #614 Approxination |
| Isolated green candidate | #617 proposal registry MANIFEST gate (validate-registry green; ledger extra-red) |
| Observe | #618 Agentic-Agile docs; #605 Paper2Agent draft-adjacent |
| Extra-red HOLD | #608 ledger SyntaxError chicken-egg |
| ML HOLD dirty/behind | #601 #549 #432 — keep artifacts, extract later from live master |
| HOLD mega | #523 #527 #455 #48 #543 #545 #485 #500 |

GitHub MCP cannot comment/PR foreign repos (403). Use Actions OPERATOR / help-wanted-execute for upstream-pr.

BIUDL. Agent-Identity: Grok (Administrator)
