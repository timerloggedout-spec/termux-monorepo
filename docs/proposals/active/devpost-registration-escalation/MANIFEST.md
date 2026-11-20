---
id: devpost-registration-escalation
title: "Devpost registration, escalation, and Wagering Book reconciliation"
author: ChatGPT
posted_at: 2026-11-20
source: source.md
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [5727, 5051, 5063]
related_branches:
  - feat/challenge-game-off-2026-intake
  - feat/unified-wager-event-projections
  - feat/devpost-registration-escalation-2026-11-20
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — devpost-registration-escalation

## Summary

Reconcile authenticated Devpost registrations, submission evidence, official eligibility and judging rules, deadline escalation timeboxes, and the public Wagering Book/countdown projections. Preserve source-of-record boundaries: Devpost owns registration/submission facts; the coordinator and event log own challenge state; desk-feed timeboxes are operational projections; Tracking register items remain the source for external calendar anchors.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | 2026-11-20 | Review scope, registration evidence, and promotion decision |
| ChatGPT | author+executor | executing | 2026-11-20 | Implementation and evidence collection |

## Review log

### 2026-11-20 — initial registration

- Disposition: posted
- Notes: Authenticated Devpost account list confirmed C12, C18, and C19 registrations. C12 Receipts Vault submission is published; C18/C19 have no linked project in the current project listing. Exact join instants were unavailable.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: DRE-001`
- [ ] repo-gate and termux-smoke green on the master-based PR
- [ ] Closed + moved to `closed/` when terminal

## Links

- Master-based PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/5727

- ITEMS: ./ITEMS.md
- Source: ./source.md
