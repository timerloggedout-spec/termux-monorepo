# Routing control-plane reconciliation

**Status:** architecture reconciliation / traceability index; not a replacement policy.
**Reconciled against:** `master` at `5b1d989fa2441d280c7db25e2adbe90645385cfe` (2026-11-12).
**Scope:** task declaration, queue admission, provider selection, inference routing, evidence fan-out, and read projections.
**Terminology:** use *contract-to-runtime traceability graph* for the relationship model and *control-plane reconciliation matrix* for this artifact.

## Executive finding

`swarm-routing/v2` is the routed-dispatch cohort/policy identity used by the November 2026 evidence campaign. The repository does not define it as a standalone JSON Schema. It must not be conflated with `issue-dispatch/v1`, `queue.dispatch-tiers/v2`, `desk-feed/v1.3`, or the evidence-plane schemas.

There are several routing-adjacent implementations, but they operate at different control-plane boundaries. The evidence supports a layered architecture, not a finding that one router was duplicated or that the September model router was superseded.

## Contract-to-runtime matrix

| Plane | Contract / source of authority | Implementation / producer | Consumer / effect | Current interpretation |
|---|---|---|---|---|
| Task declaration | `issue-dispatch/v1`; `docs/ops/ISSUE-TEMPLATE-DISPATCH.md` | `.github/ISSUE_TEMPLATE/*` plus `SWARM-DISPATCH` block | Declares lane, tier, payload, route, dependencies, chain and stage | Filing declares an intended route; it is not permission to bypass admission |
| Queue admission | `queue.dispatch-tiers/v2`; `ops/quota/dispatch-tiers.json` | `.github/workflows/swarm-admission.yml`; `scripts/ops/swarm_admission.py` | Admits or defers the issue filing | Evaluates tier → after edges → chain stage → flow threshold; it stamps a decision and spawns nothing |
| Provider population | `desk-feed/v1.3`; `ops/challenge/desk-feed.json` → `dispatch.provider_catalog` | Contribution Desk refresh; provider-participation index work is proposed in open PR #5134 | Scout / Swarm selection inputs | Full catalog with classes; distinguish catalog visibility, dispatchability, and proven inference invocation |
| Selection policy | `dispatch.provider_catalog.rotation_rule` | Selection is described as DoE-governed pool → Scout → Swarm dispatch | Chooses an eligible arm for task class | Bench-wide task-fit; no fixed funnel; no automatic repeat of the immediately previous pick. Scoped constraints are separate |
| Execution policy | `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md` §§19–25 | Swarm dispatch surfaces; exact selector-to-workflow hand-off remains incompletely specified | Executes selected task on a provider surface | Hard-select as preference is prohibited; single-arm routing is allowed only for a genuine capability / credential / capacity constraint and must be recorded as constrained |
| Invocation-level model routing | `docs/ops/ROUTING-ORCHESTRATION-MAP.md`; `docs/ops/ROUTING-LOGIC-CHAIN.md` | Documented `scripts/model_router.py`, `.github/actions/model-router`, `llm_api_hub`, and catalog bootstrap/feed | Review/ops, chat, and MCP invocation planes | Existing model/inference routing plane; no source establishes that `swarm-routing/v2` replaced it |
| Dispatch evidence | routed-dispatch campaign; `experiments/doe/routed-dispatch/DESIGN.json` | `.github/workflows/dispatch-stamp-fanout.yml`; `scripts/dispatch/stamp_fanout.py` | Canonical stamp and downstream evidence records | Evidence fan-out, not another task selector; one canonical stamp is retained for replay/backfill |
| 3L0 evidence | `3l0-intake/v1` | `ops/3l0/intake.jsonl` via stamp fan-out | 3L0 evaluation | Append-only intake plane |
| DoE / MVT / ATES evidence | routed-dispatch `EXPERIMENT` schema 1.0 | `experiments/doe/routed-dispatch/records/` via stamp fan-out | Comparative evaluation | Observational routed production records must not be relabeled as designed A/B arms |
| MoneyBall evidence | `moneyball-plane/v2` | `ops/moneyball/routed-dispatch/` via stamp fan-out | MoneyBall scoring | Scoring consumer; not provider-selection authority |
| QUE operational read model | `que-queue-feed/v1`, `que.queue-by-tier/v1`, `que.priority-windows/v1`, `que.governor/v1` | `scripts/que/que_feed_collect.py`; `que-feed-collect.yml` | QUE dashboard surface / consumers listed in `ops/que/README.md` | Collector produces separate read-model feeds; `que-queue-feed/v1` folds dispatch claims from watchdog state at publish |
| Dispatch watchdog state | `dispatch-state-feed/v1` | Dispatch watchdog → `ops/challenge/dispatch-state-feed.json` | Tribute Desk `desk.html` and QUE collector | Separate operational state producer; not a provider selector or QUE admission evaluator |
| Tribute Desk | `desk-feed/v1.3` plus `dispatch-state-feed/v1` | `apps/tribute-dashboard/desk.html` | Human read-only desk projection | Desk page states that it mutates nothing; queue actions proceed through GitHub intake |

