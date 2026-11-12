# QUEdesk × DoE × Swarm Dispatch Integration

**Status:** architecture contract / implementation gap analysis  
**Target:** `timerloggedout-spec/termux-monorepo`  
**Related:** PR #5085; issues #5136 and #5146; `docs/ops/ISSUE-TEMPLATE-DISPATCH.md`; `docs/ops/DELPHI-ORACLE-RFP-GATE.md`; `docs/ops/DOE-FAMILY.md`; `docs/ops/DOE-DREAMBEANS-POOL.md`; `docs/ops/UNIFIED-PROVIDER-OBSERVABILITY-INDEX.md`.

## Executive contract

QUEdesk filing/dispatch is the event that starts the governed execution path. An admitted dispatch must cause the appropriate GitHub Actions workflow(s) to run; it must not stop at an intake comment, a queue label, or a dashboard projection.

The execution path must use the DoE pool generator to construct reproducible candidate assignments and the swarm tournament system to compare eligible agent/provider/model treatments. Inference is permitted only through currently verified, no-cost provider/model routes whose credentials, quota, reset window, capability, data class, and terms have passed admission. If the free entitlement or reset evidence is unknown, stale, exhausted, or card-gated, the inference leg is disabled and the dispatch is explicitly deferred or run in deterministic-only mode where the task permits it.

The system may build and improve its own code and workflow machinery, but it cannot grant itself new authority: builder output is a candidate artifact; independent tests/review/verifier and existing promotion gates remain mandatory. A tournament win is evidence for a treatment, not merge, deployment, spend, account provisioning, or permission to change policy.

## Verified current architecture

| Surface | Verified behavior | Consequence |
|---|---|---|
| `.github/ISSUE_TEMPLATE/project-task.yml` | Declares `issue-dispatch/v1`, lane `swarm-dispatch`, tier 3, payload `project-task`, route `project-task-dispatch.yml`. Form says filing is the trigger and provider selection is system-owned. | Correct intake contract; it does not name a provider. |
| `swarm-admission.yml` + `scripts/ops/swarm_admission.py` | Matches template block, evaluates tier → after → chain → flow, stamps ADMITTED/DEFERRED, applies admission label, publishes a one-run `issue-admission` artifact. Fail-soft: unknown/error defers. | Admission is a gate and receipt, not an executor. |
| `project-task-dispatch.yml` + `scripts/dispatch/project_task.py` | Validates issue body and posts `dispatch-queued` intake receipt. The parser explicitly says selection/execution happens elsewhere. | This workflow is not itself the missing downstream execution trigger. |
| `ISSUE-TEMPLATE-DISPATCH.md` | States the route named by a template executes under its own intake. It documents a workflow-run/artifact handoff for Game Development, but does not define an equivalent generic project-task worker handoff. | Generic project-task dispatch-to-execution is not established by the inspected contract. |
| `que-feed-collect.yml` + `scripts/que/que_feed_collect.py` | Scheduled/dispatchable queue census and feeds; commits queue state and transition events. | QUE feed is measurement/observability, not task execution. |
| `dispatch-watchdog.yml` | Flags unclaimed work at 30 minutes and escalates at 60 minutes. | Watchdog handles stalled claims; it is not the normal worker trigger. |
| `DOE-DREAMBEANS-POOL.md` | Versioned method/concept candidate population; title-level triage and flag-only duplicate groups. | This is a method-version pool, not a live provider/model endpoint catalog. |
| `DOE-FAMILY.md` | DoE is the experiment-design family: randomized mixes, evolutionary culling, cherry-picked propagation, with design events recorded. | Tournament assignment and selection belong to DoE; do not create a competing experiment ledger. |
| `DELPHI-ORACLE-RFP-GATE.md` | Delphi admits free-tier surfaces to shadow trials; it explicitly does not choose models for live routing. Model ballots remain disabled until no-cost entitlement and fresh quota admission are independently validated. | Delphi RFP award is not a live model-routing decision. Use the model router and DoE assignment for those separate responsibilities. |
| `UNIFIED-PROVIDER-OBSERVABILITY-INDEX.md` | Discovery, eligibility, quota, health, invocation, and admission are separate states; unknown/stale evidence and missing credentials default deny. | Reuse the existing provider and telemetry contracts; do not invent a new quota authority. |

## Required end-to-end path

