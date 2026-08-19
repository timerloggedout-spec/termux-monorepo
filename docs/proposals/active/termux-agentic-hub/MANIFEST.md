---
id: termux-agentic-hub
title: "Termux-first Agentic Hub and governed fork integration"
author: Manus
posted_at: 2026-08-15
source: source.md
status: executing
priority: P1
reviewers:
  - id: user
    role: operator+approver
    status: accepted
related_prs: [221]
related_branches:
  - feature/termux-agentic-hub
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — termux-agentic-hub

## Summary

Establish a Termux-first Agentic Hub for the BLU B160V by adding the approved user-owned MCP forks as reproducible submodules under `refTemplates/smods/`, implementing a single local policy hub and structured GitHub-backed job protocol, and extending CI with low-privilege integrity and validation workflows. The implementation keeps Android execution local, treats GitHub as the review and coordination plane, keeps direct interactive transport deferred, and excludes credentials, browser state, interactive MFA bypasses, and public device exposure.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| user | operator+approver | accepted | 2026-08-15 | Approved the execution plan after edits. |
| Manus | author+executor | executing | 2026-08-15 | Implements governed repository changes on a feature branch. |

## Review log

### 2026-08-15 — user

- Disposition: accepted
- Notes: Use `refTemplates/smods/` for fork submodules, preserve DeepSeek compatibility, remain on free/trial infrastructure, and treat the local Termux environment as the first execution target.

### 2026-08-15 — Manus

- Disposition: scope clarification
- Notes: Interactive MFA enrollment remains human-operated. Machine-to-machine integrations may use provider-supported service credentials only; no MFA bypass or second-factor secret capture is implemented.

### 2026-08-15 — Manus

- Disposition: implementation submitted
- Notes: PR #221 targets `master-staging`. Submodule integrity, hub protocol tests, feature-scoped repo gate, and Termux smoke all passed. The full comparison against `origin/master` retains three unrelated inherited syntax failures, documented in the PR body.

### 2026-08-18 — user / Manus

- Disposition: P1 scope addition in progress
- Notes: The Operator directed that the SWE-agent and mini-SWE-agent references be used for development-performance evaluation automation. THUB-007 is limited to a GitHub-native, manually dispatched control plane and deterministic result validation. It must not run an unbounded or scheduled model workload, create/rotate credentials, or make direct device control a dependency. Pull-request review and gates remain required before any integration claim.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator approval recorded
- [x] Execution branch created from `master-staging`
- [x] PR cites `Implements: THUB-001` through `THUB-006`
- [x] Feature-scoped repository gates green; inherited baseline failures documented in PR #221
- [ ] Review outcome recorded and proposal closed when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Fork inventory: ../../submodules/fork-inventory.yaml
