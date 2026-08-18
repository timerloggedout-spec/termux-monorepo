---
id: multi-ai-lightwrap-parity
title: "Termux lightweight multi-AI web-wrapper parity hub"
author: Manus
posted_at: 2026-08-18
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus
    role: implementation agent
    status: executing
related_prs: [6, 48, 174, 216]
related_branches:
  - feature/multi-ai-operational-hub
  - timerloggedout/ter-9-fix-vibe-silent-dispatch-provider-aware-stores-mark-scaffold
  - timerloggedout/ter-40-llm-api-hub-and-kai9000-split
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — multi-ai-lightwrap-parity

## Summary

This proposal replaces a checklist-only direction with a parent-owned lightweight provider wrapper hub. Its parity basis is the complete local reverse-engineering corpus of Termux Chromium/Puppeteer scripts, including manual-login, profile reuse, selector discovery, browser-mediated UI send, response stabilization, and redacted runtime metadata. It does not select an individual probe as canonical, import ChapitoAI code, modify DeepTerm, use Selenium or Playwright as an implementation dependency, or build direct provider endpoint clients.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-18 | Directed a lightweight function-parity implementation using the reverse-engineering corpus. |
| Manus | implementation agent | executing | 2026-08-18 | Creating the parent-owned wrapper runner and adapter contracts. |

## Review log

### 2026-08-18 — Manus

- **Disposition:** Executing under operator direction.
- **Evidence:** Static analysis covered 44 lightweight JavaScript modules from `deepcli`, `deepseek-cli`, and `multi-ai-cli`. Termux Chromium, Puppeteer, profile reuse, manual-login, selector discovery, browser UI send, and response extraction are recurrent patterns. Direct endpoint, token/cookie, screenshot, and raw-stream behavior remain excluded from the parent hub.
- **Scope correction:** `probe-expert-abc.mjs` is one historical example only; it is not the canonical provider implementation.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator direction recorded
- [ ] Parent-owned generic runner implemented
- [ ] Static provider profiles and fixture tests added
- [ ] PR cites `Implements: MLWP-*`
- [ ] Required gates green on the governed integration target
- [ ] Closed and moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
