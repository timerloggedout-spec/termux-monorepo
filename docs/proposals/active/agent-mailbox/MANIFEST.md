---
id: agent-mailbox
title: "Multi-Agent Coordination via MCP Agent Mail integration"
author: jules
posted_at: 2026-10-21
status: executing
priority: P1
reviewers:
  - id: jules
    role: author+executor
    status: posted
related_issues: [90, 105, 109]
related_prs: []
gates_required: [repo-gate]
---

# MANIFEST — agent-mailbox

## Summary

Integrates Rust-based MCP Agent Mail (`mcp_agent_mail_rust`) as a GitHub Actions composite action and workflow step, providing background mailboxes, message passing, file safety reservations (leases), and non-interactive Robot Mode CLI capabilities to coordinate multi-agent CI/CD operations.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| jules | author+executor | posted | 2026-10-21 | Initial implementation & GHA integration proposal |

## Review log

### 2026-10-21 — jules

- Disposition: accepted
- Notes: Action and workflow created with test coverage; approved for execution.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [x] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- DEBATE: ./DEBATE.md
