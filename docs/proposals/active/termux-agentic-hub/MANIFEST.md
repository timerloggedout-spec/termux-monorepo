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
  - id: ChatGPT
    role: implementation agent
    status: executing
related_prs: [221, 5683]
related_branches:
  - feature/termux-agentic-hub
  - feat/accessibility-agents-adaptive-integration
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — termux-agentic-hub

## Summary

Establish a Termux-first Agentic Hub for the BLU B160V by adding approved user-owned MCP forks as reproducible submodules under `refTemplates/smods/`, implementing a single local policy hub and structured GitHub-backed job protocol, and extending CI with low-privilege integrity and validation workflows. This accepted scope now includes a pinned Accessibility Agents source, a repository-native accessibility skill adapter, and drift reconciliation for external agent/tracker dependencies. The implementation keeps Android execution local, treats GitHub as the review and coordination plane, and excludes credentials, browser state, interactive MFA bypasses, and public device exposure.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| user | operator+approver | accepted | 2026-08-15 | Approved the execution plan after edits. |
| Manus | author+executor | executing | 2026-08-15 | Implements governed repository changes on a feature branch. |
| ChatGPT | implementation agent | executing | 2026-11-19 | Integrates accessibility-agent source and updates stale external integration policy under explicit operator direction. |

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

### 2026-11-19 — operator direction relayed through ChatGPT

- Disposition: accepted scope extension
- Notes: Integrate `timerloggedout-spec/accessibility-agents_fork` under `refTemplates/smods/`; use `CLAUDE.md` as the agent entry point; treat Linear as an optional degraded mirror; retire repository Jules automation effective 2026-11-01; preserve the parallel `AGENTS.md` naming migration.

### 2026-11-19 — ChatGPT

- Disposition: implementation submitted for review
- Notes: PR #5683 opened against `master-staging`; two commits cover the pinned source, native adapter, drift reconciliation, and retired Jules routes. Repository gate, Termux smoke, and submodule integrity workflows are queued; merge remains pending their verified results.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator approval recorded
- [x] Execution branch created from `master-staging`
- [x] PR #5683 cites `Implements: THUB-007`
- [ ] THUB-007 gates and review validated
- [ ] Review outcome recorded and proposal closed when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Fork inventory: ../../submodules/fork-inventory.yaml
