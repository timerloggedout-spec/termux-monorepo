# Repository Intelligence & Collaboration Data Plane (RIDP)

**Status:** proposed P0 architecture; implementation is phased and evidence-led  
**Scope:** repository-state acquisition, normalization, caching, provenance, synchronization, API-budget governance and reusable context delivery  
**Primary consumers:** GitHub Agentic Collaboration / ADE, SHE, ATES, Context Relationship Graph, repository tracking and domain-specific projections such as T.A.K.

## Mission

Minimize the cost of acquiring, understanding, coordinating, changing and validating repository state across an expanding fleet of autonomous agents.

> Acquire once. Store immutably. Cache intelligently. Share context selectively. Coordinate only conflicting writes. Dispatch from events. Defer intelligently. Measure meaningful operations. Preserve provenance. Optimize validated outcomes, not activity.

RIDP is a **logical data plane**, not a mandate to deploy six services or six databases. Phase A uses existing Git objects, GitHub Actions, repository scripts, JSONL records, existing caches/helpers and SHE/ATES. External databases, queues, hosted telemetry and new credentials require separate evidence and approval.

## Architectural relationship

```text
                 GITHUB / GIT SOURCES
       Issues · PRs · Commits · Refs · Actions
                  · Reviews · Checks
                         |
               EVENTS + RECONCILIATION
                         |
                         v
       +-------------------------------------+
       | RIDP — REPOSITORY DATA PLANE        |
       |                                     |
       |  1. Content-addressed evidence      |
       |  2. Scoped metadata cache           |
       |  3. Incremental synchronization     |
       |  4. API budget / admission          |
       |  5. Evidence and relationship index|
       |  6. Change / event journal          |
       |  7. Context envelope materializer  |
       +------------------+------------------+
                          |
             READ MODELS / CONTEXT ENVELOPES
                          |
          +---------------+------------------+
          |               |                  |
          v               v                  v
   AGENT CONDUCTOR       SHE / ATES      DOMAIN LENSES
   work ledger, DAG,    efficiency,      CRG, tracking,
   claims, routing,     quality,         T.A.K., other
   review, integration  outcomes         consumers
          |
          v
   SPECIALIST AGENTS / WORKERS
          |
          v
   BRANCH-SCOPED WRITES → REVIEW → VALIDATION
          |
          v
   INTEGRATION REF (guarded, expected-SHA checks)
```

## Separation of responsibility

- **RIDP** owns normalized repository evidence, acquisition/caching policy, freshness, provenance and context delivery.
- **Agentic Collaboration** owns task decomposition, manager policy, dependency phases, work claims, specialist routing, execution, review and integration.
- **SHE/ATES** observe and evaluate system behavior; they do not become a second source of repository truth.
- **Consumers** build domain-specific projections from RIDP evidence. T.A.K. is one such consumer; it does not define RIDP's base schema.
- Existing domain records remain authoritative within their scope. RIDP indexes or references them; it does not silently replace them.

## Design principles

1. **Immutable evidence vs mutable coordination.** Content-addressed objects and captured observations are immutable; branch heads, leases, assignments, quotas and status are versioned mutable state.
2. **One acquisition, many consumers.** Identical authorized requests are coalesced and normalized results shared within the same security scope.
3. **Git object identity first.** Git blobs, trees, commits and artifacts are keyed by object/content identity. GitHub metadata is separately keyed by endpoint, parameters, API version, authorization scope and validator.
4. **Incremental over repeated full scans.** Use event-driven updates and durable checkpoints; bounded reconciliation repairs missed events.
5. **Scope-aware caching.** Private data must never cross repository, principal, installation or permission boundaries. Authorization scope is part of cache identity.
6. **Freshness is explicit.** Every projection declares source ref/SHA, observed time, coverage, cursor/checkpoint and stale/partial/unavailable conditions.
7. **Idempotent ingestion.** Stable event identity and deterministic normalization make duplicate delivery safe.
8. **Coordinate only conflicts.** Independent refs proceed concurrently; same-ref writes require expected-version checks, leases or serialization.
9. **Background maintenance.** Index compaction and projection rebuilds must not block latency-sensitive acquisition or agent work.
10. **Quality before speed.** Lower request count, cache hit rate, throughput and $0 spend are not quality scores. A validated integrated outcome remains the objective.

