# Contract-to-runtime traceability: routing and orchestration

**Status:** architecture contract and runtime reconciliation; documentation + contract implementation
**Last reconciled:** 2026-11-12
**Purpose:** distinguish coexisting routing-related contracts and identify superseded policy statements without deleting historical evidence.

## Determination

`swarm-routing/v2` is used as a routed-dispatch policy/cohort identity in the November routed-dispatch experiment. The reviewed sources do not establish it as a standalone JSON Schema or a replacement for every other routing component. The architecture is layered: task declaration, queue admission, provider selection, task dispatch, inference/model invocation routing, evidence fan-out, and read-only projections have different responsibilities.

## Contract-to-runtime matrix

| Plane | Contract / authority | Producer or implementation | Consumer / purpose | Status |
|---|---|---|---|---|
| Task declaration | `issue-dispatch/v1`; `docs/ops/ISSUE-TEMPLATE-DISPATCH.md` | Issue template / dispatch metadata | Admission and dispatch workflow | Declares lane, tier, payload, route and chain metadata; not a provider selector |
| Queue admission | `queue.dispatch-tiers/v2`; `ops/quota/dispatch-tiers.json` | `scripts/ops/swarm_admission.py`; `.github/workflows/swarm-admission.yml`; QUE collector | Dispatch eligibility, tier ordering, dependency chains | Separate admission gate; not the Swarm provider router |
| DoE allocation and eligible pool | Active DoE campaign design; `desk-feed/v1.3` provider catalog is candidate/evidence input | DoE design + live catalog/availability/quota evidence | Declares eligible population, treatment assignment, allocation proportions, repeat policy and endpoint-level gates | DoE owns allocation/rotation; the desk feed mirrors the eligible pool and policy, not an independent selector |
| Scout selection and Swarm execution | `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md` §§1, 14–25; `docs/ops/SCOUT-ROSTER.md`; `inference-selection-receipt/v1` | DoE assigns; Scout selects within the assigned eligible pool; Swarm dispatches | Routed build/fix/review/invoke work | No global no-repeat rule; a scoped repeat constraint exists only when pre-registered in a DoE campaign; custom manager settings require an active contract |
| Scoped experiment rotation | Cert-unit DoE design and Swarm Assurance §21 | Cert-unit batch dispatcher implements its registered assignment | Per-batch comparative evaluation | Scoped no-consecutive-batch rule; DoE-owned campaign treatment, not a global catalog constraint |
| Evidence fan-out | Canonical routed-dispatch stamp; `experiments/doe/routed-dispatch/` | `scripts/dispatch/stamp_fanout.py`; dispatch stamp fan-out workflow | 3L0, DoE/MVT/ATES, MoneyBall, desk traversal evidence | One canonical stamp distributed to evaluation planes; evidence fan-out is not a second router |
| QUE read model | `que-queue-feed/v1`, `que.queue-by-tier/v1`, `que.priority-windows/v1`, `que.governor/v1` | QUE collector/governor | Tribute Desk queue projections | Independent queue feed family |
| Watchdog state | `dispatch-state-feed/v1` | Dispatch watchdog | Tribute Desk dispatch-state projection | Separate from QUE and provider selection |
| Inference/model invocation routing | `docs/ops/ROUTING-ORCHESTRATION-MAP.md`; `docs/ops/ROUTING-LOGIC-CHAIN.md`; new selection receipt contract | `scripts/model_router.py`, `.github/actions/model-router`, `scripts/ops/provider_invoke.py`, `llm_api_hub` | Review/operations, Chat and MCP invocation planes | Existing invocation-level selectors/gateways remain distinct. No reviewed runtime currently consumes the new DoE selection receipt; composition is an open integration seam |
| Tribute Desk | `apps/tribute-dashboard/desk.html` / published `desk.html` | Aggregates desk traversal, watchdog and QUE feeds | Human read-only status projection | Not an execution router; each independent feed displays its own timestamp and fresh/STALE/unknown state; missing feeds are not zero |

## Supersession register

| Earlier method or claim | Disposition | Current interpretation |
|---|---|---|
| Four-lane provider funnel as the entire dispatch bench | Retired | Jules, Gemini, DeepSeek and command-dispatch remain arms within the complete catalog; no fixed funnel/default |
| Global “no provider takes two consecutive dispatches” rule | Superseded | DoE owns the assignment/repeat policy. No global no-repeat rule; a stricter constraint is valid only when pre-registered in the relevant DoE campaign |
| Hard-selecting a preferred provider as a general dispatch policy | Prohibited | Scout selects from the DoE-governed, health-gated pool; constrained arm only for real capability/credential/capacity constraints |
| DoE evolutionary best-arm result treated as dispatch-time selection | Retracted distinction | DoE owns allocation/rotation and statistical gates; Scout selects an eligible endpoint within the assigned treatment; Swarm executes |
| Two-surface provider wiring census | Superseded | Multi-surface `inference_wiring` classification is the current classification basis |
| DeepAgent direct-to-model dispatch as qualifying Swarm execution | Rejected | Qualifying evaluation requires routing through the Swarm population; direct-to-model runs remain observational/non-qualifying |
| QUE and watchdog feeds treated as one queue | Not equivalent | Separate producers, schemas and projection responsibilities |
| `model_router.py` assumed replaced by `swarm-routing/v2` | Not established | Preserve invocation-level router; composition with task dispatch remains an open architecture contract |

## Reconciliation findings and gaps

1. **Authority drift:** Provider Dispatch Map, Swarm Assurance, DoE Family, Scout docs, desk feed and telemetry index now agree: DoE owns Swarm allocation/rotation; Scout selects within the active DoE assignment; the provider catalog is eligibility/evidence input. The cert-unit no-consecutive-batch rule remains a scoped DoE treatment.
2. **Composition contract missing:** `scripts/model_router.py` currently selects from a limited role-specific peer/residual set; `provider-invoke.yml` accepts a provider directly; `scripts/ops/provider_invoke.py` resolves a model at invocation time; `llm_api_hub` executes caller-specified model requests. The reviewed runtime paths do not consume a DoE assignment/selection receipt. This is an unresolved interface, not proof of duplicate implementations.
3. **Freshness is multi-source:** desk-feed, watchdog and QUE feeds have independent producers and timestamps. Tribute Desk now displays per-feed fresh/STALE/unknown state; the 2026-11-12 audit found the main desk snapshot older than seven days and preserved that stale truth rather than fabricating a refresh.
4. **Version semantics:** `swarm-routing/v2` remains a routed-dispatch cohort/policy identity, not a standalone JSON Schema. `inference-selection-receipt/v1` is the explicit schema for the selection-to-invocation decision.

## Required next engineering steps

- Implement the DoE assignment producer/consumer contract against the existing eligible pool owner surfaces (#5160); do not create a competing provider catalog or quota manager.
- Implement Scout's bounded endpoint selection adapter and bind its receipt to `provider-invoke.yml`, `scripts/ops/provider_invoke.py`, `model_router.py` and/or `llm_api_hub` without adding a second selector.
- Enforce endpoint identity equality between receipt and actual invocation; missing or mismatched receipts remain observational/deviant, never silently qualified.
- Implement per-endpoint statistical tests, sample/power and stopping gates, assignment-integrity/SRM checks and multiplicity handling before any endpoint significance/cull/promotion claim.
- Implement active custom-contract validation, fee distribution settlement and explicit role exemptions; do not invent pricing rates.
- Keep private participant strategies in an access-controlled store; publish only commitments/references and cull/disclosure state.
- Run the DoE contract workflow and full repository tests; validate per-feed freshness in the live Tribute deployment.

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
