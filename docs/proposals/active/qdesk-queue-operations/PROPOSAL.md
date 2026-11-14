---
title: "QDesk — Queue Operations Desk"
status: proposal
version: 0.1.0
created: 2026-11-14
owner: QDesk / QUE
authority: "QUE owns queue policy and execution; QDesk is a read/decision projection"
---

# QDesk — Queue Operations Desk
## High-detail proposal and implementation contract

> **Core decision:** evolve the existing Tribute Contribution Desk into QDesk without creating a second queue, scheduler, worker registry, quota ledger, project database, or execution authority. QDesk is the operator's evidence-backed control surface. QUE remains the queue authority.

## 1. Executive intent

QDesk makes the work system legible end-to-end:

- What work exists, why it is ranked where it is, what it is waiting on, and what happens next.
- Which workers are merely declared, assigned, claimed, executing, or independently verified.
- Which routing decision was made, by which policy version, using which evidence and eligibility checks.
- Which escalation clock is running, who owns the next decision, and what action is permitted.
- Which failures have entered SIE, what diagnosis is supported, and whether a repair passed independent verification.
- Which capacity, throttle, quota, and WagerTome allocations constrain the plan.
- How a plan maps to GitHub Issues, Pull Requests, Actions runs/jobs, and GitHub Projects.
- How plan changes move between adaptive/agentic planning and a controlled waterfall baseline.

The dashboard must optimize for **completion accuracy**, not animated activity. A pulse is not progress; a claim is not execution; a green workflow is not task completion; a merged PR is not necessarily deployment or verified outcome.

## 2. Authority map and reuse-first constraints

| Concern | Authority / existing system | QDesk responsibility |
|---|---|---|
| Queue admission, tier, ranking, claims, leases | QUE and its existing registries/feeds/executor | Display exact state and source; request/record authorized override |
| Priority algorithm and claim order | Existing QUE task-plane prioritization work, including issue #5283 | Consume versioned score/rank and rationale; do not fork the ranker |
| Queue health, cadence, throttle, quota | Existing cadence/quota registries and throttle surfaces | Display gauges, freshness, budget basis, and HOLD reason |
| Execution | Existing dispatch executor, GitHub Actions, configured workers | Show observed execution receipts; do not synthesize workers |
| Failure lifecycle | SIE and existing self-repair machinery | Present investigation status and evidence links |
| Experiment design and independent evaluation | DoE | Display design, allocation, verification, and outcome receipts |
| RFP / adjudication | Delphi | Link RFP and award/decision; do not impersonate adjudicator |
| Cross-project work planning | GitHub Projects v2 and existing project integrations | Read/project mapping and reconcile state; do not create a parallel project store |
| WagerTome / wagering allocation | Existing wagering book/feed and its owning ledger | Display source-backed allocation and constraints; no allocation mutation |
| Browser execution | Separate Browser Quarantine project | Optional isolated adapter; QDesk ingress validates requests, never receives browser credentials |
| Visualization | Tribute dashboard | Render projections; keep canonical URLs and existing nav compatibility |