## Logical components

| Component | Responsibility | Initial implementation boundary |
|---|---|---|
| Event ingestion | Accept push, PR, review, check, workflow and issue transitions | Native Actions triggers first; webhook receiver only if justified |
| Change journal | Append normalized, deduplicated metadata events | Repository-native JSONL / existing event records |
| Content-address registry | Map immutable object/evidence digest to source and provenance | Git object IDs + SHA-256 evidence manifests |
| Metadata cache | ETag/Last-Modified-aware metadata and response reuse | Extend existing helper/cache patterns; no cross-scope reuse |
| Incremental sync | Checkpoints, cursor progression, event reconciliation | Existing collectors and bounded API calls |
| Budget manager | Identify credential principal + API bucket, reserve, admit/defer, attribute spend | Reuse github_pat.py, spend.jsonl, Delphi defer_api and current quota records |
| Evidence index | Searchable references to repository records, artifacts and relationships | Extend Context Relationship Graph and existing indexes |
| Context materializer | Produce bounded task-specific context envelopes | Existing repository scripts and agent handoff artifacts |
| Ref coordination | Branch/ref-scoped claims, expected-SHA validation and idempotent writes | Existing dependency-phase/claim contracts; no global repository lock |
| Projection/compaction | Rebuild indexes and SHE/domain views from canonical evidence | Offline/background collectors; projections remain disposable |

These are logical capabilities, not a requirement for one module, service or datastore per row.

## Evidence and identity model

### Immutable evidence

Examples: Git object IDs, commit SHAs, source snapshots, workflow receipts, validation results, research records, artifact manifests and normalized event records.

Each evidence record should carry, where available: stable evidence ID and schema version; evidence kind and source system; repository identity and authorization scope identifier (never token value); source object/ref/SHA or API resource identity; content digest and algorithm; observed/captured timestamp; collector/version and acquisition method; provenance links; and coverage state.

Do not store credentials, raw prompts/completions, arbitrary tool payloads or secrets. Hashes of sensitive text are pseudonyms, not anonymization; do not hash and retain arbitrary private content as a workaround.

### Mutable coordination

Examples: branch head, task assignment, lease, work claim, PR lifecycle, provider availability and budget reservation.

Mutable records require stable identity; monotonically versioned state or expected source version; actor/owner identity and role provenance; idempotency key; created/updated/expiry times where applicable; and explicit conflict/stale/recovery state.

A token string or credential fingerprint is never a principal identity. Use a safe configured principal identifier and bucket class; do not infer independent quotas from different tokens belonging to the same user.

## API budget and admission governance — P0

The existing docs/ops/RATE-LIMIT-2026-10-29.md is the incident and policy evidence baseline. It records distinct PAT core, Actions installation, Search, Code Search and GraphQL buckets; it also documents the PAT helper's current scope limitation and the need to avoid tight polling.

RIDP must not create a competing quota subsystem. Consolidate contracts around github_pat.py and its circuit breaker; spend.jsonl request-spend attribution; dynamic reserve/preflight behavior; Delphi defer_api for installation-token admission; dispatch-tree and cadence-owner boundaries; and existing provider/quota registries.

Required behavior:

1. Resolve the actual credential principal and API resource bucket for each request.
2. Keep PAT core, Actions installation, Search, Code Search, GraphQL and other buckets distinct.
3. Never treat another PAT for the same user as a new primary quota pool.
4. Derive reserves from live authoritative limit/remaining/reset evidence; never hardcode a universal reserve count.
5. Attribute consumer, workflow/lane, endpoint class, admission, execution, deferral and observed result where evidence permits.
6. Protect explicitly authorized critical operations without bypassing secondary limits or repository permissions.
7. On insufficient budget or rate-limit response, defer fail-soft, record reset/Retry-After and stop retry loops. Switching tokens/endpoints to evade limits is prohibited.
8. Keep capacity state separate from agent quality and task outcome.

