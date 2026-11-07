# Autonomous Escalation & Recovery — BIUDL Master Plan

**Proposal:** `langgraph-biudl-integration`
**Plan ID:** `autonomous-escalation-orchestration`
**Status:** P1 contracts and a pure-Python P2 controller are implemented on the feature branch; schema/runtime validation and repository gates are pending
**Decision:** escalation is autonomous specialist escalation, not human-in-the-loop approval.

## 1. Executive decision

The system should not stop and wait for a person when an agent lacks context, capability, confidence, progress, or a successful execution path. It should autonomously diagnose the gap, select a more suitable specialist or manager policy, transfer a bounded evidence package, and continue.

**HITL is not the target architecture.** Remove approval interrupts, approval queues, human-resume workflows, and "ask a person to continue" as normal recovery paths from the LangGraph treatment and its benchmarks.

This does not mean agents may grant themselves new permissions. Escalation changes the executor, expertise, strategy, or scrutiny—not the authorization envelope. A policy-denied action stays denied. If a credential, external permission, device interaction, or irreversible operation is unavailable to the system, record a blocked terminal state and continue with independent safe work; do not disguise a human approval requirement as an agent escalation.

## 2. Desired outcome

A self-correcting orchestration system that:

1. detects task risk, uncertainty, stagnation, tool failure, and capability mismatch early;
2. tries the cheapest safe recovery at the current tier;
3. escalates to a better-matched specialist when local recovery is insufficient;
4. uses an independent verifier or red-team agent for consequential outputs;
5. preserves task identity, evidence, provenance, and state across handoffs/restarts;
6. prevents duplicate side effects, escalation loops, retry storms, and permission drift;
7. learns which escalation paths work for which task classes;
8. completes autonomously whenever the task is inside the pre-authorized capability and permission envelope.

## 3. Terminology and non-goals

- **Retry:** same executor, same strategy, transient failure only.
- **Repair:** same tier changes its plan or corrects a bounded defect.
- **Escalation:** transfer to a different executor, capability tier, or manager strategy because the current path is insufficient.
- **Verification:** independent check of the claimed result against deterministic acceptance criteria and source evidence.
- **Arbitration:** manager resolves conflicting specialist results using policy and evidence.
- **Containment:** stop or isolate an unsafe/unauthorized path while allowing unrelated safe tasks to continue.
- **Human-in-the-loop:** pause for a person to approve, provide input, or resume. Excluded from normal workflow design.

Not a goal: removing authorization controls, granting broader permissions on escalation, maximizing agent count, maximizing model calls, or using a framework's internal state as canonical project evidence.

## 4. Autonomous escalation ladder

The ladder is capability-based, not a fixed provider hierarchy. The manager resolves actual eligible adapters from the live roster, catalog, quota, and task requirements.

| Tier | Name | Action | Enter when | Exit when |
|---|---|---|---|---|
| E0 | Local execution | Current worker follows the original plan | Task is understood and eligible | Verified pass or a trigger fires |
| E1 | Self-repair | Re-read evidence, correct assumptions, retry a bounded operation, or choose an alternate tool | Transient error, malformed result, low progress, or verifier feedback | Progress resumes, pass, or repair budget exhausted |
| E2 | Specialist handoff | Delegate a well-scoped subtask to a capability-matched peer | Skill/domain gap, missing independent evidence, tool-specific expertise needed | Specialist returns evidence-backed result or fails |
| E3 | Senior specialist / alternate model | Route to a higher-capability or different-family executor | E2 failed, disagreement, repeated hallucination, complex diagnosis | New plan/result passes independent verification |
| E4 | Manager arbitration | Manager compares candidate plans/results, splits the task, changes sequencing, or chooses a different treatment | Conflicting outputs, repeated stagnation, coordination deadlock, resource imbalance | One evidence-backed route is selected or safe terminal state |
| E5 | Independent assurance | Separate verifier/security/reviewer lane challenges the result and checks policy/evidence | High-impact output, security-sensitive change, uncertain provenance, or promotion candidate | Pass, repair loop within budget, or quarantine/fail |

