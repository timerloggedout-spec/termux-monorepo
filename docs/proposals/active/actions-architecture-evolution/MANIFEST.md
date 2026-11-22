---
id: actions-architecture-evolution
title: "Actions architecture evolution — typed automation registry, DoE evidence, BRR provenance, and Tribute feed"
author: ChatGPT
posted_at: 2026-11-22
source: "../../superpowers/specs/2026-11-22-actions-architecture-evolution.md"
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: []
related_prs: []
related_branches:
  - docs/actions-architecture-evolution-20261122
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — actions-architecture-evolution

## Summary

Unify the classification and lifecycle model for workflows, reusable workflows, composite actions, skills, AppID identities, modularization epochs, DoE observations, and BRR/QUE receipts. Deliver a read-only Tribute display-feed MVP over the existing generated-feed contract. Repo-Story remains a future candidate.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-22 | A+B+C scope and Repo-Story future-candidate boundary confirmed |
| ChatGPT | author+executor | executing | 2026-11-22 | Design baseline and proposal itemization |

## Review log

### 2026-11-22 — timerloggedout-spec

- Disposition: accepted
- Notes: A+B+C; Repo-Story noted as potential future C; style-led display-feed MVP requested.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ../../superpowers/specs/2026-11-22-actions-architecture-evolution.md
