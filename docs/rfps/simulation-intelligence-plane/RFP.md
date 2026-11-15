# RFP — Simulation Intelligence Plane (SIP)

**RFP ID:** SIP-RFP-001  
**Status:** Draft for parallel research and technical evaluation  
**Owner lane:** Simulation Intelligence Plane  
**Date:** 2026-11-14  
**Relationship:** Parallel to QUE / QDesk / Delphi / DoE RFP pipelines; not a replacement or competing admission path.

## 1. Executive request

Design, implement and evaluate a reproducible simulation capability that transforms curated evidence and a versioned knowledge-graph snapshot into synthetic agent populations, executes controlled social simulations, and returns auditable evidence for comparative analysis.

The reference workflow is MiroFish's graph-to-simulation pattern. CAMEL-AI OASIS is the primary execution-engine candidate. A MiroFish refactor/fork reference is included because its separation of workbench core, resource adapters, composable tools and API shells is a useful architectural model. Alternative engines and orchestration substrates must be compared rather than assumed inferior.

The deliverable is a research and experimentation instrument, not an oracle, forecasting authority, autonomous public actor, or production decision-maker.

## 2. Problem statement

The repository has mature orchestration, provider adapters, graph/decision-analysis work, DoE, ATES and evidence contracts. What is not yet demonstrated as one end-to-end capability is a repeatable pipeline that:

1. selects a precise source-evidence cohort and graph snapshot;
2. preserves provenance while extracting entities, relations and claims;
3. creates synthetic personas with traceable source references and declared generation assumptions;
4. runs multi-agent interaction under a configurable social platform and bounded resources;
5. captures actions, environment state, agent/model identity and execution lifecycle;
6. compares policies or interventions under controlled, reproducible experimental designs;
7. distinguishes simulation output, derived interpretation, externally observed evidence and verified facts;
8. makes outputs inspectable and reusable without changing production routing or the canonical historical corpus.

## 3. Outcomes sought

- A deterministic offline reference implementation and fixture suite.
- A provider-neutral Scenario/Experiment/Run contract.
- A pluggable simulation-engine adapter, initially OASIS.
- A graph/persona preparation adapter, informed by MiroFish architecture.
- A provenance-preserving event and artifact pipeline using Integration Intelligence / CEEL.
- A DoE-ready experiment manifest and ATES-compatible trace mapping.
- A comparison report covering quality, reproducibility, throughput, resource use, failure recovery, maintainability, security and license obligations.
- A bounded pilot with synthetic or explicitly approved public-source data only.

## 4. Non-goals

- Replacing QUE, QDesk, Workflow Contract, DoE, ATES, Delphic, the canonical context graph, or any existing scheduler.
- Sending messages or taking actions on real social platforms.
- Treating synthetic agents as real people or synthetic relationships as observed relationships.
- Automatically merging simulated graph deltas into factual graph/corpus stores.
- Production forecasting, policy enforcement, model routing, public communications or automated decisions.
- Unbounded agent populations, unbounded steps, open-ended model spend or autonomous experiment scheduling.
- Copying AGPL-licensed MiroFish code into this repository without a recorded compatibility decision.
- Installing external software, provisioning accounts, storing credentials or invoking paid APIs as part of this proposal build.

## 5. Candidate source and engine set

### Primary reference workflow: MiroFish
MiroFish is a reference for document/evidence ingestion, ontology and graph preparation, entity filtering, persona construction, OASIS-backed multi-agent simulation, graph-memory updates, report generation and post-run interaction. Its upstream implementation is evidence of a working integration pattern, not proof of compatibility with this repository.

### Architectural refactor reference: mj3b/MiroFish
The refactoring work is particularly relevant: consolidate a workbench core, separate resource adapters, make tools composable, and keep API shells thin. SIP should adopt the separation principle without importing its implementation wholesale. Validate the fork's current branch, license, dependency graph, persistence and API behavior before selecting any code reuse.

### Primary execution candidate: CAMEL-AI OASIS
Evaluate OASIS as the social simulation runtime: agent population, platform actions, recommendation/environment dynamics, custom agent models/tools/prompts, action logs and database persistence. Confirm the exact supported platform, action semantics, scale, process lifecycle, storage and version behavior against a pinned release.

### Alternatives to compare
- Mesa (Python agent-based modeling): strong model-first ABM alternative; evaluate discrete environment semantics and deterministic control.
- Agent-based modeling with Repast / NetLogo: established ABM environments; evaluate integration and reproducibility cost.
- LangGraph / AutoGen / CrewAI / OpenAI Agents SDK: agent orchestration frameworks, not automatically equivalent to a social simulation environment. Evaluate only as orchestration/control alternatives, not as drop-in OASIS replacements.
- Custom deterministic simulator: minimal dependency baseline for fixtures and policy tests.
- Temporal: durable workflow substrate candidate only if existing GitHub Actions / QUE / Workflow Contract execution proves insufficient; not a second queue or scheduler.
- Existing repository graph and Delphic engines: reuse for graph analysis and decision support; do not assume they provide a social simulation runtime.

## 6. Requirements

