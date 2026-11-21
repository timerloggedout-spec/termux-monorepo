---
id: archwiz-data-flow-manifest
title: "ArchWiz local data-flow manifest provenance and snapshot repair"
author: ChatGPT
posted_at: 2026-11-21
source: source.md
status: executing
priority: P1
reviewers:
  - timerloggedout-spec
  - ChatGPT
related_prs: []
related_branches:
  - fix/archwiz-data-flow-manifest-provenance
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — archwiz-data-flow-manifest

## Summary

Repair the legacy ArchWiz local data-flow snapshot pipeline so its scanner and manifest builder accept explicit paths, publish to the checkout-relative tracked manifest, attach verifiable source and input provenance, quantify coverage, and label lexical references as candidate mentions rather than verified writers.

## Authority

The operator explicitly directed continuation of the ArchWiz snapshot-pipeline repair after merging the architecture audit. This proposal records that execution scope and the associated acceptance evidence.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-21 | Explicit continuation and implementation authorization in this conversation |
| ChatGPT | author+executor | executing | 2026-11-21 | Implementation and validation |

## Review log

### 2026-11-21 — timerloggedout-spec

- Disposition: accepted
- Notes: Continue the identified ArchWiz local snapshot-pipeline repair.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Non-author operator authorization recorded
- [ ] Required implementation review recorded
- [ ] PR cites `Implements: ARCH-SNAPSHOT-001`
- [ ] Repository gate and Termux smoke green on the same head
- [ ] Local Termux snapshot regeneration and metadata verified when source inputs are available
- [ ] Close proposal after all items reach terminal state

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Design: ../../superpowers/specs/2026-11-21-archwiz-data-flow-manifest-design.md
- Plan: ../../superpowers/plans/2026-11-21-archwiz-data-flow-manifest.md
