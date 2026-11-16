# Monorepo Brain — ownership and integration map

**Status:** P0 source reconciliation, source-inspected on branch `feat/root-brain-rust-core-final` at the current filing snapshot.  
**Purpose:** identify the existing canonical owner for each Brain responsibility before writing adapters or duplicating functionality.

Brain is the **repository-wide cognitive coordination layer**. It observes, contextualizes, reasons, plans, explains and proposes feedback across the monorepo. It is not a new execution plane. Existing systems remain authoritative for identity, admission, policy, dispatch, memory, provider routing, execution, verification and persistent evidence.

## Ownership rules

1. **Reuse before build.** A subsystem with an existing owner gets an adapter, not a replacement.
2. **Projection is not authority.** Generated feeds, dashboards, indexes and caches are read models unless their contract explicitly says otherwise.
3. **Decision is not execution.** A Brain plan is not a claim, dispatch, workflow, task completion or promotion.
4. **Evidence is not policy.** Provider catalog evidence, research references and Delphi scores cannot grant authority.
5. **No implicit persistence.** Reflection emits candidates; the existing memory/evidence owner decides what to persist.
6. **Fail closed on uncertainty.** Missing owner, stale context, unknown sensitivity, conflicting authority or unverified contracts stop the adapter or require review.
7. **Stable identity across handoffs.** Preserve task, participant, orchestration, cycle, attempt, correlation and evidence references end-to-end.

## Existing subsystem owners

