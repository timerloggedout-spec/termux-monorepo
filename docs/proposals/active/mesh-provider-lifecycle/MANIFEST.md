---
id: mesh-provider-lifecycle
title: "Mesh provider lifecycle reconciliation and retired-provider regression guard"
author: ChatGPT
posted_at: 2026-11-24
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: [1622, 5552]
related_prs: [5807, 4020, 1626, 3908, 3628, 2663, 5630]
related_branches:
  - fix/mesh-provider-lifecycle-20261123
  - docs/mesh-extended-utilization-20261123-v2
  - feat/mesh-resiliency-admission
  - research/mesh-resiliency-provider-evidence-20261024
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — mesh-provider-lifecycle

## Summary

Reconcile the mesh and VM architecture inventory, retire Fly.io and Koyeb from execution, and add a regression guard that reuses the existing deployment-lane and DevOps authorities. Preserve provider history, separate function workloads from VM compute, and connect related branches/commits through the existing BRR and GitHub evidence surfaces.

## Scope boundaries

- `docs/DEPLOYMENT-LANES.md` remains the Vercel deployment-lane SSOT and the shared hosting-surface index.
- `docs/ops/DEVOPS-REGISTER.md` owns the dated operational lifecycle disposition.
- `docs/ops/INTEGRATION-MESH-MATRIX.md` remains the dated integration census snapshot.
- Infrastructure CMDB/IDRR design remains the reconciliation model; this proposal reuses existing sources and adds no parallel provider registry or poller.
- Fly.io and Koyeb workflows become manual-dispatch retirement receipts; historical quota records, commits, and deployments remain as provenance.
- Provider resource teardown, account changes, and credential rotation remain human-authorized operations.
- BRR remains read-only; its private 4,103-branch registry cycle and consumer read remain a separate evidence gate.

## Authorization and review record

Operator instruction received 2026-11-24: retire Fly.io and Koyeb from the mesh, reconcile the provider/VM inventory, and fix the recurring regression. This authorizes the bounded implementation items below. Provider resource deletion, credential changes, and production failover remain outside this execution scope.

## Review log

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-24 | Explicit owner directive authorizes the retirement and reconciliation scope. |
| ChatGPT | author+executor | executing | 2026-11-24 | Implementing workflow guards, topology index, and regression tests. |

## Checklist

- [x] Registered and itemized on the implementation branch
- [ ] Independent implementation review recorded
- [ ] repo-gate and termux-smoke green on the same head SHA
- [ ] Review/check disposition reconciled
- [ ] Merge under repository promotion policy

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Debate: ./DEBATE.md
