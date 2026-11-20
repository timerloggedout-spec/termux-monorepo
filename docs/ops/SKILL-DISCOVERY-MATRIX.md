# Skill Discovery Matrix — adaptive wait + evidence-led repo ops

**Discovery basis:** recursive Git tree of `master` at baseline SHA `f1840cf0488bb48bbbf7df1b62d15808d58b5dfe`, plus the session-scoped skill attachments, plugin skill catalog, and tool-action catalog captured 2026-11-19. See [Contextual Capability Activation Matrix](CAPABILITY-ACTIVATION-MATRIX.md) for the complete activation route.

## Repository-native related skills

| Cluster | Skill | Path | Role |
|---|---|---|---|
| Wait/control | adaptive-wait | `.agents/skills/adaptive-wait/SKILL.md` | asynchronous cadence, stall detection, disjoint work, promotion boundary |
| Feedback | adaptive-feedback-cycle | `.agents/skills/adaptive-feedback-cycle/SKILL.md` | continuous observation, historical evaluation, feed-forward learning |
| Evidence/admin | evidence-led-monorepo-ops | `.agents/skills/evidence-led-monorepo-ops/SKILL.md` | current-state reconstruction, provenance, admin closeout |
| Review | review-loop | `.agents/skills/review-loop/SKILL.md` | review ingestion, repeated validation, attribution |
| Review UX | plan-canvas | `.agents/skills/plan-canvas/SKILL.md` | local annotated plan review; approval mirrored to Desk/Issue HITL |
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

## Complete repository skill census

The recursive tree at `f1840cf0488bb48bbbf7df1b62d15808d58b5dfe` contains **45 `SKILL.md` paths** and zero tracked `.skill` archives:

- 32 agent-loadable definitions under `.agents/skills/`;
- 1 Claude-harness companion under `.claude/skills/`;
- 10 CI/production definitions under `.github/skills/`;
- 2 documentation mirrors under `docs/ops/skills/`.

The complete path list and contextual triggers live in [CAPABILITY-ACTIVATION-MATRIX.md](CAPABILITY-ACTIVATION-MATRIX.md). `SKILLS-INVENTORY.md` is the role-oriented navigation index.

## Session-scoped `.skill` discoveries

Three uploaded `.skill` packages were inspected in this session:

- `termux-mcp-project-steward.skill` — constrained Termux/GitHub stewardship; read-only by default, isolated worktree discipline, explicit apply mode, and device-resource preflight.
- `context-relationship-graph.skill` — metadata-only evidence graph; exact-root querying, verified/candidate separation, and bounded historical collection.
- `context-relationship-graph_2.skill` — a second package with the same skill name and a newer-looking contract that adds timeline events, direct review/comment permalink resolution, and bounded file-review timelines.

These uploaded packages are **session evidence, not repository SSOT**. They should not be installed or copied into the repo without an explicit provenance/adoption decision.

## External candidate references supplied with this session

- **Loopy API / Loop Library Skill** — describes bounded Observe -> Choose -> Act -> Verify -> Record -> Repeat workflows, explicit terminal states, and run receipts. Candidate adaptation only; no repository adoption is implied.
- **Google Jules skill/workflow references** — supplied material describes `skills/<skill-name>/SKILL.md`, issue automation, PR review, test-driven development, and subagent-driven development. Candidate ecosystem evidence only; no external policy is imported automatically.

## Session plugin and tool inventory

The 2026-11-19 ChatGPT session discovery snapshot contains **545 plugin skill references across 74 skill packages**, plus **4,705 callable tool actions across 123 MCP namespaces** and 3 additional core namespaces. Full activation descriptions and action names are captured in:

- `docs/integrations/session-plugin-skill-catalog.json`
- `docs/integrations/session-tool-catalog.json`

These snapshots describe the active session only. They do not establish availability, entitlement, authorization, repository adapters, or production readiness in Termux, Actions, another agent harness, or a later session.

The uploaded `Notation Registry Proposal.txt` was inspected by content and is a duplicate of the historical PR #523 WAIT/WATCH status report, not a notation-registry proposal. It is excluded as notation-source evidence until the correct proposal is available.

## Additional session-supplied architecture and operations references

- **`Diagnose Routing Architecture.txt`** — historical team-centric orchestration, provider attribution, manager comparison, MoneyBall/3L0 and outcome-based efficiency. Map to `docs/ops/AGENT-TEAM-ORCHESTRATION.md`, `docs/ops/AGENT-THROUGHPUT-METRICS.md`, `docs/ops/AGENT-OBSERVABILITY-RESEARCH-MATRIX.md` and `docs/ops/ROUTING-ORCHESTRATION-MAP.md`.
- **`Implement GitLab Sync Diagnosis.txt`** — historical PR #311 cross-platform credential placement, authenticated GitLab transport, single-writer review coordination and canonical-branch reconciliation. Map to `docs/ops/SECRET-NAMING-CONVENTION.md`, `docs/ops/secrets-and-variables-registry.md`, `docs/integrations/INTEGRATION-REGISTRY.md` and current GitHub/GitLab workflow evidence before any operational decision.
- **`Awesome Jules Skills Actions and Workflows for GitHub Development.`** — external Jules action/skill reference material. Treat action versions, account access, trigger behavior and runtime support as candidate claims pending current official-source verification.
- **`skill-loopy-api-loop-library-skill.json`** — bounded Observe → Choose → Act → Verify → Record → Repeat patterns, terminal states and run receipts. Reuse through the repository adaptive-WAIT and orchestration contracts.
- **`Notation Registry Proposal.txt`** — content inspection identifies a duplicate historical WAIT/WATCH status report. Use the canonical notation register and repository Linguist/Siglary mandate for notation work.

These attachments are session evidence. Their repository mappings are the durable navigation path; their historical status claims require fresh verification before execution.

## Adoption rule

Use the smallest repository-native skill that fills the evidence gap. If an external skill is considered, record source, version/commit, scope, permissions, overlap, maintenance evidence, and the smallest safe adaptation before adoption.

## Adopted session skills and Wingman

- `termux-mcp-project-steward.skill` → adopted as `.agents/skills/termux-mcp-project-steward/SKILL.md`.
- `context-relationship-graph_2.skill` → current repository relationship-graph contract.
- The older duplicate `context-relationship-graph.skill` remains reference-only.
- Loopy bounded Observe → Choose → Act → Verify → Record → Repeat semantics are adapted into the repository-native WAIT loop.
- `timerloggedout-spec/Wingman_fork` is pinned at `a6d5cea2d48009b5555e138c8d6b8f620388fb1b` as a reference/customization/template resource.

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
