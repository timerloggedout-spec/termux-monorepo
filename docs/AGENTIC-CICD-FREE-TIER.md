# Agentic CI/CD — Free-tier stack (termux-monorepo)

This document describes the free-tier-only autonomous / agentic development CI/CD integrations.

## Active free-tier components

| Component | Role | Status | Free tier notes |
|-----------|------|--------|-----------------|
| **Jules** (Google Labs) | Async autonomous coding agent (fix bugs, features, tests) | Integrated (`.Jules/`, `.github/workflows/agent-review-auto-jules.yml`, `.github/workflows/agent-jules-on-issues.yml`) | Introductory daily task limits |
| **CodeRabbit** | AI PR review + autofix | Integrated (`.coderabbit.yaml`) | Free summaries + limited reviews; full free for public/OSS |
| **Gemini CLI GitHub Action** | Issue triage, PR review, `@gemini-cli` on-demand teammate | Integrated | Google AI Studio free quota |
| **GitHub MCP Server** | Tool access for agents (issues/PRs/code) | Usable via Gemini settings | Fully free / OSS |
| Render (Marketplace) | Deploy / self-healing hooks (noted in README) | Already installed per README | Free tier exists |

## How the loop works

1. Issue opened by OWNER/MEMBER/COLLABORATOR → Gemini triage (labels, priority, duplicate check).
2. PR opened (non-fork, non-draft) → CodeRabbit review + Gemini review comment.
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

See also: `docs/ARCHW1Z-OPERATOR-CHECKLIST.md` for operator setup steps.

## Activation note

GitHub only runs `issues` / `issue_comment` workflows from the **default branch** (`master`). The agentic workflow files must exist there for `@jules` / `@gemini-cli` mentions to respond.

## Security notes — intentional agentic command surface (PromptPwnd / Aikido)

**This repository is an Automated Agentic Development Environment (ADE).** Agents are expected to use tools, shell, and `gh` CLI to implement fixes, open branches/PRs, and operate the repo. That capability is a **required feature**, not an accidental exposure.

Aikido’s *PromptPwnd* class of findings (untrusted issue/PR text → agent prompt → privileged tools) is real and applies to any agentic CI/CD stack. We accept a controlled form of that surface so agents can do real engineering work.

### Mitigations already in place

| Control | Where |
|---------|--------|
| `@gemini-cli` / `@jules` triggers limited to **OWNER / MEMBER / COLLABORATOR** | `gemini-dispatch.yml`, `agent-jules-on-issues.yml` |
| Automatic issue triage only for trusted association | `gemini-dispatch.yml` |
| Fork PRs excluded from auto review | `gemini-dispatch.yml` |
| `synchronize` does **not** auto-re-review (quota + noise) | `gemini-dispatch.yml` |
| Hard rules: no secrets in git, master-staging, gates, claim markers | `GEMINI.md`, `AGENTS.md` |
| Prior open agent PR inventory injected into prompts | dispatch → triage/review/invoke |
| Job permissions scoped to `contents: read` + issues/PR write (not admin) | workflow `permissions:` blocks |
| `persist-credentials: false` on checkout | Gemini workflows |

### Recommended Aikido / SAST exclusions

If Aikido (or similar) flags `run-gemini-cli`, `GEMINI_CLI_TRUST_WORKSPACE`, or agent shell tools as PromptPwnd:

1. **Whitelist / exclude** these workflow paths as *intentional ADE agent runners*:
   - `.github/workflows/gemini-*.yml`
   - `.github/workflows/agent-jules-on-issues.yml`
   - `.github/workflows/agent-review-auto-jules.yml`
2. Keep scanning **application code** and non-agent workflows at full sensitivity.
3. Do **not** disable association gates or re-enable untrusted issue-body → shell interpolation without a new design review.

### What we deliberately do *not* do

- Embed raw `${{ github.event.issue.body }}` into shell scripts (prompt text only, via action inputs).
- Grant `administration` or unconstrained `contents: write` to Gemini jobs.
- Auto-merge agent PRs without gates (`repo_gate.py` + `termux_smoke.py`).
