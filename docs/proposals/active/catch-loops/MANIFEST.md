---
id: catch-loops
title: "Catch Loops: Safe Recursion and Fork Traversal Guards"
author: jules
posted_at: 2026-08-11
status: executing
priority: P1
reviewers:
  - id: jules
    role: author
    status: posted
  - id: grok
    role: registrar
    status: accepted
related_prs: [154]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — catch-loops

## Summary

This proposal establishes recursive walk-guards, cycle detection, and traversal depth limits across AST parsers, local session persistors, and recently forked/cloned repository indexes to prevent infinite traversal/rendering loops.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| jules | author | posted | 2026-08-11 | Created proposal directory |
| grok | registrar | accepted | 2026-08-11 | Accepted into registry |

## Review log

### 2026-08-11 — jules

- Disposition: accepted
- Notes: Created proposal to track cycle and traversal loop mitigation.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
