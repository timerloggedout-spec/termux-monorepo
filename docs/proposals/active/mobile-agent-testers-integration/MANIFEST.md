---
id: mobile-agent-testers-integration
title: "Mobile Agent Testers — persona-driven exploratory QA integration"
author: ChatGPT
posted_at: 2026-11-23
source: "Operator directive: integrate timerloggedout-spec/mobile-agent-testers_fork with existing mobile emulators and Termux device fleet"
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: []
related_branches:
  - feat/mobile-agent-testers-integration
related_repos:
  - https://github.com/timerloggedout-spec/mobile-agent-testers_fork
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---

# MANIFEST — Mobile Agent Testers Integration

## Summary

Integrate the forked Mobile Agent Testers workflow as an ephemeral, persona-driven exploratory QA provider. Reuse the existing StudySprint SDK-direct APK build and emulator smoke gate, existing Termux device queue, Integration Intelligence event envelope, and repository evidence ledger.

## Boundaries

- Deterministic emulator tests remain the regression gate; agent exploration is advisory discovery.
- Existing physical Termux devices remain governed by the device registry and pull-queue contract.
- The external tester fork remains an execution provider, not a second scheduler or source of truth.
- Android is the first supported StudySprint pilot; the inspected StudySprint target has no iOS app.
- Public Actions artifacts stay encrypted. Decryption and evidence normalization occur on a trusted local machine.
- Private keys, model credentials, API keys, real learner data, and decrypted raw reports stay outside Git and CI.
- Paid model inference requires an explicit per-run budget; this integration does not auto-dispatch paid runs.
- Provider findings remain unverified observations until reproduced by deterministic tests or a human reviewer.

## Architecture

StudySprint build → existing emulator smoke → optional Mobile Agent Testers personas → encrypted provider artifacts → trusted local collection → normalized Integration Intelligence JSONL → existing evidence / review lanes.

The Termux device fleet remains a separate provider for physical-device work. The adapter emits evidence only; it does not enqueue arbitrary shell tasks or control phones.

## Review log

### 2026-11-23 — timerloggedout-spec

- Disposition: accepted by the operator directive “DO it all”.
- Scope: bounded repository integration, adapter, tests, runbook, and reusable StudySprint brief.
- Budget: provider runs remain manually initiated and budgeted per run.

## Checklist

- [x] Proposal registered
- [x] Work item created
- [x] Provider brief and invocation contract documented
- [ ] Evidence adapter and sanitized fixtures implemented
- [ ] Registry and catalog updated
- [ ] Focused tests pass
- [ ] PR cites Implements: MAT-001
- [ ] Proposal lifecycle, repo gate, and Termux smoke pass on the same PR head
- [ ] Provider run evidence and cost recorded before validation
- [ ] Close only after all gates are terminal

## Links

- ITEMS: ./ITEMS.md
- Design and execution plan: ../../../superpowers/plans/2026-11-23-mobile-agent-testers-integration.md
- Runbook: ../../../ops/MOBILE-AGENT-TESTERS-INTEGRATION.md
