---
id: hackathon-desk
title: "Hackathon Desk — teammate collaboration portal, guide, and accessibility"
author: ChatGPT
posted_at: 2026-11-24
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs:
  - 5840
related_branches:
  - feat/hackathon-desk-full-20261124
gates_required: [proposal-lifecycle, repo-gate]
---

# MANIFEST — hackathon-desk

## Summary

Build a teammate-facing Hackathon Desk inside the existing Tribute dashboard. The desk connects current opportunities, challenge records, hackathons, teammates, proposal intake, GitHub contribution workflows, and pipeline evidence into one accessible read-only projection. GitHub remains the identity and write-authority provider; contribution actions navigate to GitHub, where GitHub authenticates the teammate and enforces repository permissions.

## Scope

- Responsive Hackathon Desk integrated into Tribute navigation and sitemap.
- Opportunities and challenges backed by the QUE priority feed and challenge coordinator.
- Hackathon event/deadline display using the existing countdown projection.
- Teammate onboarding and contribution guidance with GitHub-owned identity and permission enforcement.
- Proposal intake/navigation that reuses the existing proposal lifecycle.
- Pipeline visibility sourced from existing desk, dispatch, and QUE feeds.
- Standalone teammate guide and accessibility guide.
- WCAG 2.2 AA-oriented implementation and verification.
- ICM route proposal through the existing Challenge and Certifications Program object and governed ICM maintenance pipeline.

## Authority and boundaries

- ops/que/feeds/opportunity-priority.json owns ranked opportunity state and freshness.
- ops/challenge/coordinator.json owns challenge event, participant, and gate state.
- apps/tribute-dashboard/data/challenge-countdowns-feed.json owns the published countdown instants/prize projection.
- Desk feed supplies traversal/status evidence; deprecated priority-timebox data is excluded from opportunity ranking.
- Public teammate UI excludes metrics_internal, win_probability, internal admin feeds, credentials, and private operational metrics.
- The public portal is a read-only projection. GitHub Issues, Pull Requests, and repository pages enforce identity and write permissions.
- Discord contact details remain optional and unpublished until teammate opt-in. A Discord handle is a contact reference, not a GitHub identity.
- Existing challenge, proposal, QUE, and dispatch systems remain authoritative. The Desk adds no parallel scheduler, state store, dispatch engine, or permission model.
- ICM map edits remain behind the human review checkpoint in docs/icm/maintenance/02_design/.

## Operator decisions recorded

- Access model: GitHub-authenticated contribution flow.
- Scope: full Desk, teammate guide, and accessibility.
- Architecture call: static Tribute page; GitHub authenticates contribution actions at the destination. Custom OAuth/backend is outside this proposal.

## Review log

### 2026-11-24 — timerloggedout-spec

- Disposition: accepted
- Notes: Explicit chat instruction authorized proposal registration, ICM routing, and full-scope implementation; access=github; scope=full.

## Checklist

- [x] Registered in docs/proposals/registry.yaml
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [ ] ICM map-change proposal reviewed through the ICM human checkpoint
- [ ] Implementation plan reviewed
- [ ] Focused tests and accessibility checks pass
- [ ] Repository gate, focused tests, and accessibility checks pass on the same head
- [x] Termux device/session execution is recorded as NOT PERFORMED — OFFLINE; any Ubuntu-hosted `agentic termux smoke` result is recorded separately as Linux CI only
- [ ] Required PR checks complete and head SHA re-fetched
- [ ] Deployment freshness and live route verified
- [ ] All items terminal and proposal closed through the lifecycle
