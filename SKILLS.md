# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry.

| Need | Path |
|---|---|
| **Primary agent entry (BIUDL)** | [`CLAUDE.md`](CLAUDE.md) |
| Adaptive wait / feedback | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| Admin / Termux stewardship | `.agents/skills/termux-mcp-project-steward/SKILL.md` |
| Wingman reference/adaptation | `.agents/skills/wingman-project-integration/SKILL.md` |
| Context relationship evidence | `.agents/skills/context-relationship-graph/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |

## Layout

```text
.agents/skills/<name>/SKILL.md
.github/skills/<name>/SKILL.md
docs/ops/SKILLS-INVENTORY.md
SKILLS.md
```

Every skill directory must contain a `SKILL.md`. Inventory lists the loadable skills.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**

Shared operational invariant:

```text
RECON → PLAN / MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT
```

Do not treat queued/in-progress as success. Preserve provenance and keep promotion separate from execution and validation.
