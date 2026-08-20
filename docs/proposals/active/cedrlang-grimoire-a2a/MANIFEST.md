---
id: cedrlang-grimoire-a2a
title: "CEDRlang deterministic codec, Grimoire boundary, and local A2A envelope foundation"
author: Manus AI
posted_at: 2026-08-20
source: source.md
status: draft
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [126, 154, 177, 196, 208, 218, 228]
related_issues: [117, 175, 274]
related_branches: [feature/cedrlang-grimoire-a2a]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — CEDRlang / Grimoire / A2A

## Summary

This proposal reconstructs the useful, independently testable core of the Linguist PR family in a clean scope. It introduces a deterministic, non-executing CEDRlang canonical record and symbolic codec with a synthetic public test mapper, unambiguous reverse mapping, coverage reporting, integrity verification, and local Agent2Agent envelope validation. It explicitly separates the codec from CEDARscript execution and CID pointer registration, does not publish obfuscated comments, does not call external install scripts, and does not commit any private mapping material. The proposal responds to the current review findings for [#126](https://github.com/timerloggedout-spec/termux-monorepo/pull/126), [#154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154), and [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177), while preserving only their unique safe value.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| Manus AI | author / executor | posted | 2026-08-20 | Bounded implementation branch; no integration or external workflow write. |
| timerloggedout-spec | operator-authorizer | requested | 2026-08-20 | Formal proposal acceptance is required before an integration claim or merge. |

## Review log

### 2026-08-20 — Manus AI

- Disposition: commented
- Notes: Read-only reconnaissance found seven pull requests with `Linguist` in the title and no matching issue titles. The active open PRs #154 and #177 are both dirty; the owner-directed disposition for #154 is to reconstruct unique value in a small rebased hygiene-passed diff. The private/lossless-mapper claim is not currently implemented by the tracked regex tables or tracked pointer files. See `docs/reviews/linguist-177/` for the metadata-only evidence record and inventory.

### 2026-08-20 — Manus AI publication update

- Disposition: changes_requested
- Notes: Published the review packet and required follow-up work as [issue #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274); cross-linked the evidence to issues [#117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117) and [#175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175), and to open PRs [#154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154) and [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177). No acceptance, merge, or private-mapper decision is implied. `RESEARCH.md` contains the pending decision/vote questions.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml` on this feature branch
- [x] ITEMS.md itemized before implementation
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: LGA-01` or the applicable work-item ID
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Evidence: `../../../reviews/linguist-177/`
- Related A2A proposal: [Issue #117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117)
- Publication and subtask tracker: [Issue #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274)
- Operator priority/gate record: [Issue #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)
- Research and decision requests: ./RESEARCH.md