E5 is independent verification, not approval. The verifier cannot grant permissions or authorize an otherwise prohibited action. Escalation may move sideways to an independent peer rather than always upward to a larger model.

## 5. Trigger model

Every trigger is observable, typed, and tied to a response. Avoid confidence-only escalation; model self-reported confidence is a weak signal.

| Trigger | Evidence | Response |
|---|---|---|
| Capability mismatch | Required capability absent from roster or tool adapter | Route to eligible specialist; if none exists, mark blocked-capability |
| Repeated tool failure | Same normalized error class across bounded attempts | Change adapter/provider or escalate; do not replay identical request indefinitely |
| Low progress / stagnation | No accepted state/evidence delta across configured observation window | E1 repair, then E2/E4 if no measurable delta |
| Contradictory outputs | Independent workers disagree on a material fact or patch | E4 arbitration; E5 verifier for high-impact claims |
| Verifier rejection | Deterministic test/contract/citation check fails | Route exact failing evidence to responsible specialist |
| Context saturation | Truncation, lost constraints, excessive irrelevant context, or unstable state | Compress to a provenance-preserving task packet; spawn clean specialist context |
| Provider degradation | Rate limit, outage, quota exhaustion, abnormal latency | Cooldown and dynamic route to eligible alternative |
| Security anomaly | Prompt injection, secret exposure attempt, policy mismatch, suspicious tool output | Contain affected branch; isolate untrusted content; invoke security verifier |
| Deadline/resource pressure | Forecast budget burn exceeds remaining value | Re-plan, narrow scope, parallelize independent work, or return partial verified result |
| Repeated escalation | Same task returns to same executor/strategy without new evidence | Detect cycle; prohibit route; manager changes treatment or terminates |

Thresholds must be calibrated from the repository's observed latency/progress distributions, not arbitrary global timeouts. Initial test defaults may be used in fixtures, but production thresholds are data-driven and cohort-specific.

## 6. Escalation packet contract

Each handoff carries a compact, typed, privacy-safe packet:

- canonical `orchestration_id`, `cycle_id`, `attempt_id`, `action_id`;
- task objective and acceptance criteria;
- task class, required capabilities, risk classification;
- repository/ref/SHA or source snapshot identity;
- current execution state and bounded progress summary;
- attempts made, normalized error classes, and strategies already tried;
- verified facts with source/evidence IDs and confidence/attribution;
- unresolved questions and explicit assumptions;
- allowed tools, scope, side-effect budget, and existing authorization envelope;
- requested specialist role and expected output schema;
- deadline/resource budget and escalation reason.

Do not transfer raw secrets, credentials, session stores, unrestricted prompts, private checkpoint blobs, or unnecessary conversation history. Give each specialist the minimum context required to complete its subtask. The packet references evidence; it does not duplicate the whole transcript.

## 7. Routing and team coordination

The normative P1 handoff and decision contracts are [ESCALATION-PACKET.schema.json](./ESCALATION-PACKET.schema.json), [ESCALATION-DECISION.schema.json](./ESCALATION-DECISION.schema.json), and [AUTONOMOUS-ESCALATION-POLICY.md](./AUTONOMOUS-ESCALATION-POLICY.md). The schemas define bounded packet fields, reason/decision vocabularies, budget snapshots, terminal states, and the invariant that authorization is inherited and cannot expand. Schema validation and runtime counter alignment remain explicit P1/P2 exit checks.

Use existing `docs/ops/AGENT-TEAM-ORCHESTRATION.md`, `docs/schemas/agent-roster.yaml`, provider catalogs, and execution adapters as the source of eligibility.

Routing order:

1. classify task and required capability;
2. filter by permission, adapter availability, live health, quota, and task fit;
3. rank candidates using observed outcome, useful feedback cycles, integrated-result time, reliability, context efficiency, cost, and attribution confidence;
4. prefer a different executor/family after a repeated failure when independence is valuable;
5. dispatch only if an actual adapter exists;
6. record route resolution separately from invocation and outcome;
7. re-evaluate from evidence after each attempt.

