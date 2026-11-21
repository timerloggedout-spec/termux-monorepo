# Repository Architecture

**Status:** living navigation and architecture entry  
**Owner/lane:** Repository Architecture / ICM  
**Canonical for:** repository-wide architecture navigation, system taxonomy, and directory orientation  
**Source-of-truth rule:** domain specifications, source code, schemas, workflow definitions, and runtime evidence own their facts. This file routes readers to those sources; it does not supersede them.

> Start here for the repository-wide shape. Continue through the [ICM system map](docs/icm/CLAUDE.md) to select one bounded component, then read its owning source.

## Contents

- [1. Reading protocol](#1-reading-protocol)
- [2. System taxonomy](#2-system-taxonomy)
  - [2.1 Execution and device plane](#21-execution-and-device-plane)
  - [2.2 Agent control and orchestration plane](#22-agent-control-and-orchestration-plane)
  - [2.3 Provider and integration plane](#23-provider-and-integration-plane)
  - [2.4 Evidence, telemetry, and data plane](#24-evidence-telemetry-and-data-plane)
  - [2.5 Intelligence and learning plane](#25-intelligence-and-learning-plane)
  - [2.6 User surfaces and projections](#26-user-surfaces-and-projections)
  - [2.7 Governance and delivery plane](#27-governance-and-delivery-plane)
- [3. Repository-wide data flow](#3-repository-wide-data-flow)
  - [3.1 Entities and origins](#31-entities-and-origins)
  - [3.2 Producers and transformations](#32-producers-and-transformations)
  - [3.3 Stores and consumers](#33-stores-and-consumers)
  - [3.4 Confidence semantics](#34-confidence-semantics)
- [4. Directory taxonomy](#4-directory-taxonomy)
  - [4.1 Root control and navigation](#41-root-control-and-navigation)
  - [4.2 Documentation estate](#42-documentation-estate)
  - [4.3 Runtime and application families](#43-runtime-and-application-families)
  - [4.4 Automation, operations, and research](#44-automation-operations-and-research)
- [5. Canonical source index](#5-canonical-source-index)
- [6. Change-impact routing](#6-change-impact-routing)
- [7. Maintenance and freshness](#7-maintenance-and-freshness)
- [8. Linked modular flow maps](#8-linked-modular-flow-maps)

## 1. Reading protocol

1. Read [root CLAUDE.md](CLAUDE.md) for governance, permissions, and validation gates.
2. Read the [ICM system map](docs/icm/CLAUDE.md) and select one relevant object, process, or effects card.
3. Read the canonical architecture or operational contract linked by that card.
4. Verify implementation claims against code, schemas, workflows, and current evidence.
5. Record changes through the proposal and validation lifecycle.

Authority order: governing policy → canonical domain contract → implementation → generated projection. When sources disagree, record the discrepancy and reconcile at the owning source.

## 2. System taxonomy

The monorepo is an Android/Termux-first execution environment, agent-development control plane, provider integration estate, evidence platform, and research workspace. These planes describe responsibilities; they do not imply one process or shared datastore.

### 2.1 Execution and device plane

- Target: Android / Termux device runtime.
- Hub: `hub_mcp/` and the documented Termux Agentic Hub capability boundary.
- Operator interface: `archwiz/`, including the Termux cockpit / Hyper-Forge.
- Session and CLI surfaces: `deepcli/`, `deepcli-tui/`, `multi-ai-cli/`, `termux-multi-agent/`, and `cli-synthegration/`.
- Contracts: [Termux Agentic Hub](docs/architecture/termux-agentic-hub.md), [transport and identity decision](docs/architecture/transport-and-identity-decision.md), [session SSOT](docs/schemas/session-ssot.md).

### 2.2 Agent control and orchestration plane

- Lifecycle: scout → candidate → experiment → telemetry → review → admission / synthesis.
- Dispatch: GitHub Actions, provider command dispatch, ArchWiz dispatch, and bounded DAG planning.
- Coordination: Manager / Conductor, team lanes, admission policy, and BIUDL.
- Canonical map: [Agent Team Control Plane](docs/architecture/AGENT-TEAM-CONTROL-PLANE.md) and [Mermaid source](docs/architecture/AGENT-TEAM-CONTROL-PLANE.mmd).

### 2.3 Provider and integration plane

- Local model API: `llm_api_hub/` and [routing contract](llm_api_hub/ROUTING.md).
- Provider clients and adapters: provider-specific clients, protocol extensions, and governed adapter contracts.
- Integration registry: [integration catalog](docs/integrations/README.md), [adapter contract](docs/integrations/ADAPTER-CONTRACT.md), and `docs/integrations/schemas/`.
- Capacity and entitlement: `ops/quota/` and [quota registry](docs/ops/QUOTA-REGISTRY.md).

### 2.4 Evidence, telemetry, and data plane

- PR evidence: production ledger and Evidence Projection Surface (EPS).
- Agent throughput: ATES observers, sanitizer, reducer, and JSONL evidence artifacts.
- Context relationships: Context Relationship Graph (CRG) collectors, normalization, confidence labels, and canonical index.
- Historical corpus: bounded GitHub history ingestion, corpus nodes / edges, manifests, and checkpoints.
- Operational event stores: lane events and Receiver Mesh events in Neon; each event stream retains its own contract.
- Dashboard feeds: operational feeds under `apps/tribute-dashboard/data/`.
- Source contracts: [EPS](docs/ops/EVIDENCE-PROJECTION-SURFACE.md), [CRG](docs/ops/CONTEXT-RELATIONSHIP-INDEX.md), [telemetry recon](docs/ops/TELEMETRY-VIZ-RECON.md), and [ATES Phase B](docs/ops/AGENT-THROUGHPUT-PHASE-B.md).

### 2.5 Intelligence and learning plane

- Evaluation: Agent Evaluation Framework, blind evaluation, DoE / MVT, and outcome classification.
- Performance intelligence: Moneyball / 3L0 and evidence-backed provider / agent evaluation.
- Context intelligence: ICM cards, CRG, ArchWiz indexes, and bounded context deltas.
- Learning loop: verified outcomes inform reviewed policy, skills, and future task selection.
- Sources: [Agent Evaluation Framework](docs/architecture/AGENT-EVALUATION-FRAMEWORK.md), [ATES metrics](docs/ops/AGENT-THROUGHPUT-METRICS.md), and [DoE registry](docs/ops/DOE-COMPONENT-REGISTRY.md).

### 2.6 User surfaces and projections

- SHE: versioned, read-only dashboard snapshots; Vercel is the primary interactive surface, with optional mirrors / analytical consumers where configured.
- Tribute dashboard: read-only consumer of committed surface feeds.
- ArchWiz: operator cockpit, indexes, query/context builder, and visualization entry points.
- Mermaid: editable graph source; rendered images are downstream presentation artifacts.
- Contracts: [SHE architecture](docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd), [snapshot contract](docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md), and [dashboard PRD](docs/ops/SHE-DASHBOARD-PRD.md).

### 2.7 Governance and delivery plane

- Collaborator entry: root `CLAUDE.md`.
- ICM routing: `docs/icm/CLAUDE.md` and its object / process / effects cards.
- Proposal lifecycle: `docs/proposals/registry.yaml`, `docs/proposals/PROCESS.md`, and `docs/proposals/active/`.
- Validation: `scripts/ci/repo_gate.py`, `scripts/ci/termux_smoke.py`, and required GitHub Actions checks.
- Security and authority: `docs/proposals/AGENTIC-PERMISSIONS.md` and `docs/SECURITY-REMEDIATION.md`.

## 3. Repository-wide data flow

### 3.1 Entities and origins

| Entity | Origin / producer | Stable anchors |
|---|---|---|
| Repository change | Git commits and changed files | commit SHA, path, blob SHA |
| Collaboration event | GitHub PRs, issues, reviews, comments, checks | repository, event / PR / issue IDs, SHA |
| Execution evidence | GitHub Actions and agent workflows | workflow run ID, attempt, job / step IDs, artifact digest |
| Provider observation | Governed provider adapters | provider, model, operation, timestamp, provenance |
| Session activity | Termux / ArchWiz session callers | session ID, message / event identity |
| Operational event | Actions lane recorder or Cloudflare webhook receiver | event ID, idempotency key, source identity |
| Context relationship | Repository collectors and GitHub metadata | source SHA, entity IDs, confidence class |
| Dashboard projection | Operational inputs, Actions, GitHub, feed collector | source references, schema version, generation metadata |

### 3.2 Producers and transformations

1. **Observe:** PR ledger, ATES observer, context collectors, historical corpus builder, dashboard feed collector, lane-event recorder, Receiver Mesh processor, and provider adapters.
2. **Normalize:** EPS event shaping, ATES sanitization, CRG normalization / compilation, corpus indexing, feed shaping, and integration-event schema validation.
3. **Persist:** immutable artifacts, canonical indexes, Neon event tables, committed JSON feeds, session SSOT, and versioned snapshots.
4. **Reduce:** ATES metrics, SHE pure reducers, corpus projections, and evaluation / learning pipelines.
5. **Consume:** dashboards, analytics, Moneyball / 3L0, DOE / MVT, ArchWiz context assembly, and bounded agent task context.

### 3.3 Stores and consumers

EPS NDJSON, ATES JSONL, normalized integration events, Neon lane events, Neon receiver events, context-index artifacts, historical corpus artifacts, committed dashboard feeds, session SSOT, and SHE snapshots remain separate data products. Analytics consumers join validated observations only through an explicitly governed projection.

ArchWiz `DispatchPipeline` fans out to Session SSOT and the Codex index, plus a Linear sync hint that is log-only. Treat the hint as an observation, not a completed Linear synchronization.

Editable diagram source: [repository-data-flow.mmd](docs/ops/diagrams/repository-data-flow.mmd). Interactive versioned view: [Mermaid.ai root diagram](https://mermaid.ai/app/projects/affbc609-b2b7-420c-af5b-ca0ccb74fe14/diagrams/080c5454-1215-40a8-afb5-7ef30e42dfcb/version/v0.1/edit). Focused views: [flow module index](docs/architecture/flows/README.md). Solid and dashed edges carry the semantics below.

### 3.4 Confidence semantics

- **Solid edge:** documented / implemented flow supported by current source inspection.
- **Dashed edge:** optional consumer, contract-only route, intended longitudinal join, or partially verified integration.
- **CRG confidence:** `verified`, `derived`, `inferred`, and `candidate`; preserve each class through projections.
- **Evidence anchors:** source SHA, GitHub IDs, immutable artifact IDs / digests, schema version, and generation metadata.

## 4. Directory taxonomy

This is a navigation taxonomy of major ownership zones, not a recursive inventory. Read each directory's local README, index, or ICM card for current child structure.

### 4.1 Root control and navigation

| Path | Responsibility |
|---|---|
| `CLAUDE.md` | Governance, collaborator entry, operating rules, validation gates |
| `README.md` | Human-facing overview and subsystem navigation |
| `architecture.md` | Repository-wide architecture entry (this document) |
| `docs/` | Canonical documentation, contracts, plans, operations, and ICM |
| `wiki/` | Supplemental / historical high-level architecture overview |
| `.github/` | Actions workflows, templates, repository automation |
| `.agents/`, `.github/skills/` | Repository-local agent skills and workflow skills |
| `scripts/` | CI gates, maintenance, validation, automation |
| `tests/` | Automated tests and fixtures |

### 4.2 Documentation estate

| Path | Responsibility |
|---|---|
| `docs/architecture/` | Architecture specs, decisions, and architecture index |
| `docs/icm/` | ICM system map: objects, processes, effects, maintenance |
| `docs/ops/` | Operational contracts, telemetry, dashboards, runbooks, diagrams, evidence |
| `docs/proposals/` | Proposal registry, active work packages, review lifecycle |
| `docs/schemas/` | Shared schemas and capability contracts |
| `docs/integrations/` | Integration catalog, adapter contracts, event schemas |
| `docs/superpowers/` | Engineering methodology specs and plans |
| `docs/agentic/` | Agentic dependency phases and operating documentation |

### 4.3 Runtime and application families

| Path | Responsibility |
|---|---|
| `archwiz/` | Indexing, provenance, recovery, cockpit, and dispatch tooling |
| `hub_mcp/` | Termux Agentic Hub MCP runtime |
| `llm_api_hub/` | Local OpenAI-compatible model API and provider plane |
| `deepcli/`, `deepcli-tui/`, `deepseek-cli/` | DeepSeek-oriented CLI and terminal surfaces |
| `multi-ai-cli/`, `termux-multi-agent/` | Multi-model and multi-agent terminal tooling |
| `cli-synthegration/` | Conversation synthesis, branching, export, and metrics |
| `apps/` | Application surfaces, including Tribute dashboard |
| `src/`, `bin/`, `config/` | Shared source, executable entry points, and configuration |

### 4.4 Automation, operations, and research

| Path | Responsibility |
|---|---|
| `.github/workflows/` | CI, provider dispatch, telemetry, reconciliation, delivery automation |
| `ops/` | Operational registries and machine-consumed state, including quota allocations |
| `scripts/ci/` | Repository and Termux validation gates |
| `workspace/` | Work-in-progress and generated indexes; each child has its own promotion boundary |
| `research/`, `guides/` | Research artifacts, investigation inputs, user and operator guides |
| `refTemplates/` | Reference material and shallow gitlink pins; input material rather than runtime control plane |
| `sandbox/` | Experiments and isolated exploration |
| `workspace/llm_map/` | Generated repository maps, distinct from the hand-maintained ICM map |
| `docs/ops/archive/`, `docs/ops/generated/` | Dated records and generated projections; canonical sources retain semantic ownership |

## 5. Canonical source index

| Domain | Canonical entry |
|---|---|
| Architecture catalog and conventions | [docs/architecture/README.md](docs/architecture/README.md) |
| Agent team control plane | [AGENT-TEAM-CONTROL-PLANE.md](docs/architecture/AGENT-TEAM-CONTROL-PLANE.md) |
| Termux Agentic Hub | [termux-agentic-hub.md](docs/architecture/termux-agentic-hub.md) |
| Agent evaluation | [AGENT-EVALUATION-FRAMEWORK.md](docs/architecture/AGENT-EVALUATION-FRAMEWORK.md) |
| Routing and orchestration | [ROUTING-ORCHESTRATION-MAP.md](docs/ops/ROUTING-ORCHESTRATION-MAP.md) |
| Evidence projection | [EVIDENCE-PROJECTION-SURFACE.md](docs/ops/EVIDENCE-PROJECTION-SURFACE.md) |
| Evidence substrate | [AGENT-EVIDENCE-SUBSTRATE.md](docs/ops/AGENT-EVIDENCE-SUBSTRATE.md) |
| Context relationship graph | [CONTEXT-RELATIONSHIP-INDEX.md](docs/ops/CONTEXT-RELATIONSHIP-INDEX.md) |
| Agent throughput telemetry | [AGENT-THROUGHPUT-PHASE-B.md](docs/ops/AGENT-THROUGHPUT-PHASE-B.md) |
| Integration mesh | [docs/integrations/README.md](docs/integrations/README.md) |
| Provider capabilities | [provider-capabilities.md](docs/schemas/provider-capabilities.md) |
| ICM map | [docs/icm/CLAUDE.md](docs/icm/CLAUDE.md) |

## 6. Change-impact routing

| Change target | Read first | Verify |
|---|---|---|
| Device / Termux runtime | ICM platform card + Termux Hub architecture | Termux smoke, capability boundary, device evidence |
| Agent lifecycle / dispatch | Agent Team Control Plane + routing map | workflow contracts, dispatch tests, required gates |
| Provider / adapter | Integration catalog + adapter contract + provider capability schema | schema validation, auth boundary, provider-specific tests |
| Evidence / telemetry | EPS, ATES, CRG, or event-store contract for the owning stream | provenance, idempotency, schema, reducer fixtures |
| Dashboard / snapshot | SHE or Tribute contract and feed producer | snapshot provenance, source SHA, schema, consumer tests |
| ICM / navigation | ICM maintenance guide + owning card | link integrity, scope, source ownership |
| Governance / promotion | root CLAUDE + proposal process + permissions | proposal status, repo gate, Termux smoke, required CI |

## 7. Maintenance and freshness

- Keep this entry navigational; place domain behavior in its canonical source.
- Add major subsystems to the relevant taxonomy and directory table when ownership is established.
- Add architecture-grade documents to [docs/architecture/README.md](docs/architecture/README.md) or the appropriate domain pointer table.
- Keep ICM routes concise and point here for repository-wide orientation.
- Update the data-flow diagram when a producer, transformation, store, consumer, or confidence boundary changes.
- Label proposed, optional, historical, inferred, and partially verified edges explicitly.
- Run link checks, `git diff --check`, `python3 scripts/ci/repo_gate.py`, and `python3 scripts/ci/termux_smoke.py` through the authorized project lane; record each result with the commit SHA.

**Freshness:** initial consolidation from repository documentation and selected implementation paths, 2026-11-21. Revalidate dynamic directory inventories and runtime integrations against the live tree before treating them as exhaustive.


## 8. Linked modular flow maps

The root map is the system index. Follow a plane into its paired detailed Markdown map and editable Mermaid source.

### Execution and Session Plane

**Origins:** Android/Termux device, hub_mcp capability boundary, CLI/TUI and agent session callers.

**Flow:** callers supply session identity and structured events → ArchWiz DispatchPipeline → Session SSOT and Codex index. The documented Linear route is a log-only sync hint.

**Consumers:** operator cockpit, session continuation, context retrieval and bounded task context.

**Findings:** caller → ArchWiz → Session SSOT/Codex is documented. Device/remote MCP reachability needs deployment evidence. Separate CLI families do not prove a shared session store. Linear hint does not prove a completed write.

**Sources:** [Termux Agentic Hub](../../architecture/termux-agentic-hub.md) · [Session SSOT](../../schemas/session-ssot.md) · [ICM platform cards](../../icm/objects/platform/CONTEXT.md)


[Detailed mapping](docs/architecture/flows/execution-session.md) · [Mermaid source](docs/architecture/flows/execution-session.mmd)

### Agent Orchestration and Provider Routing

**Planes:** ephemeral GitHub Actions review/ops; chat completion through llm_api_hub and CLI wrappers; MCP tool execution through hosted/device MCP servers; provider adapters translate external calls into repository event envelopes.

**Flow:** task/role selection → model-router and quota gate → chat or MCP route → scoped adapter → schema/privacy/provenance validation → normalized integration event.

**Findings:** chat and MCP paths are distinct. Hosted MCP, device MCP, Actions and local gateway are separate execution surfaces. Adapter contract is generic; provider promotion state lives in integration registry. Aggregate quota coverage does not prove every provider has a live reader. Provider outputs remain untrusted observations.

**Sources:** [Routing map](../../ops/ROUTING-ORCHESTRATION-MAP.md) · [Adapter contract](../../integrations/ADAPTER-CONTRACT.md) · [Integration catalog](../../integrations/README.md) · [Quota registry](../../ops/QUOTA-REGISTRY.md)


[Detailed mapping](docs/architecture/flows/agent-orchestration.md) · [Mermaid source](docs/architecture/flows/agent-orchestration.mmd)

### Evidence and Telemetry Plane

**Sources:** GitHub PRs/issues/commits/reviews/checks; Actions runs/attempts/jobs/steps/artifacts; admitted agent workflows; selected lane events; Cloudflare webhook events.

**Producers:** PR production ledger → EPS deterministic provenance-bound NDJSON. ATES observes completed admitted runs, sanitizes task-boundary evidence and reduces events. Lane recorder and Receiver Mesh write separate append-only Neon streams.

**Stores:** EPS NDJSON, ATES JSONL/reducer/receipt, Neon lane_events and Neon receiver_events remain separate products.

**Findings:** PR ledger → EPS and admitted workflow_run → ATES → reducer are connected. Jules execution-time ATES is excluded pending attributable receipts. ATES parallel-yield metrics remain null pending comparable serial baseline. Neon streams have separate contracts; unified join is unproven. Privacy excludes prompts, completions, credentials and raw payloads.

**Sources:** [EPS](../../ops/EVIDENCE-PROJECTION-SURFACE.md) · [ATES Phase B](../../ops/AGENT-THROUGHPUT-PHASE-B.md) · [Adapter contract](../../integrations/ADAPTER-CONTRACT.md)


[Detailed mapping](docs/architecture/flows/evidence-telemetry.md) · [Mermaid source](docs/architecture/flows/evidence-telemetry.mmd)

### Context Relationship and Historical Corpus

**Sources:** Git tree/files at pinned SHA; GitHub issues, PRs, commits, reviews, comments and workflow metadata; prior canonical nodes/edges and coverage checkpoints.

**Pipeline:** source_collector.py + github_collector.py → seed_merger.py → compiler.py → build_index.py → canonical JSONL nodes/edges, manifest, reports and checkpoint. Temporal helpers build snapshots, lineage and comparisons.

**Consumers:** ArchWiz context query, bounded agent context deltas, temporal views, Mermaid projections and SHE reducers.

**Findings:** Git/GitHub collectors → compiler → canonical index is connected. COMPLETE requires contiguous page windows from page one; otherwise preserve PARTIAL_CONTINUATION_REQUIRED or UNVERIFIED. Confidence labels verified/derived/inferred/candidate remain distinct. Mermaid graphs are projections, not source evidence. Freshness depends on source SHA, observed_at, checkpoint and coverage.

**Sources:** [CRG contract](../../ops/CONTEXT-RELATIONSHIP-INDEX.md) · [build_index.py](../../../archwiz/context_relationships/build_index.py) · [Temporal evidence](../../ops/CONTEXT-RELATIONSHIP-TEMPORAL-EVIDENCE.md)


[Detailed mapping](docs/architecture/flows/context-historical.md) · [Mermaid source](docs/architecture/flows/context-historical.mmd)

### Dashboard, Snapshot and Surface Consumers

**Inputs:** historical corpus/CRG; validated EPS and ATES evidence where configured; operational feeds; Tribute JSON feeds.

**Snapshot path:** SHE pure reducers → snapshot builder → versioned read-only snapshot. Contract requires schema_version, snapshot_id, source_ref, source_sha, generated_at, coverage and corpus manifest SHA. Vercel is the primary interactive surface; Pages and Hex are optional consumers. Tribute consumes a separate committed feed family.

**Findings:** corpus → SHE reducers → snapshot → Vercel is documented. Pages/Hex require current deployment/import evidence. Tribute feeds are a separate projection silo; shared repository does not prove automatic synchronization. Display source_sha, generated_at, coverage and manifest SHA together. Historical views use immutable L2 snapshots.

**Sources:** [SHE architecture](../../ops/SHE-DASHBOARD-ARCHITECTURE.mmd) · [Snapshot contract](../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md) · [Tribute feed](../../ops/TRIBUTE-EVIDENCE-FEED.md)


[Detailed mapping](docs/architecture/flows/dashboard-snapshots.md) · [Mermaid source](docs/architecture/flows/dashboard-snapshots.mmd)

### Legacy Local Snapshot Pipeline — Gap Audit

<badge color="danger">Disconnected / requires repair</badge>

**Observed:** archwiz/trace_data_flow.py scans local source directories for data-file path strings and writes $HOME/tmp/data_flow_map.txt. archwiz/build_data_flow_manifest.py reads $HOME/central_index.jsonl and the temporary map, then writes to absolute path $HOME/archwiz/DATA_FLOW_MANIFEST.md. The builder stamps a wall-clock Generated field and indexed-file count. The tracked archwiz/DATA_FLOW_MANIFEST.md blob is zero bytes at observed master SHA 5135731c389c6b1b8ed8332b3415a60f8163c2a1.

**Findings:** output path mismatch; no source SHA/tree SHA/generator version/input digest; substring/basename heuristics create candidate matches, not verified writer edges; temporary map is untracked scratch; central_index.jsonl lacks repo-owned freshness/coverage contract; no verified consumer reaches CRG/SHE/EPS; Generated proves run time, not input freshness.

**Repair contract:** resolve repo root from script location or explicit output path; publish to declared repo-owned generated directory; include generated_at, source_sha, tree_sha, generator_version, input_manifest_sha256, indexed_file_count, mapped_file_count, coverage_status and unmapped_count; classify heuristic matches as candidate; add freshness validation. Connect to CRG/SHE only after provenance and coverage pass.

Actual local generated_at remains unknown; this audit does not infer it.


[Detailed mapping](docs/architecture/flows/legacy-snapshot-audit.md) · [Mermaid source](docs/architecture/flows/legacy-snapshot-audit.mmd)

### Snapshot freshness and legacy inventory gap

SHE snapshots require source_sha, generated_at, coverage and corpus manifest SHA. The legacy ArchWiz data-flow manifest generator emits a local wall-clock Generated field, but its tracked output is zero bytes, its script writes to an absolute home-directory path, and it omits source SHA, tree SHA and input digest. Its generated timestamp proves execution time only, not input freshness. No verified consumer connects this inventory to CRG, SHE or EPS. See the [legacy snapshot gap audit](docs/architecture/flows/legacy-snapshot-audit.md). The actual local generated_at is unknown; audit date 2026-11-21 is not a substitute.
