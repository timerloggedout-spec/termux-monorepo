---
id: qdesk-replica-reconciliation
title: "QDesk visual extension — Replica, Clerk, release and DoE integration"
author: ChatGPT
posted_at: 2026-11-19
source: source.md
status: draft
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [5145, 5197, 5199, 5330, 5376, 5622]
related_branches:
  - docs/qdesk-replica-reconciliation
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — qdesk-replica-reconciliation

## Summary

Extend the existing QDesk/QUE architecture with a Replica-informed visual workspace, guided issue-filing portal, user-selectable model-provider path, Browser Quarantine Clerk proposal/access-risk view, and stronger release-preview evidence. Reuse the current Contribution Desk, Admin Graph, versioning, QDesk portfolio/DoE RFP, admission/claim authorities and model routers. The 11-step sequence covers overlap reconciliation, accepted scope, source/provider contracts, Gantt integration, issue filing, quota isolation, Clerk/release comparison, DoE, vertical-slice implementation, exact-SHA validation and version selection/retirement. The initial visual shell remains read-only; issue submission and model-provider wiring require separate authenticated and security-reviewed adapters.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| ChatGPT | author+executor | executing | 2026-11-19 | Live repository and source recon; design-only branch |
| timerloggedout-spec | operator-authorizer | requested | 2026-11-19 | Confirm naming and scope through proposal review |

## Existing QDesk lineage

Related active work: PR #5145 (Observatory + Delphi + DoE pipeline), #5197 (portfolio decision/report contract), #5199 (deadline desk and freshness), #5330/#5376 (admission and provider-execution boundaries), and #5622 (QUE ranking/claim pipeline). This proposal owns only the Replica-informed visual extension, Clerk presentation and release-preview comparison integration.

## Review log

### 2026-11-19 — ChatGPT

- Disposition: draft submitted
- Notes: Verified Replica README/setup, current desk/admin-graph/versioning surfaces, refTemplates reference-input contract, DoE family/taxonomy, experiment schema and proposal/dependency authority. See source.md and ITEMS.md. Current preview-manifest completeness and exact submodule gitlink SHAs remain implementation-time verification items.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before implementation merges
- [ ] PRs cite `Implements: QDESK-001` through `QDESK-011` as applicable
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
