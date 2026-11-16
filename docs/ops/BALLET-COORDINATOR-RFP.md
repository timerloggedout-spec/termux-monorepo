# Ballet Coordinator — Request for Proposal and Critical Alternatives Evaluation

**Status:** proposed architecture plus reference implementation in review  
**Decision:** adopt a bounded Tier-2 orchestration coordinator, subject to DoE and online validation  
**Authority:** existing lane manager and operator; Ballet has no independent dispatch or promotion authority

## 1. Executive decision

Adopt Ballet as an orchestration-policy component under the existing orchestration lane manager. It converts manager-approved task/dependency state into safe execution waves, synchronization points, handoff records, and integration checkpoints.

Do not create a second scheduler, provider router, dependency-phase engine, telemetry store, or source of truth. Ballet is a policy implementation and experiment treatment over existing control planes.

The reference implementation is deepcli/deepcli/observatory/ballet.py. It plans deterministic dependency waves, isolates conflicting writes, rejects malformed/cyclic graphs, scores evidence-bearing online observations, and submits strategy arms through existing DoE and tournament APIs.

## 2. Problem statement

Multi-agent work loses value when independent work is serialized unnecessarily, dependent work starts too early, multiple agents write the same surface, handoffs lose context, or parallel calls produce duplicated work that is expensive to integrate.

The established ADE control path is:
dependency DAG → wave/readiness → manager policy → specialist route → execution adapter → evidence.

Ballet fills the manager-policy choreography slice. It consumes dependency readiness rather than replacing it; plans remain subject to manager approval and existing execution adapters.

## 3. Goals and non-goals

### Goals
- Deterministic, inspectable task waves from a validated dependency graph.
- Parallel work only when dependencies, write ownership, and task safety permit it.
- Explicit handoff and integration checkpoints.
- Preserve manager-approved plan, policy version, cohort, task identity, and execution evidence.
- Compare orchestration strategies through repository DoE/MVT and tournament mechanisms.
- Optimize integrated correctness and accepted outcomes per total operational cost.
- Retain losing, failed, and censored trials; preserve the incumbent.

### Non-goals
- Provider/model selection or live catalog discovery.
- Autonomous dispatch, credentials, or permission escalation.
- New scheduler, dependency graph store, claim protocol, or telemetry database.
- Executing generated code or agents during offline replay.
- Self-modifying production policy or automatic promotion.
- Claiming correctness from latency, planned routes, queued jobs, or workflow conclusion alone.

## 4. Placement and responsibility boundary

Operator / lane manager (authority + approval)
→ Dependency-phase engine (canonical readiness + claims)
→ Ballet Coordinator (policy + choreography plan)
→ Existing specialist router (provider/model selection)
→ Existing execution adapters
→ ATES / Action→Effect / canonical receipts
→ Existing evaluators, Moneyball and manager tournament

Ballet is Tier-2 coordination: it owns a bounded slice and reports to the lane manager. The manager retains plan approval, escalation, culling, and promotion. Router selects eligible provider/model. Evidence collectors record actual execution.

The generic role is not yet a registry-issued lane moniker or GitHub actor. Any formal display moniker must follow AGENT-MONIKERS.md registration rules.

## 5. Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| BAL-01 | Validate unique task IDs and dependency references | deterministic unit tests |
| BAL-02 | Reject cycles and self-dependencies | negative tests |
| BAL-03 | Group only dependency-ready tasks | wave invariants |
| BAL-04 | Serialize overlapping write sets | conflict tests |
| BAL-05 | Honor non-parallel-safe tasks | isolation tests |
| BAL-06 | Support sequential, parallel, adaptive strategies | same-cohort arm outputs |
| BAL-07 | Preserve plan, strategy, capacity, cohort and schema version | JSON receipt |
| BAL-08 | Reject missing acceptance/correctness/cost/latency/coordination evidence | validation tests |
| BAL-09 | Submit candidates through existing DoE and tournament APIs | integration test |
| BAL-10 | Keep promotion candidate-only until fresh online cohort and dual gates | promotion contract |

## 6. Non-functional and governance requirements

- Determinism: same graph and policy inputs produce the same plan.
- Safety: no same-wave write overlap; no implicit dispatch.
- Provenance: record repository SHA, task/cohort, policy ID/version, run/attempt, manager, adapter, and evidence references at integration.
- Null semantics: unavailable metrics remain unknown/null, never zero or success.
- Reproducibility: fixed cohort, benchmark, environment, evaluator and arm-factor hashes.
- Least privilege: no secrets in policy artifacts or receipts.
- Resource discipline: no arbitrary hard concurrency ceiling; respect manager admission, quota, cooldown and platform limits.
- Promotion: correctness gates plus explicit operator promotion; metrics are not approval authority.

## 7. Alternatives and critical evaluation

