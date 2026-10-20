# Skill Discovery Matrix — adaptive wait + evidence-led repo ops

**Discovery basis:** recursive Git tree of `master` at SHA `2327859f0b2432631177346e93492e67cdc7b3d2`, plus the session-scoped `.skill` attachments and supplied skill/loop references.

## Repository-native related skills

| Cluster | Skill | Path | Role |
|---|---|---|---|
| Wait/control | adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` | asynchronous cadence, stall detection, disjoint work, promotion boundary |
| Feedback | adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | continuous observation, historical evaluation, feed-forward learning |
| Evidence/admin | evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` | current-state reconstruction, provenance, admin closeout |
| Review | review-loop | `.agents/skills/review-loop/SKILL.md` | review ingestion, repeated validation, attribution |
| Relationships | context-relationship-graph | `.agents/skills/context-relationship-graph/SKILL.md` | verified/candidate relationship evidence |
| Reconciliation | production-reconciliation | `.github/skills/production-reconciliation/SKILL.md` | ref alignment and WAIT/VALIDATE/RE-FETCH |
| Measurement | action-effectiveness-ledger | `.github/skills/action-effectiveness-ledger/SKILL.md` | action-to-outcome measurement |
| Provenance | evidence-envelope | `.github/skills/evidence-envelope/SKILL.md` | normalized observation contract |
| Provenance | evidence-provenance | `.github/skills/evidence-provenance/SKILL.md` | shared evidence vocabulary |
| Orchestration | workflow-orchestration | `.github/skills/workflow-orchestration/SKILL.md` | modular Actions and retry discipline |
| Replay | evolutionary-replay | `.agents/skills/evolutionary-replay/SKILL.md` | bounded policy replay with preserved history |
| Evaluation | pr-evidence-evaluation | `.github/skills/pr-evidence-evaluation/SKILL.md` | current-SHA evidence quality |
| Evaluation | mvt-experiment | `.github/skills/mvt-experiment/SKILL.md` | controlled experiment lane |
| Discovery | find-skills | `.agents/skills/find-skills/SKILL.md` | external skill discovery/install guidance |

## Other repository-native skill files

The recursive tree contains 27 paths matching `**/SKILL.md` or `*.skill`: 25 `SKILL.md` files and 2 documentation mirrors. The repository tree currently contains **no tracked `.skill` archive**.

Agent-loadable paths also include: approxination-lane, blind-agent-evaluation, gemini-performance-psychology, github-pages-operator, help-wanted-lane, multivariate-doe, termux-monorepo, termux-monorepo-agentic-governance, and the Claude companion skill.

CI/production paths also include: github-pages-operator, forensic-recovery, pr-evidence-evaluation, and the evidence/provenance/action-effectiveness lanes listed above.

## Session-scoped `.skill` discoveries

Three uploaded `.skill` packages were inspected in this session:

- `termux-mcp-project-steward.skill` — constrained Termux/GitHub stewardship; read-only by default, isolated worktree discipline, explicit apply mode, and device-resource preflight.
- `context-relationship-graph.skill` — metadata-only evidence graph; exact-root querying, verified/candidate separation, and bounded historical collection.
- `context-relationship-graph_2.skill` — a second package with the same skill name and a newer-looking contract that adds timeline events, direct review/comment permalink resolution, and bounded file-review timelines.

These uploaded packages are **session evidence, not repository SSOT**. They should not be installed or copied into the repo without an explicit provenance/adoption decision.

## External candidate references supplied with this session

- **Loopy API / Loop Library Skill** — describes bounded Observe -> Choose -> Act -> Verify -> Record -> Repeat workflows, explicit terminal states, and run receipts. Candidate adaptation only; no repository adoption is implied.
- **Google Jules skill/workflow references** — supplied material describes `skills/<skill-name>/SKILL.md`, issue automation, PR review, test-driven development, and subagent-driven development. Candidate ecosystem evidence only; no external policy is imported automatically.

## Adoption rule

Use the smallest repository-native skill that fills the evidence gap. If an external skill is considered, record source, version/commit, scope, permissions, overlap, maintenance evidence, and the smallest safe adaptation before adoption.

## Current operating chain

adaptive-wait -> adaptive-feedback-cycle -> evidence-led-monorepo-ops -> review-loop -> context-relationship-graph -> production-reconciliation -> evidence envelope/provenance -> workflow/effectiveness measurement

Promotion remains downstream of current-SHA task-outcome verification and the repository's dual gates.

**Discovery note:** `SKILLS-INVENTORY.md` remains the repository navigator; this matrix is the focused discovery/audit companion for wait/evidence operations.

## Native orchestration treatment layer

| Cluster | Skill | Path | Role |
|---|---|---|---|
| Orchestration | orchestration-treatment-registry | `.agents/skills/orchestration-treatment-registry/SKILL.md` | normalize orchestration treatments and lifecycle receipts without parallel state machines |
| Orchestration contract | treatment schema | `docs/ops/ORCHESTRATION-TREATMENT.schema.json` | source/strategy/wait/retry/evidence/validation contract |
| Orchestration contract | receipt schema | `docs/ops/ORCHESTRATION-RECEIPT.schema.json` | shared execution-state/outcome/promotion projection |

External loop/framework material remains candidate pattern evidence until explicit schema mapping, bounded implementation, deterministic validation, evidence capture, and promotion.
