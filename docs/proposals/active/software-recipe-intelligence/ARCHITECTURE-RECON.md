# Architecture Recon — Software Recipe Intelligence

**Decision state:** ownership unresolved by design.  
**Question:** where should a cross-cutting software-recipe intelligence capability live, and which existing systems should consume it?

## 1. Confirmed repository prior art

### Recipe systems already exist

**Repo Replay** is owned by its own repository, `timerloggedout-spec/repo-replay`, with `replay-store/v1` and RevWright. The monorepo imports methods by reference and is a consumer/test subject. Its recipe is based on ordered session/message/block/hash pointers plus operations; its own history is a DAG distinct from Git history.

**Commit Replay** is a separate Git-plane design in this monorepo. It uses `commit-store/v1`, fragment-level Git pointers, and `grecipe/v1`. Its source is Git objects and history; it explicitly keeps its index separate from Repo Replay's session-provenance index. It is not a repository rebuild product.

**Implication:** do not create a third file-reconstruction or pointer-replay engine. The proposed model must represent higher-order capability contracts and lifecycle evidence, and link to these specialized recipe artifacts where appropriate.

## 2. System landscape and candidate relationships

| Existing system / authority | Confirmed responsibility from repository sources | Potential contribution | Ownership decision |
|---|---|---|---|
| Repo Replay (external repo; imported by reference) | Session-provenance recipe/pointer composition and replay plane | Source recipe/provenance adapter; avoid reimplementing methods | Not owner by default |
| Commit Replay | Git-object/fragment pointer recipes and Git-plane composition | Code-fragment ingredients, Git provenance, safe materialization references | Not owner by default |
| Monorepo Brain (PR #5492) | Proposed repository-wide cognitive coordination layer; subsystem map includes a distinct `domains` / domain-cognition family with shared Brain contracts. The ownership map explicitly keeps execution, policy, memory, routing, verification and evidence with existing owners. | Candidate integration contract or software-domain cognition package; reuse its typed reasoning and domain interfaces if admitted. | **Strong candidate interface to investigate, not an assigned owner.** PR #5492 is open and unmerged at this snapshot. |
| MOSAIC Brain (PR #5502) | Dedicated ArchWiz subsystem, crate `mosaic-brain`, scope `methodology_intelligence`, advisory-only recommendations over CRG/ICM/DoE/Delphi evidence. | Consume methodology/experiment recipe references and evaluate methodology treatments. | **Not the owner for broad software capability recipes.** PR #5502 is open and unmerged at this snapshot. |
| Agent Team Control Plane / Agent Team Orchestration | Existing manager/router/specialist/evidence-collector/review/MoneyBall/3L0/BIUDL operating model; provider and agent identities remain distinct. | Agent/team/workflow recipe source and composition contract. | Existing orchestration authority; do not create another manager, router, roster or control plane. |
| Native Orchestration Contracts | `ORCHESTRATION-TREATMENT.schema.json` defines repeatable orchestration treatments; `ORCHESTRATION-RECEIPT.schema.json` defines one cycle receipt. | Reuse the treatment schema for orchestration/workflow recipe instances and the receipt schema for execution observations. | **Direct overlap.** Do not create a second orchestration-treatment or run-receipt schema. |
| Termux Multi-Agent | Existing `termux-multi-agent/` implementation/documentation describes task registry, agent provisioning, scheduler, dashboard and CedarScript MCP. | Agent recipes and local execution-environment references. | Existing implementation surface; current live runtime/deployment state not verified in this recon. |
| Temporal Durable Execution / AI Cookbook | Existing RECON/RFP/PASS records an Oracle Method cycle and evaluates ai-cookbook patterns (agentic loop, HITL approval, deep research), with no Temporal substrate selected. | Workflow recipe starters, durable wait/resume and idempotency patterns. | Pattern source and experiment history; not a selected runtime or new orchestration owner. |
| System One classifier census | Existing classifier/decision-system research inventory. | Candidate algorithm adapters and classification baselines. | Research catalogue, not a new classifier registry or proven deployed classifier. |
| Agent Evaluation Lane Registry | Existing evaluation taxonomy separates repository-native evidence, ATES/3L0, external evaluators, SWE cohorts and local harnesses. | Evaluation contracts and evidence adapters for recipe quality. | Observational adapters only; repository evidence remains canonical. |
| Integration Intelligence | Canonical integration registry, normalized event contract, provider adapters | Integration/capability identity, source evidence, provider state | Existing authority to reuse |
| CEEL | Continuous capability discovery, classification, mapping, proposal, experiment, verification, integration, measurement and evolution | Discovery/evolution lifecycle | Existing process lane; not a duplicate orchestrator |
| Context Relationship Graph (CRG) | Metadata-only, evidence-backed relationship graph with verified/candidate distinction | Relationships between recipes, source files, symbols, PRs, issues and capabilities | Existing graph authority; projection only |
| DoE / MVT | Experiment family and canonical `EXPERIMENT.schema.json` | Controlled comparison and run observations | Existing experiment authority |
| Delphi / EGM | Independent challenge/admission | Independent review of proposals and claims | Existing admission authority |
| SHE / 3L0 / MoneyBall / ATES / WTCV / TCV / TPV | Outcome, quality, throughput, cost and operational evidence surfaces | Recipe outcome dimensions and evaluation projections | Existing evaluation authorities |
| ICM / proposal registry | Ownership, navigation, lifecycle and source routing | Identity and lifecycle references | Existing registry authority |
| Linguist / Siglary / Grimoire / Name Forge | Notation, nomenclature, vocabulary, alias and crosswalk governance | Human/machine labels and collision review | Existing naming authorities |
| Kahn DAG / Gantt / existing planners | Dependency ordering and planning primitives | Procedure DAGs and scheduling references | Reuse after contract validation |
| Agent teams / Jules / skills / workflows | Isolated agent tasks, skill-defined procedures, CI-triggered work | Agent and workflow recipe sources | Adapters; no new orchestrator assumed |
| Termux MCP stewardship | Device-aware, lean-worktree, read-only-first operational discipline | Local execution constraints and bounded apply process | Operational source; not the recipe owner |

The table distinguishes confirmed responsibilities from candidate contributions. It does not establish implementation maturity, live deployment, or ownership beyond the cited repository records.



### Deployment and maturity snapshot (2026-11-16)

- **Monorepo Brain — PR #5492:** open, non-draft, unmerged. The branch contains a Rust kernel, tests, and a source-inspected ownership/subsystem architecture. Its design defines domain cognition as one subsystem family; it does not establish that the kernel is deployed or that any particular domain package is admitted.
- **MOSAIC / MOSAIC Brain — PR #5502:** open, non-draft, unmerged. The branch is a methodology program/specification and implementation plan. MOSAIC Brain's declared scope is `methodology_intelligence`, with advisory-only output; this is narrower than the software capability/recipe domain.
- **Termux Multi-Agent:** implementation files and operator documentation exist on `master`; documentation describes how to run provisioning, scheduling, dashboard and MCP components. This recon did not start the runtime or verify current device deployment.
- **Agent Team Control Plane / Agent Team Orchestration:** canonical architecture and schemas exist on `master`; the roster distinguishes providers, models, agents, adapters and roles. A roster entry or catalog probe does not prove a configured execution adapter or active deployment.
- **CEEL / Integration Intelligence:** architecture, registry and lifecycle specifications exist. CEEL is explicitly a discovery/evolution lane that reuses Integration Intelligence, DoE, ATES, Delphi and proposal authorities; it is not a second control plane.
- **Temporal Durable Execution:** a PASS record documents a completed research/experiment cycle on 2026-10-27. The pass records candidate patterns such as `cookbook-agent-loop`; it does not mean Temporal was selected as the fleet execution substrate.
- **System One classifier census:** a research inventory exists; no assumption is made here that its candidates are deployed as a unified classifier runtime.

This is a repository artifact/status snapshot, not a device-health or live-runtime audit. “Implemented in repository,” “documented as runnable,” “workflow configured,” “connected in this session,” “validated,” and “deployed” remain separate states.

### Most plausible integration hypothesis — not a placement decision

The Monorepo Brain subsystem map's **domain-cognition** family is a plausible shared contract for a software-domain package. That is materially different from making the entire capability a child of MOSAIC Brain. The broad recipe model may instead be a shared domain contract with adapters to Repo Replay, Commit Replay, orchestration treatments, agent/team systems, Integration Intelligence, DoE, CRG and existing Brain interfaces. The system-wide ownership and interface census must test these options before an owner is selected.

## 3. Responsibility boundaries to preserve

- A recipe is a **description and contract**, not an executable permission token.
- An ingredient reference does not confer access to that ingredient.
- A procedure step does not authorize an external write, secret read, deployment, financial action, or production operation.
- CRG relationships are metadata projections; no second graph database.
- Integration Intelligence remains authoritative for integration identity/event contracts; no parallel provider registry.
- DoE records remain in the canonical experiment schema; no second experiment ledger.
- CEEL coordinates discovery/evolution; no second scheduler or evolution control plane.
- Delphi/EGM and repository admission gates remain independent; no self-review or self-promotion.
- Existing Repo Replay and Commit Replay remain distinct and must not be merged or conflated.
- Brain ownership remains open until subsystem contracts, deployment state, dependencies, and source ownership are verified.

## 4. Model boundaries and capability layers

The model should describe at least these layers without requiring a single runtime:

1. **Atomic technique:** algorithm, function, command, tool, API operation, test, transformation.
2. **Component recipe:** composition of atomic techniques with dependencies and contracts.
3. **Workflow recipe:** ordered/conditional/parallel/wait/retry procedure with stop semantics.
4. **Agent recipe:** role, model/provider reference, skill set, tools, context contract, constraints, verification and handoff.
5. **Team recipe:** multiple agent roles, task partitioning, coordination, independent review and integration contract.
6. **Integration recipe:** provider identity, adapter contract, event schema, auth boundary by reference, idempotency and evidence.
7. **Experiment recipe:** question, baseline, factors, arms, randomization/blocking, outcomes, analysis and stopping criteria.
8. **Operational recipe:** environment, resources, recovery, rollback, health checks, observability and operator gates.
9. **Composite capability:** a versioned DAG of recipes with compatibility and provenance constraints.

These are model classes, not a mandate to create separate services.

## 5. Candidate architecture shapes to compare

| Shape | Description | Benefits | Risks / test |
|---|---|---|---|
| A. Shared domain model + adapters | One neutral schema and validators; existing systems remain owners of their own runtime and evidence | Lowest duplication; broad reuse | Must avoid creating an unowned abstraction with no steward |
| B. Capability inside an existing system | Select one current owner after capability/authority mapping | Fewer moving parts | High risk of forcing broad semantics into a narrow subsystem |
| C. Federated projections | Small local models/projections linked by stable IDs and existing registries/CRG | Preserves specialized ownership | Cross-system consistency and versioning complexity |
| D. New standalone subsystem | Only if no current owner can meet the capability contract | Clear dedicated lifecycle | Highest duplication, operations and governance cost; require demonstrated gap |

**Current recommendation:** evaluate A and C first. Do not select B or D until the ownership census and interface review are complete.

## 6. Technical model

A recipe record should include:

- identity: stable ID, schema version, revision digest, aliases, status, owner reference (nullable until assigned);
- intent: objective, scope, acceptance contract and non-goals;
- ingredients: typed source/dependency/API/data/configuration/tool/policy/runtime/subrecipe references with version and digest;
- preparation: parsing, normalization, preconditions, environment checks, unresolved assumptions;
- procedure: typed operations, dependencies, branches, loops, parallel groups, waits, retries, timeouts, idempotency, effect class and policy reference;
- environment: OS, runtime, toolchain, image, resources, network policy and reproducibility;
- outputs: typed result/artifact/interface and side-effect declarations;
- evaluation: tests, quality, reliability, security, cost, latency, human rework, uncertainty and abstention;
- provenance: source commit, immutable references, extractor/model versions, timestamps and evidence class;
- lineage: parent/superseding revisions, derivation and rollback references.

Keep declared, extracted, inferred, tested, observed, independently verified, disputed, stale and unavailable facts distinct. Similarity is not equivalence. Missing evidence is not a zero score.

## 7. Intelligence methods to compare independently

- Deterministic metadata/rules baseline.
- Multi-label statistical classification (e.g. Naive Bayes/logistic regression).
- Lexical similarity (TF-IDF/token overlap).
- Structural extraction and comparison (Tree-sitter AST/CST).
- Dependency/call-graph and typed CRG traversal.
- Ingredient/contract similarity with normalization and weights.
- Embedding retrieval and evidence-aware reranking.
- Sequence/state-machine analysis for workflow recipes.
- Anomaly detection for drift, missing dependencies, and inconsistent declarations.
- Constraint-based composition/ranking with explicit abstention.

Classification, similarity, duplicate detection, compatibility, change-impact prediction, retrieval, and composition are separate tasks with separate labels and metrics. Do not pick one model and claim it solves all of them.

## 8. Evidence and experiment design

Use the canonical DoE family and `docs/ops/corpus/EXPERIMENT.schema.json`. Start with existing repository search/metadata as A0; compare deterministic extraction, statistical classification, structural/graph features, and embeddings as isolated treatments. Block by language, repository, capability family, difficulty and source age. Prevent near-duplicate and temporal leakage. Use held-out repositories or later time windows for confirmation.

Primary outcomes: top-k retrieval relevance; macro/micro F1 and calibration; duplicate precision/recall; compatibility false-positive rate; change-impact precision/recall; reproducibility on eligible tasks. Secondary outcomes: latency, token/compute cost, index size, review burden, rework, abstention and maintenance cost.

Do not use one opaque composite score to erase trade-offs. Keep safety failures non-tradeable.

## 9. Admission and safety

Initial phase is read-only extraction, analysis and recommendation. Recipe execution is a separate future workstream requiring an explicit threat model, isolated runtime, deny-by-default network, scoped credentials, resource/time caps, artifact quarantine, deterministic receipts, cancellation, and independent review. No model-generated recipe can grant itself authority.

## 10. Decisions still open

- Canonical owner/steward and consuming systems.
- Whether the model is shared, federated, or an extension.
- Exact schema namespace and identifier scheme.
- CRG edge mapping and publisher path.
- Integration registry references and capability IDs.
- How Repo Replay/Commit Replay artifacts are represented without conflating their planes.
- Name and acronym after Name Forge/registry/external collision review.
- Which initial cohort provides the strongest measurable benefit.

These decisions must be resolved from source-owner evidence, not from naming similarity or the presence of a Brain in a title.
