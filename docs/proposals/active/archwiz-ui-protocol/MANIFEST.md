---
id: archwiz-ui-protocol
title: "ArchW1z Termux UI over shared agentic protocols"
author: ChatGPT
posted_at: 2026-08-21
source: source.md
status: posted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: pending
related_issues: [292]
related_prs: [329]
related_branches:
  - proposal/archwiz-ui-protocol-clean
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — archwiz-ui-protocol

## Summary

Define ArchW1z as the Termux/mobile UI and operator cockpit over shared agentic protocols. ArchW1z began as a TUI development lane and remains a parallel implementation until its client contracts are merged. The underlying job, event, handoff, capability, authorization, and evidence semantics remain UI-agnostic.

## Review posture

This is an architectural proposal, not an authorization to change runtime transport or device exposure. Implementation should follow the registered work items and existing repository gates.

## Related work

- Issue #292
- PR #221 / `termux-agentic-hub`
- `docs/ARCHW1Z-GATE.md`
- `docs/CONSENSUS.md`
- `docs/proposals/AGENTIC-PERMISSIONS.md`
