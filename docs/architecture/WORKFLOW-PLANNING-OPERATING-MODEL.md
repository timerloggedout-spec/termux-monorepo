# Workflow Planning Operating Model

**Status:** proposed architecture contract  
**Scope:** QUE, routing, DoE/MVT, Platform201 blueprint packaging, n8n adapters, operational dashboards, and MiroFish scenario research  
**Authority:** Git history + canonical workflow contract + runtime evidence; no visual/editor adapter is a source of truth

## 1. Decision

The MonoRepo should adopt a **canonical declarative Workflow Contract (WFC)** and treat PDDL, Mermaid, n8n, Platform201 blueprint manifests, and dashboard views as projections or execution adapters of that contract.

This avoids creating multiple independently edited descriptions of the same workflow.

The layers are:

1. **Intent** — objective, desired outcome, constraints, risk and acceptance conditions.
2. **Workflow contract** — typed tasks, states, dependencies, guards, resources, retries, deadlines, ownership, evidence requirements and side effects.
3. **Planning** — QUE admission/priority, dependency resolution, resource feasibility, and optional PDDL/HTN planning.
4. **Routing** — choose eligible roles, agents, providers, endpoints, and execution topology under hard constraints.
5. **Execution** — GitHub Actions / Termux / Temporal / explicitly approved service runtimes.
6. **Observation** — events, run/job/step evidence, receipts, cost, latency, failures and provenance.
7. **Evaluation** — DoE/MVT, causal comparisons, Bayesian updates, MoneyBall/3L0.
8. **Projection** — Desk/Admin UI, Mermaid diagrams, n8n import/export, Platform201 blueprint packaging, reports.

## 2. Existing-system boundaries (preserve)

| Existing system | Keep as authority for | Do not turn it into |
|---|---|---|
| QUE | queue state, admission/governor, claims, priority windows and queue measurements | a second general workflow engine |
| GitHub Actions | canonical repository automation and CI execution evidence | a hidden planner |
| Temporal | durable multi-step execution where adopted | universal replacement for all Actions |
| Termux Fleet Swarm App | device/agent dispatch transport where already used | a source of inferred success |
| n8n | optional visual composition and operator adapter; sanitized receipts | scheduler or system of record |
| Platform201 | optional packaged service/blueprint runtime after its spend/consumer gates | dashboard telemetry host or mandatory dependency |
| PDDL | explicit planning problem/domain representation | application schema or runtime evidence ledger |
| Mermaid (.mmd) | architecture/workflow visualization | executable workflow authority |
| SHE / Desk / Admin | read-only or operator-facing projections of canonical state | independent state stores |
| MiroFish | scenario exploration and simulated populations | production executor or evidence authority |
| DoE / MVT | experimental design and comparative inference | unconstrained production traffic router |

Existing QUE contract: `ops/que/README.md` and `docs/ops/QUE.md`. Existing n8n boundary: `docs/ops/N8N-FREE-COMMUNITY-WIRING.md`. Existing visual contract: `docs/ops/SHE-DASHBOARD-PRD.md`. Existing routing map: `docs/ops/ROUTING-ORCHESTRATION-MAP.md`.

## 3. Canonical Workflow Contract (WFC)

A workflow is a versioned graph of typed task nodes and typed transitions.

### 3.1 Required dimensions

| Dimension | Required fields / concepts |
|---|---|
| Identity | workflow_id, contract_version, name, owner, source_ref |
| Objective | objective, outcome_class, success_predicate, failure_predicates |
| Scope | repository, ref/SHA, paths, task cohort, environment |
| Task graph | task_id, task_type, dependencies, inputs, outputs |
| State | declared states, allowed transitions, terminal states |
| Guards | preconditions, authorization, policy, evidence gates |
| Resources | concurrency, CPU/memory class, token/cost budget, provider quota, queue tier |
| Scheduling | priority, deadline, not_before, lease, timeout, critical path |
| Routing | eligible roles, capability requirements, provider/model allowlist, fallback policy |
| Reliability | retryable errors, max_attempts, backoff, idempotency key, checkpoint policy |
| Side effects | read/write class, external systems, approval requirements, compensation |
| Evidence | required event types, run/job/step identifiers, artifact digests, source links |
| Evaluation | metrics, baseline, treatment, cohort, sample requirements, uncertainty |
| Governance | approver, policy version, promotion state, rollback/kill criteria |
| Projection | diagram refs, n8n mapping, Platform201 service mapping, dashboard view |