### Functional
F-01 Scenario creation must be schema-valid, versioned and immutable once admitted.
F-02 Evidence inputs must reference immutable source IDs, content digests, capture time and trust labels.
F-03 Graph snapshots must be versioned and content-addressed.
F-04 Persona records must distinguish source-grounded attributes from generated assumptions.
F-05 Agent identities must be synthetic, scoped to one run or declared cohort and non-resolvable to real persons.
F-06 The engine adapter must support prepare, start, observe, stop, finalize and health-check operations, or explicitly declare unsupported operations.
F-07 Every run must emit a lifecycle receipt and normalized events.
F-08 Every run must record engine/version, adapter version, code SHA, config/prompt hashes, seed, dataset/graph digest, model IDs, limits and outcome.
F-09 Run outputs must be queryable by scenario, experiment, factor, cohort, seed and engine.
F-10 Comparison must preserve baseline/candidate pairing and common-random-number semantics where valid.
F-11 Simulation graph deltas must remain in a separate overlay namespace.
F-12 Report generation must cite source evidence and mark inferred/simulated claims.

### Non-functional
NF-01 Offline tests must run without network, credentials or model calls.
NF-02 Resource limits must be enforced before dispatch: agents, steps, concurrency, wall time, tokens and spend.
NF-03 Events must be idempotent and append-only.
NF-04 Process lifecycle must not confuse application-level completion with subprocess exit.
NF-05 Logs must exclude secrets, raw credentials and unapproved private prompts/completions.
NF-06 External content is untrusted data and never executable instructions.
NF-07 The adapter must fail closed on unsupported schema versions, missing provenance, over-budget requests and unknown engine states.
NF-08 No live engine/provider call may be required for the default CI suite.

## 7. Comparative evaluation design

Run a multi-criteria DoE comparison with the same frozen scenarios and cohorts across candidates. Minimum candidates:
A. deterministic in-repo simulator baseline;
B. CAMEL-AI OASIS adapter;
C. MiroFish-compatible workflow using OASIS;
D. one alternative ABM engine (Mesa recommended initial candidate);
E. optional orchestration substrate variant only if a measurable durability question exists.

Factors: engine, agent count, steps, activation probability, persona source, memory mode, recommendation policy, intervention, seed, model/provider class and persistence mode. Keep dataset, graph snapshot, scenario contract, outcome rubric and evaluator fixed within each paired comparison.

Primary outcomes: behavioral validity against declared ground truth/known invariants, reproducibility, trace completeness, lifecycle correctness and evidence provenance.
Secondary outcomes: throughput, wall-clock time, token/cost use, memory/storage, failure recovery, operator effort and adapter maintenance burden.

Do not equate agent activity volume with simulation quality. Do not use qualitative judge scores to rescue deterministic invariant failures.

## 8. Required deliverables

D1. Research and source register with exact commit/release, license, docs and retrieval date.
D2. Architecture decision record comparing engines and refactoring options.
D3. Scenario, Experiment, Persona, Run, Event and GraphDelta schemas.
D4. Offline validator and deterministic fixture set.
D5. Adapter interface plus fake-engine implementation.
D6. OASIS adapter prototype with live calls disabled by default.
D7. MiroFish-compatible ingestion/persona/report adapter, license-reviewed.
D8. DoE matrix and paired-run analysis.
D9. ATES trace bridge and Integration Intelligence/CEEL event mapping.
D10. Security, privacy, cost, dependency and failure-mode assessment.
D11. Reproducibility report and go/no-go recommendation.

## 9. Governance and integration

- The proposal is tracked under the existing proposal lifecycle.
- QUE remains the sole admission/dispatch authority.
- A Workflow Contract describes the requested experiment and constraints.
- DoE owns the experimental design and records one experiment observation per executed run according to the existing family contract.
- ATES receives sanitized trace spans and deterministic checks.
- Integration Intelligence registry records the external systems and adapter lifecycle.
- CEEL carries normalized events; no new generic event bus is introduced.
- No live run is admitted until the RFP review, license review, security review, resource budget and exact-head tests are accepted.

## 10. License and provenance review

Preliminary research indicates MiroFish upstream is AGPL-3.0 and CAMEL-AI OASIS is Apache-2.0. Treat these as provisional until verified against exact pinned source files and release tags. Keep any AGPL-derived service/process isolated pending legal review; do not copy code or create a derivative work in this repository without explicit compatibility review. Record all transitive licenses and model/data terms.

## 11. Success criteria

A reviewer can reproduce a small run from its manifest; identify every source, graph, prompt/config, engine and model version; reconstruct lifecycle and resource use; distinguish synthetic output from factual evidence; compare at least two policies under paired seeds; and verify that no QUE authority, canonical corpus state or production routing was mutated.

## 12. Questions for RFP review

1. Which graph snapshot is the first approved source cohort?
2. Which exact MiroFish repository/fork and commit are eligible for evaluation?
3. Is an isolated AGPL service acceptable, subject to review, or should SIP remain clean-room/protocol-only?
4. Which OASIS version and platform semantics should be pinned?
5. Which existing QUE Workflow Contract fields are required to admit a bounded experiment?
6. Which ATES and DoE record extensions are needed, if any, rather than adding a second record format?
7. What resource ceiling is acceptable for the first live pilot?
8. Who is the human owner of factual-corpus promotion review?
