# Termux Monorepo Brain — subsystem and capability architecture

**Status:** proposed target architecture, built on the root Rust kernel in PR #5492  
**Owner concept:** Brain is the monorepo-wide consciousness / cognitive coordination layer  
**Boundary:** shared cognition and coordination; existing systems remain authoritative for execution, policy, persistence, identity, scheduling and evidence.

## 1. Definition

The Monorepo Brain is the shared, evidence-grounded cognitive layer that constructs an operational understanding of the repository, interprets intent, discovers relevant capabilities, forms and compares plans, requests authorized action through existing control planes, evaluates verified outcomes, and proposes governed learning updates.

It spans the entire Termux monorepo. It is not a narrow agent, LLM wrapper, monolithic replacement, second control plane, or unrestricted execution process.

**Brain = shared cognition + repository-wide context integration + decision coordination + feedback interpretation.**

Owner-directed architecture assumption: Termux is controller/origin; GitHub and configured execution infrastructure are the hub/execution station; Android/mobile is an owner interface. Verify these assumptions against the live integration contracts before wiring adapters.

## 2. Subsystem taxonomy

| # | Subsystem | Responsibility | Output | Canonical owner / boundary |
|---:|---|---|---|---|
| 00 | Identity & intent | Resolve actor, request, goal, scope, constraints and outcome | Typed intent with provenance | Existing identity/intake contracts |
| 01 | Perception & ingestion | Observe repo, events, files, issues, PRs, workflows, devices and research | Normalized observations | Existing adapters/evidence envelope |
| 02 | Context assembly | Select current and historical context by relevance, freshness, sensitivity, provenance and budget | Bounded context packet | ICM / CRG / source SSOT |
| 03 | Knowledge & memory | Coordinate working, episodic, semantic, procedural and graph knowledge | Retrievals and learning candidates | Existing memory stores own persistence |
| 04 | Repository ontology | Understand components, ownership, interfaces, dependencies and lifecycle relationships | Capability/ownership graph | ICM, registries, graph SSOT |
| 05 | Research intelligence | Discover, compare, extract, qualify and cite academic/FOSS patterns | Evidence-backed research dossiers | refTemplates and 17_Papers |
| 06 | Capability discovery | Find eligible agents, tools, providers, MCP servers, workflows and skills | Candidate capability set | Existing tool/provider/capability registries |
| 07 | Reasoning & synthesis | Analyze, infer, compare hypotheses, reason under uncertainty | Decision rationale | Brain kernel + injected backend |
| 08 | Decomposition & planning | Decompose goals into bounded tasks and dependency DAGs | Typed plan + verification criteria | Brain emits; QUE/admission governs |
| 09 | Simulation & prediction | Evaluate scenarios, expected value, risk, failure paths and resource envelope | Forecast with uncertainty | Existing DoE / Bayesian / Markov / ForeSight |
| 10 | Policy, safety & authority | Check identity, scope, permissions, risk, privacy, budget and escalation | Allow / deny / review / escalate | hub_mcp, capability policy, owner controls |
| 11 | Orchestration coordination | Coordinate handoff to QUE, dispatch, claim, workflows and peer agents | Handoff request + correlation IDs | Existing QUE, scheduler, dispatchers |
| 12 | Execution interface | Describe and observe tool/device/provider operations | Execution request and receipt | Existing Harness / Hands / MCP / Actions |
| 13 | Verification & evidence | Evaluate outputs, tests, source pins, receipts and task outcomes | Verified / failed / unknown evidence | Evidence-led ops and domain validators |
| 14 | Observability & explainability | Trace decisions, provenance, confidence, latency, cost and interventions | Trace, metrics, audit projection | Existing receipts, telemetry, dashboards |
| 15 | Adaptation & learning | Convert verified outcomes into controlled improvement candidates | Learning candidate / experiment | Delphi, DoE, ELO, HindSight/ForeSight |
| 16 | Resilience & resources | Surface fallback, retries, circuit breakers, quota, cost and recovery constraints | Degraded state / backoff / escalation | Existing quota, adaptive-wait and SHE |
| 17 | Security & adversarial defense | Detect prompt injection, unsafe artifacts, supply-chain risk and secret exposure | Threat findings / quarantine request | Existing security and sandbox boundaries |
| 18 | Multi-agent / swarm cognition | Coordinate specialization, debate, consensus and handoffs | Attributed candidate synthesis | Existing swarm admission and Delphi |
| 19 | Domain cognition | Host domain-specific reasoning packages: software, research, robotics, security, data, etc. | Domain plans/findings | Separate domain lanes, shared Brain contracts |
| 20 | Owner experience | Expose decisions, evidence, status, pause/revoke controls | ArchWiz/QDesk/Termux/mobile projections | UI projects state; it does not own it |

