---
id: gantt-dependency-phases
title: "Dependency-phase automation and GitHub Projects integration"
author: Manus AI
posted_at: 2026-08-18
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus AI
    role: executor
    status: executing
  - id: Grok
    role: collaborator-administrator
    status: executing
related_prs: [248, 252, 253, 254, 257, 717, 774, 828]
related_issues: [246, 247, 255, 259, 184]
related_branches:
  - master
  - feat/dph-all-collaborator-plan-20261018
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — gantt-dependency-phases

## Summary

Repository-native dependency-phase system: versioned plan, Project items, PR/check evidence, explicit approvals, idempotent claims. Derived Mermaid/Markdown/Project views are not authority.

**Live entry:** [`docs/agentic/README.md`](../../../agentic/README.md)  
**Collaborator plan (all DPH-*):** [`docs/agentic/COLLABORATOR-DPH-PLAN.md`](../../../agentic/COLLABORATOR-DPH-PLAN.md)  
**Primary Collaborator entry:** [`CLAUDE.md`](../../../../CLAUDE.md)

## Review log (delta)

### 2026-10-18 — Grok (Administrator)

- Disposition: executing (Operator Continue / Do ALL DPH-*)
- Notes: Prior branch `feat/dph-all-collaborator-plan-20261003` never opened a PR (form await). Rebased content onto tip `1d9a957f` as `feat/dph-all-collaborator-plan-20261018`. Approvals + Collaborator plan + ITEMS refresh. No YOLO merge or Project apply in-commit.
- Next: dual-gate on Implements PR → merge → project-sync dry-run/apply → evaluate unlock.

### 2026-10-03 — Grok (Administrator)

- Disposition: executing (Operator: Do ALL DPH-*)
- Notes: Recorded explicit approvals for DPH-100 and DPH-200. Added Collaborator execution plan covering all four phases.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Core engine + four workflows on master (#248 family)
- [x] Explicit approvals file for approval_required phases
- [x] Collaborator plan documented
- [ ] Implements PR merged with dual-gate green (DPH-100/200/300)
- [ ] Project sync apply reflects Done for completed phases
- [ ] Closed + moved to `closed/` when all terminal

## Links

- ITEMS: ./ITEMS.md
- Collaborator plan: ../../../agentic/COLLABORATOR-DPH-PLAN.md
- Live system: ../../../agentic/README.md
- Credentials names-only: issue #184
