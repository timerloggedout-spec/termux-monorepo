# Skills Inventory (termux-monorepo)

**Version:** 2026-11-19 · live recursive-tree census at `f1840cf`
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)
**Collaborator short entry:** [`SKILLS.md`](../../SKILLS.md)

## Collaborator access (parity)

Canonical agent and automation skills live under `.agents/skills/` and `.github/skills/`. The `.claude/skills/` entry is a harness companion; `docs/ops/skills/` entries are documentation mirrors. Neither creates a competing policy source. Local agent mirrors (e.g. `.grok/skills/`) are convenience only.

| Entry | Purpose |
|-------|---------|
| [`SKILLS.md`](../../SKILLS.md) | Short collaborator pointer |
| This file | Full inventory + role matrix |
| [`CAPABILITY-ACTIVATION-MATRIX.md`](CAPABILITY-ACTIVATION-MATRIX.md) | Contextual skill/plugin/tool activation, full repository skill triggers, and session catalog links |
| Each `**/SKILL.md` | Executable skill body |

## Role load matrix

| Role | Load first | Then |
|------|------------|------|
| **Admin / Grok Administrator** | `superpowers` · `evidence-led-monorepo-ops` + `adaptive-wait` + **`stepie-stepwise-ops`** + `ml-pipeline-ops` | `review-loop` · `tribute-lane` · `github-pages-operator` · `icm-cctv-ops` |
| **Admin / Termux stewardship** | `termux-mcp-project-steward` + `adaptive-wait` | `context-relationship-graph` · `wingman-project-integration` |
| **Wingman adaptation** | `wingman-project-integration` | `adaptive-wait` · `context-relationship-graph` | `review-loop` · `tribute-lane` · `github-pages-operator` · `approxination-lane` |
| **Collaborator** | `superpowers` · `adaptive-feedback-cycle` | dual-gate · `find-skills` |
| **Oversight / external contrib** | `tribute-lane` | evidence-led + adaptive-wait · living status board |
| **Dashboard / Pages** | `github-pages-operator` | tribute-lane · deploy workflow |
| **Evaluation / DOE** | `design-of-experiments` + `multivariate-doe` + `blind-agent-evaluation` | `skill-evaluation` · `orchestration-treatment-registry` · `approxination-lane` · `mvt-experiment` |
| **Plugin / tool activation** | `CAPABILITY-ACTIVATION-MATRIX.md` | exact plugin skill URI · exact tool action · live schema · permission check |
| **CI / production recon** | `production-reconciliation` | `action-effectiveness-ledger` · `workflow-orchestration` |

## `.agents/skills/` (agent loadable; 32 skills)

