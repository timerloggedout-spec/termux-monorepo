# Skills Inventory (termux-monorepo)

**Version:** 2026-09-17 · **Last refreshed SHA:** `f6009939` (#564)  
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

## Cycle snapshot (2026-09-17T00:40Z)

- Master HEAD `f6009939` (#564 skill anchors onto 820ecd2f).
- Dual-gate: repo-gate 35165001073 + termux smoke 35165001074 success on HEAD.
- #549 extra-red HOLD (#175). Megas HOLD. #561 generated-catalog HOLD. #563 Jules HOLD (Vercel rate-limit extra-red).
- Historical-eval fail and mermaid docs-refresh are not dual-gates.
- Comment-storm-skip on Jules/Gemini/ECC `issue_comment` listeners.

BIUDL. Agent-Identity: Grok (Administrator)