| Brain responsibility | Existing canonical owner / source-inspected surface | What it owns today | Brain integration boundary |
|---|---|---|---|
| Orchestration contract and lifecycle vocabulary | [ORCHESTRATION-CONTRACTS.md](../ops/ORCHESTRATION-CONTRACTS.md) | Canonical orchestration layers, lifecycle states, identity chain and normalized receipts | Use its vocabulary and identity chain; do not create a second lifecycle model |
| Multi-agent control-plane sequence | [AGENT-TEAM-CONTROL-PLANE.md](AGENT-TEAM-CONTROL-PLANE.md) | Scout → MVT/DoE → telemetry → bilateral review → promotion → synthesis | Coordinate reasoning and evidence around this sequence; do not invent a parallel promotion pipeline |
| QUE queue projections | [que-queue-feed.json](../../ops/que/feeds/que-queue-feed.json), [queue-by-tier.json](../../ops/que/feeds/queue-by-tier.json) | Generated queue and tier feeds | Read-only observation; never write queue state through a generated feed |
| Project-task intake | [project_task.py](../../scripts/dispatch/project_task.py) | Parses the project-task issue-form body and produces an intake representation | Brain may prepare a task proposal; canonical intake remains the parser/issue contract |
| Claim and lease | [claim_task.py](../../scripts/dispatch/claim_task.py), [auto_claim.py](../../scripts/dispatch/auto_claim.py) | Claim/lease step and watchdog claim decision logic | Brain cannot claim, renew, steal or release a lease |
| Lane-aware admission | [dispatch_admission.js](../../scripts/ci/dispatch_admission.js) | Quota/lane-aware admission before dispatch | Brain supplies a candidate; admission owner decides eligibility |
| Admitted dispatch and execution trigger | [dispatch_executor.py](../../scripts/ops/dispatch_executor.py) | Converts admitted, dispatch-queued and unclaimed work into producer claim and build-dispatch fire | Brain requests handoff through the existing executor; it does not fire workflows or devices |
| Capability and device safety policy | [hub_mcp/policy.py](../../hub_mcp/policy.py) | Named capability policy; deliberately rejects arbitrary shell text and caller-provided executable fragments | Brain selects named capability IDs; policy owner authorizes them |
| Context relationship graph — build | [build_index.py](../../archwiz/context_relationships/build_index.py) | Builds and atomically publishes the canonical context-relationship index | Read adapter only; graph construction and publication remain with CRG |
| Context relationship graph — query | [query.py](../../archwiz/context_relationships/query.py) | Searches the compiled relationship index and renders bounded timelines/Mermaid | Use query results with source references and bounded scope |
| Context relationship graph — temporal | [temporal.py](../../archwiz/context_relationships/temporal.py) | Immutable temporal snapshots and deterministic deltas | Use snapshot/delta references; do not create a second history store |
| CRG Rust acceleration | [rust_accel.py](../../archwiz/context_relationships/rust_accel.py), [polyglot acceleration contract](../ops/CONTEXT-RELATIONSHIP-POLYGLOT-ACCELERATION.md) | Optional Rust hot-path adapter; Python remains authoritative | Reuse the documented JSONL/polyglot pattern; never replace Python authority by implication |
| ICM knowledge projections | [Context Relationship Index object](../icm/objects/knowledge/context-relationship-index.md), [ICM index](../icm/objects/_index.md) | Governed knowledge-object descriptions and navigation | Brain reads ICM metadata; ICM remains the knowledge-object authority |
| Provider catalog protocols | [provider_catalog_protocols.py](../../scripts/provider_catalog_protocols.py) | Fixed-host catalog protocols, bounded pagination and unknown-price handling | Use as a safe source adapter; no provider selection authority |
| Provider model evidence | [provider_model_catalog.py](../../scripts/provider_model_catalog.py) | Polls model catalogs and normalizes access/quota evidence; catalog state is evidence, not routing policy | Feed capability discovery with timestamped evidence; do not infer entitlement or route on catalog presence |
| Provider routing governance | [Provider Routing object](../icm/objects/knowledge/provider-routing.md) | Documents provider routing governance | Delegate route choice and quota enforcement to the existing router/governance |
| Quota and dispatch tier model | [dispatch-tiers.json](../../ops/quota/dispatch-tiers.json) | Defines quota/dispatch chains and tier relationships | Read constraints; never create a parallel quota ledger or countdown |
| LLM-map context cache | [context_cache.py](../../workspace/llm_map/context_cache.py) | Caches orchestrator context bundles by file-content hashes | Reuse or adapt only after cache invalidation/authority contract is verified |
| LLM-map agent suggestion | [manager_agent.py](../../workspace/llm_map/manager_agent.py) | Keyword/path scoring and agent suggestion | Treat as a candidate-discovery heuristic, not a capability registry or final dispatch decision |
| LLM-map task dispatch | [dispatch_task.py](../../workspace/llm_map/dispatch_task.py) | Working task dispatcher with logging | Reconcile with canonical QUE/dispatch before integration; do not assume it is the current authority |
| Comparative deterministic decision engines | [decision_engines.py](../../scripts/decision_engines.py) | System-1/schema decision engines used as pre-gates; explicitly not the LLM provider catalog | Call through a typed adapter where a registered deterministic pre-gate fits |
| Existing Python orchestration runtime | [orchestrator.py](../../src/orchestrator.py) | Provider calls, code patching, tests, telemetry, retries and rollback are currently combined in one orchestrator | Treat as an existing harness/adapter target; do not silently replace or claim a Rust runtime cutover |
| Delphi RFP gate | [gate.py](../../scripts/delphi/gate.py), [Delphi gate contract](../ops/DELPHI-ORACLE-RFP-GATE.md) | Transparent rubric-based RFP admission; model voting requires a separate configuration | Brain can prepare evidence and explain results; gate score is not task verification, architecture merit or runtime authority |
| Delphi RFP comparison feed | [rfp_flood_feed.py](../../scripts/delphi/rfp_flood_feed.py), [segmentation contract](../ops/DELPHI-RFP-SEGMENTATION.md) | Collects RFP records and assigns explicit segment membership | Brain can analyze segment evidence; it cannot award itself a disposition |
| Research templates and citations | [refTemplates source map](../../refTemplates/00_Index/SOURCE-MAP.md), [Brain research dossier](../../refTemplates/17_Papers/citations/brain-file-and-agent-architecture-survey.md) | Research-source discovery, provenance, linked slots and citation records | Brain consumes qualified references; a link is not an adopted dependency or reproduced result |
| Owner / architecture navigation | [Monorepo Brain ICM object](../icm/objects/operations/monorepo-brain.md), [ICM index](../icm/objects/_index.md) | Owner-facing architecture and knowledge navigation | Expose explanations, evidence and intervention state; do not claim that a dashboard grants authority |

## Explicit gaps and unverified contracts

The following must remain explicit dependencies until the exact owner and versioned contract are inspected:

