---
id: apache-camel-smods-integration
title: "Apache Camel integration opportunity — governed MCP, event routing, and EIP adapter"
author: ChatGPT
posted_at: 2026-11-16
source: RFP.md
status: in_review
priority: P1
execution: true
execution_scope: "Bounded source research, architecture mapping, and isolated offline/runtime experiments; production integration and live gitlink remain gated."
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
  - id: ChatGPT
    role: author+executor
    status: executing
related_issues: []
related_prs: []
related_branches:
  - proposal/apache-camel-smods-integration
gates_required:
  - proposal-lifecycle
  - repo-gate
  - termux-smoke
---

# MANIFEST — apache-camel-smods-integration

## Summary

Evaluate the user-owned Apache Camel fork as an optional integration runtime and MCP interoperability layer. Register it as metadata-first research now; defer the live `refTemplates/smods/camel_fork-apache` gitlink until source provenance, compatibility, security, and repository gates are proven.

## Execution

`execution: true` authorizes bounded proposal execution: source review, capability mapping, offline fixtures, and isolated compatibility experiments. It does not authorize production deployment, unrestricted MCP tool exposure, credential changes, or bypassing the accepted-proposal and dual-gate requirements.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| ChatGPT | author+executor | executing | 2026-11-16 | Source and architecture reconnaissance recorded |
| timerloggedout-spec | operator-authorizer | requested | 2026-11-16 | Review scope, ranking, and future gitlink gate |

## Review log

No independent review recorded yet.

## Checklist

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before implementation merges
- [ ] PRs cite `Implements: CAMEL-ITEM-ID`
- [ ] repo-gate and termux-smoke green on exact PR SHA
- [ ] Live gitlink decision supported by immutable pin and compatibility evidence

## Links

- RFP: ./RFP.md
- ITEMS: ./ITEMS.md
- Reference metadata: `refTemplates/12_External_Agents/apache-camel/`
- Proposed future live pin: `refTemplates/smods/camel_fork-apache`
