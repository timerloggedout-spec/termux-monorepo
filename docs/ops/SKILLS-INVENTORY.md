# Skills Inventory (termux-monorepo)

**Version:** 2026-09-17 · **Last refreshed SHA:** `d1ee07e8` (#563)  
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)

## Role load matrix

| Role | Load first | Then |
|------|------------|------|
| **Admin / Grok Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` | `review-loop` |
| **Collaborator** | `adaptive-feedback-cycle` | dual-gate |

## Active ops skills

| Skill | Path |
|-------|------|
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` |

## Cycle snapshot (2026-09-17T02:08Z)

- Master HEAD `d1ee07e8` (#563 linguist NSE-020; #561 RL-19 landed immediately prior).
- Dual-gate: repo-gate 35169094011 + termux smoke 35169093992 success on HEAD.
- #549 extra-red HOLD (#175 ML). Megas HOLD (#523 #527 #142 #455 #48 #543 #545).
- Vercel rate-limit extra-red on #545 is not a dual-gate.
- Historical-eval / swe-reference-evaluation fail and mermaid docs-refresh are not dual-gates.
- Comment-storm-skip on Jules/Gemini/ECC `issue_comment` listeners.

BIUDL. Agent-Identity: Grok (Administrator)
