---
id: gantt-dependency-phases
title: "Dependency-phase automation and GitHub Projects integration"
author: Manus AI
posted_at: 2026-08-18
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus AI
    role: executor
    status: executing
related_prs: []
related_branches:
  - manus/dependency-phase-automation
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — gantt-dependency-phases

## Summary

Implement a repository-native dependency-phase system that derives lifecycle state from a versioned phase plan, GitHub Project items, pull-request/check evidence, explicit approval records, and idempotent claims. Mermaid and Markdown reports are derived inspection views; they do not control dispatch or completion.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-18 | Authorized full implementation after evaluation clarified that a Mermaid view is illustrative only. |
| Manus AI | executor | executing | 2026-08-18 | Implements the full lifecycle system on `master-staging` integration spine. |

## Review log

### 2026-08-18 — Manus AI

- Disposition: accepted
- Notes: The live project is user-owned Project #1 (`PVT_kwHODennMc4BfLt5`), with `Todo`, `In progress`, and `Done` status options. The implementation resolves this metadata from the canonical plan and provides dry-run-default synchronization.

### 2026-08-18 — Manus AI

- Disposition: in_review
- Notes: The full implementation passed `repo_gate.py --base origin/master-staging` and `termux_smoke.py`, with seven lifecycle/adapter unit tests passing. The live dry-run identified the canonical Project mapping. Issue #246 (`DPH-000`) and issue #247 (`DPH-100`) were created during reconciliation attempts; the authenticated integration token can read but lacks permission to add items to the user-owned Project. `PROJECTS_TOKEN` with Projects write permission is therefore the remaining deployment configuration requirement.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [ ] Code and workflow review completed
- [ ] PR opened with item references
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
