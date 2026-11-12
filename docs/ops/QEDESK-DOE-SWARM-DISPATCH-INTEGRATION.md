# QUEdesk × DoE × Swarm — integration boundary and workstream crosswalk

**Status:** cross-workstream reconciliation; supplemental to the canonical architecture contracts  
**Reconciled:** 2026-11-12  
**Related PR:** #5085 (autonomous escalation / optional LangGraph treatment)

## Purpose and authority

This document connects the autonomous escalation work in PR #5085 to the repository's newer QUEdesk, DoE, Scout, Swarm and multi-arm build work. It is **not** a replacement router, scheduler, queue, provider registry, quota ledger, experiment ledger or execution authority.

Canonical architecture sources:
- `docs/architecture/CONTRACT-TO-RUNTIME-TRACEABILITY.md` and `docs/architecture/DOE-GOVERNED-INFERENCE-ALLOCATION.md` (PR #5224).
- `docs/architecture/ROUTING-CONTROL-PLANE-RECONCILIATION.md` and its graph (PR #5222, coordinated with #5224 because both branches edit the graph path).
- `ops/quota/dispatch-tiers.json` — QUE tier/dependency policy SSOT.
- `ops/challenge/desk-feed.json` — provider catalog and machine-readable selection policy.
- `docs/ops/DOE-FAMILY.md` and the registered campaign designs.

## Determination

The architecture is layered. The repository contains distinct task-admission, build-dispatch, inference-allocation, invocation-routing, evidence and read-model planes. Similar words such as *provider*, *arm*, *router* and *dispatch* do not make these interchangeable.

### Do not conflate these two arm populations

| Population | Unit | Authority / implementation |
|---|---|---|
| **Build-dispatch arms** | Harness × endpoint for a full-checkout builder | #5151 / merged PR #5178; `ops/dispatch/build-arms.json`; `scripts/ops/build_arm_harness.py`; `.github/workflows/build-dispatch.yml` |
| **Inference endpoint arms** | Provider × surface × exact model@version × protocol/endpoint | DoE allocation + Scout selection; #5160, #5224, #5223; `inference-selection-receipt/v1` |

#5176 converts admitted task filings into build-dispatch executions. It does not implement inference endpoint allocation or the Scout-to-`llm_api_hub` invocation adapter.

## Current workstream ownership and sequence

| Workstream | Current record | Responsibility / disposition |
|---|---|---|
| QUE admission reliability | #4979 / PR #5238 (open, validation pending) | Feed-first queue picture, bounded stale-feed fallback, named failure reason, Swarm token leg. Upstream dependency for the executor. |
| Admission threshold conformance | #5239 (open) | Remove copied `FLOW_THRESHOLDS`; read tier/depth semantics from `dispatch-tiers.json` v2 at evaluation time. |
| Admitted → execution | #5176 (open; QDesk slot after #4979) | Convert `swarm-admitted ∧ dispatch-queued ∧ unclaimed` into claim + build-dispatch fire. Claim is the exactly-once mutex; watchdog owns aging/stale-claim behavior. |
| Build-arm routing | #5151 / PR #5178 (merged) | Build-arm registry, generic harness, census and dispatch-stamp fan-out. The merge opened #5176's build slot. |
| Per-arm quota evidence | #5152 (open) | Cadence-owned usage ledger and quota-terminal events; quota-aware-before-failure is standing law. |
| Inference endpoint population/cadence | #5160 (open; sequenced after #5176) | Deterministic pool generation, evidence-gated free endpoint eligibility and adaptive quota cadence. This is not the Dreambeans method pool. |
| DoE inference allocation | PR #5224 (open) | DoE owns allocation/rotation/statistical gates; defines `inference-selection-receipt/v1`; Scout selects within the assigned eligible pool. |
| Runtime selector enforcement | #5223 (open) | Trace and enforce Scout → workflow/provider invocation; scoped rotation; exact receipt-to-invocation identity; model-router composition and feed freshness. |
| Free-inference tournament | PR #5198 (open) | Declarative staged order; initial scope is offline reconciliation, deterministic simulation and preregistration. No live inference authorized by the order. |
| QDesk Observatory / Dreambeans | #5146 / PR #5145 | Separate RFP for deterministic method-version candidate generation, DoE registration and Observatory. Its method pool is not the inference endpoint roster. |
| Participant identity | #5136 (open) | Registry-issued identities, least privilege and receipted participant actions. No account/credential creation by a clone or workflow without its own gate. |
| Role clones | #5183 (open) | Role-clone census and later participant issuance; sequencing depends on #5136 and #5176. |
| Self-repair | PR #5208 (merged) | Existing bounded QUE self-repair observe/promote/learn loop. It is not a replacement for the admitted-task executor or DoE tournament. |

## Verified integration findings

### 1. Build-arm selection must not bypass census eligibility

In merged `scripts/ops/build_arm_harness.py`, automatic selection requires a census verdict of `eligible`. The explicit-arm branch checks registry `selectable` and quota-terminal state but does not require a successful census verdict. Several candidate arms are marked `selectable: true`; the workflow exposes them as explicit `workflow_dispatch` choices.

This means explicit selection can bypass the census gate. The intended correction is: explicit choice may override ordering, never eligibility. Production build selection requires a current `verdict=eligible` and valid quota evidence. Any candidate-arm diagnostic must be a separate non-production probe with no build, commit or PR side effects.

This finding was recorded on #5223 and in the #5176 execution requirements. It is a follow-up against the merged #5178 implementation, not a second selector.

### 2. Inference selection-to-invocation remains unimplemented

The current source trace, also recorded in PR #5224, establishes:
- `scripts/scout_roster.py` produces an `observe_only` roster; it does not select.
- `scripts/model_router.py` uses role-specific configured peer/residual candidates and does not consume a DoE assignment receipt.
- `.github/workflows/provider-invoke.yml` accepts a provider directly through `workflow_dispatch`.
- `scripts/ops/provider_invoke.py` resolves models at invocation time, may try another catalog model on 404, and may attempt a provider default when catalog resolution fails. It does not bind the call to an `inference-selection-receipt/v1`.
- `dispatch-stamp-fanout.yml` is downstream evidence fan-out, not selection authority.

The receipt schema and DoE/Scout authority contract exist in PR #5224, but runtime enforcement does not. A reviewed adapter must consume the receipt, validate freshness/eligibility and require exact equality between receipt endpoint identity and the actual provider, surface, model, protocol and route. Missing, stale, mismatched or ineligible receipts mean **no inference call**. No catalog substitution, implicit default or alternate model should qualify as the assigned treatment.

### 3. The relationship graph has a branch-level consolidation conflict

PR #5222 and PR #5224 both edit `docs/architecture/ROUTING-CONTROL-PLANE-GRAPH.mmd` with different content. Consolidate to one canonical graph. Carry forward #5222's verified feed timestamps, freshness caveats, watchdog/QUE separation, D1 closure and supersession chronology into the richer #5224 contract matrix/graph. Do not merge competing graph variants.

### 4. Context relationship index is not current enough for this reconciliation

The master manifest at `workspace/llm_map/context_relationships/manifest.json` reports collection at 2026-10-26, only 50 issues and 50 PRs per family, `PARTIAL_CONTINUATION_REQUIRED`, `next_start_page=2`, and 120 unresolved internal references. It predates the November workstreams listed above. Use current GitHub issue/PR/file evidence for this reconciliation; do not treat the October graph as a complete current relationship map. Refresh only through the trusted publisher or bounded historical-backfill workflow.

## Composition boundary for PR #5085

PR #5085 supplies a bounded deterministic escalation policy and an optional LangGraph treatment. The current LangGraph handoff and repair nodes are explicitly local stubs: handoff records a selected executor but does not invoke it; repair marks a local state transition but performs no real repair. No provider/tool side effects occur in this module.

Therefore:
- Keep QUE admission and #5176 as the dispatch authority.
- Keep #5178 as the build-arm selection/execution surface, subject to the census-eligibility correction.
- Keep DoE/Scout and the inference receipt as the separate inference-selection authority.
- Use escalation decisions to choose bounded repair/handoff/verification treatment within those existing lifecycles; do not create a parallel execution route.
- Preserve independent verification, authorization scope, idempotency, quota preflight, DoE treatment identity and provenance.
- Do not describe PR #5085 as production self-building until a governed adapter composes it with the existing executor and the tournament machinery.

## Recommended integration order

1. Complete and oracle-verify #4979 / PR #5238.
2. Complete #5239 so admission consumes the v2 SSOT rather than an embedded threshold mirror.
3. Execute #5176 using the merged #5178 build-arm contract, with explicit selection unable to bypass census eligibility and with claim/fire idempotency.
4. Complete #5152 quota metering and #5160 evidence-gated inference endpoint population/cadence.
5. Implement #5224/#5223 receipt-bound Scout-to-invocation enforcement without a second router.
6. Run the offline deterministic stages of #5198; enable no live tournament calls until endpoint entitlement, quota, receipt and QDesk gates are satisfied.
7. Integrate #5146's deterministic Dreambeans method pool and Observatory as a compatible, separate population.
8. Compose PR #5085 escalation decisions into the established execution lifecycle only after the relevant contracts and verifier boundaries are proven.

## Validation disposition (2026-11-12)

- PR #5178: merged; build-arm registry/harness/census/fan-out landed. Census at merge identified Gemini CLI as the only eligible build arm; other arms remain failed/candidate pending adapter work.
- PR #5238: open; 48 checks observed, only 1 success, 31 queued at the last fetched head. No promotion claim.
- PR #5224: open; the dedicated contract check failed on a case-sensitive phrase check despite the design declaring the endpoint-level unit; the mutation and ledger failures examined in logs were GitHub API installation rate-limit 403s. Runtime receipt enforcement remains outstanding.
- PR #5222: open draft; shares the graph path with #5224 and requires consolidation.
- PR #5198: open; declarative/offline plan only, not authorization for live inference.
- PR #5085 at `716a0e1e178f40dfb99b2290e677c480fa15a085`: 50 check-runs, 42 success, 8 skipped, zero failed; no LangGraph-specific check name was present in that set. No local Termux test execution is claimed.
- No live inference, provider account changes, quota mutation, production routing change, merge or deployment was performed by this reconciliation.
