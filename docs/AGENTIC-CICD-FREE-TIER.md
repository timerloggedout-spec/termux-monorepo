# Agentic CI/CD — Free-tier stack (termux-monorepo)

This document describes the free-tier-only autonomous / agentic development CI/CD integrations.

## Active free-tier components

| Component | Role | Status | Free tier notes |
|-----------|------|--------|-----------------|
| **Jules** (Google Labs) | Async autonomous coding agent (fix bugs, features, tests) | Integrated (`.Jules/`, `agent-review-auto-jules.yml`) | Introductory daily task limits |
| **CodeRabbit** | AI PR review + autofix | Integrated (`.coderabbit.yaml`) | Free summaries + limited reviews; full free for public/OSS |
| **Gemini CLI GitHub Action** | Issue triage, PR review, `@gemini-cli` on-demand teammate | Added in this branch | Google AI Studio free quota |
| **GitHub MCP Server** | Tool access for agents (issues/PRs/code) | Usable via Gemini settings | Fully free / OSS |
| Render (Marketplace) | Deploy / self-healing hooks (noted in README) | Already installed per README | Free tier exists |

## How the loop works

1. Issue opened → Gemini triage (labels, priority, duplicate check).
2. PR opened → CodeRabbit review + Gemini review comment.
3. Bot feedback (CodeRabbit/Devin/…) → existing `agent-review-auto-jules.yml` posts `@jules` and optionally invokes Jules API.
4. Human or bot comments `@gemini-cli <request>` → Gemini on-demand invoke.
5. Jules works asynchronously in a Cloud VM and opens/updates PRs for review.

All pieces above have a free tier. Paid upgrades (Google AI Pro/Ultra for higher Jules limits, CodeRabbit Pro, etc.) are optional.

## Required secrets / variables (user action)

See the PR / section below for exact steps you must take.

## Security notes

- Gemini workflows restrict `@gemini-cli` comment triggers to OWNER/MEMBER/COLLABORATOR.
- Fork PRs are excluded from automatic review triggers.
- GEMINI.md encodes the same hard rules as AGENTS.md (no secrets in git, master-staging, gates).
