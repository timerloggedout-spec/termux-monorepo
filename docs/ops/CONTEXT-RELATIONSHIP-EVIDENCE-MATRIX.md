# Context Relationship Evidence Matrix

## Purpose and Authority

`CRG-14` and `AR-19` add a **read-only, metadata-only decision-support projection** to the existing Context Relationship + Lead/Lag Audit artifact. The projection uses the audit event, GitHub check metadata, and the checked-in canonical graph build summary to organize relationship evidence by authority, provenance, freshness, risk, duplication, coverage, and independently bound outcomes.

> The matrix is **not** a canonical graph publisher, a second datastore, a super-orchestrator, a provider router, or a write authorization surface. It cannot infer causality from time proximity, execute provider commands, promote a routing choice, write a branch, alter a generated index, or relax the retained Issue #192 holds.

| Contract element | Matrix behavior | Explicit non-behavior |
|---|---|---|
| Root and scope | Reports typed Issue/PR roots exactly when the audit supplies their numeric ID. `fuzzy_fallback` is always `false`. | Does not infer a near match for an absent typed root. |
| Evidence locator | Retains fixed GitHub API/action/check/comment locators and source binding IDs. | Does not retain raw issue, comment, or review bodies. |
| Classification | Keeps `verified` and `candidate` records separate. A check becomes verified only with check ID, source SHA, and completion time. | Does not turn unknown/missing bindings into success. |
| Risk and disposition | Quarantines unbound check observations and reports warning-derived gaps. | Does not score agents, providers, or domains. |
| Freshness and coverage | Carries audit observation time and exposes graph ref/history/parser gaps from `build-summary.json`. | Does not claim present-lineage coverage from a stale or partial graph. |
| Duplicate concentration | Counts repeated immutable locators deterministically. | Does not collapse independent evidence sources or manufacture authority. |

## Backlink-Analysis Methodology Crosswalk

The implementation adapts the **questions** of relationship analysis, not SEO data, scoring, or tooling. This preserves a useful review vocabulary without importing domain authority, traffic, rankings, disavow mechanics, or external SEO APIs.

| Relationship-analysis analogy | Matrix implementation | Boundary |
|---|---|---|
| Inbound link | Typed, metadata-only relationship evidence arriving at an exact Issue/PR/SHA scope. | It is not a web link graph or PageRank input. |
| Referring domain | Evidence authority and provenance class, such as read-only GitHub Actions, GitHub API, or Checks API. | There is no numeric authority score. |
| Authority distribution | Deterministic counts by `authority_distribution` and `provenance_distribution`. | Counts are descriptive evidence inventory, not a routing score. |
| Link growth/loss | Observed freshness, stale/partial graph disclosure, and explicit coverage gaps. | No traffic or ranking trend is asserted. |
| Toxic link | `risk.state` and `disposition`, including `missing_binding` and `quarantined`. | No deletion, disavow, suppression, or provider-control effect exists. |
| Anchor/reference type | Typed relationship and provenance fields. | Raw prose/body content is excluded. |
| Link gap | An expected-coverage subject with a concrete gap reason. | A gap is not proof that a relationship does not exist. |

## Data Flow and Safety

The audit script uses `gh api --paginate --slurp` for paginated read endpoints. Each slurped page is normalized according to its known endpoint shape before any comment or check metadata is emitted. This corrects the previous concatenated-JSON parsing failure instead of discarding it. A malformed page becomes a classified `WARNING`/`UNKNOWN` collector record and a coverage gap; it is excluded from temporal pairing and cannot become successful check evidence.

The optional canonical build summary supplies **coverage disclosure only**. It is not used to assert a relationship or to mutate the canonical index. When its ref is not `master`, history is incomplete, parser failures exist, or it lacks a source-SHA binding, the matrix reports the limitation. This preserves the graph’s existing publisher/reconciler boundary and the live audit’s least-privilege workflow boundary.

## Reuse and Tool Decisions

| Candidate capability or source | Decision | Rationale |
|---|---|---|
| Repository-local `context-relationship-graph` discipline | Reuse | It already defines metadata exclusion, exact-root behavior, verified/candidate separation, and trusted publication boundaries. |
| Repository-local `adaptive-feedback-cycle` discipline | Reuse | It supplies the `WARNING`/`UNKNOWN` separation used for malformed collection outcomes. |
| Repository-local `review-loop` discipline | Reuse | It supplies provenance-first review and distinguishes correctness findings from provider control/cancellation evidence. |
| Repository-local `evidence-led-monorepo-ops` telemetry | Reference only | Existing telemetry remains its own owner; CRG-14 does not create metrics collection or a duplicate telemetry plane. |
| Repository-local `agentic-dev-automation` discipline | Reference only | The matrix is observe-only and has no execution, scheduling, or provider control effect. |
| Backlink-analysis methodology | Adapt vocabulary only | The crosswalk above omits SEO scoring, APIs, traffic, rankings, competitors, and disavow semantics. |
| Session MCP services and external connectors | Rejected/deferred | They are unnecessary for a local deterministic projection and would add permission/scope overlap without filling an evidence gap. |
| Global-skill rewrites | Rejected | This PR reuses repository-local operational contracts; it does not alter shared skills. |

## Cherry-Pick Disposition

No open pull request is a safe carrier for this increment. PRs #263, #350, #351, and #352 are respectively historical restoration, unrelated canary, separate telemetry, or dirty lag-index work. The merged current-master predecessors `f3724f0`/PR #349, `ff2a3af`, `ed7e203`, `c30d19e`, and `ab1144b` are cited as reusable prior art rather than cherry-picked. The new single PR is therefore limited to the existing audit collector, the new deterministic projection, focused tests, and governing documentation.

## Retained Holds

The matrix cannot authorize B3 retries, B4/AR-04, B5/A-14, PR #276, provider AutoFix, browser/UI use, issue/comment-to-shell execution, direct default-branch writes, secret handling, or generated graph hand edits. Any later effectful use requires a separately accepted item with current authority, SHA binding, provenance, idempotency, and validation evidence.