## Policy lineage and supersession

| Earlier method / claim | Disposition | Current scope / correction |
|---|---|---|
| Four-lane funnel (Jules, Gemini, DeepSeek, command-dispatch) as the entire dispatch bench | Retired | These are members of the wider catalog, not the fixed funnel or default roster |
| Global rule: no provider may take two consecutive dispatches for the same entry | Superseded by machine feed | Current global rule is task-fit across the full bench with no automatic repeat of the immediately previous pick. The prose in `PROVIDER-DISPATCH-MAP.md` and Swarm Assurance §3.1 remains stale and needs a source-aligned follow-up |
| D1 next-dispatch exclusion after DeepSeek and Gemini have fired | Scoped rule | `reselection_d1` is an explicit D1/task-class constraint; it does not restore the old global no-consecutive rule |
| Cert-unit provider rotation: no arm takes two consecutive batches | Scoped rule | Swarm Assurance §21 records this as a cert-unit batch policy; keep it separate from bench-wide selection |
| `util-1-provider-rotation` preregistered hypothesis: no provider takes two consecutive dispatches for the same entry | Stale hypothesis / needs amendment | Do not silently rewrite a preregistration. Reconcile the campaign design and auditor interpretation against the current machine rule with a versioned amendment |
| Four-arm / provider-only census treated as complete wiring truth | Superseded classification | Current participation work distinguishes provider/model records, dispatch classes, inference wiring, catalog-only and invocation evidence |
| Hard-select a preferred provider as ordinary dispatch | Prohibited | DoE governs the pool/policy; Scout selects; Swarm executes. Constraint-driven single-arm dispatch must carry the constraint reason |
| DoE evolutionary best-arm culling interpreted as a dispatch-time hard selection | Retracted interpretation | Experimental population governance and live task-fit selection are separate decisions |
| DeepAgent direct-to-named-model runs counted as Swarm-routed evaluation | Excluded from qualifying routed cohort | Direct runs remain observational; qualifying cohort evidence requires the Swarm route and its stamp |
| `model_router.py` assumed to be replaced by `swarm-routing/v2` | Not established | Preserve the invocation-level router until an explicit composition contract or ADR defines its relationship to task dispatch |

## Freshness and projection consistency