### 3.2 Minimal JSON-shaped example

```json
{
  "schema_version": "wfc/v1",
  "workflow_id": "repo.routing-benchmark",
  "objective": "Select a routing policy with better verified task utility",
  "scope": {
    "repository": "timerloggedout-spec/termux-monorepo",
    "base_sha": "<immutable-sha>",
    "cohort": "routing-doe-01"
  },
  "tasks": [
    {"id": "prepare", "type": "prepare", "depends_on": []},
    {"id": "execute", "type": "experiment", "depends_on": ["prepare"]},
    {"id": "verify", "type": "verification", "depends_on": ["execute"]}
  ],
  "constraints": {
    "max_parallel": 3,
    "max_attempts": 2,
    "external_writes": "approval_required",
    "budget": {"unit": "inference_tokens", "limit": 120000}
  },
  "success": ["verified_outcome == PASS"],
  "evidence": ["source_sha", "run_id", "attempt", "artifact_digest"]
}
```

The initial structural contract is published at `docs/schemas/workflow-contract-v1.schema.json`. A standard-library validator at `scripts/workflows/validate_wfc.py` checks required fields, identifiers, SHA shape, task references, DAG cycles, side-effect classes and budget/constraint types. Its regression suite is `tests/test_workflow_contract_validator.py`. This is an initial structural validator, not a complete JSON Schema draft-2020-12 implementation or production admission gate.

### 3.3 State model

Keep separate state dimensions rather than one overloaded status:

- **Planning:** DRAFT, FEASIBLE, BLOCKED, ADMITTED.
- **Execution:** NOT_STARTED, QUEUED, RUNNING, WAITING, SUCCEEDED, FAILED, CANCELLED, EXPIRED.
- **Evidence:** MISSING, PARTIAL, COMPLETE, INVALID.
- **Evaluation:** UNASSESSED, PASS, FAIL, INCONCLUSIVE.
- **Promotion:** NOT_PROPOSED, PROPOSED, APPROVED, PROMOTED, REJECTED, ROLLED_BACK.

A successful execution is not automatically a successful outcome; a validated result is not automatically promoted.

## 4. Planning formalism selection

Use the least powerful formalism that faithfully represents the problem.

| Formalism | Use when | Limitation / boundary |
|---|---|---|
| DAG / dependency graph | task ordering and fan-in/fan-out | does not express rich state/resource constraints |
| Finite-state machine | lifecycle and legal transitions | not a general optimizer |
| BPMN 2.0 | human-readable business process, events, gateways, timers | verbose; execution semantics vary by engine |
| PDDL STRIPS + typing | discrete actions, predicates, preconditions/effects, goal reachability | classical form omits durations, concurrency and uncertainty |
| PDDL 2.1+ | durative actions, numeric fluents, resource/time constraints | planner support varies; keep a tested subset |
| HTN planning | decomposing high-level missions into methods/subtasks | requires method library and domain-specific decomposition |
| CP-SAT / MILP | assignment, capacity, scheduling, budget and resource optimization | optimization model, not the complete workflow lifecycle |
| MDP / POMDP | sequential decisions with uncertain state and action outcomes | model/transition assumptions can be costly |
| Temporal workflow engine | durable retries, timers, signals, long-running execution | execution engine, not source contract |
| JSON/YAML WFC | canonical typed interoperability and validation | requires explicit semantics and validators |

