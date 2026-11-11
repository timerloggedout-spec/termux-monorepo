---
id: linguist-machine-parity
title: "Linguist README machine-parity enhancement"
author: Manus AI
posted_at: 2026-08-20
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus AI
    role: registrar
    status: posted
related_prs:
  - 5188
related_branches:
  - docs/linguist-readme-evolution-20261111
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Linguist README machine-parity enhancement

## Summary

This is a separately scoped documentation and development lane for **Linguist-guided README evolution**. LMP-01 now implements comparative branch/version measurements, a deterministic report-only change-budget planner, explicit links to canonical mapping authorities, and reviewable README visuals. It does not modify the DeepWiki badge, repository-surface reconciler, provider credentials, or the separate README repair under AR-12.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| `timerloggedout-spec` | operator-authorizer | accepted | 2026-08-20 | Explicitly directed that this work remain a separate scope and development lane. |
| `Manus AI` | registrar | posted | 2026-08-20 | Registered only; historical registration note; superseded by the separately authorized LMP-01 execution recorded on 2026-11-11. |

## Review log

### 2026-08-20 — Manus AI

- Disposition: accepted as a **separate scope placeholder**
- Notes: `AR-12` may add the ordinary DeepWiki badge and correct Wiki-discovery documentation. It must not introduce Linguist-specific compression, machine-parity behavior, or a related badge enhancement.

## Checklist (process)

- [x] Proposal-specific requirements and compatibility boundaries are recorded.
- [x] `LMP-01` separately accepted by operator direction on 2026-11-11.
- [x] README representation remains readable without a private pointer registry.
- [x] PR #5188 cites `Implements: LMP-01`.
- [ ] Repository gate and Termux smoke checks are green on merge.
- [ ] Proposal is closed or advanced only after a separate review.

## Links

- ITEMS: [ITEMS.md](ITEMS.md)
- Source: [source.md](source.md)
- Excluded current lane: [`AR-12`](../actions-refinements/ITEMS.md)


## Review log

### 2026-11-11 — Operator implementation direction

- Disposition: LMP-01 implementation authorized as a separately scoped README evolution lane.
- Scope: comparative README versioning, canonical Linguist mapping references, deterministic report-only change budgets, and README visual/navigation improvements.
- Boundary: no private pointer dependency, no random semantic rewrites, no unrelated web application rename, and no claim of deployment.
