# Skills Inventory (termux-monorepo)

**Version:** 2026-09-17 · **Last refreshed SHA:** `ebb9bc1a`
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

## Cycle snapshot (2026-09-17T04:05Z)

- Master HEAD `ebb9bc1a` (skill-anchor refresh after #568; dual-gate verified on this SHA).
- Dual-gate: repo-gate 35177365258 + termux smoke 35177365245 success on HEAD.
- #549 extra-red HOLD (#175 ML, mergeable_state=dirty). Sibling #432 HOLD.
- Megas HOLD (#523 #527 #142 #455 #48 #543 #545).
- Vercel rate-limit extra-red on #545/#549 is not a dual-gate.
- Historical-eval / swe-reference-evaluation fail, mermaid docs-refresh, agent-jules-on-issues and actions-run-watcher startup_failure are not dual-gates.
- Comment-storm-skip on Jules/Gemini/ECC `issue_comment` listeners.

BIUDL. Agent-Identity: Grok (Administrator)