| Feed / surface | Latest observed timestamp | Meaning |
|---|---|---|
| `ops/challenge/desk-feed.json` (`desk-feed/v1.3`) | `2026-11-04T10:26:53Z` | Provider catalog and traversal evidence; older than the 2026-11-12 watchdog and QUE feeds |
| `ops/challenge/dispatch-state-feed.json` (`dispatch-state-feed/v1`) | `2026-11-12T04:17:52Z` | Watchdog operational state |
| `ops/que/feeds/que-queue-feed.json` (`que-queue-feed/v1`) | `2026-11-12T10:06:11Z` | QUE producer-of-record feed; dispatch claims are folded from watchdog state at publish |
| `ops/que/feeds/queue-by-tier.json` (`que.queue-by-tier/v1`) | `2026-11-12T10:06:11Z` | Queue census by tier; observed totals 399 queued / 6 in progress at that generation |
| `ops/que/feeds/priority-windows.json` (`que.priority-windows/v1`) | `2026-11-12T10:06:11Z` | Priority-window projection |
| `ops/que/feeds/governor.json` (`que.governor/v1`) | `2026-11-12T10:06:11Z` | Admission / flow-governor projection |

These are independently generated views, not one atomic snapshot. The Tribute Desk page reads the desk feed and watchdog dispatch-state feed; the QUE collector also folds watchdog claims into its own feed family. Consumers must display source timestamps and must not infer synchronized state from a page render.

## Unresolved composition / enforcement questions

1. **Selection hand-off:** where does Scout's selected arm become an execution input — issue route metadata, workflow input, dispatch receipt, or another typed object?
2. **Selector enforcement:** which runtime component enforces `rotation_rule`, health gating, task-fit, and constrained-arm classification? The policy is documented, but this reconciliation does not identify a single verified enforcement function.
3. **Inference router composition:** does `model_router.py` receive an already-selected task/arm, or does it independently select a model inside an invocation plane? No explicit contract was found tying the two.
4. **Scoped rotation policies:** identify the enforcement point and exact scope for D1 reselection and cert-unit batch rotation; amend the `util-1-provider-rotation` preregistration without rewriting history.
5. **Provider-index PR:** PR #5134 is open and unmerged at reconciliation time. Its participation-index additions and updated provider counts are proposed branch state, not master facts. Reconcile this matrix after that PR lands or is superseded.
6. **Feed freshness:** desk-feed is older than watchdog and QUE feed snapshots. Define per-feed freshness thresholds and visible stale-state behavior.
7. **Schema governance:** if `swarm-routing/v2` is intended to become a formal schema, publish an actual schema artifact with fields, required/optional semantics, validation, version compatibility, producers, consumers, and deprecation rules. Until then, label it cohort/policy identity.

## Change-control rules

- Do not delete or rename historical policy statements, schemas, feeds, workflows, or experiment registrations during reconciliation.
- Preserve old experiment hypotheses and append versioned amendments with effective dates and reasons.
- A global policy change updates the machine-readable authority, human mirror, assurance text, experiment references, and this matrix together.
- A schema version change requires producer/consumer inventory, compatibility rules, validation, migration, and deprecation behavior.
- Documentation reconciliation does not claim runtime enforcement or passing CI.

## Primary source links

- [Provider dispatch map](../ops/PROVIDER-DISPATCH-MAP.md)
- [Desk feed](../../ops/challenge/desk-feed.json)
- [Swarm optimization assurance](../ops/SWARM-OPTIMIZATION-ASSURANCE.md)
- [Issue dispatch contract](../ops/ISSUE-TEMPLATE-DISPATCH.md)
- [Dispatch tiers](../../ops/quota/dispatch-tiers.json)
- [QUE feed architecture](../../ops/que/README.md)
- [Routing and orchestration map](../ops/ROUTING-ORCHESTRATION-MAP.md)
- [Routing logic chain](../ops/ROUTING-LOGIC-CHAIN.md)
- [Routed-dispatch design](../../experiments/doe/routed-dispatch/DESIGN.json)
- [Stamp fan-out workflow](../../.github/workflows/dispatch-stamp-fanout.yml)
- [Stamp fan-out implementation](../../scripts/dispatch/stamp_fanout.py)
- [Provider participation PR #5134](https://github.com/timerloggedout-spec/termux-monorepo/pull/5134)