```text
Issue template / QUEdesk dispatch
        |
        v
swarm-admission (tier -> after -> chain -> flow)
        |  ADMITTED receipt + issue-admission artifact
        v
route-specific QUE dispatcher  <--- missing generic project-task handoff to prove/build
        |
        +--> validate issue + exact target/scope/authority + idempotency key
        |
        v
DoE design/pool generator
        |  deterministic seed, design version, method candidates,
        |  provider/model eligibility snapshot, treatment assignment
        v
Swarm tournament scheduler
        |  bounded parallel workers / isolated workspaces
        |  no provider selection from issue text
        v
Free-provider inference adapter (only after fresh quota + credential + policy admission)
        |
        v
Builder outputs (branch/patch/artifact; no auto-merge)
        |
        v
Independent verifier + tests + provenance + cost/quota receipt
        |
        +--> DoE outcomes / cull / retain / propagate winning method
        |
        v
Existing merge/promotion/deployment gates (separate authorization)
        |
        v
QUE receipt + telemetry / ATES / 3L0 / HindSight / provenance projections
```

## Three pools — never conflate them

1. **Method pool (Dreambeans):** versioned orchestration, planning, testing, selection, and recovery methods. Candidate cards are triaged and registered as method versions; duplicates are flagged, not deleted.
2. **Provider/model pool:** provider endpoints and model IDs discovered from the reviewed provider catalog / authenticated model catalogs. Each candidate has a source, protocol, capability, credential alias/presence, terms/data class, region, observed quota and reset evidence, and freshness timestamp.
3. **Tournament treatment pool:** a DoE design that assigns eligible method × provider/model × agent-role × task/workload treatments to independent experimental units. It records the exact treatment instance and seed. It does not convert title-level fit or a catalog listing into a successful inference route.

The DoE generator should be deterministic and offline-capable. It can construct the candidate design without inference. The inference execution stage is separately admitted and uses only free, verified routes. A provider being labelled free or exposing a `:free` model name is not proof of remaining quota or no-cost entitlement.

## Dispatch contract and receipts

Every dispatch execution must carry:

- `dispatch_id`: stable idempotency key derived from repository, issue number, template identity, and admission event identity; never from mutable issue-body text alone.
- `issue_number`, `template`, `lane`, `que_tier`, `route`, `admission_run_id`, and admission decision.
- `target_repo`, exact allowed path scope, authority reference, and done-evidence contract.
- `design_id`, design version/hash, deterministic seed, method candidate IDs/versions, and tournament cell/assignment.
- Provider/model exact IDs, protocol, endpoint source reference, credential **name/alias only**, quota source/scope/observed-at/reset, eligibility verdict, and fallback/defer reason.
- Builder identity/role distinct from verifier identity/role; worker run IDs; artifact/branch/commit references.
- Test and independent-verification results, provenance digest, resource usage, inference usage, and final disposition.

The first admission stamp remains the QUE admission receipt. The execution worker appends a separate start/finish receipt keyed by the same `dispatch_id`; retries must be idempotent and preserve prior receipts. The issue body and comments are untrusted task data, never executable shell, workflow, or provider configuration.

## Trigger/handoff implementation requirements

1. Keep `swarm-admission.yml` as the single admission authority. Do not let issue events fan out directly to builders.
2. Add a route-specific `workflow_run: completed` consumer for the generic `project-task` route, modeled on the existing Game Development artifact handoff. It must download the artifact from the exact admission run, verify repository/workflow/run identity, and require `matched=true`, the expected template, and `decision=ADMITTED`.
3. Make the generic consumer invoke a QUE dispatcher entrypoint; do not duplicate tier/after/chain/flow logic in the consumer.
4. Re-read the issue by number at execution time. Revalidate open state, required fields, target repository, scope and authority. Reject stale or edited intake unless its current content hash matches the admitted snapshot or a new admission is issued.
5. The dispatcher asks the DoE generator for a deterministic plan, then asks the provider eligibility gate for eligible inference candidates. If none are eligible, record `DEFERRED_NO_FREE_ROUTE` (or deterministic-only when explicitly allowed by the task); never fall back to paid inference.
6. Run tournament workers in isolated branches/workspaces with bounded concurrency, time, tokens, and retries. A builder cannot verify or promote its own output.
7. Feed immutable treatment and outcome receipts to the existing DoE/ATES/3L0/provenance surfaces. The canonical result store remains the existing one; dashboards are projections.
8. A workflow-run trigger is only a handoff. It must not use an untrusted issue field as a workflow filename, shell fragment, provider key, endpoint URL, secret name, or permission grant.

