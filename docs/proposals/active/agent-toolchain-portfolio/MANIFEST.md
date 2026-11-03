---
id: agent-toolchain-portfolio
title: "Agent toolchain portfolio — Context, Mintlify, model routing, MCP discovery, and isolated execution"
author: ChatGPT
posted_at: 2026-11-02
source: "Operator directive: BUILD IT ALL; follow-on to issue #4008 and canonical Integration Intelligence"
status: executing
priority: P0
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues:
  - 4008
related_prs:
  - 4019
  - 4021
  - 4086
related_branches:
  - feat/agent-toolchain-portfolio
  - feat/agent-toolchain-adapters
gates_required: [proposal-lifecycle, repo-gate, termux-smoke]
---

# MANIFEST — agent-toolchain-portfolio

## Summary

Extend the existing Integration Intelligence system with an evidence-backed portfolio for Context.dev, Context7, Mintlify, Smart Model Router, HAPI MCP Registry, and Sprites. Reuse the canonical registry, adapter contract, event envelope, proposal lifecycle, and repository routing authorities.

## Boundaries

- The registry is the only canonical integration inventory; no parallel registry or orchestrator is introduced.
- Connector visibility is session-scoped and does not prove runtime authentication or CI reachability.
- Discovery is not trust approval; documentation is not test evidence; model recommendations do not change routing.
- Read-only metadata/evidence capture is the default.
- No secrets, private session transcripts, raw prompts, or credentials are committed.
- No provider account provisioning, external writes, paid inference, live model routing, MCP server execution/admission, Sprite creation/execution, or Mintlify publication is authorized by this proposal.
- Existing repository governance, dual gates, and human approval boundaries remain authoritative.

## Review log

### 2026-11-02 — operator directive
- Disposition: implementation of the bounded portfolio and phased plan authorized.
- Runtime adapters and consequential external actions remain separately gated.

### 2026-11-03 — ATP-002 / ATP-003 implementation
- Added offline HAPI MCP Registry, Context7, and Context.dev normalizers and provider-observation schema in PR #4086.
- The HAPI registry sample exposed versioned server records and multiple remote transports; output preserves version/transport identity while forcing `not_reviewed`, `not_admitted`, and `execution_allowed=false`.
- Context7 normalizer requires exact library ID/version; Context.dev normalizer strips URL query strings/fragments and bounds excerpts.
- No runtime authentication, provider polling, artifact persistence, server admission, or live provider integration is claimed.

## Checklist

- [x] Tracking issue #4008 exists
- [x] Reuse canonical Integration Intelligence branch as base
- [x] Registry/catalog/adapter contract updated
- [ ] Proposal registry and lifecycle validation pass on final adapter head
- [ ] repo-gate and termux-smoke pass on the same immutable adapter head
- [ ] Non-author review and current check disposition recorded
- [ ] Runtime pilots separately authorized and evidenced

## Links

- ITEMS: ./ITEMS.md
- Portfolio: ../../../integrations/AGENT-TOOLCHAIN-PORTFOLIO.md
- Canonical registry: ../../../integrations/registry.json
- Adapter contract: ../../../integrations/ADAPTER-CONTRACT.md
