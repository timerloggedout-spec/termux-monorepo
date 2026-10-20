# Project-Management / Gantt Integration Source Catalog

**Status:** Reconsolidated research and implementation intake  
**Updated:** 2026-09-21  
**Authority:** Discovery catalog only. The repository-native dependency-phase plan remains authoritative.

## Purpose

This catalog consolidates the prior Gantt work in termux-monorepo, the user's forked Gantt repositories, and a fresh external search of project-management templates. The goal is pattern extraction + deterministic adapters, not replacing the repository's control plane with a third-party UI.

The existing architecture already establishes the key boundary: phases, dependencies, approvals, PR/check evidence, and GitHub Project reconciliation are authoritative; Gantt/Markdown/Mermaid/dashboard views are derived.

## Reconnaissance: user-owned Gantt forks

| Source | Role discovered | Reusable capability | Disposition |
|---|---|---|---|
| timerloggedout-spec/GanTTY_fork | Python terminal planner | interactive dependency editing, task state, compact terminal UX | reference only |
| timerloggedout-spec/ganttless_fork-agentic | Rust ASCII renderer | deterministic compact timeline from YAML/CLI input | renderer adapter |
| timerloggedout-spec/gantt-cli_fork_agentic | Rust TUI planner | parent/child tasks, dependencies, topological scheduling, JSON persistence, undo/redo | exporter/pattern adapter |
| timerloggedout-spec/Gantt-Chart-Code_fork | Rust program ingester | flat-record to hierarchy transformation | ingestion pattern |
| timerloggedout-spec/montt_fork | Rust Monte Carlo Gantt forecasting | resource/estimate DSL and probabilistic schedule concepts | deferred research seed |

These are forks of upstream projects rather than authoritative monorepo components. The current fork metadata identifies the upstreams as timeopochin/GanTTY, kyoheiu/ganttless, zhangjinshui-nerveee/gantt-cli, bytesandbalance/Gantt-Chart-Code, and simon-siggaard/montt.

## Prior repository work recovered

- docs/agentic/dependency-phases.json — canonical phase/dependency model and GitHub Project identifiers.
- scripts/agentic/dependency_phase_engine.py — validation, stable plan hashing, topological ordering, wave calculation, evidence evaluation, and derived Mermaid/Markdown rendering.
- docs/proposals/active/gantt-dependency-phases/ — proposal, work items, manifest, source, and acceptance contract.
- docs/agentic/TEMPLATE_CAPABILITY_ASSESSMENT.md — earlier source-reviewed candidate assessment.
- docs/agentic/template-candidates.yaml — machine-readable candidate registry.
- termux-multi-agent/templates/gantt_core.py — historical Gantt prototype; useful provenance, but it uses ambient wall-clock time and is not suitable as deterministic control-plane implementation.

The proposal explicitly defines the Gantt representation as a derived view that cannot authorize dispatch or completion. That remains the governing rule.

## Fresh external template/search corpus

| Source | Useful pattern | Integration class | Key caveat |
|---|---|---|---|
| Project Planner | dependency-first planning, Gantt + graph + Kanban, critical path, suggested dates, Markdown/Dataview persistence | data-model/reference | Obsidian plugin domain |
| task-cli | AI decomposition -> tasks -> Gantt -> report/Q&A CLI lifecycle | agent workflow reference | LLM planning must not become authority |
| GanttReady | CPM, EVM, resources, calendars, AI scheduling | scheduling research | .NET/SQLite application boundary |
| Agentic Project Management | persistent agent context, manager/worker/handoff model | orchestration reference | broader agent framework |
| Agent Kanban | agents as first-class actors, assignment/provenance/dependencies/review | agent-control reference | board product, not repository SSOT |
| DuneBoard | Markdown SSOT, task graph, parent/child, dependencies, readiness rules | schema/reference | local task-board product |
| Plandeck | durable file plans, deterministic completion gate, dependency unlocks, critical path | agent skill reference | CLI-oriented |
| It's a Plan | project/issue/cycle/timeline model, REST/MCP/webhooks, agents as project members | integration reference | AGPL core; active development |
| Taskboard | local PM + CLI + MCP, tickets/dependencies/teams, single-binary model | MCP integration reference | SQLite application boundary |
| Pith | MCP-first, CLI-native agent/human task management, subtask/progress APIs | MCP integration reference | external service model |
| kanban-mcp | persistent items, relationships/epics, blocking edges, semantic search | MCP/relationship reference | database-backed board |
| pm-gantt-chart | dependency-aware schedule, critical path, slack, Mermaid/HTML/SVG/CSV/JSON exports | Gantt exporter reference | preserve canonical IDs |
| gantts-app | WBS, CPM, baselines, resources, calendars, file-based interchange | scheduling/UI reference | browser-first application |
| GanttProject | hierarchy, dependencies, milestones, baselines, resources, costs, interoperability | mature PM reference | desktop application |

