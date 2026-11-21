---
id: cns-integration
title: "Central Nervous System — repository-wide integration programme"
author: ChatGPT
posted_at: 2026-11-19
source: source.md
status: accepted
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author-executor
    status: executing
related_issues: [5688, 5689, 5690, 5691, 5692, 5693, 5694, 5695, 5696, 5697, 5698, 5699, 5700, 5701, 5702, 5703]
related_prs: [5503, 5525, 5531, 5544, 5635, 5637, 5708, 5709]
related_branches: [feat/cns-integration-final-20261120]
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — CNS Integration

## Summary

Coordinate the repository's existing knowledge, reasoning, orchestration, routing, execution, evidence, scoring, learning, governance, and presentation organs through shared identity, versioned interfaces, canonical provenance, and measurable health. CNS is the integration architecture and read-only system view; existing organs retain their canonical state and authority.

## Scope and boundaries

- Establish the organ registry, integration map, authority matrix, event/identity mapping, and health model.
- Reconcile the active CRG historical corpus and its Explorer projection.
- Integrate Brain, Synaptic Bus, ORBIT, and SHIELD through their existing owner contracts.
- Strengthen attributable 3L0 intake and controlled orchestration experiments.
- Consolidate wait-loop, Jules, and notation practices against current repository governance.
- Preserve the existing GitHub master promotion spine, dual gates, privacy boundaries, and canonical event/ledger ownership.
- Treat this proposal as the coordination index; implementation remains itemized in CNS-01 through CNS-16.

## Review log

### 2026-11-20 — timerloggedout-spec

- Disposition: accepted
- Notes: Direct operator instruction in the conversation: "Do it; ALL CNS-#". Authorization applies to the sixteen CNS work items and the repository-governed implementation process.

### 2026-11-20 — ChatGPT

- Disposition: accepted for execution planning
- Notes: Existing master sources and active PRs were reconciled before opening the CNS issue set. Each CNS item has a dedicated GitHub issue. The first implementation slice establishes canonical architecture artifacts and this proposal record.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] CNS-01 through CNS-16 have dedicated GitHub issues
- [x] Initial implementation PR #5709 cites `Implements: CNS-01, CNS-02, CNS-04, CNS-05, CNS-14`; subsequent item PRs retain the same rule
- [ ] Repo gate and Termux smoke pass on integration PRs
- [ ] Runtime acceptance evidence recorded
- [ ] All items terminal before proposal closure

## Links

- ITEMS: [./ITEMS.md](./ITEMS.md)
- Source and evidence basis: [./source.md](./source.md)
- Organ registry: [../../../architecture/CNS-ORGAN-REGISTRY.yaml](../../../architecture/CNS-ORGAN-REGISTRY.yaml)
- Integration map: [../../../architecture/CNS-INTEGRATION-MAP.mmd](../../../architecture/CNS-INTEGRATION-MAP.mmd)
- Authority matrix: [../../../architecture/CNS-AUTHORITY-MATRIX.md](../../../architecture/CNS-AUTHORITY-MATRIX.md)
- Identity and event contract: [../../../architecture/CNS-EVENT-IDENTITY-CONTRACT.md](../../../architecture/CNS-EVENT-IDENTITY-CONTRACT.md)
- Health model: [../../../architecture/CNS-HEALTH-MODEL.md](../../../architecture/CNS-HEALTH-MODEL.md)
- Implementation plan: [../../../../superpowers/plans/2026-11-19-cns-integration-program.md](../../superpowers/plans/2026-11-19-cns-integration-program.md)
