# QDesk Parallel Operations Console — Implementation Plan

> Execute this plan task-by-task with test-driven development. Independent deliverables are grouped so separate implementation lanes can work without changing the same files.

**Goal:** Build a parallel, read-only QDesk operator console that makes QUE work priority, worker evidence, routing, waits/escalations, intake quarantine, quota/Wagertome provenance, and GitHub Projects planning visible without creating another operational authority.

**Architecture:** A static Tribute page with a pure browser/Node projection module. It consumes existing public JSON feeds, marks missing/stale/conflicting evidence explicitly, and provides only local proposal/preview interactions. All queue admission, claims, execution, quota, allocation, project writes, and completion remain with existing authorities.

**Tech Stack:** Existing Tribute HTML/CSS, vanilla JavaScript, Node built-in test runner, Python pytest static-contract test.

**Spec:** GitHub issue #5432 and proposal on branch qdesk/queue-operations-proposal-20261114.

## Global Constraints
- QUE owns admission, ranking, claims, leases, execution and throttle policy.
- QDesk is a derived, read-only projection; no second scheduler, ranker, worker registry, quota ledger, wagering wallet, project store or failure engine.
- que-task-rank/v1 is the ranking method of record; feed currently labels claim order advisory.
- E0 simulation must never count as observed execution, progress, verification or completion.
- Unknown is not zero; missing or stale sources are visible.
- docs/agentic/dependency-phases.json remains canonical; dashboard Gantt is derived.
- Wagertome book and quota allocations are separate authorities; no wagering or money movement.
- GitHub Projects integration is read-only; no browser token or credential.
- No merge, production dispatch, workflow dispatch, deployment, secret, billing or account mutation.

## Review Focus
- Queue summary counts disagree with active-claim row count: show integrity warning; never silently reconcile.
- Dispatch-state source is much older than the QUE feed: freshness is per-source.
- Rank summary provides issue IDs but no per-item score/rationale in current claim rows: do not fabricate factors.
- A claimed owner is not an observed worker; require execution run/session and heartbeat evidence.
- Wagertome book is old and observational; quota consumption coverage is explicitly unpublished.

## File map
- Create apps/tribute-dashboard/qdesk.html: operator cockpit and semantic sections.
- Create apps/tribute-dashboard/qdesk.css: page-local responsive styling, reduced motion.
- Create apps/tribute-dashboard/qdesk.js: pure normalization/validation plus safe DOM rendering and read-only fetches.
- Create tests/qdesk.test.cjs: Node built-in unit tests for evidence/freshness/reconciliation/priority/intake/dependencies.
- Create tests/test_qdesk_dashboard.py: Python static contract tests for page wiring and authority boundaries.
- Create docs/superpowers/plans/2026-11-14-qdesk-parallel-console.md: this plan.

## Task 1 — Evidence and source projection
Files: apps/tribute-dashboard/qdesk.js, tests/qdesk.test.cjs
Interfaces:
- freshness(source, now, maxAgeMs?) -> {state, ageMs, reason}
- evidenceLevel(record, now, heartbeatMaxAgeMs?) -> {level, label, canCountAsActive, canCountAsComplete}
- reconcileClaims(summary, rows) -> {summaryCount, rowCount, delta, consistent}
- priorityProjection(feed) -> {method, advisory, claimOrder, deltaVsAge, rows, limitations}
- workerProjection(claims, executionReceipts) -> {workers, observedExecuting, claimedUnverified}
- dependencyProjection(plan) -> {phases, cycles, valid}
Steps: write Node tests; run them RED; implement pure projections; run GREEN; commit.

## Task 2 — QDesk static operator cockpit
Files: apps/tribute-dashboard/qdesk.html, apps/tribute-dashboard/qdesk.css, apps/tribute-dashboard/qdesk.js
Steps: add static-contract tests and verify RED; build Overview, Priority, Workers, Routing, Waiting/Escalations, Throttle, Wagertome, AgenticGantt, GitHub Projects and Sources panels; load existing public feeds only; render rank-only IDs separately from claim rows; preserve null rank/score; safely render untrusted text; run tests.

## Task 3 — QDesk → QUE intake and override proposal controls
Files: apps/tribute-dashboard/qdesk.js, tests/qdesk.test.cjs, apps/tribute-dashboard/qdesk.html
Steps: test ALLOW/HOLD/REJECT/ESCALATE, invalid URLs, credential-like content, high-risk side effects and incomplete criteria; test proposal-only override packet; implement local preflight; add override preview with reason/rationale/scope/expiry; no network or dispatch; run tests.

## Task 4 — Planning and resource integrations
Files: apps/tribute-dashboard/qdesk.js, apps/tribute-dashboard/qdesk.html, apps/tribute-dashboard/qdesk.css
Steps: test stale/unknown quota and Wagertome provenance; display quota freshness/coverage, canonical allocation source link, book subjects/positions/settlements and explicit freshness; render canonical dependency phases and Project #1 metadata as read-only links; preserve approval requirements; show missing live ProjectV2 feed as a coverage gap; run tests.

## Task 5 — Review and delivery
Review changes against issue #5432; run node --test tests/qdesk.test.cjs and pytest -q tests/test_qdesk_dashboard.py; verify no credential, dispatch, queue, quota, allocation, Project write or simulation-to-completion path; commit/push small coherent commits; do not merge or deploy.