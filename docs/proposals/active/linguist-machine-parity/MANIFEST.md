---
id: linguist-machine-parity
title: "Linguist README machine-parity enhancement"
author: Manus AI
posted_at: 2026-08-20
source: source.md
status: posted
priority: P2
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus AI
    role: registrar
    status: posted
related_prs: []
related_branches: []
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Linguist README machine-parity enhancement

## Summary

This is a deliberately separate documentation and development lane for a **Linguist machine-parity enhancement** to the root README. It may investigate byte-efficient, machine-readable documentation representations and any associated badge design only after a scoped proposal, compatibility boundary, and validation plan are accepted. It does not modify the DeepWiki badge, repository-surface reconciler, provider credentials, or the current README repair under `AR-12`.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| `timerloggedout-spec` | operator-authorizer | accepted | 2026-08-20 | Explicitly directed that this work remain a separate scope and development lane. |
| `Manus AI` | registrar | posted | 2026-08-20 | Registered only; no implementation is authorized by this placeholder. |

## Review log

### 2026-08-20 — Manus AI

- Disposition: accepted as a **separate scope placeholder**
- Notes: `AR-12` may add the ordinary DeepWiki badge and correct Wiki-discovery documentation. It must not introduce Linguist-specific compression, machine-parity behavior, or a related badge enhancement.

## Checklist (process)

- [ ] Proposal-specific requirements and compatibility boundaries are recorded.
- [ ] `LMP-01` is accepted before implementation begins.
- [ ] Any README representation is readable without a private pointer registry.
- [ ] PRs cite `Implements: LMP-01`.
- [ ] Repository gate and Termux smoke checks are green on merge.
- [ ] Proposal is closed or advanced only after a separate review.

## Links

- ITEMS: [ITEMS.md](ITEMS.md)
- Source: [source.md](source.md)
- Excluded current lane: [`AR-12`](../actions-refinements/ITEMS.md)