| Skill | Path |
|-------|------|
| adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` |
| approxination-lane | `.agents/skills/approxination-lane/SKILL.md` |
| blind-agent-evaluation | `.agents/skills/blind-agent-evaluation/SKILL.md` |
| context-relationship-graph | `.agents/skills/context-relationship-graph/SKILL.md` |
| data-agent-kit | `.agents/skills/data-agent-kit/SKILL.md` |
| design-of-experiments | `.agents/skills/design-of-experiments/SKILL.md` |
| evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |
| evolutionary-replay | `.agents/skills/evolutionary-replay/SKILL.md` |
| find-skills | `.agents/skills/find-skills/SKILL.md` |
| gemini-performance-psychology | `.agents/skills/gemini-performance-psychology/SKILL.md` |
| github-pages-operator | `.agents/skills/github-pages-operator/SKILL.md` |
| icm-cctv-ops | `.agents/skills/icm-cctv-ops/SKILL.md` |
| minesweeper-ops | `.agents/skills/minesweeper-ops/SKILL.md` |
| ml-command-center | `.agents/skills/ml-command-center/SKILL.md` |
| ml-pipeline-ops | `.agents/skills/ml-pipeline-ops/SKILL.md` |
| ml-recon-08 | `.agents/skills/ml-recon-08/SKILL.md` |
| multivariate-doe | `.agents/skills/multivariate-doe/SKILL.md` |
| operator-hub-175 (legacy snapshot) | `.agents/skills/operator-hub-175/SKILL.md` |
| orchestration-treatment-registry | `.agents/skills/orchestration-treatment-registry/SKILL.md` |
| plan-canvas | `.agents/skills/plan-canvas/SKILL.md` |
| review-loop | `.agents/skills/review-loop/SKILL.md` |
| siglary-a2a | `.agents/skills/siglary-a2a/SKILL.md` |
| skill-evaluation | `.agents/skills/skill-evaluation/SKILL.md` |
| stepie-stepwise-ops | `.agents/skills/stepie-stepwise-ops/SKILL.md` |
| superpowers | `.agents/skills/superpowers/SKILL.md` |
| termux-mcp-project-steward | `.agents/skills/termux-mcp-project-steward/SKILL.md` |
| termux-monorepo-agentic-governance | `.agents/skills/termux-monorepo-agentic-governance/SKILL.md` |
| termux-monorepo-conventions | `.agents/skills/termux-monorepo/SKILL.md` |
| tribute-lane | `.agents/skills/tribute-lane/SKILL.md` |
| web-adapter-foundry | `.agents/skills/web-adapter-foundry/SKILL.md` |
| wingman-project-integration | `.agents/skills/wingman-project-integration/SKILL.md`

## `.claude/skills/` (harness companion; 1 skill)

| Skill | Path |
|-------|------|
| termux-monorepo-conventions | `.claude/skills/termux-monorepo/SKILL.md` |

## `.github/skills/` (CI / production; 10 skills)

| Skill | Path |
|-------|------|
| action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` |
| evidence-envelope | `.github/skills/evidence-envelope/SKILL.md` |
| evidence-provenance | `.github/skills/evidence-provenance/SKILL.md` |
| forensic-recovery | `.github/skills/forensic-recovery/SKILL.md` |
| github-pages-operator | `.github/skills/github-pages-operator/SKILL.md` |
| ml-command-center | `.github/skills/ml-command-center/SKILL.md` |
| mvt-experiment | `.github/skills/mvt-experiment/SKILL.md` |
| pr-evidence-evaluation | `.github/skills/pr-evidence-evaluation/SKILL.md` |
| production-reconciliation | `.github/skills/production-reconciliation/SKILL.md` |
| workflow-orchestration | `.github/skills/workflow-orchestration/SKILL.md` |

## `docs/ops/skills/` (documentation mirrors; 2 paths)