**Known overlap to reconcile rather than duplicate:** QUE task-plane score/rank/claim-order work (#5283); QDesk observatory/DoE pipeline RFP (#5146 / PR #5145); QDesk portfolio/report work (#5271); QUE throttle/token fan-out work (#5219); GCP throttle/escalation proposal (#5232); QDesk self-repair / SIE work (#5210, #5214, #5212); and the existing adaptive dispatch contract. The implementation issue must record the exact current state of each before changing its scope.

## 3. Completion accuracy: evidence semantics

### 3.1 Canonical lifecycle

Use a single explicit state vocabulary, mapped from source-native statuses rather than overwriting them:

1. **Proposed** — hypothesis or request; not admitted.
2. **Submitted** — schema and ingress checks received.
3. **Quarantined** — validation or policy review required; not eligible for dispatch.
4. **Rejected** — invalid, unsafe, duplicate, unauthorized, or out of scope; reason retained.
5. **Admitted** — QUE accepted it under an identified policy version.
6. **Queued** — eligible or waiting for dispatch; no worker implied.
7. **Claimed** — a lease/claim exists; execution not implied.
8. **Executing** — an execution adapter has a live run/session receipt and recent heartbeat/progress evidence.
9. **Blocked / Waiting** — explicit reason code, owner, since timestamp, and next wake/escalation.
10. **Reviewing** — output exists and awaits required verification/review.
11. **Verified** — acceptance checks passed with evidence bound to exact task/commit/run.
12. **Completed** — terminal business/task outcome recorded by the owning authority.
13. **Failed / Cancelled / Superseded** — terminal states with reason and lineage.

A source may use different labels. The projection stores source state plus normalized state and mapping version.

### 3.2 Evidence levels

| Level | Meaning | Permitted UI claim |
|---|---|---|
| E0 | Mock, demo, fixture, simulated pulse | "Simulation" only |
| E1 | Declared worker/capability/assignment | "Available by declaration" |
| E2 | Queue claim or lease | "Claimed; execution unverified" |
| E3 | Live run/session/job + heartbeat/log evidence | "Observed executing" |
| E4 | Output artifact/commit/PR linked to task | "Output produced" |
| E5 | Independent checks/reviewer/DoE receipt passes | "Verified" |
| E6 | Owning authority records terminal outcome | "Completed" |

No E0–E5 event may be silently promoted to E6. Every displayed badge must expose evidence level, source URI, observed_at, source_updated_at, and freshness. Simulated pulses remain in a visibly isolated demo mode and must never increment production completion, worker-active, throughput, or success gauges.

### 3.3 Completion formula

A task is completed only when its declared acceptance contract is satisfied and the owning authority emits a terminal completion receipt. The dashboard may show a provisional derived status, but it must be labelled **derived** and include the exact missing evidence. For PR-backed work, distinguish PR opened, checks passed on exact head SHA, review approved, merged, deployed (if relevant), and post-deploy verified.

## 4. QDesk information architecture

Keep the canonical existing route `/tribute/desk.html`. Upgrade its title and nav label to **QDesk — Queue Operations Desk**; preserve existing Contribution Desk traversals as a first-class section and maintain existing deep links.

### 4.1 Overview cockpit

- Work totals by normalized and source-native state, tier, lane, project, and risk.
- Queue age, claim age, execution duration, waiting age, and time-since-progress as separate measures.
- Feed/collector freshness, source coverage, last successful collection, and stale/missing-source alerts.
- Worker capacity and live execution counts with evidence level.
- QUE governor, per-tier admission/defer gauges, provider/API quotas, concurrency, cooldown, circuit-breaker and kill-switch state.
- Escalation queue, due/overdue clocks, human decision queue.
- WagerTome allocation totals and remaining/committed/reserved amounts, only where source semantics and freshness support the comparison.
- GitHub Projects roll-up: project/item status, issue/PR links, milestone, iteration, blocked state, and drift.
- SIE failure intake and repair outcomes; verified recovery and regression recurrence.

Every gauge includes numerator/denominator, units, time window, source, timestamp, freshness, and policy version. Unknown denominators or stale sources render **Unknown / stale**, never 0 or green.

### 4.2 Priority worklist

Required columns:

- Rank and score, with ranker method/version and computed_at.
- Priority class/tier and exact source policy.
- Human-readable rationale with factor contributions and source references.
- Due/landing wall, deadline proximity, age contribution, dependency criticality, blast radius, security/correctness impact, blocked status, and fairness/aging contribution where available.
- State, owner/claimant, worker execution evidence, lease, last progress, wait reason, and next action.
- Escalation stage, time-to-trigger, escalation owner, and decision link.
- GitHub issue/PR/project item and related run/job links.

**Override UX:** authorized operator can propose a bounded override (rank pin, tier exception, hold, release, defer, reassign, or rationale annotation only where policy allows). Preview old/new order and downstream effect; require reason code, free-text rationale, actor, timestamp, scope/expiry, policy guard evaluation, and confirmation. Record an immutable decision receipt. Override must not mutate QUE admission thresholds, bypass hard safety gates, invent quota, or execute privileged work. The UI submits a signed/permission-checked intent to the owning QUE decision endpoint/workflow; it never writes directly to feed JSON. If no safe action endpoint exists, provide a copyable issue/comment packet and label the control **proposal only**.

### 4.3 Worker registry and live roster

Display distinct entities:

- Declared worker/capability.
- Provider/model/arm and endpoint.
- Execution adapter (Actions workflow, local runner, Termux MCP, browser quarantine, etc.).
- Claim owner and lease.
- Observed worker/run/session.

States: `observed-executing`, `claimed-unverified`, `declared-only`, `recently-observed`, `cooldown`, `quota-held`, `unavailable`, `unknown`. Never infer active worker from a `claim.by` string. Show last heartbeat, active task, concurrency, last success/failure, capability match, health and quota evidence. Provider identity must not be conflated with role, agent identity, GitHub actor, or task owner.

### 4.4 Routing and waiting

Render the full decision chain and each evaluated gate:

`Ingress → validation/quarantine → QUE admission → priority/tier → dependency DAG → capability match → health/quota/cooldown → route selection → claim/lease → execution → evidence collection → verification → terminal outcome`.

Each branch records decision id, policy version, inputs, result, reason code, source timestamp, and next wake. Waiting reasons must be typed, not inferred from silence:

- `dependency-blocked`
- `no-eligible-worker`
- `quota-held`
- `rate-limited`
- `cooldown`
- `runner-capacity`
- `auth-or-permission`
- `external-dependency`
- `review-pending`
- `human-decision`
- `manual-hold`
- `provider-outage`
- `source-stale`
- `unknown-not-recorded`

Show `waiting_since`, `next_wake_at`, `flag_after`, `escalate_after`, `escalation_owner`, `lease_expires_at`, `last_heartbeat_at`, `last_progress_at`. Keep queue age, claim age, execution time, wait age, and idle-since-progress independent.

### 4.5 Escalation ladder

Use source-configured thresholds; do not hard-code new global clocks. Proposed ladder:

- L0 observe: normal wait; no action.
- L1 nudge: threshold crossed; notify current owner/worker; retain lease.
- L2 reroute review: eligibility/health reevaluation; suggest alternative route; no duplicate claim.
- L3 operator decision: quota, dependency, capability, deadline, or policy exception requires authorized decision.
- L4 critical escalation: deadline/breach/security/correctness blast radius; notify accountable owner and freeze unsafe automation.
- Recovery: condition cleared; resume through QUE's normal re-evaluation; record recovery and elapsed time.

Escalation must be idempotent, deduplicated by task + threshold + policy version + event window, and must not create repeated notifications or duplicate claims.

### 4.6 Throttle and allocation gauges

Reuse existing throttle dashboard gauges and quota registries. Surface:

- Requests/runs/tokens/API calls by actor, role, provider, endpoint, repository and time window where source supports.
- Concurrency, queue depth, run churn, backoff, rate-limit responses, retry amplification, cache/coalescing effect.
- Primary spendable quota vs reserved escalation slice; authoritative reset time/timezone; observed balance timestamp; stale/unknown status.
- Per-role context/model escalation ladder and kill switch.
- WagerTome allocation by pool/strategy/experiment/task, amount or units, reserved/committed/consumed/returned, exposure/risk cap, expected vs realized, source ledger and approval.
- Cost per verified completion and cost per recovered failure, not just raw tokens or run count.

Unknown or stale quota means HOLD for provider-dependent execution. No estimated free-tier entitlement, automatic paid fallback, or allocation mutation.

### 4.7 WagerTome integration

Treat WagerTome as an allocation/provenance view, not an independent wallet. Reconcile the canonical wagering-book feed and its owning ledger before rendering balances. Distinguish forecast, proposed allocation, approved allocation, reserved, committed, consumed, released, and realized outcome. Preserve allocation id, strategy, task/experiment link, source ledger version, currency/units, timestamp, approver and risk limit. Never place a wager or transfer funds from QDesk.

### 4.8 AgenticGantt: adaptive plan ↔ waterfall baseline

Provide two synchronized views of one dependency graph:

- **Adaptive/agentic plan:** task DAG, parallel-safe work, critical path, blockers, replanning events, confidence, dynamic estimates, and accepted plan revisions.
- **Waterfall baseline:** approved phases, milestone dates, predecessor constraints, scope baseline, change-control and variance.

Each task carries stable id, parent, dependencies, phase, estimate range, start/finish window, owner, status, confidence, critical-path flag, baseline version, plan revision, and evidence refs. Accepted replans are append-only revisions; preserve the original baseline and history. Do not rewrite completed/started tasks or erase the reason for a change. Show planned vs actual and forecast vs baseline separately. GitHub Projects iteration/milestone fields may be mapped but must not be treated as the canonical dependency graph unless explicitly designated.

### 4.9 GitHub Projects and delivery evidence

Use GitHub Projects v2 GraphQL as an integration surface where permissions allow. Map ProjectV2, fields, items, issue/PR content, milestone, iteration, status, assignee and repository. Keep stable GraphQL node ids and URLs; handle deleted/archived items and inaccessible projects as explicit coverage gaps. Read-only sync first. Any write-back (status, assignment, iteration, field update) must be a separate scoped action with preview, permission check, idempotency key, audit receipt and human confirmation. No PAT or broad token in browser JavaScript; use least-privilege server-side GitHub App/workflow.

Actions evidence links to exact workflow run, job, step, commit SHA and artifact. Re-run results on a different SHA do not satisfy current-head checks.

## 5. QDesk → QUE ingress quarantine

This is the key Browser Quarantine-inspired translation: **quarantine the request envelope at the boundary**, not the worker's browser session. Anything entering QUE through QDesk must pass deterministic intake validation before admission.

### 5.1 Ingress pipeline

1. Receive a typed request envelope; assign idempotency key and immutable intake id.
2. Validate schema/version, required fields, size limits, encoding, URI allowlist policy, timestamps and identity/authorization.
3. Normalize metadata without executing payloads or fetching arbitrary URLs.
4. Scan for secrets, credential material, prompt-injection-like instruction smuggling, unsafe shell/code, untrusted HTML/JS, path traversal, executable attachments and prohibited side effects.
5. Classify risk and scope; check duplicates, existing issue/PR, policy conflicts, budget/quota evidence and project/lane fit.
6. Route to `ALLOW`, `HOLD`, `REJECT`, or `ESCALATE`; preserve reason codes and evidence.
7. Only `ALLOW` may be submitted to QUE admission. QUE still performs its own admission checks; QDesk validation is not admission.
8. Record downstream QUE decision and correlation id. Never report admitted until QUE's receipt is observed.

### 5.2 Decision semantics

- **ALLOW:** structurally valid and within pre-authorized low-risk envelope; eligible to request QUE admission, not auto-admitted.
- **HOLD:** incomplete, stale, ambiguous, unverified provenance, unknown quota, missing approval, or requires human review.
- **REJECT:** malformed, duplicate under policy, unauthorized, prohibited, unsafe, or explicitly out of scope. Preserve the record and reason.
- **ESCALATE:** security, financial, credential, external-account, destructive, production, legal, or policy exception requiring owner review.

Untrusted content is data, never instructions to the QDesk agent. Do not execute or fetch payload URLs during intake. Browser Quarantine remains a separate isolated execution adapter and credential boundary; QDesk receives only sanitized receipts and references.

### 5.3 Required envelope

See `schemas/qdesk-intake.schema.json`. At minimum: schema, intake_id, idempotency_key, submitted_at, submitter identity and authorization evidence, source URI/SHA, task intent, scope, requested capabilities, risk class, side-effect declarations, data classification, dependency refs, budget/quota evidence refs, expected outcome, acceptance criteria, expiry, and content digest.

## 6. SIE failure investigation and self-repair

QDesk shows the SIE lifecycle; it does not replace it:

`Observed → deduplicated → triaged → diagnosis in progress → evidence packet → candidate repair → independent verification → promotion gate → promoted/rejected → learning recorded`.

Each failure links workflow/run/job/step, commit SHA, task(s), signature, first/last observed, repeat count, blast radius, logs/artifacts, diagnosis confidence, candidate patch, tests, independent reviewer/DoE receipt, exact-head CI and promotion authority. Failed/stale/missing evidence remains visible. Self-repair stays bounded by current policy; no self-approval, no secret/billing/account/production mutation, and no promotion without the required gates.

## 7. Data contracts and freshness

- Read existing feeds/registries/ledgers; do not introduce another canonical store.
- Each source adapter declares schema version, source URI, source SHA/revision, generated_at, observed_at, collection window, coverage, freshness SLA, last success, and parse/validation result.
- Normalize in the browser/read model only when deterministic and lossless; preserve original fields and source-native status.
- Use null for unknown. Zero means measured zero. Never backfill unknown with guessed defaults.
- Every cross-source join carries its join key and match quality: exact, derived, candidate, unmatched.
- Discrepancies (e.g. summary claim count vs claim rows) become explicit integrity alerts; never silently reconcile by dropping rows.
- Feed freshness is per source; a fresh queue feed does not make a stale dispatch feed fresh.

## 8. Security, privacy and governance

- QDesk frontend is read-only by default and contains no tokens, secrets, browser credentials, or broad GitHub permissions.
- All writes go through owning service/workflow and enforce least privilege, authorization, idempotency, audit trail, CSRF/origin controls where relevant, and explicit confirmation.
- Quarantine all untrusted inbound text/files/URLs. No arbitrary URL fetch, shell execution, workflow dispatch, repo write, browser action, credential use, money movement, or production mutation from a rendered card.
- Human approval required for security-sensitive, destructive, financial, account, external service, credential, billing, production, and policy-exception actions.
- Preserve immutable audit receipts for overrides, routing decisions, escalations, project write-backs and allocations.
- Accessibility: keyboard-first, semantic tables, reduced motion, clear status text, no color-only semantics.

## 9. Implementation phases and gates

| Phase | Deliverable | Gate / acceptance |
|---|---|---|
| P0 Contract census | Source/authority map, current PR/issue overlap, feed/schema/freshness inventory | No duplicated owner, ranker, scheduler, ledger or intake |
| P1 Evidence model | Lifecycle/evidence vocabulary, normalized read-model schema, fixtures | E0 simulation cannot increment E3–E6 metrics |
| P2 QDesk read-only cockpit | Overview, priority list, workers, routing, wait/escalation, throttle, WagerTome, SIE, project roll-up | All values sourced, freshness shown, unknowns preserved |
| P3 Ingress gate | Schema validation, deterministic policy checks, quarantine decision receipt | Fuzz/negative tests; HOLD/REJECT/ESCALATE never dispatch |
| P4 Decision controls | Override preview + signed QUE intent + audit receipt | RBAC, expiry, idempotency, hard-gate preservation, rollback/expiry |
| P5 AgenticGantt | DAG + waterfall baseline + append-only revisions | Cycle detection, stable IDs, dependency and baseline tests |
| P6 Integrations | GitHub Projects v2, Actions evidence, Browser Quarantine receipts | Read-only first; least privilege; no credential leakage |
| P7 Operational hardening | SIE/DoE verification, stale-source alarms, accessibility, load tests | Independent review, exact-head CI, documented rollback |

Each phase lands in small commits and a focused PR. No merge or production promotion is implied by this proposal.

## 10. Acceptance criteria

1. Every queue row has source-native state, normalized state, rank/score or explicit not-established, ranker version, rationale, source link, freshness and next action.
2. Priority ordering can be explained factor-by-factor and compared against the prior method; operator overrides are authorized, bounded, auditable and expiring.
3. Queue, claim, execution, wait, progress and completion clocks are distinct.
4. Workers are counted active only with live execution evidence and heartbeat within source SLA.
5. E0 simulated pulses are visibly marked and excluded from production metrics.
6. Summary counts reconcile to item rows or display a discrepancy.
7. Routing graph shows every evaluated gate and a typed reason for each defer/hold/re-route.
8. Escalations are threshold-driven, idempotent, deduplicated and never create duplicate claims.
9. Throttle gauges include numerator/denominator, time window, units, quota source, reset timezone and freshness.
10. WagerTome allocations reconcile to their authoritative ledger; QDesk cannot move funds or create wagers.
11. AgenticGantt preserves both baseline and accepted revisions; dependencies are cycle-checked.
12. GitHub Projects links resolve to stable ProjectV2/item/issue/PR identifiers; read-only sync is demonstrably non-mutating.
13. QDesk→QUE intake validates and quarantines unsafe/incomplete/ambiguous submissions; QUE admission remains a separate authority.
14. SIE repair states are evidenced; no candidate patch is marked promoted before independent gates pass.
15. Stale, missing, contradictory and not-established data are first-class visible states.
16. No tokens, credentials, arbitrary browser actions, or unapproved external side effects are available to QDesk frontend.

## 11. Out of scope / explicit non-goals

- Replacing QUE admission, ranking, claims, leases, executor, or throttle policy.
- Building a second queue, scheduler, worker registry, quota ledger, project store, wagering wallet, or failure engine.
- Treating animation, simulation, comments, labels, or declared capabilities as execution evidence.
- Direct browser automation or credential custody inside QDesk.
- Automatic paid fallback, spending, wagering, production deployment, merge, or destructive action.
- Conflating GitHub Projects status with QUE queue state or task completion.
- Replacing Delphi adjudication or DoE independent verification.

## 12. Current-source reconciliation required before code changes

At proposal time, repository search identified active overlapping work:
- #5283 — QUE task-plane priority score/rank/claim order; use its ranker and decision stamp.
- #5146 / PR #5145 — QDesk Observatory + Delphi/DoE pipeline RFP.
- #5271 — QDesk portfolio report current-master reconciliation.
- #5219 — QUE rate-limit governance, token migration and fan-out coalescing.
- #5232 — throttle and escalation ladder proposal.
- #5210 / #5212 / #5214 — QDesk self-repair and failure evidence.
- #5176 / #5246 — admitted-to-dispatch executor lineage (re-fetch current state).
- #4979 — admission collector/feed picture and freshness.
- `docs/ops/ADAPTIVE-DISPATCH.md` — Desk remains visual decision surface; direct action requires separate guarded interface.
- `docs/ops/GITHUB-OBSERVABILITY.md` — Projects v2 extraction and Actions observability constraints.
- `docs/proposals/active/gantt-dependency-phases/` — existing dependency-phase/Gantt proposal.

The first implementation pass must reconcile these against current master and avoid overlapping ownership. This document is a new integration contract, not a claim that those upstream capabilities are complete.

## 13. Decision requested

Approve the QDesk integration direction and phase sequence; retain QUE as queue authority, keep QDesk read-only until guarded decision endpoints are proven, and require the QDesk→QUE quarantine contract before enabling any intake write path.