The quota manager is an orchestration admission signal. SKIPPED_CAPACITY is not an agent PASS or FAIL.

## Shared cache and request coalescing — P0

Suggested cache key: repository + endpoint + canonical parameters + API version + authorization scope.

| Resource | Policy |
|---|---|
| Git blob/tree/commit by object ID | Immutable, content-addressed |
| Artifact by verified digest | Immutable, subject to retention/access policy |
| Mutable repository metadata | ETag/Last-Modified + conditional refresh |
| PR/issue/review metadata | Event invalidation + conditional refresh |
| Branch/ref head | Short-lived and/or expected-SHA checked |
| Check/workflow state | Event-driven invalidation + bounded reconciliation |
| Provider catalog/availability | Time-bounded, source-stamped |
| Quota reading | Reuse only within decision window and bucket identity |

A single-flight request coalescer collapses concurrent identical cache misses into one acquisition, then distributes the result to authorized waiters. Cache entries include response status, validator, observed time, source version and freshness state. A 304 validates cached content; it is not a new content body.

A cache hit is not safe solely because URL/path matches. Authorization scope and visibility are mandatory dimensions.

## Event-driven synchronization — P0

Preferred event families: push, pull_request, pull_request_review, check_suite, check_run, workflow_run, issues and issue_comment.

Processing path:

`receive → validate trust/signature → normalize → deduplicate → bind source SHA → append journal → update affected indexes → notify interested consumers`

Use native Actions triggers where sufficient. A dedicated webhook receiver is a later adapter, not a prerequisite. Event payloads are untrusted inputs: validate schema, repository identity, action type, sender/installation authorization and source references before use.

Events can be duplicated, delayed, reordered or missed. Use stable delivery/event identity, append-only journal semantics, monotonic checkpoints and bounded adaptive reconciliation. Polling cadence remains governed by RATE-LIMIT-2026-10-29.md and its cadence owner; this proposal does not unilaterally change schedules.

## Agent context envelopes — P0

Illustrative shape (not yet a committed runtime schema):

```json
{
  "schema": "ridp-context-envelope/v1",
  "repository": "owner/name",
  "base_sha": "<40-character commit SHA>",
  "context_version": 1,
  "scope": ["docs/ops", ".github/workflows", "scripts/ci"],
  "evidence_refs": ["sha256:<digest>"],
  "freshness": {
    "observed_at": "<ISO-8601>",
    "head_sha": "<observed SHA>",
    "coverage": "complete|partial|stale|unavailable"
  },
  "task_ref": "issue-or-pr-reference",
  "authorization_scope": "non-secret scope identifier"
}
```

Runtime contract requirements: explicit base SHA and source scope; task and dependency references; immutable evidence references with digest verification; freshness, coverage and missing-evidence disclosures; authorization scope and access check at materialization and consumption; schema/version and materializer identity; no raw prompts, completions, credentials or arbitrary private message bodies.

A consumer must reject or refresh an envelope whose source SHA is incompatible with the intended write base. Envelopes are derived artifacts, not canonical source truth.

## Ref-scoped concurrency and integration — P1

The inspiration from GitHub's Ref-CAS model is architectural only; RIDP cannot assume access to GitHub internal storage APIs.

- Different branches/refs may proceed concurrently when tasks and files are independent.
- Same-ref writes must use expected-SHA validation and a scoped claim/lease or equivalent serialization.
- Claims are idempotent, owner-attributed, time-bounded and recoverable after worker failure.
- A stale base SHA triggers rebase/revalidation or explicit rejection; it never silently overwrites.
- File-overlap detection is an advisory conflict signal, not proof that edits conflict semantically.
- Integration to protected refs remains under normal PR review, required checks, branch protection and authorized merge policy.
- No repository-wide lock for unrelated branch work.
- No automatic force push or branch deletion as a conflict-resolution shortcut.

