# Agentic CI/CD — Free-tier stack (termux-monorepo)

This document describes the free-tier-only autonomous / agentic development CI/CD integrations.

## Active free-tier components

| Component | Role | Status | Free tier notes |
|-----------|------|--------|-----------------|
| **Jules** (Google Labs) | Async autonomous coding agent (fix bugs, features, tests) | Integrated (`.Jules/`, `agent-review-auto-jules.yml`, `agent-jules-on-issues.yml`) | Introductory daily task limits |
| **CodeRabbit** | AI PR review + autofix | Integrated (`.coderabbit.yaml`) | Free summaries + limited reviews; full free for public/OSS |
| **Gemini CLI GitHub Action** | Issue triage, PR review, `@gemini-cli` on-demand teammate | Integrated | Google AI Studio free quota |
| **GitHub MCP Server** | Tool access for agents (issues/PRs/code) | Usable via Gemini settings | Fully free / OSS |
| Render (Marketplace) | Deploy / self-healing hooks (noted in README) | Already installed per README | Free tier exists |

## How the loop works

1. Issue opened → Gemini triage (labels, priority, duplicate check).
2. PR opened → CodeRabbit review + Gemini review comment.
3. Bot feedback (CodeRabbit/Devin/…) → existing `agent-review-auto-jules.yml` posts `@jules` and optionally invokes Jules API.
4. Human or bot comments `@gemini-cli <request>` → Gemini on-demand invoke (👀 ack).
5. Human comments `@jules <task>` or labels `jules` → Jules on-issues workflow + App path.
6. Jules works asynchronously in a Cloud VM and opens/updates PRs for review.
7. **Coordination**: both Jules and Gemini prompts receive an inventory of open agent PRs and must avoid overlapping files; they post `<!-- agent-claim -->` markers when claiming work.

All pieces above have a free tier. Paid upgrades (Google AI Pro/Ultra for higher Jules limits, CodeRabbit Pro, etc.) are optional.

## Required secrets / variables (user action)

- `GEMINI_API_KEY` — Google AI Studio free key (required for Gemini workflows)
- `JULES_API_KEY` — optional; enables structured `jules-invoke` (App + `@jules` comment still work without it)
- Workflow permissions: Read and write for GITHUB_TOKEN (Settings → Actions → General)

## Activation note

GitHub only runs `issues` / `issue_comment` workflows from the **default branch** (`master`). The agentic workflow files must exist there for `@jules` / `@gemini-cli` mentions to respond.

## Security notes

- Gemini workflows restrict `@gemini-cli` comment triggers to OWNER/MEMBER/COLLABORATOR.
- Jules mention triggers similarly restricted.
- Fork PRs are excluded from automatic review triggers.
- GEMINI.md encodes the same hard rules as AGENTS.md (no secrets in git, master-staging, gates) plus coordination rules.
