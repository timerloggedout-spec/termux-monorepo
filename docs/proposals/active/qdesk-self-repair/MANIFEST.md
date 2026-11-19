---
id: qdesk-self-repair
title: "QDesk self-repair loop: detect, fix, merge, measure"
author: termux-ops
posted_at: 2026-11-12
source: PROPOSAL.md
status: executing
priority: P1
reviewers:
  - {id: timerloggedout-spec, role: operator-authorizer, status: accepted}
  - {id: ChatGPT, role: author+executor, status: executing}
related_issues: [5214]
related_prs: [5207, 5523]
related_branches: [feat/que-brr-clean-integration-2026-11-16]
gates_required: [repo-gate, proposal-lifecycle, termux-smoke]
---

# MANIFEST — qdesk-self-repair

## Summary

Self-repair loop for QDesk (.github/workflows/qdesk-self-repair.yml). Spec: `PROPOSAL.md`. Kill switch: repo variable QDESK_LOOP_ENABLED=false (docs/ops/QDESK-KILL-SWITCH.md).

## Branch reconciliation (BRR) integration

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
