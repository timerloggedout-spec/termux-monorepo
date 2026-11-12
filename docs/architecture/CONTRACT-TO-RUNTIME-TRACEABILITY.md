# Contract-to-runtime traceability: routing and orchestration

**Status:** architecture reconciliation baseline; documentation-only change
**Last reconciled:** 2026-11-12
**Purpose:** distinguish coexisting routing-related contracts and identify superseded policy statements without deleting historical evidence.

## Determination

`swarm-routing/v2` is used as a routed-dispatch policy/cohort identity in the November routed-dispatch experiment. The reviewed sources do not establish it as a standalone JSON Schema or a replacement for every other routing component. The architecture is layered: task declaration, queue admission, provider selection, task dispatch, inference/model invocation routing, evidence fan-out, and read-only projections have different responsibilities.

## Contract-to-runtime matrix

| Plane | Contract / authority | Producer or implementation | Consumer / purpose | Status |
|---|---|---|---|---|
| Task declaration | `issue-dispatch/v1`; `docs/ops/ISSUE-TEMPLATE-DISPATCH.md` | Issue template / dispatch metadata | Admission and dispatch workflow | Declares lane, tier, payload, route and chain metadata; not a provider selector |
| Queue admission | `queue.dispatch-tiers/v2`; `ops/quota/dispatch-tiers.json` | `scripts/ops/swarm_admission.py`; `.github/workflows/swarm-admission.yml`; QUE collector | Dispatch eligibility, tier ordering, dependency chains | Separate admission gate; not the Swarm provider router |
| Provider catalog and global selection | `desk-feed/v1.3`; `dispatch.provider_catalog.rotation_rule` in `ops/challenge/desk-feed.json` | Contribution Desk refresh; Scout consumes DoE-governed pool | Task-fit selection across the full wired bench | Machine-readable rule of record; no fixed funnel and no automatic repeat of previous pick |
| Swarm execution | `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md` §§19–25 | Scout selects; Swarm dispatches; provider surfaces execute | Routed build/fix/review/invoke work | No-hard-select is the general rule; constrained single-arm routing requires a genuine task constraint and must be recorded |
| Scoped experiment rotation | Swarm Assurance §21 | Cert-unit batch dispatcher | Per-batch comparative evaluation | Scoped no-consecutive-batch rule; not a global catalog constraint |
| Evidence fan-out | Canonical routed-dispatch stamp; `experiments/doe/routed-dispatch/` | `scripts/dispatch/stamp_fanout.py`; dispatch stamp fan-out workflow | 3L0, DoE/MVT/ATES, MoneyBall, desk traversal evidence | One canonical stamp distributed to evaluation planes; evidence fan-out is not a second router |
| QUE read model | `que-queue-feed/v1`, `que.queue-by-tier/v1`, `que.priority-windows/v1`, `que.governor/v1` | QUE collector/governor | Tribute Desk queue projections | Independent queue feed family |
| Watchdog state | `dispatch-state-feed/v1` | Dispatch watchdog | Tribute Desk dispatch-state projection | Separate from QUE and provider selection |
| Inference/model invocation routing | `docs/ops/ROUTING-ORCHESTRATION-MAP.md`; `docs/ops/ROUTING-LOGIC-CHAIN.md` | `scripts/model_router.py`, `.github/actions/model-router`, `llm_api_hub`, live catalog feed | Review/operations, Chat and MCP invocation planes | Existing invocation-level routing; reviewed sources do not say it is superseded by `swarm-routing/v2` |
| Tribute Desk | `apps/tribute-dashboard/desk.html` / published `desk.html` | Aggregates desk traversal, watchdog and QUE feeds | Human read-only status projection | Not an execution router; feed timestamps are independent |

## Supersession register

| Earlier method or claim | Disposition | Current interpretation |
|---|---|---|
| Four-lane provider funnel as the entire dispatch bench | Retired | Jules, Gemini, DeepSeek and command-dispatch remain arms within the complete catalog; no fixed funnel/default |
| Global “no provider takes two consecutive dispatches” rule | Superseded | `desk-feed.json` sets bench-wide task-fit with no automatic repeat of the previous pick; a stricter rule must be explicitly scoped |
| Hard-selecting a preferred provider as a general dispatch policy | Prohibited | Scout selects from the DoE-governed, health-gated pool; constrained arm only for real capability/credential/capacity constraints |
| DoE evolutionary best-arm result treated as dispatch-time selection | Retracted distinction | DoE governs pool/policy; Scout selects for the task; Swarm executes |
| Two-surface provider wiring census | Superseded | Multi-surface `inference_wiring` classification is the current classification basis |
| DeepAgent direct-to-model dispatch as qualifying Swarm execution | Rejected | Qualifying evaluation requires routing through the Swarm population; direct-to-model runs remain observational/non-qualifying |
| QUE and watchdog feeds treated as one queue | Not equivalent | Separate producers, schemas and projection responsibilities |
| `model_router.py` assumed replaced by `swarm-routing/v2` | Not established | Preserve invocation-level router; composition with task dispatch remains an open architecture contract |

## Reconciliation findings and gaps

1. **Rotation prose drift:** Provider Dispatch Map §Rotation and Swarm Assurance §1 still stated the old global no-two-consecutive rule. The machine feed's `rotation_rule` explicitly supersedes it. This change corrects those human mirrors while retaining §21's cert-unit rule as a scoped experiment constraint.
2. **Composition contract missing:** the September model-routing map documents review/operations, Chat and MCP routing planes; the November Swarm policy documents task dispatch and provider-arm selection. No reviewed source establishes the exact hand-off from Scout's selected arm into `model_router.py` or `llm_api_hub`. This is an unresolved interface, not proof of duplicate implementations.
3. **Freshness is multi-source:** desk-feed, watchdog and QUE feeds have independent producers and timestamps. The dashboard should expose per-feed freshness and avoid implying an atomic snapshot.
4. **Version semantics:** do not describe `swarm-routing/v2` as a JSON Schema version until a formal schema file defines fields, required/optional semantics, validation, compatibility, migration and deprecation.

## Required next engineering steps

- Trace the actual call chain from issue metadata through admission, Scout selection, workflow inputs and provider invocation; record exact file/function/field names.
- Identify the single enforcement point for the global `rotation_rule` and prove that the emitted stamp is required before execution.
- Locate and test the cert-unit batch rotation enforcement separately from global selection.
- Define a versioned dispatch-to-inference hand-off contract (selected provider/arm, surface, model, constraint reason, correlation/session/run IDs); do not add a second selector.
- Add schema validation and freshness checks for each feed producer/consumer; display stale/unknown state explicitly.
- Add automated drift checks that compare machine policy to human mirrors and fail when a superseded global rule reappears.

## Primary sources

- `ops/challenge/desk-feed.json` → `dispatch.provider_catalog.rotation_rule`
- `docs/ops/PROVIDER-DISPATCH-MAP.md` §Rotation
- `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md` §§1, 15, 19–25
- `docs/ops/ISSUE-TEMPLATE-DISPATCH.md`
- `ops/quota/dispatch-tiers.json`
- `scripts/ops/swarm_admission.py`
- `scripts/que/que_feed_collect.py`
- `scripts/dispatch/stamp_fanout.py`
- `experiments/doe/routed-dispatch/README.md`
- `docs/ops/ROUTING-ORCHESTRATION-MAP.md`
- `docs/ops/ROUTING-LOGIC-CHAIN.md`
- `apps/tribute-dashboard/desk.html`
