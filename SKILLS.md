# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry. Apply [the DO-statement mandate](docs/ops/DO-STATEMENT-MANDATE.md) to new skill content, comments, commits, PRs, and chat relays.

| Need | Path |
|------|------|
| **Full inventory + role load matrix** | [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) |
| **Superpowers engineering methodology** | [`.agents/skills/superpowers/SKILL.md`](.agents/skills/superpowers/SKILL.md) |
| **Primary agent entry (BIUDL)** | [`CLAUDE.md`](CLAUDE.md) |
| **DO-statement mandate** | [`docs/ops/DO-STATEMENT-MANDATE.md`](docs/ops/DO-STATEMENT-MANDATE.md) |
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
| Agent Readability / Agent Ready | `.agents/skills/agent-readability/SKILL.md` |
| Bounded feedback loops / Loopy API | `.agents/skills/loopy-api-loop-library/SKILL.md` |
| Jules GitHub development | `.agents/skills/jules-github-development/SKILL.md` |
| Wingman reference/adaptation | `.agents/skills/wingman-project-integration/SKILL.md` |
| Context relationship evidence | `.agents/skills/context-relationship-graph/SKILL.md` |
| External contribute (help-wanted) | `.agents/skills/tribute-lane/SKILL.md` |
| Web operation -> API/CLI adapter (foundry) | `.agents/skills/web-adapter-foundry/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |
| Siglary A2A notation (room↔room comms) | `.agents/skills/siglary-a2a/SKILL.md` |

Root `AGENTS.md` routes through `moniker.md` to `CLAUDE.md`. Load the moniker route, then this primary governance entry.

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
| Oversight / external PR | `tribute-lane` |
| Evaluation / DOE | `multivariate-doe` + `blind-agent-evaluation` |
| Concurrent-agent collision | `minesweeper-ops` |

Keep skill policy in the in-repository SSOT and synchronize local `.grok/skills/` convenience mirrors.

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**
Fully Continuous Automated Development Evaluation Environment.
Route consequential actions through their named authorization and verification gates.
Agent-Identity: Grok (Administrator)

## Shared wait-loop invariant

```text
RECON → PLAN / MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT
```

Keep queued/in-progress in WAIT until terminal evidence arrives. Preserve provenance and separate promotion from execution and validation.
