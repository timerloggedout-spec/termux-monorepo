---
id: pit-crew-doe-oversight
title: "Pit Crew whole architecture, analogy mappings and DoE oversight tournaments"
author: ChatGPT
posted_at: 2026-11-16
source: source.md
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: [5529, 5503]
related_branches:
  - docs/pit-crew-doe-oversight
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — pit-crew-doe-oversight

## Summary

Define Pit Crew as a role-specialized bounded execution-team architecture that composes the existing Brain, Ballet, QUE/QDesk, dependency-phase engine, specialist router, execution adapters, evidence substrate, DoE Family, ATES and MoneyBall/3L0. DoE is the independent oversight authority for experiment design, assignment, measurement validity, stopping, analysis and recommendation; it is not a production dispatch or promotion authority. This proposal extends, rather than duplicates, the Ballet Coordinator work in PR #5529 and the Brain architecture in #5501/#5503.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| ChatGPT | author + implementation | executing | 2026-11-16 | Documentation architecture and tournament contracts |
| timerloggedout-spec | operator-authorizer | requested | 2026-11-16 | Independent scope and authority review |

## Review log

### 2026-11-16 — ChatGPT

- Disposition: posted
- Notes: Initial architecture, analogy-to-architecture mappings, role boundaries, DoE oversight protocol, tournament illustration and integration map added on an isolated branch. No runtime dispatch, production policy, schema authority or promotion behavior changed.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before any execution work beyond this documentation/design slice
- [ ] PRs cite `Implements: PCDOE-001`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- Architecture: `docs/ops/PIT-CREW-ARCHITECTURE.md`
- DoE tournaments: `docs/ops/PIT-CREW-DOE-TOURNAMENTS.md`
- Diagram: `docs/architecture/PIT-CREW-DOE-OVERSIGHT.mmd`
- Related Ballet RFP: `https://github.com/timerloggedout-spec/termux-monorepo/blob/feat/ballet-coordinator-doe-rfp/docs/ops/BALLET-COORDINATOR-RFP.md`
- Related Brain RFP: `https://github.com/timerloggedout-spec/termux-monorepo/issues/5501`
