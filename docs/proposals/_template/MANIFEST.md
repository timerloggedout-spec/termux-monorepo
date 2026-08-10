---
id: PROPOSAL-ID
title: "Title"
author: NAME
posted_at: YYYY-MM-DD
source: source.md
status: draft   # draft|posted|in_review|accepted|executing|blocked|closed
priority: P2    # P0|P1|P2|P3
reviewers: []
related_prs: []
related_branches: []
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — PROPOSAL-ID

## Summary

One paragraph intent.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| | author | posted | | |

## Review log

### YYYY-MM-DD — reviewer-id

- Disposition: accepted | changes_requested | commented
- Notes:

## Checklist (process)

- [ ] Registered in `docs/proposals/registry.yaml`
- [ ] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
