# Skill Discovery Matrix — adaptive wait + evidence-led repo ops

**Discovery basis:** recursive Git tree of `master` at SHA `2327859f0b2432631177346e93492e67cdc7b3d2`, plus the session-scoped `.skill` attachments and supplied skill/loop references.

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
| Graph orchestration | langgraph-orchestration | `.agents/skills/langgraph-orchestration/SKILL.md` | LangGraph state graphs, routing, fan-out, persistence, HITL, and BIUDL/ATES integration |

## Other repository-native skill files

The recursive tree contains 27 paths matching `**/SKILL.md` or `*.skill`: 25 `SKILL.md` files and 2 documentation mirrors. The repository tree currently contains **no tracked `.skill` archive**.

Agent-loadable paths also include: approxination-lane, blind-agent-evaluation, gemini-performance-psychology, github-pages-operator, tribute-lane, multivariate-doe, termux-monorepo, termux-monorepo-agentic-governance, and the Claude companion skill.

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


## LangGraph ecosystem discovery (2026-11-06)

**Source index:** [vonzosten/awesome-LangGraph](https://github.com/vonzosten/awesome-LangGraph) — curated discovery input, not an endorsement or adoption order.

**Best official SKILL.md sources:** `ecosystem-primer` first; then [langgraph-fundamentals](https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-fundamentals), [langgraph-human-in-the-loop](https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-human-in-the-loop), and [langgraph-persistence](https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-persistence). Add [langgraph-cli](https://github.com/langchain-ai/langchain-skills/tree/main/config/skills/langgraph-cli) for scaffold/build/deploy, and language quickstarts only for explicit new-project tasks. `deep-agents-core` + `deep-agents-orchestration` are the adjacent higher-level alternative. Their source blob SHAs and load conditions are pinned in `.agents/skills/langgraph-orchestration/SKILL.md`. The upstream skills README warns the catalog is early development and may change.

**Best ecosystem candidates to evaluate:** official supervisor/swarm packages, `langchain-mcp-adapters`, `deepagents`, `open_deep_research`, and `open-swe`. Guardrail/provenance projects such as `aport-agent-guardrails` and `sidclawhq/platform` remain research-only until their enforcement model, maintenance, license, and threat model are independently reviewed.

**Source-level corrections:** `langgraph-supervisor-py` was archived 2026-09-20 and its README recommends tool-based supervisor patterns for most new work; `langchain-mcp-adapters` was archived 2026-09-17 and points to `langchain[mcp]` / `langchain.mcp`; `open-swe` warns that stability/correctness are not guaranteed; `swarm-at-ledger` says its sample data is synthetic rather than real agent telemetry. These are recorded as legacy, migration, research, or pattern-only dispositions rather than default adoption candidates.

**Adoption decision:** reuse native orchestration treatments, receipts, OTEL/ATES, Temporal, and the maintained MCP boundary. The LangGraph integration is an optional orchestration treatment, not a replacement control plane. No dependency, fork, submodule, or deployment is implied by discovery.


**Runtime package observation:** PyPI latest stable at recon was `langgraph==1.2.20` (2026-11-05), MIT, Python `>=3.10`; published wheel SHA-256 `2b9fd01c3d5e0652e6c9b436dc0341413788010eb279ac8c46a733cf485d848b`. PyPI did not report release provenance. No dependency was installed or added; re-verify before any runtime adoption.
