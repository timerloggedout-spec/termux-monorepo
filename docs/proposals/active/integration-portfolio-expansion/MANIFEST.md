---
id: integration-portfolio-expansion
title: "Integration portfolio expansion and documentation readiness"
author: ChatGPT
posted_at: 2026-11-05
source: "Operator directive: maintain documentation, upgrade named integrations, and provision available capabilities"
status: accepted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_prs: []
related_branches:
  - docs/integration-portfolio-expansion-20261105
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---

# MANIFEST: integration-portfolio-expansion

## Summary

Expand the existing Integration Intelligence registry from eight baseline integrations to include the 24 additional integration surfaces explicitly named by the operator. Publish a human-readable readiness audit through the existing Mintlify documentation site.

## Boundaries

- This is an inventory, documentation, and readiness baseline, not an assertion that every provider adapter is implemented.
- Session connectors, installed skills, account authentication, repository adapters, validated runtime execution, and production promotion remain distinct states.
- User-reported secret provisioning remains unverified until an authorized runtime run proves it.
- No credentials, private prompts, private session transcripts, personal calendar data, paid upgrades, billing changes, or account mutations are included.
- Existing DeepWiki refresh campaign ownership and builder/evaluator separation remain authoritative.
- Existing integration event schema and adapter contract are preserved.

## Review log

### 2026-11-05 — timerloggedout-spec

- Disposition: accepted for the scoped portfolio and documentation expansion.
- Notes: operator directive explicitly requested maintenance and provisioning of the named integration set.

## Checklist

- [x] Proposal registered
- [x] Work item created
- [ ] PR cites `Implements: IPX-001`
- [ ] Proposal lifecycle, repo gate, and Termux smoke pass on the same head SHA
- [ ] Current check disposition and evidence recorded
- [ ] Close only after all gates are terminal

## Links

- ITEMS: ./ITEMS.md
- Design: ../../../superpowers/specs/2026-11-05-integration-portfolio-expansion-design.md
- Plan: ../../../superpowers/plans/2026-11-05-integration-portfolio-expansion.md