## Self-build / self-improvement boundary

Allowed without expanding authority:
- Generate candidate patches, tests, docs, and workflow changes on isolated branches.
- Run deterministic repository checks and bounded free inference experiments after admission.
- Compare variants using predeclared DoE factors, independent experimental units, and fixed acceptance metrics.
- Cull failed method versions and propagate a selected implementation only through a recorded design event and normal PR review/promotion.

Never self-authorize:
- Merge, release, deploy, modify branch protection, create credentials/accounts, change permission scopes, bypass review, approve provider billing, or promote a model based only on its own score.
- Treat builder assertions, generated ballots, rubric output, or a single successful request as independent verification or a statistical win.
- Persist provider secret values, user data, full prompt payloads, or private issue bodies in experiment records.

## Implementation tranches

| Tranche | Deliverable | Acceptance evidence |
|---|---|---|
| QD-0 — reconcile | Map QUE, templates, route registry, DoE, provider catalog, quotas, and tournament records to canonical owners. | Verified relationship map; no duplicate system of record. |
| QD-1 — handoff | Generic project-task workflow-run consumer gated by the admission artifact. | Tests for admitted, deferred, unmatched, wrong-template, wrong-run, missing-artifact, stale-body, and duplicate delivery. |
| QD-2 — deterministic generator | Stable DoE plan from registered method and eligible provider/model candidates; deterministic replay. | Same inputs/seed produce byte-stable plan; invalid/stale candidates excluded with reason. |
| QD-3 — free inference admission | Provider adapter resolves exact endpoint/model and proves current no-cost eligibility before invoke. | No credential/quota/terms/region evidence => zero inference calls; no paid fallback. |
| QD-4 — tournament workers | Bounded isolated swarm execution and distinct independent verifier. | Replayable treatment assignments, per-worker receipts, verifier separation, failure containment. |
| QD-5 — self-build loop | Results feed method culling/propagation and candidate PR generation. | Pre-registered metrics, independent verification, PR-only promotion, provenance and rollback evidence. |
| QD-6 — observatory | QUE/DoE/ATES/3L0 projections show queued → admitted → dispatched → running → verified → promoted/deferred. | Reconciled counts against canonical receipts; missing/unknown stays unknown. |

## Immediate blockers / facts to resolve before live inference

- The inspected project-task workflow is intake-only; generic admitted-artifact-to-worker execution is not established by the current docs/workflow reviewed here.
- Issue #5146's RFP explicitly says no provider inference is needed for initial review or deterministic pool generation; provider inference is a later, separately admitted implementation-worker phase. Preserve that separation.
- Delphi's gate says it does not select live models and keeps model ballots disabled until independently validated no-cost entitlement and fresh quota admission exist.
- The current issue #5136 Participant Identity Plane specifies pre-issued participant identities, least privilege, route receipts, and no account creation/credential sharing without its own gates. The dispatch worker must consume those identities; it must not improvise identities or credentials.
- The precise provider/model pool source, live free quota authority, endpoint list, and tournament metric contract must be read from their canonical files at implementation time. This document does not claim any endpoint is currently eligible or any provider inference has succeeded.

## Related source files

- `.github/ISSUE_TEMPLATE/project-task.yml`
- `.github/workflows/swarm-admission.yml`
- `.github/workflows/project-task-dispatch.yml`
- `.github/workflows/que-feed-collect.yml`
- `.github/workflows/dispatch-watchdog.yml`
- `scripts/ops/swarm_admission.py`
- `scripts/dispatch/project_task.py`
- `scripts/que/que_feed_collect.py`
- `ops/quota/dispatch-tiers.json`
- `ops/quota/registry.json`
- `docs/ops/ISSUE-TEMPLATE-DISPATCH.md`
- `docs/ops/DOE-FAMILY.md`
- `docs/ops/DOE-DREAMBEANS-POOL.md`
- `docs/ops/DELPHI-ORACLE-RFP-GATE.md`
- `docs/ops/UNIFIED-PROVIDER-OBSERVABILITY-INDEX.md`
- Issue #5136 (Participant Identity Plane)
- Issue #5146 (QDesk Observatory / DoE pipeline RFP)
