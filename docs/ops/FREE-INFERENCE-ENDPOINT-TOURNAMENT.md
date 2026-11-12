# Free Inference Endpoint Tournament

**Order:** [QDESK-FIT-001](../../ops/que/orders/free-inference-tournament.yml)  
**Execution authority:** existing QDesk / QUE admission and project-task dispatch  
**Status:** order prepared; no tournament inference has been authorized or executed by this document.

## Why this is an order, not another orchestration system

The repository already owns the necessary control planes:

- Project Task issue form: `.github/ISSUE_TEMPLATE/project-task.yml`
- QUE admission: `.github/workflows/swarm-admission.yml` and `scripts/ops/swarm_admission.py`
- task intake/queue receipt: `.github/workflows/project-task-dispatch.yml`
- dispatch tiers and dependencies: `ops/quota/dispatch-tiers.json`
- provider dispatch census: `docs/ops/PROVIDER-DISPATCH-MAP.md`
- provider credentials, catalog, and no-cost eligibility contracts: `docs/ops/PROVIDER-FREE-INFERENCE.md`, `docs/ops/OPENROUTER-FREE-CATALOG.md`
- manager comparison: `docs/research/MANAGER-TOURNAMENT-CONTRACT.md` and `docs/ops/MANAGER-TOURNAMENT.schema.json`
- canonical evidence: `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md`
- QUE's producer-owned queue feeds: `ops/que/feeds/`

The order is a declarative campaign plan consumed by QDesk/QUE operators and existing dispatch machinery. It is **not** a new scheduler, queue, executor, provider registry, or evidence store. The Desk remains a read model; the admission workflow is the execution gate.

## What qualifies as a free endpoint

The tournament unit is a provider × endpoint × exact model × transport tuple, not a provider name and not a model alias.

A candidate is inference-eligible only when the live evidence proves:

1. the exact model is present in a current catalog;
2. its prompt and completion prices are explicitly zero (or an equivalent provider-native no-cost contract is independently proven);
3. the required account-level no-cost entitlement is verified where applicable;
4. the exact invocation route is wired and available;
5. the credential is present without exposing its value;
6. the request can be constrained to zero maximum price and has no provider fallback.

A `:free` suffix, a catalog row, a configured Actions secret, or a green workflow does not independently prove free inference. Unknown entitlement means catalog-only. Funding-blocked, paid, ambiguous, stale, or uninvocable endpoints remain in the census with a reason, but are not called.

### Existing evidence that constrains the first cohort

The repository's guarded OpenRouter smoke has already established an important distinction: the exact allowlisted `liquid/lfm-2.5-2.6b:free` model and free-tier account were verified, but the single bounded completion request returned HTTP 429. That is **not** a successful inference result and does not establish why the request was rate-limited. The original evidence does not authorize another request or a retry.

Gemini and Felo credentials have been observed in Actions, but account-specific no-cost inference entitlement was not established in the inspected evidence. Their first-stage role is catalog observation, not inference. Other providers must independently satisfy the same candidate gate; no provider is promoted because it appears in a registry or research list.

## Self-implementation sequence

The machine-readable order defines nine dependency-gated stages:

| Stage | Priority | Deliverable | Exit condition |
|---|---:|---|---|
| FIT-00 | P0 | Recon and contract freeze | Current source paths/SHAs reconciled; no duplicate control plane |
| FIT-01 | P0 | Endpoint universe + eligibility reconciler | Stable endpoint identities; explicit eligible/ineligible/unknown dispositions |
| FIT-02 | P0 | Guarded provider smoke adapters | Exact zero-cost, no-fallback, one-request contract; failure classes tested |
| FIT-03 | P1 | Frozen task cohort | Public/synthetic tasks, hashes, deterministic checks, complexity bands |
| FIT-04 | P1 | Evidence and artifact pipeline | JSONL/receipts linked to source SHA, run, attempt, candidate, manager, cohort |
| FIT-05 | P1 | Manager tournament runner | Identical cohort/environment/budget; blocked randomized order; 3 repetitions |
| FIT-06 | P1 | Scoring and culling | Acceptance-first comparison, uncertainty, no-selection when evidence is weak |
| FIT-07 | P2 | QDesk/QUE projection | Existing feeds and Desk projections expose progress without dispatch authority |
| FIT-08 | P2 | First controlled cohort | One manual cohort, re-fetched artifacts, reconciled outcome; no routing mutation |

### Dispatch procedure

Each work package is filed through the existing Project Task form. The form declares `issue-dispatch/v1`, lane `swarm-dispatch`, QUE tier 3, payload `project-task`, and route `project-task-dispatch.yml`. The `swarm-admission` workflow must stamp the issue `swarm-admitted` before the downstream task is actionable.

The required issue-body headings are:

- `### Entry`
- `### Task / spec`
- `### Scope`
- `### Done-evidence`

A deferred or unmatched filing is not an execution. The order's dependency graph controls stage sequencing; the QUE admission workflow remains the per-filing gate. Do not invent a custom chain entry in `dispatch-tiers.json` for this campaign.

## Tournament design

Four initial manager policies are specified:

- **baseline_single_endpoint** — one eligible endpoint, no peer fan-out.
- **sequential_peer_verify** — a primary endpoint plus one independent peer only when a defined verification gap exists.
- **parallel_triage_then_integrate** — bounded independent proposals followed by one reconciliation pass.
- **quota_aware_router** — task-fit selection among currently eligible endpoints, with no inference when quota state is unknown.

All arms receive the same tasks, evaluator, tool permissions, environment, budgets, and evidence contract. The initial design uses three repetitions per manager, blocked by task and complexity band, with randomized order and provider rotation. The sample is intentionally small; uncertainty must be reported and a weak result must produce `no_selection`, not a manufactured winner.

Primary outcomes are correctness, deterministic validation, final acceptance, and integrated result. Secondary observations include time-to-integration, useful/duplicate work, feedback cycles, retries, conflicts, human intervention, provider/model/manager/environment failures, attribution confidence, and variance.

## Safety and non-negotiable boundaries

- Manual, explicitly bounded inference only; no scheduled inference.
- One smoke completion request per candidate; no retries after 429, timeout, or ambiguous outcome.
- Zero maximum prompt/completion/request/image prices; no paid fallback or alternate provider.
- Do not create, rotate, export, or mutate credentials or accounts.
- Do not persist secret values, raw prompts/completions, raw account metadata, raw error bodies, or private context.
- Missing evidence remains `null`, never zero.
- Preserve failed, cancelled, deferred, and skipped outcomes.
- Workflow success means the workflow completed; it does not mean inference succeeded.
- No production routing, weights, provider allow-lists, or account settings change through this tournament.
- Promotion requires repository gates on the same SHA, independent review, provenance validation, and explicit operator promotion.

## Current disposition

This order is prepared, not dispatched. Its YAML is not yet consumed automatically by the QUE collector; it is the campaign specification for filing the stage work packages through the existing Project Task and QUE admission path. No inference call, quota reservation, scheduled job, or production routing change is performed by preparing the order.
