---
id: qdesk-replica-reconciliation
title: "QDesk + Drafting Desk — Replica prototyping, project profiles, Clerk, release and DoE"
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

Extend the existing QDesk/QUE architecture with a separate Replica-powered Drafting Desk for profile-bound prototyping and alternate-version comparison, alongside the operational Contribution Desk; add the QDesk overview, guided issue-filing portal, user-selectable model-provider path, Browser Quarantine Clerk proposal/access-risk view, and stronger release-preview evidence. Project profiles remain monorepo-managed through the existing project-profile/v1 schema and the planned ARCHWIZ S2 registry/resolver. Replica consumes resolved project scope and produces versioned candidates; selection hands a reviewed draft to the existing issue form and QUE admission route. Reuse the current Admin Graph, versioning, QDesk portfolio/DoE RFP, admission/claim authorities and model routers. The 11-step sequence covers overlap reconciliation, source/profile verification before acceptance, two-desk/Gantt design, profile-aware filing, quota isolation, Clerk/release comparison, DoE, vertical-slice implementation, exact-SHA validation and version selection/retirement. Runtime issue submission and provider/model wiring require separate authenticated and security-reviewed adapters.

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
- Notes: Verified Replica README/setup, current desk/admin-graph/versioning surfaces, refTemplates reference-input contract, DoE family/taxonomy, experiment schema and proposal/dependency authority. See source.md and ITEMS.md. Current preview-manifest completeness remains an implementation-time verification item. Exact relevant submodule gitlink SHAs are an explicit pre-acceptance gate and must be recorded in step 2 before proposal acceptance in step 3.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Exact relevant smods gitlink SHAs recorded before acceptance
- [ ] Project-profile S2 registry/resolver dependency confirmed before Drafting Desk implementation
- [ ] Status → accepted before implementation merges
- [ ] PRs cite `Implements: QDESK-001` through `QDESK-013` as applicable
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
