# Source — Repository Intelligence & Collaboration Data Plane

## Origin

This proposal carries forward the original architecture brief, “Git storage architecture → API efficiency → Agentic Collaboration”, supplied in the project conversation. Its central opportunity is not merely faster API calls; it is changing how repository agents acquire, exchange, cache, reconcile and reason about repository state.

The source brief identifies five major opportunities:

1. Reduce redundant GitHub API requests through content-addressed caching.
2. Replace repeated repository-wide retrieval with incremental synchronization.
3. Make Git objects and GitHub metadata complementary sources of truth.
4. Coordinate agents around shared, immutable evidence rather than repeated context ingestion.
5. Build a measurable optimization layer for API consumption, data freshness and collaboration efficiency.

## Source architecture retained

The original logical RIDP includes Content Address Registry, Metadata Cache, Incremental Sync Engine, Request Budget Manager, Evidence Index and Change/Event Journal.

It is intentionally a logical architecture implemented initially with existing GitHub Actions, Git objects, JSONL evidence, repository scripts and SHE infrastructure—not six new databases or services.

The original immutable/mutable distinction is retained:

- Immutable evidence: commit objects, source snapshots, workflow receipts, agent execution events, validation results, research findings and artifact manifests.
- Mutable coordination: branch heads, PR status, agent claims, review ownership, work assignments, provider availability and quota budgets.

The original implementation inspirations are retained as design translations, not claims of access to GitHub internals:

- Content-addressed storage → SHA-keyed evidence registry.
- Virtual replicas → lightweight agent context/cache.
- Ref-CAS → per-branch/PR write coordination.
- Ref version checks → SHA freshness checks.
- Pack compaction → background evidence/index consolidation.
- Materialized views → precomputed SHE projections.
- Event streams → event-driven conductor.
- Partial replicas → selective repository context.
- Atomic commit API → future integration interface only if supported.

## Existing implementation evidence supplied in the source brief

The source brief points to docs/ops/RATE-LIMIT-2026-10-29.md and identifies existing work around github_pat.py, spend.jsonl, ETag conditional requests, per-session hourly budgets, derived reserve preflight, Delphi defer_api, Historical Corpus, SHE and ATES.

It explicitly identifies a gap: the PAT helper circuit breaker applies only to callers of the shared helper on its VM; Actions workflows and other non-helper consumers are not automatically protected. RIDP-02 must re-verify current paths and actual coverage before implementation.

## Original measurement proposals

The source brief proposes API calls per task, API calls per accepted effect, cache hit ratio, conditional hit ratio, request deduplication, read amplification, context reuse, API wait time, event freshness, fan-out, conflict rate and integration efficiency.

It also proposes two experimental indicators:

- Validated Outcome per API Cost (VOAC)
- Context Reuse Efficiency (CRE)

These are not adopted as merge gates or standalone quality scores. The existing ATES quality-first contract remains authoritative.

## Source boundaries and subsequent refinement

The original brief proposes event sources including push, pull_request, pull_request_review, check_suite, check_run, workflow_run, issues and issue_comment; event-driven updates with bounded adaptive reconciliation; API resource bucket separation; a possible GitHub App topology; branch-scoped leases and expected-SHA checks; background compaction; and controlled experiments.

This proposal preserves those directions while making explicit that GitHub internal Ref-CAS, pack storage and atomic commit services are architectural inspiration, not assumed public APIs. GitHub App creation/installation and credential provisioning are owner-controlled, not completed. New queues, databases and hosted observability are not Phase A prerequisites. Existing proposal, cadence, quota, repo-tracking, dispatch-tree, CRG and SHE/ATES ownership remains in force. T.A.K. is a downstream domain lens, not the general-purpose evidence schema.

## Repository evidence reviewed for this proposal

- docs/ops/RATE-LIMIT-2026-10-29.md
- docs/ops/AGENT-TEAM-ORCHESTRATION.md
- docs/architecture/AGENT-TEAM-CONTROL-PLANE.md
- docs/ops/AGENT-TEAM-ROSTER.md
- docs/ops/AGENT-THROUGHPUT-METRICS.md
- docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md
- docs/ops/REPO-TRACKING.md
- docs/ops/DISPATCH-TREE-FEED.md
- docs/proposals/PROCESS.md

This list is a review inventory, not proof that every integration is implemented or operationally complete.
