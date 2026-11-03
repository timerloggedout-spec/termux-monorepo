---
id: external-agent-toolchain-integration
title: "Agent toolchain integration portfolio — capability, authority, and evidence mapping"
author: ChatGPT
posted_at: 2026-11-03
source: source.md
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_issues:
  - 4008
related_prs: []
related_branches:
  - proposal/external-agent-toolchain-integration
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---

# MANIFEST — external-agent-toolchain-integration

## Summary

A read-only-first portfolio to map the requested agent/developer tools into the existing Termux Monorepo architecture. The initial deliverable is a source-backed capability, authority, consumer, trust-boundary, and evidence matrix. Runtime integrations remain separate follow-on decisions; this proposal does not authorize installation, credentials, external account changes, polling, deployment, or provider-routing changes.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | 2026-11-03 | Review scope, tool evidence classifications, and phase boundaries |
| ChatGPT | author+executor | posted | 2026-11-03 | Prepared proposal and initial evidence map |

## Review log

### 2026-11-03 — ChatGPT

- Disposition: posted
- Notes: Intake issue #4008 created. Existing CMDB/IDRR, integration mesh, model-selection-market, and MCP risk-split authorities are reused. No implementation or production readiness is claimed.

## Checklist (process)

- [x] Registered in docs/proposals/registry.yaml on proposal branch
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite Implements: <ITEM-ID>
- [ ] Gates green on merge
- [ ] Closed + moved to closed/ when terminal

## Links

- Tracking issue: https://github.com/timerloggedout-spec/termux-monorepo/issues/4008
- Proposal PR: https://github.com/timerloggedout-spec/termux-monorepo/pull/4011
- ITEMS: ./ITEMS.md
- Source: ./source.md
