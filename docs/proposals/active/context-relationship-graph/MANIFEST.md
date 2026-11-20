---
id: context-relationship-graph
title: "GitHub-native context relationship graph and scope index"
author: Manus
posted_at: 2026-08-18
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus
    role: author-executor
    status: executing
related_prs: [232]
related_branches: [manus/context-relationship-graph]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Context Relationship Graph

## Summary

Build a repository-native, evidence-backed relationship graph that starts with a deterministic schema compiler and sparse matrix. It will unify safe, normalized metadata about source files and symbols with GitHub pull requests, issues, labels, comments, commits, and explicit references. The resulting index will support bounded timeline search and optional Mermaid export while deliberately excluding session stores, browser profiles, tokens, and full discussion bodies.

## Scope and Boundary

The work extends the existing local context graph rather than treating it as authoritative. It must not preserve the existing home-directory-wide scan, session extraction, browser data, or `thinking_content` as index inputs. The new index is repository-rooted, metadata-only by default, and records source URLs and relationship provenance for every asserted edge.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| `timerloggedout-spec` | Operator authorizer | accepted | 2026-08-18 | Authorized full implementation after branch-aware reconnaissance. |
| `Manus` | Author and executor | executing | 2026-08-18 | Implements the scoped items on a `master-staging`-based feature branch. |

## Review Log

### 2026-08-18 — timerloggedout-spec

- Disposition: accepted
- Notes: Authorized the full implementation and required branch-aware reconnaissance rather than relying on a stale ICM item ledger.

### 2026-08-18 — Manus

- Disposition: accepted
- Notes: Reconciliation confirmed PR #232 was merged into `master` and is present in the current `master-staging` spine. The previous ICM-07 deferral is therefore historical context, not a block on this successor implementation.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Status is `executing`
- [ ] Commits and pull request cite `Implements: CRG-<id>`
- [ ] Required gates pass or inherited baseline failures are recorded
- [ ] Items are terminal and proposal is closed when implementation is accepted

## Links

- ITEMS: [./ITEMS.md](./ITEMS.md)
- Source: [./source.md](./source.md)
- ICM navigation surface: [../../icm/objects/knowledge/navigation-and-indexes.md](../../icm/objects/knowledge/navigation-and-indexes.md)
