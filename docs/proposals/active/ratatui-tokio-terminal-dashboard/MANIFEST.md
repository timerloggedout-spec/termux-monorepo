---
id: ratatui-tokio-terminal-dashboard
title: "Termux-first Ratatui + Tokio responsive terminal dashboard"
author: ChatGPT
posted_at: 2026-09-30
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: []
related_branches:
  - feat/ratatui-tokio-terminal-dashboard
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — ratatui-tokio-terminal-dashboard

## Summary

Build a Termux-first Rust terminal dashboard using Tokio for asynchronous producers and Ratatui for responsive rendering. The first production slice is a process/system monitor with bounded event channels, model/render separation, dirty-frame coalescing, graceful metric fallback, and clean terminal lifecycle handling.

## Source

Issue #934. The design is grounded in the requested Ratatui/Tokio dashboard concept: active streams, latency/throughput, CPU/memory, thread-pool/process views, and low-latency redraw behavior.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | requested | 2026-09-30 | operator lane |
| ChatGPT | author+executor | executing | 2026-09-30 | implementation |

## Promotion

Execution is bounded to the integration crate. Promotion requires repo-gate, termux-smoke, Rust formatting/check/test evidence, and verification that the runtime remains graceful when a metric source is unavailable.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [x] Status is executing under the explicit implementation request
- [ ] PR cites `Implements: TUI-RATATUI-001`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
