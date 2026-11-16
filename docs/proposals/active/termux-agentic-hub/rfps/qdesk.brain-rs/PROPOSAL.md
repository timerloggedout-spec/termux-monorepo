# qdesk.brain-rs — Rust Brain for the Termux Monorepo

**Status:** RFP package submitted through QUE/Delphi intake; admission parked; technical architecture evaluation pending  
**Surface ID:** qdesk.brain-rs · **Revision:** 1 · **Requested disposition:** evaluate fit and readiness  
**Implementation seed:** [PR #5492](https://github.com/timerloggedout-spec/termux-monorepo/pull/5492)  
**Branch:** feat/root-brain-rust-core-final · **Pinned filing source SHA:** 2532f3cd4372fecbbbf71c06b4fa7005f53c23d6  
**QUE/Delphi filing:** [Issue #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501) · **Authority:** Filing requests evaluation only; it grants no execution, deployment, merge, provider or permission authority.

## 1. Decision sought

Evaluate a Rust-based, repository-wide Brain as the shared consciousness/cognitive coordination layer of the Termux monorepo. Brain builds a current, evidence-grounded model of the repository, interprets owner intent, discovers existing capabilities, reasons and plans, requests action through existing authorized control planes, verifies outcomes, and proposes governed learning updates.

The root brain.rs kernel in PR #5492 is the first implementation slice, not the finished system. This RFP evaluates the complete subsystem roadmap and integration boundaries.

## 2. Architecture

- Controller/origin: Termux.
- Hub/execution station: GitHub and configured execution infrastructure.
- Owner interface: Android mobile, including Termux/ArchWiz/QDesk surfaces.
- Integration home: QUE / QDesk and the existing monorepo orchestration layer.
- Implementation language: Rust for the shared Brain core; adapters may use existing project languages.
- Existing surfaces to reuse: ArchWiz, HyperForge, ICM, Context Relationship Graph, hub_mcp, GitHub Actions, provider routing/3L0, QUE admission, dispatch/claim, evidence-led ops, Delphi/DoE, ForeSight/HindSight, adaptive-wait and SHE.
- Contracts to verify before adapters: exact QUE ownership/intake, QDesk/ArchWiz projection, genome component semantics, identity/authority, dispatch/claim/receipt, policy and memory APIs, Rust package placement and JSONL bridge.

Full design: [Monorepo Brain subsystem map](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md); [source-inspected ownership and integration map](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/docs/architecture/TERMUX-MONOREPO-BRAIN-OWNERSHIP-MAP.md).

## 3. Problem

Cognitive responsibilities are distributed across orchestrators, managers, agents, context/relationship graphs, memory stores, provider routers, capability registries, policy gates, task queues, workflows, tests, evidence stores, research lanes and dashboards. This is good separation of ownership, but no shared component consistently assembles repository-wide operational understanding and connects intent to evidence-backed decisions across those boundaries.

A monolithic replacement would be unsafe and duplicative. The proposal adds one cognitive layer that composes existing owners through typed adapters.

## 4. Hypotheses

1. A shared typed Brain contract reduces duplicated reasoning and inconsistent handoffs.
2. Provenance-aware context assembly reduces stale, irrelevant, sensitive or unsupported context.
3. A shared capability/ownership map reduces duplicate tools, registries and competing implementations.
4. Brain / Harness / Hands separation improves authority traceability and testable autonomy.
5. Decision-to-evidence links improve review, debugging and outcome attribution.
6. Reflection candidates tied to verified outcomes improve adaptation without self-awarded success.
7. Rust core plus versioned JSONL adapters creates a stable cross-language boundary without forcing Python migration.

## 5. Capabilities in scope

Repository perception and event normalization; identity- and intent-aware request interpretation; provenance/freshness/sensitivity/budget-aware context; read adapters over ICM, CRG, memory and reference catalogs; component ownership/dependency ontology; academic/FOSS research discovery and citation grading; capability discovery across tools/providers/MCP/workflows/agents/skills; typed reasoning, decomposition and bounded DAG planning; scenario evaluation through existing engines; delegation to policy and authority gates; QUE/QDesk admission and handoff; execution observation through existing Harness/Hands; evidence correlation and verification; reflection candidates through Delphi/DoE/ForeSight/HindSight; resilience signals; owner-visible decision and intervention projections.

## 6. Non-goals

- No replacement queue, scheduler, task tracker, claim/lease engine or dispatch controller.
- No replacement identity registry, capability registry, provider router, policy engine or completion gate.
- No second persistent memory database, relationship graph, telemetry ledger or outcome ledger.
- No direct tool/device execution from the Brain kernel.
- No automatic recursive clone or execution of refTemplates upstream installers.
- No automatic promotion, merge, deployment, credential creation or scope expansion.
- No assumption that all execution happens on Android.
- No Python requirement merely because public projects use brain.py.
- No claim to reproduce scientific results without independent reproduction evidence.

## 7. Research transfer

See [the full refTemplates/17_Papers dossier](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/refTemplates/17_Papers/citations/brain-file-and-agent-architecture-survey.md). The survey distinguishes neural-network modules, biological simulators, belief-updating agents, model gateways, application decision layers, autonomous loops, memory facades, safeguards, deterministic routers, log-parsing research and research-derived reimplementations.

Adopt patterns: brain/body separation; composable orchestration; memory facade separation; explicit belief/prediction modules; operational safeguards; deterministic baselines and abstention; research provenance. Limitations: README claims are not source proof; third-party reimplementations are not original paper artifacts; secondary analyses are lower confidence; filename identity does not establish architectural equivalence.

## 8. Integration and prohibited duplication

| Reuse | Brain addition | Prohibited duplication |
|---|---|---|
| ICM / CRG | Read-only context and relationship adapters | New ontology/graph store |
| QUE / QDesk | Typed decision handoff and result correlation | Queue or ticket lifecycle |
| hub_mcp | Capability metadata and policy request | Tool permission engine |
| Existing orchestrators / Actions | Plan-to-handoff adapters and observation | Scheduler or workflow engine |
| Provider routing / 3L0 | Provider capability signals | Provider catalog/quota authority |
| Existing memory systems | Retrieval and learning-candidate adapters | Canonical memory DB |
| Evidence-led ops | Evidence refs and outcome interpretation | Duplicate receipt ledger |
| Delphi / DoE | Candidate evaluation and measured adaptation | Parallel panel or score ledger |
| ForeSight / HindSight | Forecast/outcome interfaces | Second forecast ledger |

## 9. First vertical slice

Existing task/request → Brain context assembly → typed reasoning/plan → existing QUE admission → existing dispatch/claim → configured execution → authoritative verification → owner-visible feedback.

Start shadow/read-only before any action. Demonstrate correlation IDs and immutable evidence references end-to-end. The current kernel alone is not this complete slice.

## 10. Evaluation

**Baseline:** existing QUE/QDesk behavior and current orchestrator path on a comparable, pinned task cohort.

**Metrics:** verified completion rate; time to verified completion; duplicate/invalid handoffs; stale-context and unsupported-claim rate; evidence coverage; owner intervention and revocation latency; fallback/degraded rate; resource use per verified outcome; rollback/stop effectiveness; citation completeness and source freshness.

**Acceptance criteria:**
1. Reuse canonical identity, policy, queue, dispatch, memory and evidence owners.
2. Preserve source, freshness, sensitivity and evidence state for context.
3. Every plan step has stable identity, dependencies and verification criteria.
4. Existing owner revalidates authority at the execution boundary.
5. Workflow/run success is distinct from TASK_PASS and PROMOTABLE.
6. Stale, missing, conflicting or unsupported evidence fails closed or escalates.
7. Duplicate triggers and late results are idempotently correlated.
8. First vertical slice is tested against baseline and receipted.
9. Rollback disables Brain adapter without corrupting canonical state.
10. No provider inference or paid quota is assumed; unknown is not unlimited.

**Failure scenarios:** duplicate trigger; revoked authority; ineligible participant; quota changes after planning; workflow succeeds but acceptance fails; controller disconnect; stale context; late result after newer attempt; policy unavailable; provider fallback; prompt injection; secret contamination; partial execution; rollback failure.

## 11. Delivery phases

| Phase | Deliverable | Exit criteria |
|---|---|---|
| P0 | Source and ownership reconciliation | Current contracts and duplicate census pinned |
| P1 | Rust cognitive kernel | fmt/check/test/clippy green |
| P2 | Read-only knowledge adapters | ICM/CRG/refTemplates/evidence provenance verified |
| P3 | Capability and ontology map | Existing registries reused; unknowns explicit |
| P4 | Shadow QUE/QDesk handoff | No execution; idempotent decision receipts |
| P5 | Authorized end-to-end vertical slice | Existing admission/dispatch/execution/verification only |
| P6 | Delphi/DoE learning loop | Preregistered metrics, held-out evidence, no self-grading |
| P7 | Owner cockpit integration | Inspect, pause, revoke and explain controls |
| P8 | Controlled bounded autonomy | Separate authorization, budgets, rollback and stop tests |

## 12. Rollback and stop conditions

Rollback disables the Brain adapter or returns selection to the existing orchestrator; preserves canonical task/dispatch/execution/verification records; does not rewrite queue state or historical evidence.

Stop/park if existing capability is sufficient; integration bypasses identity/policy/QUE/admission; duplicate execution cannot be bounded; provenance/sensitivity cannot be preserved; a parallel control plane is required; evaluation shows no useful improvement; or research evidence is too weak.

## 13. Authority

- filing_grants_execution: false.
- Intended future mode: bounded_autonomous, only after separate admission and authorization.
- Authority contract status: unverified until current owner contracts are inspected.
- Required controls: canonical identity; existing admission/claim; execution-boundary authority revalidation; bounded retries/resources; owner pause/revocation; explicit escalation; no secrets in receipts.
- Escalate on scope expansion, missing/conflicting authority, budget increase, new privileged path or verification-policy change.

The filing requests Delphi fit/readiness evaluation. It does not submit scores, assert consensus, claim an award, authorize unscoped implementation, or activate runtime autonomy.

## 13a. Delphi admission outcome

The existing `delphi:rfp` gate processed [issue #5501](https://github.com/timerloggedout-spec/termux-monorepo/issues/5501) and recorded **parked, 6.69/25**, after three rubric rounds, with recheck after **2026-12-16T09:39Z**. The gate did not find this proposal in `ops/delphi/surfaces.json`, so it treated the RFP as an unsourced synthetic surface. The resulting score is an admission/backlog classification, not an independent technical evaluation of the Brain architecture and not an implementation authorization.

To make the comparison context explicit without changing gate scoring, [PR #5503](https://github.com/timerloggedout-spec/termux-monorepo/pull/5503) registers a dedicated `brain-architecture` segment in the existing RFP feed. That segment evaluates the proposal against its own ownership, evidence, authority and vertical-slice criteria. It creates no new panel or scoring engine.

## 14. Open questions

1. Which exact QDesk/QUE owner interface governs the first vertical slice?
2. What does the repository's genome component mean, and what is its versioned Brain interface?
3. Which Rust package and JSONL bridge convention should be canonical?
4. Which Delphi method revision governs this filing?
5. Which owner-facing cockpit projection is authoritative for Brain decisions?
6. Which source owns participant identity and runtime revocation?

## 15. Evidence links

- [Root Brain kernel PR #5492](https://github.com/timerloggedout-spec/termux-monorepo/pull/5492)
- [Native Orchestration Contracts](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/ORCHESTRATION-CONTRACTS.md)
- [Delphi Oracle RFP Gate](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DELPHI-ORACLE-RFP-GATE.md)
- [Delphi lane contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/DELPHI-LANE-CONTRACT.md)
- [refTemplates consolidation](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/REFTEMPLATES-CONSOLIDATION.md)
- [refTemplates recovery](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/refTemplates/00_Index/RECOVERY.md)
- [refTemplates source map](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/refTemplates/00_Index/SOURCE-MAP.md)
- [refTemplates continuous evaluation](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/REFTEMPLATES-CONTINUOUS-EVAL.md)
- [Brain research dossier](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/refTemplates/17_Papers/citations/brain-file-and-agent-architecture-survey.md)
- [Subsystem map](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/docs/architecture/TERMUX-MONOREPO-BRAIN-SUBSYSTEM-MAP.md)
- [Proposed filing schema](https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/root-brain-rust-core-final/docs/schemas/delphi-rfp-filing.schema.json)

**Evidence status:** owner directives, repository implementation and external research are distinct evidence classes. External sources retain individual verification status and limitations.
