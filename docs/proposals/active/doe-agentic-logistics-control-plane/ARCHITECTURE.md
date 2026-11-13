# Architecture — DoE agentic logistics control plane

## Separation of concerns

| Layer | Canonical role | Candidate / interface | Must not own |
|---|---|---|---|
| Agent components | Prompt/model/tool/retrieval composition | LangChain | Global scheduler, provider entitlement, durable workflow state |
| Stateful orchestration | Graph state, node transitions, fan-out, checkpoints | Existing LangGraph integration PR #5045 | Cross-worker durable timer/queue authority |
| Durable execution | Long-running workflow state and recovery across workers | Existing Temporal adapter | Model selection and experiment truth |
| Symbolic planner | Action preconditions/effects, goal reachability, precedence | PDDL + Unified Planning / compatible planner | Live quota, continuously changing numeric capacity |
| Learned logistics policy | Data-driven local navigation/task execution over a validated library map | Existing Library RL Q-learning prototype, behind a typed adapter | Hard safety constraints, task authority, symbolic precedence or production admission |
| Constraint optimizer | Assignment, capacity, time windows, routing | OR-Tools CP-SAT / Routing | Provider entitlement and execution authorization |
| Runtime controller | Bounded admission, pacing, concurrency/backpressure | Fixed / hysteresis / PI / MPC treatments | Credential management, paid fallback, policy relaxation |
| Provider capability/admission | Exact route, model/account, quota, terms, health and data policy | Existing provider index, #5134/#5160, quota registry | Discovery-only catalog claims as runtime admission |
| Experiment design and measurement | Treatments, allocation, outcome, replication, evidence | DoE / ATES / 3L0 | Production approval |
| Dispatch and queue admission | Work intake, tiering, dependency order, claim/lease | QUE / QDesk | Direct model/provider selection at filing |

## Data flow

1. A request is classified and filed through the current issue/template path.
2. QUE performs admission and tier/dependency checks; a task is not considered owned until a participant claims it.
3. The task planner derives symbolic actions and hard precedence from a validated task/domain model.
4. Constraint optimization allocates numeric capacity and time windows where required.
5. Where a learned policy is evaluated, the existing Library RL implementation runs behind a typed adapter against a pinned map/task fixture; an independent verifier enforces collision, deadlock, capacity and task-completion constraints.
6. The orchestration layer executes the selected graph or direct path; Temporal wraps it only when durable cross-worker execution is needed.
7. Before a provider call, the existing per-instance admission gate verifies route, current health, no-cost entitlement, quota freshness/headroom, data classification and provenance.
8. The controller observes telemetry and may recommend bounded admission/pacing actions. Initial trials remain offline or shadow-only.
9. ATES/DoE records outcomes, and an independent verifier checks task correctness and safety.
10. The Observatory consumes canonical feeds and receipts; it does not become another ledger.

## Feedback-control model

Plant instance identity is provider × model × endpoint × account/configuration, tied to the repository's existing configured-instance contract. Role identity and agent/provider identity remain separate.

- **State vector (observed only where evidenced):** q = queue depth/age; c = in-flight concurrency; lambda = arrival rate; mu = successful completion rate; e = timeout/error/429 rates; L = latency distribution; h = quota headroom with provenance; r = time to reset with timezone; a = health evidence age.
- **Control vector (bounded candidates):** admission cap; request pacing; cooldown/backoff; per-arm concurrency ceiling; shadow allocation.
- **Disturbance vector:** arrival burst; provider/network degradation; upstream rate limits; shared-pool contention; model availability changes; reset boundary.
- **Hard constraints:** invalid action = 0; paid cost = 0; no call with stale/unknown admission evidence; no permission expansion; no controller action may change credentials or account state.

Use saturation and anti-windup for integrator-based candidates; hysteresis to prevent threshold flapping; bounded sampling and slew rate; backpressure before retries. A controller cannot create quota or healthy capacity. Unknown state means hold/defer, not optimistic estimation.

## Planning semantics

PDDL actions represent symbolic lifecycle moves such as admit-task, assign-task-to-arm, start-task and complete-task, and logistics moves such as load, unload, move and deliver. Preconditions/effects preserve dependency and state invariants.

The existing Library RL project supplies a separate learned navigation/task policy over its own GridWorld representation. Its policy output is advisory to the adapter until a deterministic verifier accepts the transition. Keep the library map, pickup/drop-off semantics and RL state/action mapping explicit; do not silently equate its encoded state IDs with PDDL predicates or OR-Tools variables.

Use PDDL for reachability and symbolic order; use CP-SAT/Routing for numeric capacities, assignment and time windows; use the Library RL policy as a measured comparative treatment for local multi-agent navigation; use runtime feedback control for dynamic pacing. Do not encode operational truth in duplicate plan files: execution receipts and task registries remain canonical.

## Failure containment

- Plan invalid or no solution: hold the task and emit a reasoned plan failure.
- Planner unsupported feature: explicit UNSUPPORTED; select a compatible treatment only if pre-registered.
- Optimizer timeout: return a verified incumbent/feasible plan if one exists; otherwise defer.
- Provider admission missing/stale/unknown: no call; continue independent offline work.
- Controller sensor stale/out-of-range: freeze to the safe baseline/defer; no extrapolated quota.
- Orchestrator worker crash: use existing durable execution/recovery owner; idempotent task identity.
- Independent verifier missing or self-equal to builder: no validated success.
- Evidence missing: status remains NOT_ESTABLISHED, BLOCKED, SKIPPED or SIMULATED as applicable.

## Initial architecture decision

The first deliverable is a deterministic offline simulator and a small set of PDDL/constraint fixtures. There is no case for installing every upstream framework, making the controller production-authoritative, or routing live traffic before repeatable measurement and admission evidence exist.