This connects to the existing dependency-phase path: dependency DAG → wave/readiness → manager policy → specialist route → execution adapter → evidence.

RIDP supplies freshness/evidence and ref-scoped coordination signals; the conductor remains the owner of admission and work assignment.

## Evidence indexing, compaction and materialized views — P1

Canonical evidence is retained according to its owning retention policy. Indexes and views are rebuildable.

- Incrementally index JSONL segments and repository events.
- Deduplicate by verified content identity without collapsing distinct provenance.
- Maintain source-to-derived-artifact lineage.
- Compact indexes/segments in background jobs.
- Rebuild SHE and consumer projections from canonical records.
- Preserve historical versions and coverage gaps.
- Garbage-collect only verified unreachable disposable cache/index material under an explicit retention policy; never delete canonical evidence merely because it was compacted.

The Context Relationship Graph is the relationship/index foundation; repo-tracking, dispatch-tree, surface feeds and SHE remain domain-owned read models. RIDP integrates with them through explicit contracts rather than replacing their source records.

## SHE / ATES measurement extension — P1

Existing docs/ops/AGENT-THROUGHPUT-METRICS.md is the quality/throughput baseline. Extend it observationally, with raw events and source evidence retained.

| Metric | Definition |
|---|---|
| API calls per task | attributed API calls / completed tasks |
| API calls per validated outcome | attributed API calls / validated integrated outcomes |
| Cache hit ratio | cache hits / eligible reads |
| Conditional validation ratio | successful conditional validations / conditional requests |
| Request coalescing ratio | waiter requests avoided / eligible concurrent duplicate requests |
| Read amplification | retrieval operations / unique source resources |
| Context reuse efficiency | verified reused context bytes / total context bytes consumed |
| Quota deferral time | time work waits due to capacity admission |
| Event freshness | usable indexed-state time − source event time |
| Fan-out ratio | authorized consumers served / source acquisitions |
| Ref conflict rate | stale/conflicting write attempts / attempted writes |
| Integration efficiency | validated integrated changes / completed agent work units |

Candidate comparative indicators:

- VOAC = validated integrated outcomes / (API calls + weighted retry overhead)
- CRE = verified reused context bytes / total context bytes consumed

These are experimental measures, not absolute quality scores. Denominators, weighting, cohort, time window, missing evidence and attribution confidence must be explicit. Do not create a speed/API-count merge gate. Missing telemetry remains null/unknown, not zero.

Display efficiency beside correctness, test evidence, attribution confidence, human intervention, conflict/retry class and promotion state. Preserve the ATES rule: quality > time.

## Phased delivery

| Phase | Priority | Deliverable | Exit evidence |
|---|---:|---|---|
| A — contracts and baseline | P0 | Architecture, ownership map, event/evidence/context schemas, current-state inventory | Contract validation; no duplicate source-of-truth claims |
| B — budget governance | P0 | Bucket/principal contract, consumer attribution, reserve/admission adapter around existing helpers | Fixture tests for bucket separation, derived reserve, defer, reset and no retry-loop |
| C — shared cache | P0 | Content-address registry, scoped metadata cache, conditional validation, single-flight | Concurrent duplicate-read fixture proves one acquisition; auth-scope isolation tests |
| D — incremental event sync | P0 | Event normalization, idempotent journal, checkpoints, affected-index updates, bounded reconciliation | Duplicate/out-of-order/missed-event fixtures and source-SHA binding |
| E — context envelopes | P0 | Bounded, authorization-aware context materializer | Deterministic envelope, digest verification, stale-base rejection, privacy tests |
| F — ref-scoped concurrency | P1 | Scoped claims/leases, expected-SHA writes, overlap signals, guarded integration | Independent-ref concurrency and same-ref conflict/recovery tests |
| G — compaction and views | P1 | Incremental indexes, provenance-preserving compaction, rebuildable SHE/consumer projections | Rebuild parity, immutable evidence retention, coverage reconciliation |
| H — efficiency evaluation | P1 | ATES/SHE RIDP observations and controlled cohorts | Reproducible baseline comparison with quality held constant |