### Capability record contract

Every capability needs a stable ID, category, owner, source path, contract/schema version, status, evidence refs, upstream refs, dependencies, security classification, freshness, tests, and deprecation/supersession links.

Use explicit status values:
- **LIVE** — implemented and source-verified on a pinned revision.
- **ADAPTER** — existing canonical subsystem owns the function; Brain consumes its contract.
- **REFERENCE** — research pattern or metadata-only refTemplate; not runtime.
- **PROPOSED** — target capability not yet implemented.
- **EXPERIMENTAL** — isolated and measured; not promoted.
- **DEPRECATED** — superseded with migration path.
- **UNKNOWN** — source or ownership not verified.

## 3. Existing systems Brain composes

| Existing system | Brain relationship | Must not duplicate |
|---|---|---|
| ICM / ICM objects | Repository ontology, navigation and context | Second documentation ontology |
| Context Relationship Graph | Historical relationships and provenance | Second relationship database |
| QUE / QDesk | Intake, task lifecycle, admission and owner-visible queue | Queue, ticket state, claim/lease engine |
| hub_mcp | Capability tiers, tool permissions and policy boundary | Tool registry or authorization engine |
| Dispatch / claim / workflow orchestration | Authorized handoff and lifecycle | Scheduler, dispatcher or run ledger |
| GitHub Actions | Execution/event fabric and evidence source | Workflow engine |
| Provider routing / 3L0 | Model/provider availability and routing | Provider catalog or quota authority |
| Memory stores | Retrieval and proposed governed updates | Canonical memory database |
| refTemplates | Reference discovery and pattern evidence | Clone-all or automatic upstream installer |
| Delphi / DoE | Candidate evaluation and outcome feedback | Parallel panel, weights ledger or award engine |
| ForeSight / HindSight | Forecast and observed-outcome evidence | Second forecast ledger |
| Adaptive-wait | Wait/watch/terminal-state collection | Polling loop or duplicate scheduler |
| SHE | Incident and recovery coordination | Unbounded self-repair execution |
| ArchWiz / Tribute | Owner cockpit and projections | Authoritative state store |

The canonical orchestration model remains four layers: surfaces → orchestration → evidence/state → SSOT/schemas. Brain is inside orchestration, not a fifth control plane. Lifecycle remains RECON → PLAN → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT.

## 4. refTemplates coverage

| refTemplates path | Brain capabilities informed |
|---|---|
| 00_Index | Source navigation, recovery and historical completeness |
| 01_Agent_Runtime | Runtime adapters, agent lifecycle and execution contracts |
| 02_Memory_Session | Working/episodic memory, session continuity and retrieval |
| 03_Agent_Communication | Agent messaging, inter-agent contracts and communication adapters |
| 04_CedarScript | Structured command/AST and deterministic action representation |
| 05_Safety_Observability | Safety controls, operational telemetry, tracing and state inspection |
| 06_Task_Tracking | QUE interoperability, identity, claim and task state |
| 07_Prompt_Context | Context assembly, prompt provenance and semantic compression |
| 08_Swarm_References | Swarm patterns, role specialization and multi-agent research references |
| 09_Auth_Networking | Identity, sessions, trust, networking and secrets |
| 10_Infrastructure | Runners, deployment, resource and reliability patterns |
| 11_Evaluation_Quality | Evaluation, test quality, benchmarks and evidence grading |
| 12_External_Agents | Peer agents, swarm interoperability and delegation |
| 13_Third_Party_Refs | External tools, services, libraries and integration references |
| 14_Plain_Files | Portable source artifacts and metadata contracts |
| 15_Research_Repo_Templates | Research lifecycle, reproducibility and agentic flywheel patterns |
| 16_Org_Phased | External organization integration and governance phases |
| 17_Papers | Academic claims, research provenance and implementation evaluation |
| smods | Selectively pinned custom forks; not a general dependency pool |

Important: refTemplates consolidation and recovery explicitly define the active tree as a **narrow slice** of historical environment reconstruction. Historical categories are not proof that every directory exists on the active branch. Keep recovery history and metadata-first rules visible; do not recursively materialize submodules by default.

## 5. Proposed Rust module boundaries

Extract modules only when each has a real public contract and tests; do not create empty modules just to match a diagram.