| Alternative | Strengths | Weaknesses / risks | Decision |
|---|---|---|---|
| A. Manager prompts only | smallest code footprint; flexible | weak repeatability, hard to test/compare, implicit conflict handling | retain as baseline |
| B. Put all choreography in dependency-phase engine | one control plane; direct readiness integration | couples policy experimentation to lifecycle/claim machinery; higher regression blast radius | phase engine owns readiness/claims only |
| C. Standalone Ballet scheduler | clean conceptual boundary | duplicates scheduling, ownership, idempotency, state and recovery | reject |
| D. Workflow-matrix-only | native GitHub parallelism; simple CI | static DAG semantics; adaptive waiting/handoff and merge conflict remain external | benchmark baseline |
| E. External multi-agent framework | feature breadth and integrations | new runtime/state/provenance dependencies; may conflict with local contracts | adapter-only research candidate |
| F. Ballet policy adapter + DoE treatment | bounded scope; deterministic; reuses gates/evidence; measurable | needs online receipts and phase-engine integration before production dispatch | **recommended** |

### Critical findings

1. A planner can prove its emitted waves respect the supplied graph/write sets; it cannot prove those declarations are complete.
2. Simulated makespan is not observed end-to-end integration time. Online receipts remain authoritative.
3. The initial weighted Moneyball score is a transparent experiment index, not objective intelligence or correctness. Publish raw dimensions and run weight sensitivity.
4. A single-cohort winner is not promoted. Use repetitions, uncertainty-aware comparison, and fresh holdout.
5. Maximum parallelism is not inherently optimal; quota pressure, context duplication, merge contention and human review can erase speed gains.
6. The reference planner is not a dispatch adapter. Live execution requires phase-engine and writer-lease integration first.

## 8. DoE / MVT proposal

### Fixed controls
- Same task cohort and task-contract hashes.
- Same dependency graph, write-set declarations, acceptance rubric and environment.
- Same specialist allowlist, adapters, quota policy and evaluator.
- Randomized/repeated arm assignment where practical.
- Incumbent manager policy retained as control.

### First-factor design

| Factor | Levels |
|---|---|
| choreography strategy | sequential, parallel, adaptive |
| capacity treatment | 1, 2, 4 (experiment setting, not production cap) |
| repetition | at least 3 per arm for pilot; expand based on variance |

The implementation emits a 3×3 full-factorial strategy/capacity design. Later L9 or fractional-factorial designs can add task family, manager policy version, cohort complexity and handoff protocol.

### Outcomes
Primary: accepted integrated outcome; deterministic correctness/validation pass; time-to-integration.

Secondary: total cost/quota, retries, duplicate actions, write conflicts, human interventions, useful parallelism, handoff latency, feedback cycles, attribution confidence, provider failures and variance.

Guardrails: no wrong-commit promotion, boundary leakage, required-fragment omission, cross-agent private-context leakage, unapproved dispatch, or missing provenance.

### Score and analysis
The reference exposes versioned weights and raw components. Default v1: 35% integrated correctness, 25% acceptance, 15% time, 15% cost, 10% coordination efficiency. Time/cost baselines are explicit evaluator inputs. Do not compare scores across different baselines or weight versions without normalization and sensitivity analysis.

Publish per-arm raw metrics, components, confidence intervals, sample count, failures/censoring and cohort/contract hashes. Composite scores cannot override correctness failures.

## 9. RFP response requirements

Bidders or internal alternatives must provide:
1. architecture and control-plane boundary map;
2. dependency, write-conflict and handoff semantics;
3. deterministic replay and online execution separation;
4. supported strategy families and capacity behavior;
5. event/evidence schema and provenance chain;
6. security, least-privilege and failure recovery model;
7. reproducible benchmark protocol and sample-size rationale;
8. cost model including integration and human effort;
9. migration plan preserving manager/phase contracts;
10. exit strategy and data portability.

Scoring: correctness/safety 30%; architecture fit 20%; evidence/reproducibility 20%; integration cost 10%; operational cost 10%; portability/maintainability 10%. A hard safety failure or source-of-truth duplication disqualifies an option regardless of weighted score.

## 10. Delivery phases

- P0 reference primitive: deterministic planner, validation, tests, versioned score and DoE bridge. Implemented in this branch.
- P1 evidence adapter: map real phase-engine and ATES/Action→Effect receipts into Ballet observation contract.
- P2 shadow mode: generate plans beside incumbent without dispatch; compare expected/actual waves and surface graph/write-set gaps.
- P3 bounded pilot: manager-approved dispatch for low-risk task families with existing leases and adapter gates.
- P4 tournament: repeated randomized cohorts, holdout validation, sensitivity analysis, incumbent preservation.
- P5 promotion: existing correctness gates and explicit operator decision only.

## 11. Open integration questions

- Which manager-policy identifier is the incumbent control for the first cohort?
- Which phase-engine API exposes authoritative ready/running/awaiting_review/blocked/complete state?
- Which canonical event schema carries choreography and handoff references?
- Which task families have reliable write-set declarations?
- What cohort size and variance justify promotion?

These are prerequisites, not reasons to create substitute control planes.

## 12. Recommendation

Proceed with option F. Keep Ballet a Tier-2 policy coordinator; keep dependency readiness, provider routing, execution, evidence and promotion in their existing owners. Run the first tournament in shadow/replay mode, then a manager-approved online holdout. Do not enable autonomous dispatch or automatic promotion in this implementation.