Do not hard-code Gemini → OpenRouter → Jules or any other permanent primary/secondary chain. Jules and other specialists are bounded escalation destinations, not universal sinks. Parallelize only independent subtasks; serialize dependent work. Use a single-writer or explicit merge-owner rule for shared files.

## 8. Graph architecture

The proposed graph is a control-flow implementation of the existing manager policy, not a second manager or permission authority.

```text
Intake / task envelope
        |
        v
Classify + normalize + policy preflight
        |
        v
Capability / risk / budget assessment
        |
        v
Select treatment + executor (E0)
        |
        v
Execute bounded task
        |
        v
Observe result + progress + evidence
        |
        v
Deterministic verifier
   | pass             | fail / stagnate / mismatch
   v                  v
Record outcome      Classify failure
   |                  |
   v                  v
Complete         E1 self-repair
                      |
                 progress?
                  /      \
                yes       no
                |          |
             Verify    E2 specialist
                           |
                       verify result
                           |
                    conflict / failure?
                       /       \
                     no         yes
                     |           |
                  Complete    E3 alternate
                                  |
                              E4 manager
                                  |
                           E5 independent
                              assurance
                                  |
                        pass / repair / contain
```

Required node families:
- `intake_validate`
- `classify_task`
- `policy_preflight`
- `resolve_capabilities`
- `select_treatment`
- `dispatch_executor`
- `observe_progress`
- `classify_failure`
- `repair_local`
- `escalate_specialist`
- `arbitrate_results`
- `verify_independently`
- `contain_branch`
- `record_receipt`
- `terminal_classify`

Every edge has a typed reason. Every cycle has a bounded attempt/escalation budget and a progress predicate. No graph node may convert a policy denial into an approval.

## 9. State, persistence, and recovery

Keep graph state minimal and typed. Store references to source evidence rather than full content where possible.

Suggested state groups:
- identity and immutable task envelope;
- execution tier and current executor;
- attempt and escalation counters;
- candidate route and adapter health snapshot;
- progress/evidence references;
- verifier results;
- normalized failure classification;
- side-effect ledger/idempotency keys;
- resource/deadline budget;
- terminal state/outcome/promotion.

Use LangGraph checkpointing only if it materially improves graph recovery. For distributed durable execution, prefer the existing Temporal boundary. Do not layer multiple durable engines around the same unit of work without a tested ownership model.

Recovery is automatic: restore last safe checkpoint, inspect completed effects, deduplicate by idempotency key, resume from the last uncommitted step, then verify. No approval interrupt is needed. Checkpoints are restricted data and are never canonical GitHub/ATES evidence.

## 10. Permission and safety invariant

Escalation never changes authorization.

- Each executor inherits the same or narrower task-scoped permission envelope.
- A higher model, senior agent, or manager cannot mint credentials, expand repository scopes, bypass branch protection, or override policy.
- Tool adapters enforce authorization at the point of action; graph-level checks are defense in depth, not the sole gate.
- Irreversible/destructive actions outside existing pre-authorization are denied, not sent to a human approval interrupt.
- Credential rotation, first-time permission grants, protected-branch configuration, device-side Termux operations, and provider logins remain unavailable unless the relevant system capability is already provisioned. Mark these blocked and continue independent work.
- Prompt-injected content and tool output are untrusted data. They cannot modify policy or escalation rules.
- Security anomaly: contain, preserve sanitized evidence, and route to an independent security lane.

This is autonomous execution within explicit authority, not autonomous authority expansion.

## 11. Retry, escalation, and termination budgets