1. identity — run identity and source attribution.
2. intent — goal normalization and constraints.
3. perception — normalized observations and event intake.
4. context — selection, sensitivity, freshness and budgets.
5. knowledge — read interfaces over ICM/CRG/memory.
6. ontology — capability, ownership and dependency graph.
7. research — source dossiers and evidence grading.
8. capabilities — adapters over existing catalogs.
9. reasoning — typed stages and uncertainty-aware synthesis.
10. planning — bounded DAG and verification contracts.
11. simulation — optional scenario/expected-outcome interfaces.
12. policy — required injected policy gate; no permissive default.
13. handoff — typed QUE/dispatch request; no direct execution.
14. evidence — normalized references and task-outcome distinction.
15. telemetry — stage and decision trace projection.
16. learning — candidate generation only; persistence elsewhere.
17. resilience — explicit degraded/fallback/resource states.
18. security — untrusted input, secret classification and policy signals.
19. swarm — role/participant coordination through existing admission.
20. domain — pluggable domain reasoning packages.
21. interfaces — JSONL/FFI/service adapters with contract versions.

## 6. Research-derived principles

The filename survey shows that brain.py / Brain.py covers unrelated lineages: neural-network computation, biological simulation, belief updates, log parsing, model gateways, application decisions, autonomous loops, memory facades, operational safeguards and deterministic routing.

Transfer patterns by responsibility, not by filename:
- Separate cognition from execution (brain vs body/harness).
- Keep model access replaceable and distinct from memory/tool registration.
- Treat belief updates and prediction as explicit, testable domain components.
- Treat memory as a governed service with provenance and retention.
- Treat safeguards as first-class, but keep authority in the existing policy owner.
- Preserve deterministic baselines and abstention when evidence is weak.
- Distinguish research-derived reimplementation from validated reproduction.
- Do not treat README claims, secondary analysis and source-inspected behavior as equivalent evidence.

Detailed citations and limitations: [Brain filename and academic research dossier](../../refTemplates/17_Papers/citations/brain-file-and-agent-architecture-survey.md).

## 7. Phased delivery

| Phase | Deliverable | Exit evidence |
|---|---|---|
| P0 — Reconcile | Ownership, contracts, source map and duplicate census | Pinned paths; no second control plane |
| P1 — Kernel | Typed stages, context, plan DAG, policy adapter, failure semantics | Rust fmt/check/test/clippy green |
| P2 — Knowledge adapters | Read-only ICM/CRG/refTemplates/evidence adapters | Provenance, freshness, sensitivity fixtures |
| P3 — Capability map | Adapter over provider/tool/agent/workflow catalogs | Eligibility and policy remain external |
| P4 — Shadow QUE/QDesk handoff | Read-only decision proposal and correlation IDs; no claim, dispatch or execution | Shadow receipts are inspectable and idempotent; canonical queue state is unchanged |
| P5 — Authorized vertical slice | Existing QUE admission → existing dispatch/claim → configured execution → authoritative verification | Separate owner authorization; existing owners only; TASK_PASS/FAIL/UNKNOWN distinct from workflow state |
| P6 — Learning loop | Reflection candidates + Delphi/DoE experiment registration | No self-awarded consensus; held-out evidence |
| P7 — Owner cockpit | Explainable decision and evidence projections | Owner pause/revoke/inspect controls |
| P8 — Controlled autonomy | Narrow bounded autonomy after separate admission | Revocation, budget, rollback and stop tests |

Metrics: verified completion rate; time to verified completion; decision calibration; invalid/duplicate handoffs; stale-context rate; evidence coverage; owner intervention rate; fallback/degraded rate; resource cost per verified outcome; rollback effectiveness.

## 8. Invariants and non-goals

- No second queue, scheduler, provider registry, identity registry, policy engine, memory database or authoritative evidence ledger.
- Model output cannot grant itself authority or declare consensus.
- Filing an RFP does not authorize execution, deployment, promotion or permission expansion.
- A completed reasoning run is not completed work.
- Workflow success is not task success or promotion.
- Unknown, stale, unverified and conflicting evidence stay visible.
- Secret, restricted and unknown-sensitivity context is excluded unless existing policy explicitly authorizes a safe path.
- External references are hypotheses until source-inspected, pinned, tested and admitted.
- Android is an owner interface, not a requirement that all execution happen on-device.

## 9. Decision

Adopt the monorepo-wide Brain as the target cognitive architecture. Continue the root Rust kernel as its shared typed core. Expand through adapter-backed vertical slices, using QUE for admission, existing execution systems for action, and existing evidence/Delphi/DoE contracts for verification and learning.
