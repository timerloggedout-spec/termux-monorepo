---
id: agent-routing-orchestrator-scope
title: "Multi-model Agent Routing Orchestrator: closing the code-writing permission gap"
author: timerloggedout-spec
posted_at: 2026-09-11
source: source.md
status: draft
priority: P1
reviewers: []
related_prs: []
related_branches: [proposal/agent-routing-orchestrator-scope]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — agent-routing-orchestrator-scope

## Summary

This proposal scopes — it does not implement — closing the gap that keeps OpenRouter/Felo-routed agent workflows (`gemini-invoke`, `gemini-review`, `gemini-triage`, `gemini-after-peers`, `ox-alpha-smoke`, `team-mvt`, `continuous-evaluation`) limited to PR/issue comments instead of writing code and opening PRs, and defines how MoneyBall/3L0/leaderboard scoring (`multivariate-doe` + `gemini-performance-psychology` + `evidence-led-monorepo-ops`) should gate any expansion as decision-support only, never overriding Tier 3/4 human authority.

**Extension (2026-09-13):** adds ARO-7..ARO-10 — formally wiring HuggingFace into the same provider-catalog/model-router pattern as OpenRouter/Felo/Omni (comment-only roles first, same permission ceiling), verifying that CellCog and Hex are real already-integrated org systems but not MCP connectors today, and publishing a connector/provider inventory (current `mcp-hub/catalog.json` hosts vs. a reasonable target list). Still Tier 0-2 only: no workflow-permission change, no credential handling, no new proposal — filed as an extension to this same initiative.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| | author | posted | 2026-09-11 | |

## Review log

### 2026-09-11 — author

- Disposition: commented
- Notes: initial scoping submission, awaiting non-author review per Tier 3 (proposal accepted needs non-author review or Operator).

### 2026-09-13 — author

- Disposition: commented
- Notes: extended with ARO-7..ARO-10 (HuggingFace wiring, CellCog/Hex verification, connector inventory). Still draft; still awaiting non-author review or Operator per Tier 3.

## Checklist (process)

- [ ] Registered in `docs/proposals/registry.yaml`
- [ ] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Status → accepted before execution merges
- [ ] PRs cite `Implements: <ITEM-ID>`
- [ ] Gates green on merge
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md