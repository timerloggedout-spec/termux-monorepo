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
related_prs: [5207]
related_branches: []
gates_required: [repo-gate]
---

# MANIFEST — qdesk-self-repair

## Summary

Self-repair loop for QDesk (.github/workflows/qdesk-self-repair.yml). Spec: `PROPOSAL.md`. Kill switch: repo variable QDESK_LOOP_ENABLED=false (docs/ops/QDESK-KILL-SWITCH.md).
