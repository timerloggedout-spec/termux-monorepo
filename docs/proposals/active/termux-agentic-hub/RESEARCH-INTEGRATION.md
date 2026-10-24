# THUB-017 Research integration proposal

**Status:** proposal / design review required
**Owning item:** THUB-017 in [ITEMS.md](ITEMS.md), already recorded on PR #1470's proposal surface. This document decomposes that existing item; it does not create a new identity.
**Evidence baseline:** PR #1470 is open, unmerged, and undeployed at `d2778bcc25966533ccd2f5bc1991aab672fb9cbe`.
**Scope:** documentation proposal only. No implementation, live provider calls, chain activity, spend, merge, or deployment is authorized here.

## Purpose and boundary

Define the smallest testable path to integrate the pinned AdvancedResearch source as an optional research capability through the existing model hub. The design must establish a real adapter contract, enforce shared quota/cooldown admission and accounting at the actual hub boundary, and emit correlated telemetry usable by `TermuxTelemetryLogger` and 3L0. It must not imply those connections already exist.

The AdvancedResearch source is pinned at `a262cb9d9703681c5a5066f03eb9fb89ad4d9cae` but is **not integrated or run**. See [the source registration at the PR revision](https://github.com/timerloggedout-spec/termux-monorepo/blob/d2778bcc25966533ccd2f5bc1991aab672fb9cbe/integrations/swarms/research-lanes.json). `research-plan.py` is an **offline plan generator only**; a generated plan is not research execution, evidence ingestion, or a provider call. The opt-in Python/Rust Swarms work uses the existing model hub; Research must join that same boundary rather than introduce another model client or quota ledger. The current master source tree is the implementation baseline; PR #1470 is review evidence only, not deployed behavior.

Termux already controls remote Actions and WorkSpaces through documented mechanisms. This proposal adds no runtime service, daemon, scheduler, or new remote control plane. Any future execution remains explicit, bounded, and subject to existing hub/model-selection policy. Paper/CSV wallet outputs remain projections within MSM-005, not a chain adapter.

## Current-state matrix

| Concern | Verified current state | Proposed target; not yet present |
|---|---|---|
| AdvancedResearch | Source is pinned; no integrated or executed runtime is evidenced. | A bounded adapter calls the pinned runtime behind the existing hub, with explicit inputs, outputs, cancellation, and errors. |
| `research-plan.py` | Offline plan generation; no claim of execution. | Keep planning distinct from execution; test generated plans offline before enabling runtime invocation. |
| Python/Rust Swarms | Opt-in adapters use the existing model hub. | Reuse that hub boundary and its model-selection path; do not add a parallel provider path. |
| Quota/reset/cooldown | Shared Research admission/consumption behavior at the actual hub boundary is not evidenced as complete. | Atomic reservation, reconciliation, and shared reset/cooldown policy at the boundary where requests are admitted and dispatched. |
| `TermuxTelemetryLogger` / 3L0 | Correlated Research-to-hub telemetry is not evidenced as complete. | Emit attributable lifecycle records that distinguish outcomes and expose missingness without leaking prompts, secrets, or provider payloads. |
| Remote operation | Termux control of remote Actions/WorkSpaces is already documented. | Continue using those surfaces; no new runtime service or scheduler. |

## Proposed contract

### Bounded AdvancedResearch adapter (THUB-017.A)

1. Adapter input is a validated, versioned research request: stable request/idempotency key, bounded task/question and allowed source/search policy, selected existing hub model reference, explicit resource/time limits, and cancellation signal. Reject unknown fields, unbounded work, unsupported model references, and execution requests lacking explicit opt-in.
2. Adapter delegates inference through the existing model hub only. Search/retrieval is injected as an explicit capability/port so fixture tests can supply deterministic fake search; it must not silently instantiate a provider SDK or create a second credential/configuration path.
3. Output is a versioned structured result containing request/run correlation IDs, status (`succeeded`, `failed`, `cancelled`, or `unknown`), bounded findings/citations as available, source/runtime pin identity, and redacted diagnostics. Errors are typed (validation, admission denied, transient hub/search failure, timeout, cancellation, and indeterminate completion); no exception may be represented as success.
4. Define timeout, cancellation propagation, retry eligibility, idempotency, and maximum retry/attempt bounds. Never retry an indeterminate side effect as if it were known not to have occurred. A retry must retain the logical request ID and create a distinct attempt ID.
5. Preserve an offline-only planning mode. Planning may produce a plan record but cannot reserve quota, call search/inference, or claim a completed research run.

### Shared quota, reset, cooldown and atomic accounting (THUB-017.B)

Implement admission and consumption at the **existing hub boundary** used by model invocations, not in an adapter-local counter. First map the concrete hub entry point and current quota semantics from master before coding. Define a shared quota key (at minimum the existing provider/model/account scope; include workload class only if the current policy defines it), a single source of truth for reset windows, and consistent handling for cooldown and unknown provider state.

For each hub attempt: atomically reserve the applicable quota before dispatch; deny without dispatch when exhausted or cooling down; reconcile the reservation exactly once against the definitive response/known usage; and preserve an explicit `unknown` reservation state when dispatch may have occurred but consumption cannot be established. Release only when evidence proves no dispatch/consumption. Reservation operations must be concurrency-safe and idempotent under duplicate request/retry handling. Reset transitions must not erase in-flight reservations or permit oversubscription. Cooldown responses record retry-after/reset evidence when available; absent or stale reset evidence fails closed for calls requiring that quota. Adapter, Swarms, and other existing hub consumers must observe the same admission state and accounting policy.

No new paid fallback, alternate provider, or unapproved routing is introduced. Quota denial, stale state, and unknown usage are first-class outcomes, not reasons to bypass policy.

### Correlated telemetry (THUB-017.C)

Use `TermuxTelemetryLogger` as the local lifecycle emission boundary, and define a stable mapping/export contract for 3L0 consumption; do not assume direct 3L0 ingestion is already wired. Each record correlates `logical_request_id`, `attempt_id`, hub invocation/reservation ID, adapter/runtime pin, model/provider identity at the approved redacted granularity, and parent trace/correlation ID. Record lifecycle events for request accepted/rejected, quota reservation/denial, dispatch, reconciliation, reset/cooldown, completion/failure/cancellation, timeout/unknown, and retry.

Include timestamps, outcome/error class, duration only as observed, quota state and reset/cooldown evidence, retry count, and provenance hashes. Preserve causal order or explicit event sequence. Never record credentials, raw auth headers, private keys, unbounded prompts, raw sensitive search results, or provider secrets. Redaction and bounded-size behavior must be tested. 3L0 receives evidence records, not reputation claims: missing, failed, cancelled, denied, unknown, and successful runs remain distinguishable and attributable.

## Work decomposition within THUB-017

These are implementation subtask keys under the already-owned THUB-017; the parent may map them to GitHub subissues. They are not new proposal or ledger identities.

| Key | Bounded work | Exit evidence |
|---|---|---|
| THUB-017.A | Specify and implement the adapter contract against the pinned AdvancedResearch runtime; preserve plan-only mode and route model inference through the existing hub. | Contract tests and pinned-source/runtime evidence; no hidden provider path. |
| THUB-017.B | Map the existing hub admission point and implement shared atomic quota reservation/reconciliation, reset, cooldown, stale/unknown state, idempotency, and concurrency behavior. | Hub-boundary tests prove common policy for Research and existing consumers. |
| THUB-017.C | Emit correlated, redacted `TermuxTelemetryLogger` records and define/validate the 3L0 evidence mapping. | Trace fixtures join adapter, hub, quota and terminal outcomes with no sensitive payload leakage. |
| THUB-017.D | Validate the whole path, provenance, failure behavior, and operational boundary. | Offline first, then genuine pinned Research runtime using fake search/inference; attributable test and source evidence. |

## Phases and acceptance tests

### Phase 0 — baseline and contract

Inspect current master and the pinned source; record exact paths, immutable source revision/hash, hub entry point, existing model-selection behavior, quota owner, and telemetry API in the implementation PR. Reconcile the open PR #1470 SHA/state before using it as evidence. Do not infer completion from PR presence. Agree the adapter schema, error semantics, retry/idempotency rules, quota key/window semantics, telemetry fields, and redaction policy before runtime integration.

**Accept when:** plan generation remains explicitly offline; no runtime or provider call is needed to validate fixtures; source and baseline identities are reproducibly recorded.

### Phase 1 — deterministic offline fixtures

Add tests for plan-only behavior, schema validation, bounded input/output, fake search/inference ports, adapter state transitions, event serialization/redaction, and provenance. Fixtures must prove that planning does not consume quota or call any external boundary.

**Accept when:** all tests are deterministic and network-independent; fixture outputs distinguish plan from executed result and success from failure/cancellation/unknown.

### Phase 2 — actual pinned Research runtime with fake boundaries

Exercise the genuine pinned AdvancedResearch runtime, not a reimplementation or mock adapter, while injecting fake search and fake inference through its supported seams. Exercise model inference through the existing hub boundary. No live provider credentials, network provider calls, blockchain, or spend.

**Accept when:** runtime identity/hash is verified; observed request/response contract matches Phase 0; all results and failures correlate to hub and telemetry records; unsupported injection seams are reported as a blocker rather than replaced with an unbounded alternate path.

### Phase 3 — hub quota correctness

At the existing hub boundary test: quota-denied request; reset boundary and reset propagation; active cooldown and expiry; stale reset metadata; unknown result/usage after possible dispatch; concurrent reservations at the remaining-quota boundary; duplicate/idempotent reservation and reconciliation; transient retry; cancellation before dispatch and after possible dispatch; repeated completion/reconciliation; and ensuring reset does not erase in-flight reservations. Verify Research and existing hub consumers share the same accounting/admission decision.

**Accept when:** no parallel quota counter exists; concurrency cannot exceed configured quota; no known-no-dispatch path is charged; uncertain dispatch remains explicitly unknown and cannot be silently retried or released; all decisions are deterministic under controlled clock/fake hub responses.

### Phase 4 — correlated end-to-end evidence

Run success, failure, cancellation, denial, timeout/unknown, cooldown, and retry cases through the adapter, hub and telemetry logger. Verify the 3L0 projection retains lineage and outcome distinctions and that no prompt/credential/provider-sensitive payload is emitted. Record source hashes and immutable remote SHA evidence for code and pinned dependency; capture test commands/results and exact reviewed commit.

**Accept when:** every test run has traceable source/runtime and remote SHA evidence, complete or explicitly missing lifecycle links, and redaction checks. Do not claim production performance or make latency/throughput claims absent measured evidence.

## Dependencies and design review questions

- Identify the precise existing model-hub dispatch/admission boundary on current master and how all Python/Rust Swarms invocations reach it.
- Confirm supported AdvancedResearch runtime invocation and fake search/inference injection points at its pinned revision; document if source API differs from this proposed shape.
- Determine the authoritative existing quota state, reset semantics, concurrency mechanism, and source of cooldown/reset evidence; do not create a second ledger.
- Confirm `TermuxTelemetryLogger` event API, persistence/retention behavior, and the expected 3L0 ingestion schema/consumer. Define a mapping if direct ingestion is not currently present.
- Confirm permitted model/provider metadata granularity and redaction rules for telemetry.
- Resolve cancellation guarantees and provider-usage ambiguity at the hub boundary before declaring reconciliation complete.

These are explicit review dependencies, not assumed facts or authority to broaden runtime capabilities.

## Rollout, rollback, and authority

Roll out in bounded stages: offline contract and fixtures first; pinned runtime with fake boundaries next; then shared hub accounting and telemetry only after tests pass. Keep Research opt-in and disabled by default until the reviewed integration is merged and its evidence is complete. Do not change existing hub consumers' policy without compatibility tests. If any phase fails, revert/disable the Research adapter while preserving existing hub paths and their quota state; do not discard ambiguous reservations or erase telemetry needed to explain them. Rollback must not create alternate routing, paid fallback, or a new background service.

This proposal records an authorized design direction only. **Runtime design review remains required.** It grants no live provider, chain, spend, deployment, merge, or paid-fallback authorization. No arbitrary dates, service-level targets, or performance commitments are set. Completion/deployment claims require implementation, review, tests, and attributable evidence for all three integration boundaries.

## Published tracking

Owning issue: [research / #1520](https://github.com/timerloggedout-spec/termux-monorepo/issues/1520). Native subissues: [THUB-017.A / #1522](https://github.com/timerloggedout-spec/termux-monorepo/issues/1522), [THUB-017.B / #1523](https://github.com/timerloggedout-spec/termux-monorepo/issues/1523), [THUB-017.C / #1524](https://github.com/timerloggedout-spec/termux-monorepo/issues/1524), [THUB-017.D / #1525](https://github.com/timerloggedout-spec/termux-monorepo/issues/1525).

[Milestones, Project and dependency map](RESEARCH-WALLET-TRACKING.md).
