# QUE × Routing × DoE Optimization Plan

**Status:** proposed bounded implementation plan  
**Depends on:** `docs/architecture/WORKFLOW-PLANNING-OPERATING-MODEL.md`

## Objective

Improve the probability and speed of producing a verified integrated result per unit of inference, compute, queue capacity and human attention — without weakening correctness, security, attribution or repository governance.

## 1. Baseline map

| Plane | Existing artifact | Responsibility | Planned seam |
|---|---|---|---|
| Queue producer | `ops/que/feeds/que-queue-feed.json` | queue/tier/claim read model | WFC admission envelope |
| Queue measurement | `ops/que/events/YYYY-MM-DD.jsonl` | queued/started/completed/cancelled/vanished events | queue-wait and gap metrics |
| Governor | `ops/que/feeds/governor.json` | thresholds and deferrals | resource-aware admission |
| Dispatch state | `ops/challenge/dispatch-state-feed.json` | claims and dispatch status | readiness/dependency join |
| Routing | `.github/actions/model-router`, `scripts/model_router.py` | provider/model selection | policy-versioned routing decision |
| Invocation | `.github/actions/http-llm-invoke` | actual HTTP model invocation | endpoint latency/cost/outcome telemetry |
| Evaluation | DoE/MVT + ATES + MoneyBall/3L0 | compare treatments and verified results | common experiment receipt |
| Dashboard | Desk/Admin/SHE | read-only operational view | WFC + evidence projections |

## 2. QUE control improvements

1. Preserve single-flight collection; do not create competing collectors.
2. Measure queue age, queue wait, claim latency, lease expiry, deferral reason, and completion latency separately.
3. Add explicit dependency readiness and deadline feasibility to admission, not only priority.
4. Apply backpressure when provider quota, endpoint concurrency, or device resources are constrained.
5. Keep starvation detection and bounded priority windows; aging must not bypass security or owner approval.
6. Make idempotency and lease ownership explicit; expired claims must be reconciled before reassignment.
7. Distinguish queued, running, waiting, blocked, deferred, vanished, failed and completed.
8. Emit events append-only; derive feeds from events and preserve watermarks/coverage.

## 3. Routing policy dimensions

Hard gates first:
- credential and endpoint availability;
- task capability and tool requirements;
- data handling and security policy;
- repository/ref/SHA validity;
- quota and concurrency;
- role/ownership and approval;
- task deadline and budget feasibility.

Then compare eligible topologies:
- serial specialist;
- parallel independent scouts + integrator;
- builder → independent reviewer;
- primary → fallback on classified transient failure;
- manager tournament on a controlled cohort;
- durable Temporal workflow for long-running, signal-driven tasks.

Every decision receipt records eligible candidates, exclusions and reasons, policy/config versions, selected topology, budget reservation, and fallback path.

## 4. DoE first pilot

**Question:** Which routing topology minimizes cost and time while maintaining or improving verified integrated success for a defined task family?

### Stage A — screening

Use a small, blocked factorial design:

- Factor A: serial vs parallel scouting.
- Factor B: one reviewer vs two independent reviewers.
- Factor C: fixed provider vs evidence-based dynamic provider selection.
- Factor D: compact vs provenance-rich context retrieval.

Block by task family and complexity band. Pin task suite, base SHA, prompts, endpoint catalog snapshot and environment. Randomize assignment within blocks where possible.

### Stage B — optimization

Select influential factors from Stage A. Use a bounded response-surface or Bayesian optimization study for continuous parameters such as concurrency, context budget and retry delay. Do not optimize against a single scalar until hard constraints and Pareto reporting are established.

### Responses

Primary:
- verified integrated PASS rate;
- regression-free acceptance rate;
- cost per verified PASS;
- time-to-verified-PASS.

Secondary:
- queue wait;
- token/context consumption;
- duplicate work;
- retries and provider errors;
- merge conflicts/rework;
- human intervention;
- attribution confidence;
- resource/quota pressure.

### Guardrails

- Correctness/security/required review are non-compensatory gates.
- Missing data remains missing; no synthetic zero.
- Retain all failed and interrupted attempts.
- Separate simulated MiroFish results from empirical results.
- Promote routing policies after independent evidence and verified outcomes.
- Pre-register stopping and promotion criteria.
- Independent reviewer validates treatment assignment and outcomes.

## 5. Optimization hypotheses

| Hypothesis | Observable | Disconfirming evidence |
|---|---|---|
| Parallel scouts reduce discovery time | time to accepted integrated result | integration/rework cost cancels saved time |
| Two independent reviewers reduce escaped defects | regression rate / review disagreement | no meaningful quality gain or excess latency |
| Context compression improves efficiency | cost per verified result | loss of provenance/correctness |
| Queue-aware routing reduces provider failures | transient failure and retry rates | admission overhead increases total delay |
| Single-flight feed refresh reduces waste | duplicate collector work | freshness/coverage degrades |
| Specialist handoff improves task outcome | success by task family | handoff cost exceeds marginal quality |
| MiroFish can improve experiment selection | yield of pre-registered hypotheses | simulated ranking fails on held-out empirical runs |

## 6. Rollout

- **R0 Observe:** no policy change; derive baseline metrics from existing feeds and runtime evidence.
- **R1 Shadow:** calculate proposed admission/routing decisions beside current decisions; do not dispatch from shadow output.
- **R2 Bounded cohort:** controlled task suite, fixed resource cap, explicit owner approval.
- **R3 Compare:** paired/blocked analysis, uncertainty, Pareto frontier and failure review.
- **R4 Promote:** only after both `repo-gate` and `termux-smoke` pass on the same immutable head SHA, independent review, verified task outcome and recorded rollback.
- **R5 Monitor:** change-point detection, quota/endpoint drift, regression and policy rollback thresholds.

## 7. Exit criteria

- Every sampled task joins WFC → QUE → route decision → execution → evidence → outcome.
- Queue and execution time are measured separately.
- Endpoint and prompt/config versions are attributable.
- DoE treatment assignment is reproducible.
- Verified outcome and cost denominators are explicit.
- Shadow decisions cannot dispatch or mutate state.
- At least one optimization demonstrates improvement without violating quality/safety gates before promotion.
