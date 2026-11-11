# Quota-aware API admission + resilient compute mesh contract

**Status:** proposed integration contract; not yet wired into production dispatch  
**Version:** 0.1.0  
**Related SSOT / tracking:** quota allocations [#1884](https://github.com/timerloggedout-spec/termux-monorepo/issues/1884) · mesh-resilient compute [#1622](https://github.com/timerloggedout-spec/termux-monorepo/issues/1622)  
**Existing evidence:** [Cadence tick ledger](./CADENCE-TICK-LEDGER.md) · [Quota allocation planning](./QUOTA-ALLOCATION-PLANNING.md) · [GitHub rate-limit incident record](./RATE-LIMIT-2026-10-29.md) · [Continuity SPOF census](./CONTINUITY-SPOF-CENSUS-2026-11-01.md)

## 1. Purpose and boundaries

Connect the existing quota allocation, cadence, API telemetry, and mesh-resiliency systems without creating a competing source of truth.

The contract has two independent decisions:

1. **Compute placement:** where a job executes (GitHub Actions, a self-hosted/Termux worker, or another eligible provider).
2. **API admission:** whether a particular external API request is safe to issue, against the exact principal + quota resource + reset window it consumes.

Moving compute does **not** move the quota consumed by an API credential. A job moved from GitHub Actions to another compute provider still consumes the same GitHub bucket when it uses the same GitHub principal. Provider rotation is not a rate-limit bypass.

This is an additive integration proposal. It does not change the owner-set allocation SSOT, credential custody, provider eligibility, schedules, secrets, deployment, or spend authorization.

## 2. Reuse the existing sources of truth

| Concern | Canonical existing source | Contract role |
|---|---|---|
| Pool × focus × percentage | `ops/quota/allocations.json` (#1884) | owner-set allocation; no consumer edits |
| Provider entitlements / pool metadata | `ops/quota/registry.json` | eligibility, declared limits, refill semantics |
| Current readings | `docs/ops/generated/quota-status.json` and source-specific readings | current observed capacity; unknown remains unknown |
| Proposed pacing / stranded allocation | `ops/quota/allocation-plan.json` | derived plan, not a balance or authorization |
| Per-request GitHub response observations | PAT helper `ticks.jsonl`; `CADENCE-TICK-LEDGER.md` | evidence and reconciliation |
| Attempted API spend | helper `spend.jsonl` and future App/workflow equivalents | request attribution |
| Quota wall events | `ops/quota/rate-limit-events.json` | append-only incident history |
| Mesh workload / provider research | `docs/rfps/mesh-resiliency-free-compute/` (#1622) | compute eligibility and failover evidence |

**Do not create a second allocation table, duplicate quota registry, or shadow provider roster.** New records should reference the existing pool/service IDs and source evidence.

Important existing invariant: cadence ticks are evidence, not a spend-control input. The admission controller consumes current readings, policy, and reservations; reconciliation uses ticks to measure actual burn and improve subsequent estimates. A historical tick must never authorize a new request.

## 3. Three-ledger accounting model

Each request or compute dispatch has a stable `operation_id` and a unique `attempt_id`. Keep the following ledgers separate and reconcile them by those identifiers.

### 3.1 Intent / reservation ledger

Written before execution. Records:
- operation and attempt IDs;
- workload, lane, priority, and idempotency key;
- provider and execution surface;
- API provider, principal alias, resource/bucket ID, endpoint class;
- estimated request count or GraphQL point cost (unknown if not measurable);
- allocation pool/focus and policy version;
- reservation time, expiry, and release/commit state.

Reservations prevent concurrent workers from independently spending the same locally budgeted headroom. They are not proof that the upstream provider accepted or counted the request.

### 3.2 Execution / attempt ledger

Written at the request boundary:
- timestamp, attempt ID, normalized endpoint class and method;
- principal alias (never token or secret);
- status/result class, retry-after and request ID where safe;
- counted / uncounted / unknown classification;
- local reservation consumed, released, or left uncertain;
- compute provider and worker identity.

No authorization headers, token values, request bodies, raw secret-bearing URLs, or personal identifiers are stored.

### 3.3 Provider-observation ledger

Use response metadata already returned by the call wherever possible. For GitHub this includes the `x-ratelimit-limit`, `used`, `remaining`, `reset`, and `resource` headers, plus status and retry metadata. This is not an extra API call.

Store observations with:
- exact principal/bucket/resource identity;
- provider-reported limit, used, remaining, reset;
- observation timestamp, source endpoint, HTTP status;
- freshness and confidence;
- request correlation ID when available.

For non-GitHub providers, store only the balance, usage, refill, and reset fields actually exposed by the documented API or console evidence. Never infer an unreported credit balance from successful calls.

### 3.4 Reconciliation invariants

- Intent reservations are not provider usage.
- Local attempt counts are not automatically provider-counted requests.
- Provider headers are authoritative for the resource they describe at that response time, not for unrelated buckets.
- A tick's `resource` value must remain separate: PAT core, Search, GraphQL, each App installation, Actions installation, and other resources are not one aggregate bucket.
- Delta between consecutive observations is total bucket movement in that interval; it is not per-consumer attribution unless every relevant consumer emits a correlated tick.
- Missing observations produce `unknown`, not zero.
- Late, duplicate, and out-of-order events are retained and reconciled idempotently; do not silently overwrite evidence.
- A 403, secondary-limit response, 429, or retry-after signal trips the applicable resource circuit breaker. Do not retry-loop or change credentials/providers to evade the limit.

## 4. Admission decision

Admission is evaluated per request, not once per job. It must be fast, deterministic, and fail-soft for deferrable work.

Inputs:
1. pool/resource identity and provider;
2. live or sufficiently fresh reading;
3. current reset time and refill semantics;
4. outstanding local reservations;
5. operation's estimated cost;
6. derived reserve and priority class;
7. policy freshness and provider eligibility.

Decision states:

| State | Meaning | Action |
|---|---|---|
| `ADMIT` | sufficient verified headroom after reservations and reserve | issue one request |
| `ADMIT_WITH_LIMIT` | admitted with reduced concurrency / batch size | issue bounded work |
| `DEFER_UNTIL_RESET` | known reset and insufficient headroom | release lease, enqueue for reset |
| `DEFER_READING_STALE` | no sufficiently fresh reading | request a reading only if piggybackable; otherwise defer |
| `HOLD_UNKNOWN_COST` | request cost or billing status is unknown and could be billable | hold unless explicit policy permits |
| `CIRCUIT_OPEN` | upstream limit / retry-after / repeated provider failure | stop requests until reset or probe window |
| `REJECT_POLICY` | not eligible, unauthorized, or outside approved spend/focus | do not execute |

### 4.1 Derived reserve and pacing

Preserve the existing derived-reserve principle: calculate reserve from the live provider limit and policy, not a hardcoded count. Existing GitHub PAT publish and helper guardrails use a 10%-of-live-limit pattern; this contract does not silently alter those thresholds.

The scheduler computes safe headroom as:

`available = max(0, observed_remaining - outstanding_reservations - derived_reserve)`

For a known replenishment window:

`target_flow = eligible_budget / seconds_until_reset`

Use the existing allocation planner's focus ladder and per-slice pacing. Reserve is timing slack against jitter and concurrent consumers, not quota to waste. Release slack only according to the current approved policy and reset horizon. Do not increase the flow multiplier when the observation is stale, the pool is unknown, or a circuit is open.

### 4.2 Refill semantics

Every pool must declare one of:
- `rolling_window` — replenishes continuously or on a rolling interval;
- `fixed_reset` — replenishes at a documented reset boundary;
- `monthly_allowance` — replenishes on a billing-cycle boundary;
- `promotional_credit` — finite balance with explicit expiry; not assumed to refill;
- `one_time_credit` — finite, non-renewing balance;
- `usage_metered` — cost accrues by use; free status alone is insufficient;
- `unknown` — no automatic scheduling or utilization claim.

A provider's free tier and its promotional credit are distinct pool records unless the provider explicitly defines them as one balance. A monthly allowance is not a daily refill. A credit expiry is not a reset. No refill event is synthesized without evidence.

## 5. GitHub API surface selection and priority

Choose an API method by semantic fit, authorization scope, data shape, and bucket headroom—not by opportunistically switching credentials.

| Workload | Preferred surface | Guardrails |
|---|---|---|
| Bulk repository content transfer | Git transport (clone/fetch/push) where suitable | avoid repeated REST file reads; preserve branch protection and review gates |
| Bounded metadata / single-resource operations | REST | use pagination, conditional requests/ETags, and stop-on-condition |
| Cross-resource graph aggregation | GraphQL when query cost is understood | record point cost and keep GraphQL bucket distinct |
| Repository / code discovery | Search endpoints only when needed | separate Search and code-search windows; batch queries and avoid census loops |
| In-workflow repo-local actions | scoped `GITHUB_TOKEN` or approved GitHub App installation token | account for installation bucket and permissions |
| Cross-workflow / external agent work | registered least-privilege GitHub App principal | select by authorized role and repo scope; do not rotate principals to evade a wall |
| Interactive owner-ordered publishing | approved PAT route, subject to preflight and reserve | keep human/owner critical path protected; no retry on 403 |

Method-selection rules:
1. Reuse a fetched snapshot across lanes; do not run repeated `list --all` sweeps as a heartbeat.
2. Prefer event handoffs (`workflow_run`, `pull_request`, `issue_comment`) over polling where the trigger exists.
3. Respect the existing five-minute minimum for new fixed polling; orchestrator exceptions retain their separately owned bounds.
4. Use one check-runs request per head SHA, `per_page=100` where applicable, and bounded pagination.
5. Conditional GETs and 304 responses reduce redundant transfer; retain the actual provider resource classification.
6. Use GraphQL only when its point cost and result shape beat the REST alternative; do not assume it is free.
7. Never move a call to another principal solely to obtain a fresh bucket. Different GitHub principals are used only where the application/permission model authorizes them.
8. Keep App installation buckets distinct from PAT user buckets and Actions installation buckets. Do not merge their counters.

## 6. Compute mesh placement and failover

The compute scheduler selects a worker only after checking:
- workload runtime and architecture compatibility;
- verified free/credit eligibility and current provider evidence;
- spend ceiling and explicit paid-use denial by default;
- region/data residency and secret scope;
- provider health and recent successful drill evidence;
- job idempotency, checkpointability, and output durability;
- dependency failure domains (credential, API quota, storage, database, network).

A provider is not considered a continuity alternative merely because a deployment or account exists. It must pass a forced failover drill with a receipt.

### 6.1 Job lifecycle

`QUEUED → RESERVED → DISPATCHED → RUNNING → CHECKPOINTED → SUCCEEDED`

Exceptional states: `DEFERRED_QUOTA`, `DEFERRED_PROVIDER`, `RETRYABLE_FAILURE`, `CIRCUIT_OPEN`, `NEEDS_RECONCILIATION`, `CANCELLED`, `FAILED_FINAL`.

A lease expires safely. A worker restart must not create a second active writer for the same idempotency key. A failover attempt reuses the canonical operation ID, increments attempt ID, and resumes from the latest verified checkpoint. Non-idempotent external side effects require an explicit reconciliation step before retry.

### 6.2 Failure-domain rule

Compute redundancy is not API quota redundancy. Storage redundancy is not credential redundancy. Credit redundancy is not deployment redundancy. A failover route is eligible only when its critical dependencies are independently available or explicitly accepted as shared dependencies.

If GitHub's user PAT bucket is exhausted, moving the worker does not make that bucket available. The job must defer, use an already-authorized distinct resource only if its intended permission scope legitimately fits, or continue a non-GitHub portion of the work. It must not attempt endpoint/identity rotation to bypass the limit.

## 7. Priority and allocation

Apply the existing owner allocation SSOT and focus ladder. Within an eligible pool, dispatch order is:

1. **P0 Safety:** policy enforcement, authentication boundaries, cost ceilings, quota reserve, recovery correctness.
2. **P1 Continuity:** control-plane recovery, durable queue and checkpoint restoration.
3. **P2 Production:** required builds, tests, release evidence, approved repository mutations.
4. **P3 Evidence:** quota readings, provenance, telemetry, reconciliation, freshness collectors.
5. **P4 Research:** bounded experiments and provider evaluation.
6. **P5 Opportunistic:** low-priority tasks that use otherwise-stranded capacity without displacing higher priorities.

This is an execution priority, not permission to rewrite the owner-set Pool × Focus × % allocations. Any allocation change remains a reviewed PR citing #1884.

## 8. Cadence design

- Per-request observations are emitted inline with the request; do not schedule extra API calls merely to count the call just made.
- Piggyback a fresh quota reading onto an already-planned response whenever possible.
- Event-driven triggers are preferred for state transitions and completion.
- New fixed polling must respect the existing cadence-owner floor and trigger-accounting process.
- A reset-aware wake-up is scheduled from the provider's actual reset timestamp; no tight polling while waiting.
- Daily/monthly credit checks run only when their documented refill/expiry semantics warrant them.
- A stale snapshot must not trigger a speculative burst.
- Cadence changes are proposals to the cadence owner with executions/hour and API calls/execution; no unilateral workflow schedule edits.

## 9. Security and cost invariants

- Secrets remain in approved secret stores; ledgers contain principal aliases only.
- Provider credentials are never copied between compute nodes as a failover shortcut.
- No paid fallback, account signup, payment method, credit purchase, secret provisioning, or production deployment is authorized by this contract.
- Unknown pricing, unknown billing status, or unknown free-tier eligibility fails closed for billable work.
- A provider switch must not broaden permissions or move sensitive data to an unapproved region.
- Evidence stores are append-only or content-addressed; corrections are new events.
- All automation must be bounded, cancellable, and observable.

## 10. Implementation sequence

| Phase | Deliverable | Exit evidence |
|---|---|---|
| 0 — inventory | map current tick, spend, readings, reservations, and mesh queue surfaces | source-to-consumer matrix; no duplicate SSOT |
| 1 — common identity | stable operation/attempt IDs and pool/resource identity mapping | schema validation + duplicate/out-of-order fixtures |
| 2 — reconciliation | join reservations, PAT/App/workflow ticks, provider observations | drift report with unknowns explicit |
| 3 — admission library | deterministic decision function, no network calls | unit tests for reset, reserve, stale, unknown, concurrency |
| 4 — API chokepoints | adopt helper/App/workflow request wrappers | per-principal/resource coverage report |
| 5 — mesh scheduler | provider capability/health/credit gates, lease and checkpoint | offline failover simulation |
| 6 — observability | Gantt plan-vs-actual, burn/replenishment and defer reasons | source freshness and lineage receipts |
| 7 — controlled pilot | one idempotent, non-critical workload across two independent compute failure domains | forced failover, no duplicate side effect, no paid use |

No production pilot begins until the relevant owner review and explicit pilot authorization are recorded.

## 11. Acceptance tests

1. PAT core, Search, code-search, GraphQL, App installation, and Actions installation counters remain separate.
2. A request consumes one local reservation at most; concurrent workers cannot overspend the same local budget.
3. An unknown reading yields defer/hold, never a fabricated zero or available balance.
4. A stale reading cannot authorize a burst.
5. A known reset schedules one wake-up; no retry polling occurs before it.
6. A provider's one-time credit is not treated as a recurring refill.
7. Promotional expiry and monthly reset are represented separately.
8. Provider headers are recorded without a separate quota call.
9. A 403/429/secondary-limit response opens the correct circuit and records reset/retry metadata.
10. Moving compute while retaining the same GitHub principal does not increase available GitHub quota.
11. REST, GraphQL, Search, and Git transport selection is explainable and permission-safe.
12. A different App principal is not used unless its registered role and repository permissions authorize the operation.
13. Reconciliation retains unmatched reservations and uncorrelated provider deltas as explicit unknowns.
14. Duplicate/out-of-order observations are idempotently ingested without erasing the original.
15. A worker failover resumes from a verified checkpoint and preserves operation identity.
16. A non-idempotent side effect is reconciled before retry.
17. An unverified or billable provider is not selected as a free fallback.
18. Priority ordering and #1884 allocation constraints are preserved.
19. Every schedule change includes trigger count and API calls per execution.
20. A forced provider outage test produces a durable receipt; an untested alternative remains unproven.

## 12. Known gaps and explicit non-claims

- The existing cadence ledger states that PAT-helper tick emission has landed; App-token consumers and workflow installation-token tick adoption remain in progress.
- The continuity SPOF census found no completed failover drill for the domains it examined. Redundancy must remain labelled unproven until tested.
- The mesh provider evidence matrix is a seed list, not a verified ranking of current free capacity.
- The quota planner's unknown readings must remain unknown; no numerical entitlement or balance is inferred.
- This document does not implement the admission library, unify every API chokepoint, or prove provider failover. Those are subsequent code phases with acceptance evidence above.
