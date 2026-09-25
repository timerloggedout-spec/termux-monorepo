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
related_prs: [248, 252, 253, 254, 257, 717, 774, 828]
related_branches:
  - master
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — gantt-dependency-phases

## Summary

Implement a repository-native dependency-phase system that derives lifecycle state from a versioned phase plan, GitHub Project items, pull-request/check evidence, explicit approval records, and idempotent claims. Mermaid and Markdown reports are derived inspection views; they do not control dispatch or completion.

**Live entry:** [`docs/agentic/README.md`](../../../agentic/README.md)
**Canonical plan:** [`docs/agentic/dependency-phases.json`](../../../agentic/dependency-phases.json)
**Generated status:** [`docs/agentic/DEPENDENCY_PHASES.md`](../../../agentic/DEPENDENCY_PHASES.md)
**Primary Collaborator entry:** [`CLAUDE.md`](../../../../CLAUDE.md) (root `AGENTS.md` is deprecated)

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-18 | Authorized full implementation after evaluation clarified that a Mermaid view is illustrative only. |
| Manus AI | executor | executing | 2026-08-19 | Deployed the lifecycle system and its live-reconciliation hardening on the governing `master` branch. |

## Review log

### 2026-08-18 — Manus AI

- Disposition: accepted
- Notes: The live project is user-owned Project #1 (`PVT_kwHODennMc4BfLt5`), with `Todo`, `In progress`, and `Done` status options. The implementation resolves this metadata from the canonical plan and provides dry-run-default synchronization.

### 2026-08-18 — Manus AI

- Disposition: in_review
- Notes: The full implementation passed gates with lifecycle/adapter unit tests. Live dry-run identified Project mapping. Operator-token chain required for Project writes (Projects scope). PR #248 opened against `master-staging` at the time.

### 2026-08-19 — Manus AI

- Disposition: executing
- Notes: PR #248 merged the canonical lifecycle engine and four master-governed workflows. Follow-ups #252–#257 hardened retries, REST evidence, issue creation, and Operator credential selection for ProjectV2 writes.
- Evidence: Applied reconciliation run 32220381734 reconciled phase issues into Project #1.
- Governance: No phase marked complete solely from Project status; no approval inference; no automatic proposal close.

### 2026-09-23 — Grok (Administrator)

- Disposition: executing (partial terminal)
- Notes: Derived Gantt / dependency-waves via #717; post-merge adaptive-wait #774. Generated status: DPH-000 **complete**, DPH-100 **ready**.

### 2026-09-25 — Grok (Administrator)

- Disposition: docs upgrade (PR #828)
- Notes: Evidence-led consolidation of stale design/ITEMS/backlog. Collaborator naming (Role / Name / Moniker); `AGENTS.md` deprecated redirect affirmed. #184: Projects access long present on Operator classic PATs (names-only inventory); not a capability gap — wire intended secret for apply.
- Explicit: no runtime mutation; no auto-close; no secret values in tree or issues.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Code and workflow review completed
- [x] PR #248 opened with item references
- [x] Gates green on merge
- [x] Core engine + workflows on master
- [ ] DPH-100 claimed/applied under Operator Project write credential (when ready; dry-run first)
- [ ] Closed + moved to `closed/` when all terminal items complete

## Links

- ITEMS: ./ITEMS.md
- Live system: ../../../agentic/README.md
- Design (historical): ../../../GANTT_DEPENDENCY_PHASES_ACTIONS_DESIGN.md
- Credentials (names-only): issue #184
