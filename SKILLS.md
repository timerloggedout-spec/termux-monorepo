# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry.

| Need | Path |
|------|------|
| **Full inventory + role load matrix** | [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) |
| **Superpowers engineering methodology** | [`.agents/skills/superpowers/SKILL.md`](.agents/skills/superpowers/SKILL.md) |
| **Primary agent entry (BIUDL)** | [`CLAUDE.md`](CLAUDE.md) |
| **DO phrasing / framing guide** | [`docs/ops/DO-PHRASING-FRAMING-FRAMEWORK.md`](docs/ops/DO-PHRASING-FRAMING-FRAMEWORK.md) |
| Superpowers engineering workflow | `.agents/skills/superpowers/SKILL.md` |
| Adaptive wait / feedback | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| Admin ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| ML keep-alive | `.agents/skills/ml-pipeline-ops/SKILL.md` |
| ML command-center / repo SSOT | `.agents/skills/ml-command-center/SKILL.md` |
| Plan Canvas / annotated plan review | `.agents/skills/plan-canvas/SKILL.md` |
| Minesweeper peers | `.agents/skills/minesweeper-ops/SKILL.md` |
| Legacy #175 snapshot archive (do not load for operations) | `.agents/skills/operator-hub-175/SKILL.md` |
| ICM-CCTV projection | `.agents/skills/icm-cctv-ops/SKILL.md` |
| Admin / Termux stewardship | `.agents/skills/termux-mcp-project-steward/SKILL.md` |
| Wingman reference/adaptation | `.agents/skills/wingman-project-integration/SKILL.md` |
| Context relationship evidence | `.agents/skills/context-relationship-graph/SKILL.md` |
| LangGraph orchestration / BIUDL | `.agents/skills/langgraph-orchestration/SKILL.md` |
| External contribute (help-wanted) | `.agents/skills/tribute-lane/SKILL.md` |
| Web operation -> API/CLI adapter (foundry) | `.agents/skills/web-adapter-foundry/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |

Root `AGENTS.md` is **deprecated** (Linguist / Jules redirect only). Load `CLAUDE.md` first.

## Layout (both trees are first-class)

```text
.agents/skills/<name>/SKILL.md     # agent / collaborator loadable skills
.github/skills/<name>/SKILL.md     # CI / production reconciliation skills
docs/ops/SKILLS-INVENTORY.md        # SSOT navigator + role matrix
SKILLS.md                           # this file — short collaborator entry
```

Every skill directory must contain a `SKILL.md`. Inventory lists **all** of them so collaborators do not need private mirrors.

## Role quick-load

| Role | Load first |
|------|------------|
| Collaborator | `superpowers` → `adaptive-feedback-cycle` → dual-gate |
| Admin / Grok | `evidence-led-monorepo-ops` + `adaptive-wait` + `ml-pipeline-ops` + `ml-command-center` |
| Admin / Grok | `evidence-led-monorepo-ops` + `adaptive-wait` |
| Admin / Termux | `termux-mcp-project-steward` + `adaptive-wait` |
| Wingman adaptation | `wingman-project-integration` + `context-relationship-graph` |
| Graph orchestration | `langgraph-orchestration` + `adaptive-wait` + `ORCHESTRATION-CONTRACTS.md` |
| Oversight / external PR | `tribute-lane` |
| Evaluation / DOE | `multivariate-doe` + `blind-agent-evaluation` |
| Concurrent-agent collision | `minesweeper-ops` |

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
