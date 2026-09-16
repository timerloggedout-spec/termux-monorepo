# Skills Inventory (termux-monorepo)

**Version:** 2026-09-16 · **Last refreshed SHA:** `263c3dd9` (master moved after #557/`ff81cb6b`)  
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

## Cycle snapshot (2026-09-16T22:08Z)

- Master advanced to `263c3dd9` while #559 was in flight → dirty. Successor extract on this branch.
- Dual-gate last proven on `ff81cb6b` (smoke 35151853839, hygiene 35151853836).
- #549 extra-red HOLD (#175). Megas HOLD.
- Hist-eval 35155850816: shortened checkout SHA. This extract pins full SHA.
- Next extract: `repository-observatory.yml` same short-SHA class.

BIUDL. Agent-Identity: Grok (Administrator)
