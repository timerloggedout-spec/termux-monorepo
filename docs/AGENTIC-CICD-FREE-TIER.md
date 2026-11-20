# Agentic CI/CD — Free-tier stack (termux-monorepo)

This document describes the free-tier-only autonomous / agentic development CI/CD integrations.

## Active free-tier components

| Component | Role | Status | Free tier notes |
|-----------|------|--------|-----------------|
| **Jules-derived DoE role pack** | Issue analysis, task planning, evidence custody, local verification guidance | Local skill bundle at `.agents/skills/jules-doe-role-adapter/SKILL.md`; Google hosted execution retired | Role guidance only; provider execution follows the active roster and verified adapters |
| **CodeRabbit** | AI PR review + autofix | Integrated (`.coderabbit.yaml`) | Free summaries + limited reviews; full free for public/OSS |
| **Gemini CLI GitHub Action** | Issue triage, PR review, `@gemini-cli` on-demand teammate; one optimized candidate in the shared routing pool | Integrated | Google AI Studio free quota — observed/managed by routing and availability evidence |
| **GitHub MCP Server** | Tool access for agents (issues/PRs/code) | Usable via Gemini settings | Fully free / OSS |
| Render (Marketplace) | Deploy / self-healing hooks (noted in README) | Already installed per README | Free tier exists |

## How the loop works

1. Issue opened → Gemini triage (labels, priority, duplicate check).
2. PR opened → CodeRabbit review + Gemini review comment.
3. Bot feedback (CodeRabbit/Devin/…) → capture review findings and route through the active reviewer pool; the Google Jules relay is retired.
4. Human or bot comments `@gemini-cli <request>` → Gemini on-demand invoke (👀 ack).
5. Legacy `@jules` comments and `jules` labels → retirement receipt with a link to the local DoE role guidance.
6. A selected active provider executes through its verified adapter and opens a reviewable PR; the Jules-derived skill pack supplies task-planning guidance.
7. **Coordination**: active provider prompts receive an inventory of open agent PRs and preserve exclusive file ownership through `<!-- agent-claim -->` receipts.

Active provider quotas follow their own plans. Google Jules became read-only after 2026-11-11 and is retired from hosted execution.

## Required secrets / variables (user action)

- `GEMINI_API_KEY` — Google AI Studio free key (required for Gemini workflows)
- Google Jules session dispatch is retired; the local Jules-derived skill bundle provides role guidance only.
- Workflow permissions: Read and write for GITHUB_TOKEN (Settings → Actions → General)

## Activation note

GitHub only runs `issues` / `issue_comment` workflows from the **default branch** (`master`). The agentic workflow files must exist there for supported `@gemini-cli` mentions to respond; legacy Jules mentions produce retirement receipts.

## Security notes

- Gemini workflows restrict `@gemini-cli` comment triggers to OWNER/MEMBER/COLLABORATOR.
- Legacy Jules labels and mentions are handled by the retirement receipt path.
- Fork PRs are excluded from automatic review triggers.
- GEMINI.md encodes the same hard rules as AGENTS.md (no secrets in git, master-staging, gates) plus coordination rules.

## Routing policy (optimized routing)

See issues **#272** and **#175**.

- Gemini, OmniRoute, OpenRouter, CodeRabbit, and other enabled contributors participate in a **shared candidate pool**; Google Jules is retired. The local Jules-derived DoE skill pack contributes role guidance.
- Admission uses capability, credential, live catalog, health, quota, task independence, freshness, and policy gates before scoring.
- Selection is evidence-driven using role suitability, local 3L0/Moneyball observations, integrated outcome, context/time cost, retries, conflicts, and human intervention.
- Topology is a first-class experiment variable: `single | series | dynamic | parallel | nested | co-working | volley`.
- A capacity failure causes re-admission against the current candidate set; it does not trigger a fixed provider chain.
- Quota skips remain explicit evidence; CI behavior is controlled separately from routing semantics.
- Builder execution follows the active candidate pool and verified adapter readiness; the Jules-derived role pack supports planning and verification guidance. Gemini remains an eligible review/triage/invoke contributor under the active route policy.
