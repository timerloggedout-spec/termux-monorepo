# Agentic stack: who builds code vs who reviews

## Builders (create branches, implement, open PRs)

| Agent | How it builds | Free tier? | How to trigger on this repo |
|-------|---------------|------------|-----------------------------|
| **Jules-derived DoE role pack** | Issue analysis, task planning, evidence custody, local verification guidance | Local skill bundle | `.agents/skills/jules-doe-role-adapter/SKILL.md`; execution uses the active provider roster |
| **Devin** | Session implements → PR / push fix commits | Paid product (check your plan) | `/devin` on issues; Auto-Fix on PR review settings |
| **Gemini CLI plan-execute** | Can write files + PR when workflow has `contents: write` | Yes (AI Studio quota) | `@gemini-cli /approve` path in full upstream examples; our free workflows default to triage/review/invoke |

**Builder selection is evidence-driven.** The router evaluates the eligible contributor pool against capability, task ownership, quota, freshness, and evidence. Devin, Gemini, Mistral Vibe, Tembo, OpenRouter-backed agents, and other declared builders may participate according to the active policy/topology. The Jules-derived DoE role pack contributes workflow guidance through the role register.

## Reviewers / triage (comments, labels; limited or no branch creation)

| Agent | Role |
|-------|------|
| **CodeRabbit** | PR review + autofix suggestions (commit suggestion / autofix) |
| **Gemini CLI** (our triage/review/invoke workflows) | Issue triage, PR comments, on-demand analysis; eligible shared-pool contributor (Omni/OpenRouter are also eligible) |
| **Devin Review** (without Auto-Fix) | Comments only until Auto-Fix enabled |

## Coordination (no overlapping files)

Current provider workflows inject an inventory of **open agent PRs** into their prompts.

Rules encoded in `GEMINI.md` and `.agents/skills/jules-doe-role-adapter/SKILL.md`:

1. Scan open implementation PRs, CodeRabbit findings, and related issue links before editing.
2. Do not modify files already in another open agent PR for the same issue.
3. Prefer disjoint file sets.
4. After opening a PR, post on the issue:

```text
<!-- agent-claim -->
claimed_by: <active-agent-id>
issue: N
files: path/a, path/b
pr: #
```

5. Cross-review: reviewers verify implementation PRs against the exact candidate head; the active roster selects available reviewers.

## Jules-derived DoE role pack (local guidance)

1. Use `.agents/skills/jules-doe-role-adapter/SKILL.md` for the local role bindings.
2. Google Jules became read-only after 2026-11-11; legacy labels and mentions produce a retirement receipt.
3. Route implementation through the active agent roster and a verified execution adapter.

**Workflows must live on the default branch (`master`) for `issue_comment` / `issues` events to fire.**

## Devin suggested fixes — "auto approve"

There are two different meanings:

### A) Auto-apply Devin's code suggestions (recommended)

In Devin app:

1. **Settings → Customization → Pull requests → Responding to bots**
2. Choose **Selected only** and allowlist `devin-ai-integration[bot]` (or **All bots**)
3. Enable **Auto-Fix** so Devin pushes fix *commits* to the PR branch instead of only commenting

On any Devin-authored PR, org admins can also toggle Auto-Fix from the review sidebar.

GitHub "Commit suggestion" on individual suggestion blocks still needs a human click unless Auto-Fix is on.

### B) Auto-merge / auto-approve the PR

That is GitHub branch protection + merge queue / rulesets — **not** something Devin turns on by itself. Keep a human or required checks before merge (repo gates: `repo_gate.py`, `termux_smoke.py`).

## Gemini 👀 indication

After workflows are on the **default branch** *and* `GEMINI_API_KEY` is set:

- `@gemini-cli ...` comments get a **👀** reaction + short "received" comment with Actions run link
- Same pattern as Jules / CodeRabbit

If you saw no 👀 on a prior comment: either the Gemini workflows were not yet on the branch that receives events, or `GEMINI_API_KEY` was missing (job fails before ack in some paths).
