---
id: workflow-planning-operating-model
title: "Declarative workflow planning, routing and QUE × DoE optimization"
author: ChatGPT
posted_at: 2026-11-13
source: "Operator directive: MiroFish integration, Platform201/n8n routing, QUE, PDDL and DoE optimization"
status: in_review
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_prs: [5388]
related_branches: [feat/workflow-planning-operating-model]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — workflow-planning-operating-model

## Summary

Establish a canonical declarative workflow contract that connects workflow intent, dependency/state planning, QUE admission, routing policy, execution adapters, evidence, DoE/MVT evaluation and read-only projections. PDDL, Mermaid, n8n and Platform201 blueprint layouts are projections/adapters; they do not become competing sources of truth.

## Non-negotiable boundaries

- QUE remains the queue/governor and claim authority; it does not certify outcome correctness.
- GitHub Actions, Termux and adopted Temporal workflows remain execution surfaces under their existing ownership.
- WFC is a proposed interoperability contract; it does not silently replace existing schemas or schedulers.
- PDDL plans are advisory until planner-validated and independently authorized.
- n8n is optional, local-first, and receives only allowlisted receipts.
- Platform201 deployment remains frozen under its existing owner spend/consumer gates; this proposal authorizes no deployment.
- MiroFish outputs are hypotheses and candidate treatments, never production evidence.
- Promotions require repo-gate and termux-smoke on the same immutable SHA, verified outcome and required review disposition.

## Review log

### 2026-11-13 — initial author submission

- Disposition: posted for review
- Notes: architecture and schema proposal; validator is an initial structural implementation; no production adapter or dispatch authority is enabled.
