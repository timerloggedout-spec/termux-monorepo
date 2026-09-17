# Skills Inventory (termux-monorepo)

**Version:** 2026-09-17 · **Last refreshed SHA:** `ebdd4c0f` (#568)
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

## Cycle snapshot (2026-09-17T03:12Z)

- Master HEAD `ebdd4c0f` (#568 skill anchors after #567 official GitHub MCP Docker lane).
- Dual-gate: repo-gate 35177187396 + termux smoke 35177187383 success on HEAD.
- #549 extra-red HOLD (#175 ML). Megas HOLD (#523 #527 #142 #455 #48 #543 #545).
- Vercel rate-limit extra-red on #545/#549 is not a dual-gate.
- Historical-eval / swe-reference-evaluation fail, mermaid docs-refresh, agent-jules-on-issues and actions-run-watcher startup_failure are not dual-gates.
- Comment-storm-skip on Jules/Gemini/ECC `issue_comment` listeners.

BIUDL. Agent-Identity: Grok (Administrator)
