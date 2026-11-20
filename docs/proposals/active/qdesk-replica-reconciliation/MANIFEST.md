---
id: qdesk-replica-reconciliation
title: "QDesk — Replica, refTemplates/smods, governance, release and DoE reconciliation"
author: ChatGPT
posted_at: 2026-11-19
source: source.md
status: draft
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: []
related_branches:
  - docs/qdesk-replica-reconciliation
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — qdesk-replica-reconciliation

## Summary

Reconcile the native GitHub Replica prototyping workflow and the monorepo's pinned `refTemplates/smods/` references into a QDesk control-plane design. Preserve the existing Contribution Desk, Admin Graph, versioning, proposal, integration, ICM, DoE, ATES and dependency-phase authorities. Define a read-only QDesk projection, a Browser Quarantine Clerk proposal/access-risk model, preview-to-production release evidence, and a pre-registered automation comparison plan. This proposal is design-first; it does not authorize production permission changes, external publishing, recursive submodule initialization, or a new scheduler/registry.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| ChatGPT | author+executor | executing | 2026-11-19 | Live repository and source recon; design-only branch |
| timerloggedout-spec | operator-authorizer | requested | 2026-11-19 | Confirm naming and scope through proposal review |

## Review log

### 2026-11-19 — ChatGPT

- Disposition: draft submitted
- Notes: Verified Replica README/setup, current desk/admin-graph/versioning surfaces, refTemplates reference-input contract, DoE family/taxonomy, experiment schema and proposal/dependency authority. See source.md and ITEMS.md. Current preview-manifest completeness and exact submodule gitlink SHAs remain implementation-time verification items.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before implementation merges
- [ ] PRs cite `Implements: QDESK-001` through applicable item IDs
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