Use separate counters:
- `local_repair_count`
- `same_adapter_retry_count`
- `specialist_handoff_count`
- `alternate_family_count`
- `manager_replan_count`
- `independent_verification_count)

A retry requires a transient/recoverable classification and a changed condition or backoff. An escalation requires a capability or evidence reason. Never increment both for the same no-op action.

Budget policy:
- no unbounded loops;
- no same executor + same strategy + same input after an identical failure;
- no duplicate side effects on replay;
- stop a branch when its expected value is below its remaining cost or risk budget;
- retain useful verified partial results when another branch is blocked;
- mark terminal states distinctly: `TASK_PASS`, `TASK_FAIL`, `BLOCKED_CAPABILITY`, `BLOCKED_PERMISSION`, `STAGNATED`, `BUDGET_EXHAUSTED`, `QUARANTINED`, `UNKNOWN`.

Initial numerical limits belong in test fixtures and policy config, not hard-coded in graph nodes. Calibrate production values using cohort evidence.

## 12. Observability and learning

Reuse native orchestration receipts, ATES, OpenTelemetry, context relationship graph, and provider/agent outcome catalog. Extend schemas only when existing contracts cannot express a required dimension.

Capture safe metadata:
- escalation reason and source tier / target tier;
- selected executor role/provider/model and route-resolution snapshot;
- attempt number and normalized failure class;
- progress delta and accepted evidence count;
- handoff latency and useful-output ratio;
- duplicate/conflicting work;
- verifier outcome and independent disagreement;
- cost/resource consumption and terminal classification.

Do not persist raw prompts, completions, tool arguments, checkpoint payloads, secrets, or arbitrary graph state. Hash/fingerprint labels where the current bridge requires it. Distinguish route-selected, dispatched, invoked, completed, verified, and promoted.

Learning loop:
1. compare escalated and non-escalated cohorts;
2. measure whether escalation improved verifier pass rate, time-to-integrated-result, recovery, or cost;
3. identify unhelpful routes, repeat loops, and false escalations;
4. update treatment weights/thresholds from evidence;
5. retain a rollback snapshot and source attribution;
6. rerun the same benchmark fixtures before promotion.

Do not optimize raw model score or call count. Optimize useful integrated work.

## 13. Competitive benchmark redesign

Replace the "human approval" benchmark with autonomous escalation cases:

1. deterministic tool failure → local repair → verifier pass;
2. capability mismatch → specialist handoff → evidence-backed completion;
3. contradictory specialist outputs → manager arbitration → independent verification;
4. worker/process crash → idempotent recovery without duplicate effects;
5. provider rate limit/outage → dynamic alternate route and cooldown;
6. prompt injection / permission escalation attempt → branch containment and safe continuation;
7. repository change → implementation agent, separate reviewer, deterministic tests, current-SHA evidence;
8. escalation loop trap → cycle detection, route exclusion, and explicit terminal classification.

All treatments receive identical task fixtures, tool scopes, budgets, and verifiers. Include native manager, LangGraph, Deep Agents, Agent Framework, OpenAI Agents SDK, Google ADK, LlamaIndex, CrewAI, PydanticAI, swarm/handoff, and selected hybrids. Do not require every framework in the production stack.

## 14. Metrics and promotion

Primary metrics:
- task verifier pass rate and requirement coverage;
- autonomous recovery success;
- escalation precision (useful escalations / all escalations);
- escalation recall on tasks where base tier fails;
- time to verified integrated result;
- useful-output ratio per handoff;
- repeated failure / loop rate;
- duplicate side-effect count;
- independent-verifier disagreement and catch rate;
- cost, latency, token/tool usage;
- policy violation and quarantine rate;
- evidence completeness and attribution confidence.

Hard gates: zero unauthorized side effects, zero secret leakage in exported telemetry, idempotent recovery, no self-granted permission, no false success terminal state. A single hard-gate violation disqualifies a treatment.

Promotion requires repeatable gains against native manager control, no material regressions, independent verifier pass, current-SHA repository and Termux gates, documented rollback, and a bounded production rollout. Use shadow mode first, then low-risk canary, then progressive cohort expansion. Keep human approval workflows out of the benchmark and runtime design; external platform/credential limitations remain blocked states, not HITL tasks.

## 15. Implementation roadmap

| Phase | Work | Deliverable / exit criteria |
|---|---|---|
| P0 — Correct the model | Remove HITL assumptions from LangGraph skill, architecture, benchmark, and proposal; establish this plan as SSOT | No approval interrupts or human-resume path in the target design |
| P1 — Formalize contracts | Define escalation reasons, tiers, packet, terminal states, counters, policy inheritance, receipt mapping | Schemas/config validate; current receipts reused where semantically valid |
| P2 — Deterministic controller | Implement pure routing/trigger/budget functions and unit tests without model/provider dependencies | All escalation paths deterministic under fixtures |
| P3 — Graph adapter | Add minimal optional LangGraph StateGraph treatment using stub executors and native adapters | Compile/invoke, route, reducer, and bounded-loop tests pass |
| P4 — Durable recovery | Test Temporal or selected checkpointer recovery, idempotency, duplicate suppression, crash/restart | Fault-injection tests prove exactly-once effect semantics or explicitly documented at-least-once + idempotency |
| P5 — Specialist adapters | Connect capability roster, live catalog/health/quota, specialist execution adapters, and evidence packet | No declared route without a real adapter; all invocations attributable |
| P6 — Independent assurance | Add verifier/security specialist lanes, disagreement handling, and arbitration | Adversarial and conflict tests pass; verifier cannot authorize |
| P7 — Telemetry + learning | Versioned event/receipt additions only where needed; dashboard/decision ledger; cohort metrics | Privacy tests and reproducible evaluation reports |
| P8 — Competitive evaluation | Run common corpus across selected treatments and hybrid combinations | Evidence-backed keep/adapt/combine/defer/reject dispositions |
| P9 — Progressive deployment | Shadow → low-risk canary → cohort expansion with rollback | Current-SHA dual gates, monitoring, rollback drill, promotion record |

## 16. Work breakdown and ownership

- **LGB-011:** autonomous escalation policy and tier contract (P0/P1).
- **LGB-012:** typed escalation packet, reason taxonomy, terminal states, and counters (P1).
- **LGB-013:** deterministic routing/trigger/budget controller (P2).
- **LGB-014:** LangGraph escalation graph adapter (P3).
- **LGB-015:** crash recovery, persistence, idempotency, and side-effect ledger (P4).
- **LGB-016:** capability roster and specialist adapters (P5).
- **LGB-017:** independent verifier, security lane, arbitration, containment (P6).
- **LGB-018:** sanitized escalation telemetry and learning loop (P7).
- **LGB-019:** expanded benchmark corpus and treatment experiments (P8).
- **LGB-020:** shadow/canary rollout, rollback, and promotion (P9).

The native manager owns policy and routing. Specialists own bounded delegated work. Independent verifiers own challenge/evaluation, not authorization. The evidence collector owns truthful invocation/outcome attribution. GitHub and existing repository governance own merge/promotion evidence.

## 17. Immediate next actions

1. Correct the current PR's HITL terminology and benchmark.
2. Add this plan and link it from the integration architecture and skill.
3. Update LGB-005 to persistence/recovery/idempotency without interrupt/resume.
4. Add LGB-011–020 to the proposal work register.
5. Implement P1 contracts and P2 deterministic controller before selecting a graph framework.
6. Reconcile PR branch with current master, run current-SHA repository gate and Termux smoke, and collect review findings.
7. Do not add runtime dependencies until the deterministic controller and adapter boundary prove a real LangGraph benefit.

## 18. Decision record

**Chosen:** autonomous escalation among authorized agents/specialists, manager arbitration, independent verification, bounded automatic recovery, and safe containment.

**Rejected:** human approval interrupts, human-resume queues, agent-created approval gates, permission elevation through escalation, fixed provider fallback chains, unbounded retry loops, and self-certifying success.

**Open implementation choices:** LangGraph vs native controller for the first runtime slice; Temporal vs a LangGraph checkpointer for recovery ownership; initial trigger thresholds; specialist routing weights. Resolve these through repo inspection and benchmark evidence, not assumption.