- Exact QUE/QDesk owner interface and admission receipt contract for the first vertical slice.
- Genome component semantics and its versioned interface to Brain.
- Canonical participant identity, authority freshness, pause and revocation API.
- Dispatch idempotency key, claim lease semantics, attempt correlation and late-result reconciliation.
- Runtime task verification contract that distinguishes workflow success from TASK_PASS/FAIL/UNKNOWN.
- Persistent memory write contract and owner approval for learning-candidate promotion.
- Provider routing API and the current source of quota entitlement.
- Owner cockpit projection contract for ArchWiz/Tribute.

No source-inspection result in this document upgrades those dependencies to verified.

## Brain's own module boundaries

The Rust kernel remains the shared typed reasoning core. The broader subsystem should be modularized behind explicit traits/adapters, not one giant `brain.rs` implementation:

| Proposed module family | Responsibilities | Canonical external owner |
|---|---|---|
| `identity_intent` | Request identity, actor scope, intent and complexity | Existing identity / intake |
| `perception` | Event, repository, issue, log and artifact ingestion | GitHub, QUE feeds, CRG, provider catalogs |
| `context` | Provenance, freshness, sensitivity, relevance and budget | ICM, CRG, context cache |
| `knowledge` | Repository ontology, relationships and source graph | ICM / CRG |
| `research` | Literature, GitHub implementation and citation intelligence | refTemplates / research lanes |
| `capabilities` | Discover and describe existing tools, skills, agents and providers | hub_mcp / provider catalog / GitHub workflows |
| `reasoning` | Intent, decomposition, strategy, execution design, validation, optimization, reflection | Rust kernel |
| `planning` | Typed plan DAG, dependencies, parallel groups and expected outcomes | Existing scheduler/dispatch owns execution |
| `simulation` | Candidate scenario analysis and experiment design | Existing DoE / decision engines |
| `policy` | Policy input and explanation only | Existing hub_mcp and authority owners |
| `coordination` | QUE/QDesk shadow proposal and receipt correlation | Existing QUE/QDesk |
| `execution_observation` | Observe admitted workflow/device activity | Existing Harness/Hands and Actions |
| `verification` | Evidence binding and outcome classification | Existing validators / evidence ledger |
| `telemetry` | Run traces, stage timing, degradation and resource observations | Existing telemetry/ops |
| `learning` | Reflection candidates, experiment deltas and promotion requests | Delphi / DoE / memory owner |
| `resilience` | Timeout, retry, cancellation, rollback and recovery recommendations | Existing execution owners |
| `security` | Prompt/data trust, secret boundaries and capability constraints | Existing security and policy owners |
| `swarm` | Role specialization, delegation and consensus evidence | Existing agent-team control plane |
| `domains` | Specialized scientific, operational and application cognition | Domain-specific owner |
| `owner` | Explanation, review, pause, revocation and intervention projections | ArchWiz / Tribute / QDesk |

These module names are proposed Rust boundaries, not claims that the files already exist.

## Delivery phases and gates

| Phase | Brain capability | Allowed behavior | Exit evidence |
|---|---|---|---|
| P0 | Ownership/source reconciliation | Read-only source inspection and documentation | This map plus pinned, verified contracts |
| P1 | Rust kernel hardening | Deterministic reasoning tests; no execution | Format, check, test and Clippy green |
| P2 | Knowledge adapters | Read-only ICM, CRG, refTemplates and catalog reads | Provenance, freshness, sensitivity and adapter contract tests |
| P3 | Repository ontology and capability map | Read-only graph/projection | Duplicate detection and canonical-owner references |
| P4 | QUE/QDesk shadow handoff | Proposal/receipt only; no claim, dispatch or execution | Idempotent correlation and zero canonical state mutation |
| P5 | Authorized vertical slice | Existing admission → dispatch → execution → verification only | Separate owner authorization and measured TASK_PASS/FAIL/UNKNOWN |
| P6 | Learning loop | Candidate generation and preregistered DoE only | Baseline comparison, held-out evidence and independent review |
| P7 | Owner cockpit | Explain, inspect, pause/revoke through existing controls | Verified projection and intervention contracts |
| P8 | Bounded autonomy evaluation | Only explicitly authorized, budgeted actions | Separate runtime authorization, rollback and stop-condition tests |

## Related records

- [Subsystem taxonomy](TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md)
- [qdesk.brain-rs RFP #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501)
- [Brain architecture segment PR #5503](https://github.com/timerloggedout-spec/termux-monorepo/pull/5503)
- [Kernel and architecture PR #5492](https://github.com/timerloggedout-spec/termux-monorepo/pull/5492)
