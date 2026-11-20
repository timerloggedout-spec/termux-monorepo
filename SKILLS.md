# SKILLS.md — Collaborator entry

**Parity access for every collaborator and agent.** Skills live in-repo; this file is the short entry.

| Need | Path |
|------|------|
| **Full inventory + role load matrix** | [`docs/ops/SKILLS-INVENTORY.md`](docs/ops/SKILLS-INVENTORY.md) |
| **Nested capability discovery / MOAR** | [`.agents/skills/capability-discovery/SKILL.md`](.agents/skills/capability-discovery/SKILL.md) · [`docs/ops/CAPABILITY-DISCOVERY-AND-ACTIVATION.md`](docs/ops/CAPABILITY-DISCOVERY-AND-ACTIVATION.md) |\n| **Session plugin/tool catalogs** | [Plugin skills](docs/integrations/session-plugin-skill-catalog.json) · [Tool actions](docs/integrations/session-tool-action-catalog.json) · [Source registry](ops/capability_discovery/sources.json) |
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
| External contribute (help-wanted) | `.agents/skills/tribute-lane/SKILL.md` |
| Web operation -> API/CLI adapter (foundry) | `.agents/skills/web-adapter-foundry/SKILL.md` |
| Production WAIT → VALIDATE | `.github/skills/production-reconciliation/SKILL.md` |
| Siglary A2A notation (room↔room comms) | `.agents/skills/siglary-a2a/SKILL.md` |

Root `AGENTS.md` is **deprecated** (Linguist / Jules redirect only). Load `CLAUDE.md` first.

## Canonical and candidate surfaces

```text
.agents/skills/<name>/SKILL.md      # agent / collaborator loadable skills
.github/skills/<name>/SKILL.md      # CI / production reconciliation skills
.claude/skills/<name>/SKILL.md      # harness companion skills
docs/ops/skills/<name>/SKILL.md     # documentation mirrors; canonical path linked
vendor/**/SKILL.md, *.skill        # unverified candidate inputs; metadata-only until reviewed
ops/capability_discovery/           # taxonomy, source registry and record contract
docs/integrations/session-*.json    # dated, session-scoped plugin/tool discovery snapshots
docs/ops/SKILLS-INVENTORY.md         # curated SSOT navigator + role matrix
SKILLS.md                            # this file — short collaborator entry
```

Every skill directory must contain a `SKILL.md`. Inventory lists **all** of them so collaborators do not need private mirrors.

## Role quick-load

| Role | Load first |
|------|------------|
| Collaborator | `superpowers` → `adaptive-feedback-cycle` → dual-gate |
| Capability discovery | `capability-discovery` → `context-relationship-graph` → `find-skills` / `approxination-lane` |
| Admin / Grok | `evidence-led-monorepo-ops` + `adaptive-wait` + `ml-pipeline-ops` + `ml-command-center` |
| Admin / Grok | `evidence-led-monorepo-ops` + `adaptive-wait` |
| Admin / Termux | `termux-mcp-project-steward` + `adaptive-wait` |
| Wingman adaptation | `wingman-project-integration` + `context-relationship-graph` |
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


## Repo-wide Linguist / Siglary mandate

- Canonical contract: [`docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md`](docs/ops/REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md).
- Apply DO-first CAVEMAN-6 and `CHAT := STATE-CHANGE ∨ OVERSIGHT` to repository chat, skills, comments, commits, PRs, issues, and workflow directives.
- Keep OPERATORS / GLYPHS / CHORDS distinct; resolve chords in named domains; preserve technical literals and approval boundaries.
