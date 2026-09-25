# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry.

| Need | Path |
|------|------|
| **Full inventory + role load matrix** | [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) |
| **Primary agent entry (BIUDL)** | [`CLAUDE.md`](CLAUDE.md) |
| Adaptive wait / feedback | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| Admin ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| Admin / Termux stewardship | `.agents/skills/termux-mcp-project-steward/SKILL.md` |
| Wingman reference/adaptation | `.agents/skills/wingman-project-integration/SKILL.md` |
| Context relationship evidence | `.agents/skills/context-relationship-graph/SKILL.md` |
| External contribute (help-wanted) | `.agents/skills/help-wanted-lane/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |

Root `AGENTS.md` is **deprecated** (Linguist / Jules redirect only). Load `CLAUDE.md` first.

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
| Admin / Termux | `termux-mcp-project-steward` + `adaptive-wait` |
| Wingman adaptation | `wingman-project-integration` + `context-relationship-graph` |
| Oversight / external PR | `help-wanted-lane` |
| Evaluation / DOE | `multivariate-doe` + `blind-agent-evaluation` |

Do not keep skill policy only in local `.grok/skills/` mirrors — **master is SSOT**.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**  
Fully Continuous Automated Development Evaluation Environment.  
AVOID HITL YOLO MODE YEET AUTOAPPROVE.  
Agent-Identity: Grok (Administrator)

## Shared wait-loop invariant

```text
RECON → PLAN / MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT
```

Do not treat queued/in-progress as success. Preserve provenance and keep promotion separate from execution and validation.