**Recommended composition:** WFC as canonical contract; DAG/state machine for baseline validation; PDDL/HTN for discrete planning; CP-SAT for capacity/scheduling optimization where needed; Temporal/Actions/Termux as execution adapters; Bayesian/causal methods for uncertain routing and outcome learning.

PDDL must be planner-checked. The existing Siglary PDDL example is explicitly marked candidate pending formal planner validation.

## 5. QUE integration

QUE remains the queue/governor plane. The WFC maps to QUE through an admission envelope:

- workflow_id + contract_version;
- task_id + idempotency_key;
- owner/role and capability requirements;
- tier/priority window;
- dependencies and readiness;
- estimated resource envelope;
- deadline/lease/attempt policy;
- risk/approval class;
- evidence requirements;
- deferral reason and expiry.

QUE returns admission/claim/lease/dispatch state. It does not infer task correctness. Completion must be joined to execution evidence and an independently evaluated outcome.

The existing QUE feed's separation between producer-served state, transition event records, and consumer mirrors is preserved. Consumer dashboards remain projections.

## 6. Routing and execution policy

Routing is a constrained decision, not just a provider lookup.

1. Apply hard eligibility gates: credentials, security, capability, data policy, current SHA, availability, quota and ownership.
2. Determine topology: sequential, parallel independent, fan-out/fan-in, specialist handoff, review volley, or durable long-running workflow.
3. Select among eligible agents/endpoints using task-family evidence and uncertainty.
4. Enforce budget, latency, concurrency and cancellation bounds.
5. Record the selected policy and all candidate exclusions.
6. Execute with idempotency and checkpoint rules.
7. Capture run → job → step → artifact → outcome lineage.
8. Update empirical estimates only from verified observations.

Correctness and safety are constraints, not weighted preferences. Optimize cost, latency, context, retries and human attention only among candidates that satisfy hard gates.

## 7. DoE / MVT design for routing

Start with a frozen baseline and bounded, reproducible cohorts.

### Candidate factors

- provider × model × endpoint;
- role/prompt/configuration version;
- manager policy;
- topology (serial / parallel / staged);
- context retrieval/compression policy;
- retry/backoff policy;
- concurrency level;
- toolset;
- task family and complexity stratum.

### Response variables

- verified task success / acceptance;
- integration success and regression rate;
- time-to-verified-outcome;
- total inference cost/tokens;
- context duplication;
- retries and provider failures;
- conflicts and rework;
- human intervention time;
- queue wait and resource utilization;
- attribution confidence.

### Experimental controls

- pin base SHA, task suite, environment, endpoint snapshot, prompts and policy versions;
- randomize treatment assignment within comparable strata where feasible;
- use paired tasks or blocked designs when task difficulty varies;
- separate training/tuning tasks from held-out evaluation tasks;
- repeat stochastic runs and retain all attempts;
- record missingness and censoring; never convert missing metrics to zero;
- set sample-size / stop rules before looking at results;
- report uncertainty and Pareto trade-offs, not only one scalar;
- promote only after independent validation and regression gates.

### Sequential optimization

Use factorial screening to identify influential factors; then response-surface or Bayesian optimization for expensive continuous settings; use contextual bandits/Thompson sampling only for bounded exploration after hard gates. Use causal comparisons for intervention claims. MiroFish can generate scenario hypotheses and candidate treatments, but its simulated results are not empirical DoE outcomes.

## 8. Performance and efficiency objectives

Measure end-to-end verified utility, not request price or raw throughput alone.

Primary objective vector:

- maximize verified correctness;
- maximize integrated task yield;
- minimize cost per verified outcome;
- minimize time-to-verified-outcome;
- minimize retries, conflicts, duplicate context and human intervention;
- preserve reliability, security and auditability.

Use Pareto fronts where objectives conflict. Any composite score must publish its normalization, weights, confidence, sample count and policy version.

Operational optimizations to test:

