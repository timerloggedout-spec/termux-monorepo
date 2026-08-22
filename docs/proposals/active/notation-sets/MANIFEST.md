---
id: notation-sets-evolution
title: "Notation Sets, Living Lexicon, and Cross-Domain Semantic Index"
author: ChatGPT
posted_at: 2026-08-22
source: source.md
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues: [320, 309, 182, 175]
related_prs: []
related_branches:
  - docs/notation-sets-evolution
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — notation-sets-evolution

## Summary

Establish #320 as the proposal/specification layer for a canonical, continuously evolving notation vocabulary supporting #309 Grimoire compression and its related semantic/indexing work. The proposal separates canonical notation from domain aliases and domain-specific syntax, connects the vocabulary to the repository's existing pointer/concept/tool/context indexes, and defines a research-driven evolution loop so the glossary/dictionary remains synchronized with implementation and operator governance.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | 2026-08-22 | Operator review requested before execution |
| ChatGPT | author | posted | 2026-08-22 | Proposal authored from #320 and repository structure |

## Review log

### 2026-08-22 — ChatGPT

- Disposition: posted
- Notes: Proposal connects #320 notation work to #309/#182 and #175's operational gates without claiming implementation is complete.

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
- Source: ./source.md
- Issue #320: https://github.com/timerloggedout-spec/termux-monorepo/issues/320
- Issue #309: https://github.com/timerloggedout-spec/termux-monorepo/issues/309
- Issue #182: https://github.com/timerloggedout-spec/termux-monorepo/issues/182
- Operator gate #175: https://github.com/timerloggedout-spec/termux-monorepo/issues/175