Each phase is a separately reviewable implementation slice. No phase may claim completion based solely on architecture documentation.

## Acceptance experiments

1. Ten agents request identical authorized metadata concurrently: one upstream acquisition, shared authorized response.
2. Ten consumers request the same immutable blob: no repeated network fetch after verified content is present.
3. Unchanged PR metadata: conditional validation or cache hit; stale state is not served as fresh.
4. PR update event: affected projection invalidated and refreshed against the correct SHA.
5. Duplicate event delivery: one effective state transition.
6. Out-of-order event: no regression of a newer source version.
7. Ten independent branches: no repository-wide write lock.
8. Two writers on one branch: expected-SHA/lease prevents lost update.
9. Worker crash during indexing: resume/rebuild without canonical evidence loss.
10. PAT core near reserve: noncritical work defers; Actions installation exhaustion remains a separate bucket.
11. Same user with multiple PATs: no invented additional primary quota.
12. Missing token/quota evidence: state is unknown/unavailable, not fabricated zero.
13. Context envelope with wrong base SHA or authorization scope: rejected.
14. Efficiency cohort: compare API use, context, latency, conflicts and validated outcome under equivalent task difficulty; quality remains primary.

## Explicit non-goals and guardrails

- Reimplement GitHub's internal storage system or claim access to internal Ref-CAS/pack services.
- Deploy a distributed database, message broker or observability SaaS before a measured need.
- Replace Git, GitHub, existing domain records, the Context Relationship Graph, repo-tracking, dispatch-tree, SHE or ATES.
- Merge all API resource buckets or treat token count as quota identity.
- Use polling to compensate for missing event design without cadence-owner review.
- Share private cache entries across authorization boundaries.
- Store raw prompts, completions, credentials, secrets or arbitrary tool payloads.
- Automatically merge, force-push, overwrite protected refs or bypass review/checks.
- Optimize request count or throughput at the expense of correctness.
- Treat T.A.K. as the canonical RIDP schema or require T.A.K. fields on general repository evidence.

## Existing source contracts and integration map

| Existing surface | RIDP relationship |
|---|---|
| docs/ops/RATE-LIMIT-2026-10-29.md | P0 API bucket, cadence, reserve and incident baseline |
| github_pat.py / spend.jsonl (as identified by rate-limit record) | Existing PAT helper/circuit breaker and spend evidence; inspect actual source paths before implementation |
| Delphi defer_api | Existing installation-token reserve/defer precedent |
| docs/ops/AGENT-TEAM-ORCHESTRATION.md | Conductor roles, route admission, evidence and collaboration loop |
| docs/architecture/AGENT-TEAM-CONTROL-PLANE.md | Scout → team → telemetry → review → promotion → synthesis |
| docs/ops/AGENT-TEAM-ROSTER.md | Identity/role/adapter boundaries and quota semantics |
| docs/ops/AGENT-THROUGHPUT-METRICS.md | ATES quality/throughput measurement rules |
| docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md | Read-only materialized projection contract |
| Context Relationship Graph | Evidence relationships, source records and historical graph |
| docs/ops/REPO-TRACKING.md | Domain-owned tracking view; no replacement |
| docs/ops/DISPATCH-TREE-FEED.md | Existing quota cadence/admission view; no replacement |
| T.A.K. common operating picture | Downstream domain lens over pinned RIDP evidence; separate schema and acceptance |

**Implementation rule:** before each phase changes code, inspect the current implementation and owner lane, identify exact source paths and tests, and reuse existing contracts. This document is the architecture proposal, not proof that every named helper or integration is already connected.