| Mirror | Canonical source |
|-------|------|
| `docs/ops/skills/adaptive-wait/SKILL.md` | `.agents/skills/adaptive-wait/SKILL.md` |
| `docs/ops/skills/evidence-led-monorepo-ops/SKILL.md` | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` |

**Census:** 45 `SKILL.md` paths across four surfaces; zero tracked `.skill` archives at baseline `f1840cf`. Use the activation matrix for triggers and load order.

## Help-wanted companion docs

| Doc | Role |
|-----|------|
| [`TRIBUTE-LANE.md`](TRIBUTE-LANE.md) | Production execute |
| [`TRIBUTE-PARALLEL.md`](TRIBUTE-PARALLEL.md) | Roster + limits |
| [`TRIBUTE-STATUS.md`](TRIBUTE-STATUS.md) | Living human-review surface |
| [`TRIBUTE-DASHBOARD.md`](TRIBUTE-DASHBOARD.md) | Live surfaces + deploy |
| [`TRIBUTE-EVIDENCE-FEED.md`](TRIBUTE-EVIDENCE-FEED.md) | Receipts → evaluation |

## Cycle snapshot (2026-09-21 15:07 PDT)

- New skill: **stepie-stepwise-ops** — Stepie as production planning surface (goal 2087).
- Preferred extract: #713 slim ML pipelines; #682 remains EXTRACT/WAIT.
- Dual-gate contract unchanged; Vercel rate-limit non-gate.
- Credential inventory: issue **#184** (notes only; no secret values).

Agent-Identity: Grok (Administrator)


## Adaptive-wait + evidence-led cluster

- adaptive-wait — evidence-driven asynchronous cadence, stall detection, disjoint work, terminal states.
- evidence-led-monorepo-ops — current-SHA reconstruction, evidence hierarchy, provenance, mutation/promotion discipline.
- context-relationship-graph — exact-root metadata-only relationship evidence; verified/candidate separation.
- review-loop — review ingestion and attribution.
- production-reconciliation — ref/base reconciliation.
- action-effectiveness-ledger — action-to-outcome measurement.
- evidence-envelope + evidence-provenance — normalized observation identity.
- workflow-orchestration — modular Actions and retry/stale-event discipline.

See `docs/ops/SKILL-DISCOVERY-MATRIX.md` for focused discovery and session-scoped .skill provenance.


## Native orchestration contracts

- orchestration-treatment-registry — comparable orchestration-pattern registry spanning TUI, CLI, GitHub, Devin, MCP, and agent surfaces.
- Native schemas: `docs/ops/ORCHESTRATION-TREATMENT.schema.json` and `docs/ops/ORCHESTRATION-RECEIPT.schema.json`.
- Architecture: `docs/ops/ORCHESTRATION-CONTRACTS.md`.

The treatment registry composes existing evidence, wait, relationship, and workflow contracts; it does not replace them.


## Session 2026-10-11 01:20 UTC

- Master tip: `1bba84f2ac3ef1ecdd6fc628ddcf90ae6bfc02f9`
- Dual-gate PASS on `9b40e8de8a70a46d71e7af668ecd51530c049657`: repo-gate 38098247754 + termux-smoke 38098247777
- v3 schedule 38101050389 SUCCESS
- No new master filename-named workflow failures
- #184 names-only. Issue #175 is closed/historical; do not use it for operational state or pulses. #903 HOLD
- Ghost on disabled workflow id remains non-actionable
- Open PRs monitored; promote only on current-SHA dual-gate + mergeable

Agent-Identity: Grok (Administrator)


## Superpowers — engineering methodology

| Skill | Path | Load when |
|---|---|---|
| **superpowers** | `.agents/skills/superpowers/SKILL.md` | Feature work, bug fixes, refactors, design, TDD, debugging, review, verification, and branch finishing |

The repository-local skill maps the upstream [obra/superpowers](https://github.com/obra/superpowers) methodology to this repository's proposal lifecycle, ICM routing, permissions, dual gates, and adaptive WAIT. It is a repository integration/bootstrap guide; the full upstream skill library and harness hooks should be installed separately for each agent harness. See [the dated design](../superpowers/specs/2026-11-02-integration-intelligence-design.md) and [implementation plan](../superpowers/plans/2026-11-02-integration-intelligence.md).

## Integration Intelligence

- Human-readable catalog: `docs/integrations/INTEGRATION-REGISTRY.md`
- Machine-readable registry: `docs/integrations/registry.json`
- Adapter contract: `docs/integrations/ADAPTER-CONTRACT.md`
- Normalized event schema: `docs/integrations/schemas/integration-event.schema.json`

Session-local tool availability is not proof of repository adapter implementation or production access.


## Linguist / Siglary mandate

- Canonical authoring contract: [`REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md`](REPO-WIDE-LINGUIST-SYGLARY-MANDATE.md).
- Canonical notation register: [`CAVEMAN-MICRO-DENSE-V2.md`](../proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md).
- Standard and enforcement profile: [`SIGLARY-STANDARD.md`](../proposals/active/notation-sets/SIGLARY-STANDARD.md).
- Apply DO-first CAVEMAN-6 and class-correct Siglary notation across repository-authored instructions and skills.