## Consolidated capability vocabulary

1. Stable identity: string IDs that survive reorder and rendering.
2. Dependency DAG: explicit predecessor relationships; cycles fail closed.
3. WBS / hierarchy: parent-child decomposition without conflating hierarchy with dependency.
4. Readiness: deterministic predicate derived from prerequisites and evidence.
5. Schedule projection: dates derived from dependencies, durations, calendars, and explicit anchors.
6. Critical path / float: analytical output, never authorization.
7. Resources / ownership: planning and workload metadata.
8. Progress / evidence: status tied to observable artifacts, not a chart state.
9. Human gates: approval is explicit evidence.
10. Agent provenance: actor, claim, run, PR, SHA, and plan hash are first-class.
11. Multiple projections: Mermaid, ASCII, JSON, HTML, dashboards, and GitHub Projects can consume one normalized model.
12. MCP/API adapters: external PM systems can be integration surfaces without becoming repository authority.

## Consolidation decision

### Keep as canonical

docs/agentic/dependency-phases.json + deterministic evaluator + repository proposal/check/PR evidence.

### Add now

A standard Gantt projection contract that converts the canonical phase/evaluation model into stable-ID schedule records. It supports dependency-derived relative waves, optional deterministic date anchoring, explicit duration input, critical-path calculation, JSON output for agents/tools, and Mermaid Gantt output for documentation. It never writes back to the canonical plan.

### Defer

- third-party Gantt submodules;
- database-backed PM systems as canonical state;
- autonomous AI scheduling that mutates phase dates;
- probabilistic forecasts until empirical duration history exists;
- visual boards in CI;
- automatic merge/closure.

## Adapter contract

Every future PM/Gantt adapter should consume and preserve: phase_id, title, depends_on, state, wave, duration_days, start, end, critical, plan_sha256.

An adapter may add presentation metadata but may not rewrite identity, dependency edges, approvals, or completion evidence.

## Licensing / provenance rule

Third-party code is not copied merely because a feature is useful. Before adopting implementation code, record upstream repository, revision, license, provenance, and fixture parity. Prefer small compatibility adapters and generated outputs over vendoring entire PM applications.

## Current implementation target

scripts/agentic/gantt_projection.py implements the first normalized projection. It is dependency-only when no date anchor is supplied, and becomes a deterministic date schedule only when the operator supplies an explicit start date and duration mapping. This avoids inventing calendar commitments from a visualization.

## Sources

- https://github.com/hmil1151/project-planner
- https://github.com/sunjiawe/task-cli
- https://github.com/fvftuu/GanttReady
- https://github.com/sdi2200262/agentic-project-management
- https://github.com/saltbo/agent-kanban
- https://github.com/KaEvDm/DuneBoard
- https://github.com/OthmanAdi/plandeck
- https://github.com/croffasia/itsaplan
- https://github.com/tcarac/taskboard
- https://github.com/SiluPanda/pith
- https://github.com/multidimensionalcats/kanban-mcp
- https://github.com/unbraind/pm-gantt-chart
- https://github.com/Synth88Labs/gantts-app
- https://github.com/bardsoftware/ganttproject
