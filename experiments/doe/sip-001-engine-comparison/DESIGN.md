# SIP-001 Engine and Orchestration Comparison — DoE Design Proposal

**Experiment ID:** `sip-001-engine-comparison`  
**Status:** `proposed_not_admitted`  
**Owner lane:** Simulation Intelligence Plane  
**Candidate source:** `docs/rfps/simulation-intelligence-plane/candidate-queue.json`  
**RFP:** `docs/rfps/simulation-intelligence-plane/RFP.md`  
**Design date:** 2026-11-14

> This is a proposed pre-registration design. It is not yet a DoE family campaign, execution authorization, or result. The DoE family intake rule still requires a committed design record AND EXPERIMENT-conforming run evidence before campaign admission.

## 1. Decision questions

1. Which social-simulation engine best supports bounded, reproducible, evidence-grounded synthetic agent experiments?
2. Which ABM engine provides the best scientific control and reproducibility within its role class?
3. Which graph-to-agent workbench pattern gives the strongest evidence lineage and adapter separation?
4. Does the existing LangGraph + Temporal capability set already meet SIP's orchestration and recovery requirements?
5. Which combined architecture improves measured task outcomes enough to justify its additional operational and maintenance complexity?

The design does not ask for one global winner across unlike candidate classes.

## 2. Candidate cohorts and role separation

| Cohort | Candidates | Experimental treatment | Current constraint |
|---|---|---|---|
| Offline correctness control | `deterministic-fake` | Golden fixtures, deterministic replay, schema and lifecycle tests | Must remain provider-free and network-free |
| Social simulation | `camel-ai-oasis` | OASIS native environment and action lifecycle | Primary execution candidate; no install/live run yet |
| Graph-to-simulation workbench | `mirofish`, `mirofish-refactor-fork` | Graph/persona preparation and thin adapter boundary paired with OASIS | Architecture references; AGPL source reuse prohibited pending review |
| ABM | `mesa`, `repast`, `netlogo` | Model-first agent simulation and experiment data collection | Mesa remains pre-screen/observational only; NetLogo is corpus/reference only; Repast research-only |
| Agent orchestration | `langgraph`, `autogen`, `crewai`, `openai-agents-sdk` | Workflow/state/tool coordination comparison | LangGraph existing repo work must be reused; optional alternatives only if a concrete gap remains |
| Durable execution | `temporal` | Existing workflow recovery and worker replacement | Prior RFP #1885/pass and self-host/Delphi-cycle work are reused; no duplicate RFP |

Temporal and LangGraph are integration/reuse arms, not greenfield candidates. Mesa and NetLogo's existing research status is preserved. MiroFish and its fork are reference/workbench candidates, not independent simulation engines.

## 3. Staged design

### Stage 0 — contract and safety conformance (offline; mandatory)

- Validate Scenario, Run Manifest, Event and Graph Delta v1 contracts.
- Run deterministic fake engine fixtures with fixed seeds and golden output hashes.
- Verify synthetic identity and simulation-overlay separation.
- Verify budgets, idempotency, sequence ordering and redaction.
- Reject unsupported schema versions, missing provenance, invalid lifecycle transitions and over-budget inputs.

**Gate:** every hard contract invariant passes. A candidate failing this gate is not eligible for later stages.

### Stage 1 — ABM pre-screen (no runtime adoption implied)

- Review pinned release/API/license/dependency evidence for Mesa, Repast and NetLogo.
- Mesa is restricted to its existing control-seat pre-screen and observational role. No live-evidence claim is allowed.
- NetLogo's SFI corpus reference is inspected for equivalency and portability; corpus presence is not runtime proof.
- Repast's Python component, distributed runtime and exact license are pinned before any execution request.
- Compare model expressiveness, headless execution, determinism, experiment collection and adapter effort.

**Gate:** publish a role-specific evidence matrix. Runtime execution requires a separate amended design and owner approval.

### Stage 2 — OASIS social-simulation pilot (sandbox-only proposal)

Initial factor levels, subject to G0 freeze:

| Factor | Low | High |
|---|---:|---:|
| Synthetic agents | 10 | 25 |
| Steps | 10 | 25 |
| Activation probability | 0.25 | 1.0 |
| Memory mode | none | graph-memory |
| Persona source | deterministic template | graph-grounded synthetic persona |

Use a fractional factorial or staged one-factor-at-a-time screen only if the full design is not feasible; record the choice and alias structure before execution. Use common random numbers where the engine supports stable seeding. Otherwise record seed semantics as non-equivalent and do not claim paired variance reduction.

MiroFish-compatible graph preparation is a separate treatment from the OASIS engine. The comparison distinguishes:
- OASIS alone with a fixed synthetic cohort;
- graph/persona preparation followed by OASIS;
- graph/persona preparation with a deterministic fake engine for offline validation.

No public social-platform actions are allowed.

### Stage 3 — orchestration and durability

Use the existing repository implementation as the baseline:
- LangGraph existing workflow/state integration;
- Temporal existing self-host and Delphi-cycle patterns;
- QUE/WFC admission and DAG planning as the authority boundary.

Test only a demonstrated SIP-specific gap. Optional AutoGen, CrewAI or OpenAI Agents SDK arms require a written reason why existing LangGraph is insufficient before they enter execution.

