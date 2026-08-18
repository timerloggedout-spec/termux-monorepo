---
id: agent-team-formation
title: "Role-aware agent teams, scoring, and authorized analysis boundaries"
author: Manus AI
posted_at: 2026-08-18
source: source.md
status: draft
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: awaiting_review
  - id: Manus AI
    role: author
    status: posted
related_issues: [129, 236]
related_prs: [131]
related_branches: [docs/agent-team-formation-draft]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — agent-team-formation

## Summary

This draft establishes an initial **role-aware operating model** for the Termux multi-agent roster. It preserves the repository's existing MoneyBall concept while separating teams by verifiable work type rather than assigning every candidate one generic ELO value. The draft creates distinct charters for research, development, delivery reliability, game QA, authorized mobile-app analysis, and authorized security assurance. It also defines explicit safety and authorization controls for any reverse-engineering or red-team activity.

The proposal is deliberately **not accepted**. The repository requires a recorded review before an accepted proposal may drive execution, and the configured integration branch, `master-staging`, is not currently present on the remote. This change is therefore a documentation-only draft based on the available `master` branch, not an integration-ready implementation.

## Evidence and scope notes

The existing lane SSOT assigns MoneyBall and agent mail to the multi-agent orchestration lane and names issue #129 and PR #131 as the corresponding work stream. However, the live pull request metadata currently reports PR #131 as open and dirty. This proposal treats the roster implementation status as requiring reconciliation before it is extended. The newer APK investigation list, issue #236, establishes a need for a bounded, evidence-preserving analysis workflow but does not establish permission to bypass licensing, access controls, or game protections. See [source.md](./source.md) for the evidence log.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| Manus AI | Author | posted | 2026-08-18 | Prepared an evidence-led draft and initial item list. |
| timerloggedout-spec | Operator-authorizer | awaiting_review | — | Confirm role names, scope, and whether to promote the proposal. |
| Security reviewer | Independent reviewer | awaiting_assignment | — | Required before security/red-team automation is accepted. |

## Review log

### 2026-08-18 — Manus AI

- **Disposition:** draft posted for review.
- **Notes:** The team model uses role-specific scorecards plus a shared safety/reliability floor. Scores may inform task routing but may not autonomously authorize sensitive actions, remove protected roles, or assign mobile-app targets lacking documented authorization.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml` as a draft.
- [x] Added scoped work items in `ITEMS.md`.
- [x] Recorded the evidence and status discrepancy in `source.md`.
- [ ] Obtain an Operator review and an independent security review.
- [ ] Promote to `accepted` before implementing score, roster, or workflow changes.
- [ ] Reconcile the `master-staging` branch requirement before opening an integration PR.
- [ ] Cite `Implements: ATF-<ID>` on future implementation commits and PRs.
- [ ] Run `repo_gate.py` and `termux_smoke.py` before any merge.

## Links

- [Team charter](./TEAM_CHARTER.md)
- [Initial scoped items](./ITEMS.md)
- [Evidence log](./source.md)
- [Open questions](./DEBATE.md)
- [Repository proposal process](../PROCESS.md)
- [Repository consensus rules](../../CONSENSUS.md)
