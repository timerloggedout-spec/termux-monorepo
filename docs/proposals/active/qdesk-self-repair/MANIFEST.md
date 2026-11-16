---
id: qdesk-self-repair
title: "QDesk self-repair loop (SIE ⇒ Desk QUE) with branch reconciliation intake"
author: ChatGPT
posted_at: 2026-11-16
source: "Existing QDesk self-repair proposal and operator directive to integrate BRR into QUE"
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: []
related_prs: []
related_branches:
  - feat/que-brr-clean-integration-2026-11-16
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — qdesk-self-repair

## Summary

Operate QDesk as the single scheduled execution plane for branch reconciliation. BRR observes the repository, produces a complete branch inventory, and projects actionable evidence into the existing QUE issue intake. QUE retains its existing ranking, claim, lease, reclaim, escalation and Desk surfaces.

## Non-negotiable boundaries

- BRR is read-only with respect to branch mutation.
- Reuse the one existing scheduler, queue, ranking system, claim engine and promotion controller (¬ second instance).
- A QUE claim is assignment, not merge authorization.
- Unknown ancestry remains unresolved; missing evidence is never interpreted as clean.
- QDesk/Desk, DoE, CI, branch protection and owner authorization remain separate gates.
- Keep every branch mutation (delete ∨ close ∨ retarget ∨ push ∨ merge) outside this integration; BRR ⊢ read-only.

## Acceptance

- The QDesk scheduled cycle runs the BRR census before QUE intake.
- The complete JSON and Markdown inventory is retained as a 90-day artifact.
- Actionable dispositions become idempotent QUE work keyed by branch, tip SHA and disposition.
- Focused classification and intake tests pass on the exact reviewed head.
- A scheduled QDesk cycle completes census, issue intake and artifact upload before runtime operation is declared active.
