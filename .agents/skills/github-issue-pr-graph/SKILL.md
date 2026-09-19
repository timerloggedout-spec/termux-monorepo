---
name: github-issue-pr-graph
description: Evaluate, refine, correlate, and assign GitHub issues and pull requests. Use for sub-issues, labels, projects, message threads, review threads, commit comments, mention-graph reconstruction, and PR status plus discussion management. Load with evidence-led-monorepo-ops, adaptive-wait, and context-relationship-graph.
---

# Skill: github-issue-pr-graph

**Canonical:** `.agents/skills/github-issue-pr-graph/SKILL.md` on **master**.
Companion graph substrate: `.agents/skills/context-relationship-graph/SKILL.md`.

**Load with:** `evidence-led-monorepo-ops` · `adaptive-wait` · `review-loop`.

## Intent

Operate the GitHub social graph for this monorepo without comment-storms.

| Verb | Meaning |
|------|---------|
| Evaluate | Read issue/PR + reviews + checks + linked items before acting |
| Refine | Narrow title/body/labels; extract a sub-issue instead of bloating one thread |
| Correlate | Map issue ↔ PR ↔ commit ↔ review thread ↔ project card ↔ mention |
| Assign | Set assignee/reviewer only when the person or bot is the intended actor |
| Sub-issues | Split scope; keep parent as tracker |
| Labels | Use existing repo labels; do not invent taxonomy in comments |
| Projects | Move cards; do not duplicate status in comments |
| Threads | Reply in the existing review/issue thread; one durable fact per action |

## Mention graph (test / invoke)

Official monikers live in `docs/ops/AGENT-MONIKERS.md`.

| Channel | Call |
|---------|------|
| DeepSeek CI | `@deepseek` / `@deepseek-ci` / `@deepCore` or labels `deepseek-ci`, `deepseek`, `deepCore` |
| CodeRabbit | `@coderabbitai` |
| Jules | `@jules` |
| Gemini CLI | `@gemini-cli` |

DeepSeek web-wrapper needs a live `DEEPSEEK_COOKIES` / session secret. Stale tokens fail `create_chat_session` with `40003`. That is expected after rotation — do not re-derive cookies from exposed profiles (`docs/CREDENTIAL-EXPOSURE.md`).

## Operating loop

1. Recon open issues + PRs (state, base SHA vs live master, mergeable, reviews).
2. Correlate with `context-relationship-graph` when history matters.
3. Act once — label, assign, open sub-issue, or push a scoped PR.
4. Record durable facts in the PR/issue body or `docs/ops` — not a new comment for every poll.
5. Dual-gate before merge (`repo_gate.py` + `termux_smoke.py`).
6. WAIT on CI; stay busy on disjoint work.

## Neighbor-safe rules

- Do not re-open closed help-wanted claims.
- Do not merge dirty/behind record PRs; extract onto live master.
- Do not force-merge mega-PRs.
- CodeRabbit full-repo review is requested with `@coderabbitai` on the PR plus org app install (Operator).

## Closeout

State evaluated items, correlations (issue/PR/SHA), labels/projects touched, threads resolved vs left WAIT, and the next dual-gate SHA.

Agent-Identity: Grok (Administrator)
