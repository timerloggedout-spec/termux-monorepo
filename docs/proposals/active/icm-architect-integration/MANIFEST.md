---
id: icm-architect-integration
title: "ICM Architect custom-fork submodule integration"
author: timerloggedout-spec
posted_at: 2026-08-17
source: source.md
status: executing
priority: P2
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: []
related_branches:
  - feat/icm-architect-submodule
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — ICM Architect Integration

## Summary

This change introduces the user-owned fork of **ICM Architect** as a pinned, shallow Git submodule at `refTemplates/smods/icm-architect_fork`. The integration keeps project-specific customizations isolated in `timerloggedout-spec/icm-architect_fork` while retaining the upstream relationship to `RinDig/icm-architect`. It adds a concise operating document covering initialization, upstream comparison, controlled updates, and validation, then applies the ICM System map form under `docs/icm/` to route later agents to verified monorepo components, real workflows, and first-order change impact without reorganizing source.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-17 | Direct instruction authorized the fork and monorepo implementation. |

## Review log

### 2026-08-17 — Manus AI

- Disposition: accepted for execution.
- Notes: The remote `master-staging` baseline was captured before work began. The Termux MCP transport was unavailable, so no device-side checkout was modified; an isolated feature worktree based on `master-staging` is used instead.

### 2026-08-17 — ICM System Map extension

- Disposition: accepted for execution.
- Notes: The operator authorized use of the integrated ICM Architect submodule to map the monorepo’s intended usage. The map remains beside existing documentation, cites existing sources, and does not move source, generated indexes, recovery artifacts, device state, or application code.

### 2026-08-17 — ICM maintenance-pipeline completion

- Disposition: accepted for execution.
- Notes: Research across RinDig’s `icm-architect`, `Interpretable-Context-Methodology`, `cost-of-remembering`, and `Content-Agent-Routing-Promptbase` resources confirmed the System map plus nested human-gated Pipeline composition. The completion work adds only documentation, templates, ignored stage-output markers, and routing records; no Python or application code is in scope.

### 2026-08-17 — Full methodology companion and workspace-artifact triage

- Disposition: accepted for execution.
- Notes: The operator elevated completion of the existing ICM integration to P0, citing the existing master-priority issue and PR #232. The user-owned `interpretable-context-methodology_fork` reference is synchronized from upstream and pinned as a shallow custom submodule; `workspace/` artifacts are classified in ICM documentation only. No application-code refactor, cleanup, relocation, deletion, or sensitive-runtime inspection is authorized by this scope.

### 2026-08-17 — Repository-native ICM reference inputs and visual review

- Disposition: accepted for execution.
- Notes: The operator clarified that ICM is being applied to the monorepo itself. `icm-cctv_fork` and `content-agent-routing-promptbase_fork` are shallow, optional reference inputs under `refTemplates/smods/`; the monorepo’s own `docs/icm/` contracts remain operative. The BLU B160V/free-services envelope is documented as an operator constraint only. No Termux MCP/device access, service-account operation, network deployment, application-code refactor, or visual renderer startup is authorized by this scope.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Execution branch created from `master-staging`
- [ ] PR cites `Implements: ICM-01`
- [ ] Gates green before merge
- [ ] Closed and moved to `closed/` when terminal

## Links

- ITEMS: [./ITEMS.md](./ITEMS.md)
- Source: [./source.md](./source.md)
- Integration guide: [../../../ICM-ARCHITECT-INTEGRATION.md](../../../ICM-ARCHITECT-INTEGRATION.md)