Fault-injection cases:
1. worker/process killed before an activity starts;
2. worker/process killed during an activity;
3. activity completes but completion receipt is not persisted;
4. all OASIS platforms report completion while subprocess remains alive for IPC;
5. restart/replay attempts a duplicate side effect;
6. graph preparation succeeds but simulation startup fails;
7. finalization/report generation fails after simulation completion.

Expected invariant: completion state, process liveness, IPC availability and report finalization are separate facts. Recovery is idempotent; uncertain side effects are surfaced as unknown, never blindly retried.

### Stage 4 — composition comparison

Compare only combinations that passed their role-specific gates:
- MiroFish-compatible preparation + OASIS + existing QUE/WFC orchestration;
- deterministic fake + existing workflow runtime;
- ABM candidate + canonical DoE/ATES measurement;
- existing LangGraph and Temporal composition where the task requires both orchestration and durable execution.

Do not multiply all 12 candidates into a full factorial. Candidate roles are nested/blocked and not interchangeable.

## 4. Outcomes and measurement

### Hard gates (pass/fail; not averaged)

- schema and adapter contract correctness;
- synthetic identity and privacy boundary;
- no public platform writes;
- no unapproved provider or paid inference;
- reproducible run manifest and provenance;
- event idempotency and sequence integrity;
- process/IPC/finalization recovery;
- graph overlay cannot mutate factual source graph;
- license and dependency review complete.

### Primary outcomes

| Outcome | Measurement |
|---|---|
| Behavioral validity | Scenario invariants satisfied / total declared invariants |
| Reproducibility | Identical configuration/seed output digest match rate |
| Provenance completeness | Events and outcomes with resolvable source/run/config references |
| Lifecycle correctness | Correct terminal state, no lost/duplicated finalization or side effects |
| Adapter conformance | Required operations supported or explicitly declared unsupported |
| Evidence quality | Source-grounded vs generated/simulated claims correctly distinguished |

### Secondary outcomes

Wall time, throughput, peak memory, storage, token use, inference cost, retries, operator effort, dependency footprint, portability and maintenance burden.

Do not equate agent activity volume, graph growth or report length with quality. Do not allow subjective evaluator scores to rescue hard-gate failures.

## 5. Replication and analysis

- Freeze the scenario, cohort, graph snapshot, prompts/config, evaluator version and source revision before each run.
- Use at least five seeds per final comparison cell where the engine supports controlled randomness; exploratory screening may use fewer but cannot support adoption.
- Pair treatments by scenario and seed when random streams are compatible.
- Report per-cell raw observations, confidence intervals/uncertainty and missing/failed runs.
- Separate within-engine effects from between-engine effects; never pool unlike role classes.
- Keep a Pareto view of quality, reproducibility, cost and operational burden; publish weights only after G0 review.
- Record all design deviations, culls and exclusions with reason and timestamp.

## 6. Resource and safety envelope

**Stage 0:** no network, credentials, package installation, model calls or external provider calls.

**Proposed first sandbox ceiling (not yet authorized):**
- at most 25 synthetic agents;
- at most 25 steps per run;
- one concurrent run;
- 15-minute wall-clock limit;
- no public social actions;
- no paid inference;
- provider token/cost ceiling remains zero until an owner-approved budget and explicit provider allowlist are recorded.

Any increase requires a design amendment before dispatch. A failed or over-budget run is retained as a failed observation, not deleted.

## 7. Canonical evidence outputs

Each executed run must produce:
1. one SIP Run Manifest with repository SHA, engine/adapter versions, config hashes, seed, cohort and limits;
2. append-only normalized events with source and run provenance;
3. a simulation-only graph delta;
4. exactly one canonical DoE EXPERIMENT record per dispatched/executed run;
5. ATES trace/evaluation linkage;
6. a cost/resource receipt or explicit `not_established` status.

No separate experiment ledger is created. No simulated relationship is promoted into the factual corpus by this experiment.

## 8. Decision and stopping rules

- Stop a candidate immediately on license uncertainty that blocks use, secret exposure, public-write capability, unbounded cost, unrecoverable state corruption or factual-graph contamination.
- Reject or defer a candidate that cannot meet hard gates; do not replace missing results with subjective estimates.
- Keep exploratory evidence separate from confirmatory evidence.
- Adoption requires independent review, target-specific portability evidence, reproducibility and an explicit promotion decision.
- A queue entry, RFP issue, generated proposal or successful smoke test is not adoption.

## 9. Current disposition

| Item | State |
|---|---|
| Candidate queue | Committed; 12 candidates |
| Design proposal | This file; proposed, not admitted |
| Scenario/run/event/graph contracts | Committed |
| Offline contract tests | Committed; exact-head CI result pending |
| Deterministic fake engine | Planned |
| OASIS installation / live run | Not performed |
| ABM runtime comparisons | Not performed |
| LangGraph/Temporal incremental gap proof | Not performed; existing work to be reconciled |
| DoE family campaign admission | Not admitted; no run evidence |

**Admission condition:** owner review of this design, G0 freeze of exact candidate cohort and factors, plus execution evidence conforming to the canonical experiment schema. Until then, this remains a design proposal, not a live campaign.
