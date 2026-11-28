---
id: PROPOSAL-ID
title: "Title"
author: NAME
posted_at: YYYY-MM-DD
source: source.md
status: draft
priority: P2
reviewers: []
related_prs: []
related_branches: []
gates_required: [repo-gate, termux-smoke]
---

Gate semantics: `repo-gate` is universal. `termux-smoke` is surface-conditional under `docs/ops/GATE-ADMISSION-MATRIX.md`; record `SKIPPED` with reason when the shared classifier marks the Termux surface inapplicable.

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
