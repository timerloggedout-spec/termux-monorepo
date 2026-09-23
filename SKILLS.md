# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry.

| Need | Path |
|------|------|
| **Full inventory + role load matrix** | [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) |
| **Primary agent entry (BIUDL)** | [`CLAUDE.md`](CLAUDE.md) |
| Adaptive wait / feedback | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| Admin ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| External contribute (help-wanted) | `.agents/skills/help-wanted-lane/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |
| **Plugin / connector parity** | `.agents/skills/plugin-connector-parity/SKILL.md` |
| **Bounded Loopy workflows** | `.agents/skills/loopy-api-loop-library/SKILL.md` |

Root `AGENTS.md` is **deprecated** (Linguist / Jules redirect only). Load `CLAUDE.md` first.

## Layout (both trees are first-class)

```text
.agents/skills/<name>/SKILL.md     # agent / collaborator loadable skills
.github/skills/<name>/SKILL.md     # CI / production reconciliation skills
docs/ops/SKILLS-INVENTORY.md        # SSOT navigator + role matrix
SKILLS.md                           # this file — short collaborator entry
```

Every skill directory must contain a `SKILL.md`. Inventory lists all of them so collaborators do not need private mirrors.

## Role quick-load

| Role | Load first |
|------|------------|
| Collaborator | `adaptive-feedback-cycle` → dual-gate |
| Admin / Grok | `evidence-led-monorepo-ops` + `adaptive-wait` |
| Oversight / external PR | `help-wanted-lane` |
| Evaluation / DOE | `multivariate-doe` + `blind-agent-evaluation` |
| **External integration work** | `plugin-connector-parity` → existing owner skill |

## Connector parity

Live external-tool inventory and production priority are documented in:
- `docs/ops/PLUGIN-CONNECTOR-CAPABILITY-MATRIX.md`
- `docs/ops/PLUGIN-INTEGRATION-PRIORITY.md`
- `.github/connectors/integrations.yaml`

Do not keep connector policy only in a local mirror; **master is SSOT**.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**
Fully Continuous Automated Development Evaluation Environment.
**AVOID HITL YOLO MODE YEET AUTOAPPROVE.**
Agent-Identity: Grok (Administrator)


## Plugin Connector Surface

For the complete live connector handoff registry, use `docs/ops/PLUGIN-CONNECTOR-SURFACE.md` and its machine-readable companion `.github/connectors/runtime-surface.json`. The primary coordination role is the **Plugin Connector Steward**; repository integration planning is anchored in Linear **TER-15**. Do not treat connector exposure as authorization or integration: promote only through the recorded capability-state model and validation evidence.
