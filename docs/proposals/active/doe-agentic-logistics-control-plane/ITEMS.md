# ITEMS — doe-agentic-logistics-control-plane

| ID | Priority | Status | Scope | Dependencies | Acceptance criteria |
|---|---:|---|---|---|---|
| DPLC-001 | P1 | complete | Reconcile the LangChain ecosystem README and all existing owned forks/repositories into a provenance- and license-aware inventory. | RECON | Every entry has source URL, observed README claim, repo owner/ref, purpose, evidence class and adoption state; the README taxonomy is fully indexed; discovery is not adoption. |
| DPLC-002 | P1 | queued | Define framework composition and adapter boundaries for LangChain, LangGraph, Deep Agents, integrations, LangSmith/Temporal and existing provider dispatch. | #5045 review/remediation | No second graph engine, telemetry backend, provider catalog or durable scheduler; graph use justified per workflow; versions and source SHAs pinned before code. |
| DPLC-003 | P1 | queued | Model logistics and engineering-work sequencing using PDDL plus suitable constraint/scheduling solvers. | DPLC-001 | PDDL domain/problem fixtures, planner capability matrix and deterministic tests; hard precedence separated from numeric capacity/time-window optimization; no new scheduler deployed. |
| DPLC-004 | P1 | queued | Reconcile the provider/model inference-arm population and design/simulate a constrained feedback controller for endpoint admission, pacing and concurrency. | #5134 → #5160; DPLC-001 | [FREE-INFERENCE-TOURNAMENT-ORDER.yml](FREE-INFERENCE-TOURNAMENT-ORDER.yml) DPLC-FIT-00–04: exact endpoint identity, separate discovery/transport/entitlement/quota/eligibility states, deterministic offline simulator, and fail-closed safety tests. No live inference or routing mutation. |
| DPLC-005 | P1 | queued | Pre-register a distinct free-inference endpoint cohort and later manager-policy comparison using existing DoE/ATES/3L0 contracts. Extend `util-1-provider-rotation`; do not create a duplicate campaign or pool endpoint results with its existing build-task cohort. | DPLC-002–004; `util-1-provider-rotation`; DOE-FAMILY rules 5–9 | [FREE-INFERENCE-TOURNAMENT-ORDER.yml](FREE-INFERENCE-TOURNAMENT-ORDER.yml) DPLC-FIT-03–08: versioned cohort, production-flow automation, exact instance stamps, sets-of-three, max n=12/trigger, separate endpoint and manager effects, and evidence-based INCONCLUSIVE/NOT_ESTABLISHED states. No live inference until separately authorized. |
| DPLC-006 | P1 | queued | Map scientific, optimization and control-system roles to the canonical specialist-role and DoE participant systems. | #5189; #5136/#5183 sequencing | Reuse #5189 role registry and #5183 participant rules; no clone issuance, wallet/quota provisioning or self-verification. |
| DPLC-007 | P1 | queued | Bind proposal review, QDesk dispatch, Delphi outcome, QUE admission, implementation and independent verification into the existing pipeline. | #5145/#5146; DPLC-001–006 | One stable proposal/RFP identity and hash-bound artifacts; canonical feeds only; idempotent correlation; no second queue/feed/ledger/dashboard. The Project Task form remains the intake trigger; QUE admission and provider-specific eligibility remain separate gates. The order file is proposal-scoped, not a new runtime registry. |
| DPLC-008 | P1 | queued | Deliver phased implementation, evidence package and promotion recommendation. | DPLC-001–007; all owner gates | PRs cite item IDs; tests and same-SHA gates are observed; failed, blocked, unrun and simulated states remain distinct; no automatic merge/deploy/production activation. |

## Free-inference tournament order\n\nThe detailed machine-readable implementation sequence is [`FREE-INFERENCE-TOURNAMENT-ORDER.yml`](FREE-INFERENCE-TOURNAMENT-ORDER.yml). It is scoped to DPLC-004/005 and reuses the existing `util-1-provider-rotation` campaign with a distinct, versioned inference cohort. The existing `routed-dispatch` population remains observational unless a dispatch is assigned under the pre-registered design. Build-dispatch harness arms (#5151/#5176) are not conflated with provider/model inference arms (#5134/#5160).\n\n## Execution boundary

DPLC-001 is the completed RECON/inventory slice. DPLC-002–008 remain queued pending proposal review and their named prerequisites. The QUE filing is for bounded proposal/RFP coordination first; it is not a claim that provider execution, participant issuance or production integration has started.

## Required validation

- Run scripts/proposals/validate_registry.py.
- Run focused deterministic tests for every implementation slice.
- Run scripts/ci/repo_gate.py.
- Run scripts/ci/termux_smoke.py.
- Re-fetch review threads and current-head checks before promotion.
