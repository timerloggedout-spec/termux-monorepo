# Status and Findings — Simulation Intelligence Plane

Date: 2026-11-14  
State: proposal and initial design package in parallel branch; no runtime implementation or live validation claimed.

## 1. Repository reconnaissance findings

### Confirmed existing substrate
- Integration Intelligence architecture and registry exist (merged PR #4009).
- Adapter contract defines bounded provider translation, lifecycle, provenance, read-only defaults and validation requirements.
- CEEL defines normalized event handling, idempotency, retries, redaction and least-privilege dispatch.
- ATES defines orchestrator trace schema, deterministic-first evaluation, bounded judge weight and optional MLflow projection.
- DoE is a family; MVT is a member. Existing experiment record schema is the shared family contract.
- Delphic Observatory PR #5408 proposes deterministic graph, Bayesian, information-theoretic, EVSI, Markov and expected-path-cost engines plus a read-only DoE candidate packet adapter.
- Workflow Planning Operating Model PR #5388 proposes WFC and explicit QUE × DoE optimization while reusing the existing DAG planner. Its PR status/base must be checked before depending on its files.
- Existing DoE simulation work (e.g. MSM-026 economy backtests and field-simulation forecast work) demonstrates repository familiarity with deterministic seeded simulation, paired policy comparisons and immutable manifests. These are not the same as social multi-agent simulation.

### Adapter and control-plane reconciliation

- PR #4086 adds read-only provider evidence adapters and explicitly reuses existing router/capability-spine machinery rather than adding a duplicate router. It is a strong precedent for SIP's pure normalization boundary.
- PR #5438 / #5437 establish an additive serialization adapter pattern: JSON remains canonical, external notation is an adapter, and QUE routing remains opt-in. SIP follows the same canonical-contract approach.
- PR #5222 documents swarm-routing control-plane reconciliation, contract/runtime matrix, supersession register and unresolved composition questions.
- PR #5029 establishes the Repository Intelligence & Collaboration Data Plane (RIDP); SIP must consume its repository intelligence rather than create a parallel data plane.
- PR #5170 defines control-plane implementation contracts including capability registration, bounded dispatch, action/effect receipts and Admin Graph read model.
- PR #5042 is the successor demand-driven lane matrix / Plan Canvas implementation; PR #5012 is its superseded draft.
- PR #5194 / #5198 establish the DoE agentic logistics/free-inference control-plane proposal; SIP is not a competing logistics or provider-routing controller.
- PR #5388 proposes the Workflow Contract connecting QUE, routing, PDDL/HTN, DoE/MVT and evidence while reusing the existing DAG planner. The contract was inspected on branch `feat/workflow-planning-operating-model`; its PR merge/rebase state must be verified before depending on its paths.
- Branch-name reconnaissance also surfaced `control-plane-inventory-1`, `control-plane-readmodel`, `feat/hitl-control-plane-739`, `feat/ops-hitl-control-plane`, `feat/agent-toolchain-adapters`, `feat/system-one-adapter`, `feat/temporal-langsmith-adapter`, `feat/unified-feed-adapter-20261114`, `feat/web-adapter-foundry` and `test/llm-adapters`. A branch name is discovery evidence only; these are not all verified as merged or runtime-active.

The resulting boundary is: SIP provides a domain adapter and simulation evidence model. It does not own admission, workflow planning, control-plane read models, provider routing, generic adapter infrastructure, or the canonical repository intelligence graph.

### Not yet confirmed
- No verified MiroFish or OASIS adapter in the default-branch code search performed for this proposal.
- No verified runtime deployment, credentials, package install, provider access or successful end-to-end run.
- No approved graph snapshot/cohort selected for a first pilot.
- No license compatibility decision for MiroFish-derived code.
- No explicit resource budget or human factual-promotion owner assigned.

Absence from a bounded search is not proof of absence from every branch, private fork or external runtime. This audit should be extended to all active branches and relevant PRs before implementation expands.

## 2. External source register (research baseline)

- MiroFish upstream: https://github.com/666ghj/MiroFish
- MiroFish refactor reference: https://github.com/mj3b/MiroFish
- CAMEL-AI OASIS: https://github.com/camel-ai/oasis
- OASIS docs: https://docs.oasis.camel-ai.org/
- Mesa ABM: https://mesa.readthedocs.io/
- Temporal: https://temporal.io/
- LangGraph: https://github.com/langchain-ai/langgraph
- NetLogo: https://www.netlogo.org/
- Repast: https://repast.github.io/

Source claims, versions, licenses and capabilities are provisional until exact source files/tags are fetched and pinned in the source register. The research snapshot used for initial concept framing reports MiroFish AGPL-3.0 and OASIS Apache-2.0; do not treat those as legal conclusions without exact-version verification.

## 3. MiroFish workflow details to validate

Reference stages:
1. source/document ingestion;
2. ontology extraction;
3. graph construction and backend persistence;
4. entity/agent filtering;
5. persona construction;
6. OASIS social simulation execution;
7. graph-memory/state update;
8. report generation;
9. post-run interview/chat.

The refactor reference emphasizes a consolidated workbench core, resource adapters, composable tools and thin API shells. SIP adopts the architecture principle, not the upstream code by default.

## 4. OASIS capability hypotheses to test

- Platform-oriented social environment and agent actions.
- Customizable agent models, prompts and tools.
- Environment reset/step/close lifecycle.
- SQLite or other configured persistence.
- Recommendation/environment dynamics.
- Multi-agent scale and token/cost growth.
- Multi-platform coordination and process supervision.

OASIS documentation has described very large populations; headline scale claims must not be assumed achievable in this repository's resource envelope. Begin with small deterministic/offline fixtures, then bounded sandbox tests.

## 5. Known upstream lifecycle hazards to include

- Completion event emitted while subprocess remains alive in IPC wait mode.
- Monitor incorrectly waits for process exit before recognizing all-platform completion.
- Finalization/report availability must follow successful run completion, not a superficial status flag.
- Graph build/provider authentication failures should be retryable only where idempotency and state integrity are established.
- Saved-run recovery and stale runner detection require explicit tests.

These are failure classes to test, not claims that the repository has inherited the same defects.

## 6. Architecture decision (provisional)

Adopt:
- QUE + WFC for admission and workflow definition;
- DoE for experimental design;
- OASIS as first candidate social simulator;
- MiroFish as workflow/reference architecture;
- Delphic and existing graph engines for graph/decision analysis;
- ATES for traces and deterministic evaluation;
- CEEL/Integration Intelligence for events and adapter governance;
- a deterministic fake engine as the offline contract oracle.

Do not adopt:
- a second scheduler or queue;
- a second experiment registry;
- a second event bus;
- an autonomous factual-graph merge;
- a copied AGPL implementation before review;
- live model/provider calls in ordinary CI.

## 7. Immediate next research

1. Inspect active PR #5388 and rebase status; align WFC fields exactly.
2. Inspect #5408 exact head and its graph/candidate packet contract.
3. Read the current experiment schema and DoE campaign registry to define one-record-per-run mapping.
4. Verify MiroFish and fork commit/license/dependency state.
5. Verify OASIS release, API, platform semantics and lifecycle.
6. Compare Mesa and deterministic baseline against OASIS with a common frozen cohort.
7. Review existing context-relationship graph storage and historical backfill boundaries before defining graph adapter.
8. Search all branches/PRs for existing simulation, adapter, control-plane and process-supervision work.

## 8. Decision log

| ID | Decision | State | Rationale |
|---|---|---|---|
| ADR-SIP-001 | SIP is a workload/domain adapter, not a control plane | proposed | Preserve QUE authority and avoid duplicate scheduler |
| ADR-SIP-002 | OASIS is the primary pilot candidate, not a hard schema dependency | proposed | Social simulation semantics with pluggable engine boundary |
| ADR-SIP-003 | MiroFish is a workflow/reference implementation | proposed | Useful graph-to-agent pipeline; license and coupling require review |
| ADR-SIP-004 | Source/derived/simulation graph layers stay separate | proposed | Prevent synthetic output contaminating factual graph |
| ADR-SIP-005 | Deterministic fake engine is mandatory | proposed | Offline reproducibility and CI safety |
| ADR-SIP-006 | DoE/ATES/CEEL existing records are reused | proposed | No parallel evidence or evaluation framework |

## 9. Open decisions
- First graph/evidence cohort and its owner.
- Exact MiroFish source fork and legal posture.
- Exact OASIS version and supported platform.
- Model-provider allowlist and no-cost/offline pilot mode.
- Initial maximum agents, steps, activation, concurrency, time and cost.
- First outcome rubric and ground-truth fixture.
- Factual graph promotion authority and review protocol.
