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

This change introduces the user-owned fork of **ICM Architect** as a pinned, shallow Git submodule at `refTemplates/smods/icm-architect_fork`. The integration keeps project-specific customizations isolated in `timerloggedout-spec/icm-architect_fork` while retaining the upstream relationship to `RinDig/icm-architect`. It also adds a concise operating document covering initialization, upstream comparison, controlled updates, and validation.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-17 | Direct instruction authorized the fork and monorepo implementation. |

## Review log

### 2026-08-17 — Manus AI

- Disposition: accepted for execution.
- Notes: The remote `master-staging` baseline was captured before work began. The Termux MCP transport was unavailable, so no device-side checkout was modified; an isolated feature worktree based on `master-staging` is used instead.

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