- single-flight and deduplication for identical work;
- coalesced feed refresh and bounded polling;
- queue-aware admission and backpressure;
- cache immutable artifacts by content digest;
- retrieve only relevant context and record provenance;
- avoid speculative parallelism when integration cost exceeds expected value;
- use checkpoint/resume for long tasks;
- classify retryable vs terminal errors;
- dynamic concurrency from observed quota/resource headroom;
- route simple deterministic transformations away from expensive model calls;
- use specialist escalation only when expected marginal value exceeds cost.

## 9. Platform201 and n8n adapters

### n8n

Keep n8n optional and localhost-bound by default. It may render/import operator workflows or relay allowlisted receipts. It must not receive secrets, full prompts/completions, GitHub tokens or arbitrary tool payloads. Any write-capable n8n integration requires a separate credential, review, approval gate, and audit record.

### Platform201

Platform201 blueprint packaging is a deployment projection, not workflow authority. Its existing plan records explicit spend and consumer gates, and its current owner rule freezes new spend until credit intake is obtained. No deploy is authorized by this architecture.

When eligible, map each self-contained service/container, gateway route, queue topic, database schema, scheduler and env *names* into the blueprint README graph table. Keep source in Git; record live registry updates only after verified deployment.

### Dashboard/admin surfaces

The repository search did not find a file named `AdminFesk.html`. The closest existing surfaces are `apps/tribute-dashboard/admin.html`, `desk.html`, `admin-graph.html`, and `surfaces-map.html`. This design treats them as read models over versioned feeds, not independent workflow stores.

## 10. MiroFish integration

MiroFish receives a snapshot bundle: WFC version, repository SHA, graph snapshot, task cohort, agent population/configuration versions, constraints and simulation seed. It returns a simulation receipt containing scenario ID, run ID, input digests, population manifest, assumptions, predicted outcomes, uncertainty, and report digest.

A simulation receipt is a hypothesis artifact. It cannot create QUE claims, write GitHub, settle Wagertome positions, update ATES outcomes, or promote a routing policy. It may propose DoE treatments, which must be tested against real task cohorts.

## 11. Rollout gates

**Gate 0 — inventory:** map existing workflows and their owners; identify duplicate/stale/superseded routes.

**Gate 1 — contract:** review the schema and initial validator; add full schema conformance, state-machine semantics, compatibility/versioning tests and consumer adoption checks.

**Gate 2 — read-only compiler:** generate Mermaid and planning projections; compare against existing diagrams/workflows.

**Gate 3 — QUE adapter:** submit/read admission envelopes in shadow mode; no dispatch authority.

**Gate 4 — execution adapters:** import/export selected n8n workflows and Actions/Temporal mappings; preserve source authority.

**Gate 5 — DoE:** run a bounded routing benchmark with pinned baseline and independent evaluation.

**Gate 6 — promotion:** require both repository gates, regression checks, verified task outcome and documented rollback; require Operator approval only for the human-only edges enumerated in `docs/proposals/AGENTIC-PERMISSIONS.md`. Routine authorized repository writes remain within FA-ADE automation.

## 12. Acceptance criteria

- One WFC maps to one or more deterministic projections with stable IDs.
- Every workflow node and transition has a declared owner and state semantics.
- Every write or external side effect has a declared policy class; human approval is required only where `AGENTIC-PERMISSIONS.md` reserves a human-only edge.
- PDDL artifacts pass a named planner and recorded validation command.
- Mermaid diagrams are generated/checked from the same contract or explicitly marked hand-maintained.
- n8n is optional and cannot become canonical state.
- Platform201 deployment remains frozen unless its existing owner gate is satisfied.
- QUE remains authoritative for queue admission/claims, not outcome correctness.
- DoE results include pinned inputs, cohort, repetitions, uncertainty and evidence references.
- No simulated result is represented as production evidence.
- No missing metric is converted to zero.
- Routing promotion is explainable from objective, constraints, eligible set, evidence snapshot, selected topology and measured outcome.
