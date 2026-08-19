---
id: actions-refinements
title: "Issue #192 action-integration refinements"
author: Manus AI
posted_at: 2026-08-19
status: accepted
priority: P1
reviewers:
  - id: user
    role: operator+approver
    status: accepted
  - id: Manus AI
    role: executor
    status: executing
related_issues: [192, 175]
related_prs: [193, 81, 92, 143, 72, 232]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — actions-refinements

## Summary

This proposal turns Issue #192’s starter list of GitHub Actions into a constrained implementation backlog. It does not add marketplace actions or modify runtime workflows yet. The current `master-staging` baseline contains unresolved conflict markers in `scripts/ci/repo_gate.py`, `gemini-dispatch.yml`, and `gemini-review.yml`; the related live pull requests are either merged, target `master`, are conflicted, or carry unrelated scopes. The first execution work must therefore restore a valid baseline and obtain acceptance for a smallest-scope batch before any workflow integration.

## Evidence and Scope

Issue #192 is open and has one verified GitHub-native cross-reference to merged PR #193. The Issue #192 timeline also cross-references Issue #175, whose operator matrix names the workflow quota-gate PR #81 and repository gates as current operational concerns. PR #193 and PR #232 are merged, so neither can be extended. PRs #81, #143, and #72 are open but conflicted; #81 and #143 also target `master`, contrary to the repository integration rule. PR #92 is workflow-security work targeting `master` and is not an unreviewed carrier for functional additions.

> No execution claim is made by this manifest. Marketplace-action adoption, workflow schema changes, and repository settings remain explicitly deferred until the baseline-repair item is accepted and its gates are green.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| user | operator+approver | accepted | 2026-08-19 | Directed continuation of the batched Issue #192 implementation with the action-research ledger as the governing focus. |
| Manus AI | author+executor | executing | 2026-08-19 | Created the evidence record and now implements the accepted, bounded AR-01 prerequisite. |

## Review Log

### 2026-08-19 — Manus AI
- Disposition: **posted**
- Evidence: Issue #192; its native timeline cross-reference to PR #193; Issue #175; PRs #81, #92, #143, #193, #232, and #72; and the checked `master-staging` workflow surface.
- Findings: Existing PR reuse is not safe. A dedicated branch from `master-staging` is the correct future vehicle once the P1 items below are accepted.
- Safety: Do not use mutable action tags in new workflow code. Do not add secret-writing, direct-push, or autonomous-PR functionality without a narrowly defined threat model and explicit permissions review.

### 2026-08-19 — user / Manus AI
- Disposition: **accepted for bounded execution**
- Evidence: The Operator directed continuation of the batched implementation and reaffirmed that the Issue #192 action-research ledger, rather than any one reference adapter, is the governing focus.
- Scope: Begin with AR-01 only: resolve the documented syntax-affecting conflict markers on a dedicated `master-staging` branch, preserve existing interfaces and least privilege, and validate before considering any marketplace-action addition.
- Safety: AR-02 through AR-07 retain their existing item boundaries. No secret-writing, direct-push, autonomous-PR, or issue-body-to-shell behavior is authorized by this acceptance.


## Checklist

- [x] Registered in `docs/proposals/registry.yaml`.
- [x] Items are recorded in `ITEMS.md`.
- [x] Source and relationship evidence are recorded in `source.md`.
- [x] Operator acceptance is recorded for bounded execution.
- [x] Status changed to `accepted` before workflow implementation.
- [ ] An implementation PR cites `Implements: AR-01`.
- [ ] `repo-gate` and `termux-smoke` pass for any implementation revision.
- [ ] The proposal is closed after every item reaches a terminal state.

## Links

- [Issue #192](https://github.com/timerloggedout-spec/termux-monorepo/issues/192)
- [Issue #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)
- [ITEMS](ITEMS.md)
- [Extended action research notes](action-research-notes.md)
- [Action decision ledger and autonomous implementation sequence](ACTION-DECISION-LEDGER.md)
- [Source and relationship evidence](source.md)
- [Repository proposal process](../../PROCESS.md)
- [Repository gate requirements](../../../ARCHW1Z-GATE.md)
- [Agent permissions](../../AGENTIC-PERMISSIONS.md)
