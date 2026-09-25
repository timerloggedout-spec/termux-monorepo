# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry.

| Need | Path |
|------|------|
| **Full inventory + role load matrix** | [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) |
| Primary agent entry | [`CLAUDE.md`](CLAUDE.md) |
| Adaptive wait / feedback | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| Admin ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| External contribute (help-wanted) | `.agents/skills/help-wanted-lane/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |

## Layout (both trees are first-class)

```text
.agents/skills/<name>/SKILL.md     # agent / collaborator loadable skills
.github/skills/<name>/SKILL.md      # CI / production reconciliation skills
docs/ops/SKILLS-INVENTORY.md        # SSOT navigator + role matrix
SKILLS.md                           # this file — short collaborator entry
```

Every skill directory must contain a `SKILL.md`. Inventory lists **all** of them so collaborators do not need private mirrors.

## Role quick-load

| Role | Load first |
|------|------------|
| Collaborator | `adaptive-feedback-cycle` → dual-gate |
| Admin / Grok | `evidence-led-monorepo-ops` + `adaptive-wait` |
| Oversight / external PR | `help-wanted-lane` |
| Evaluation / DOE | `multivariate-doe` + `blind-agent-evaluation` |

Do not keep skill policy only in local `.grok/skills/` mirrors — **master is SSOT**.

BIUDL · Agent-Identity: Grok (Administrator)
