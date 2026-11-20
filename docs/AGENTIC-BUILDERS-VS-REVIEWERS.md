# Agentic stack: who builds code vs who reviews

## Builders (create branches, implement, open PRs)

| Agent | How it builds | Free tier? | How to trigger on this repo |
|-------|---------------|------------|-----------------------------|
| **Jules** (Google Labs) | Cloud VM → implements → branch + PR | Yes (daily task limits) | Label issue `jules`, or `@jules` comment, or existing auto-Jules on bot PR reviews |
| **Devin** | Session implements → PR / push fix commits | Paid product (check your plan) | `/devin` on issues; Auto-Fix on PR review settings |
| **Gemini CLI plan-execute** | Can write files + PR when workflow has `contents: write` | Yes (AI Studio quota) | `@gemini-cli /approve` path in full upstream examples; our free workflows default to triage/review/invoke |

**Primary builder for this monorepo: Jules.**

## Reviewers / triage (comments, labels; limited or no branch creation)

| Agent | Role |
|-------|------|
| **CodeRabbit** | PR review + autofix suggestions (commit suggestion / autofix) |
| **Gemini CLI** (our triage/review/invoke workflows) | Issue triage, PR comments, on-demand analysis |
| **Devin Review** (without Auto-Fix) | Comments only until Auto-Fix enabled |

## Coordination (no overlapping files)

Both Jules and Gemini workflows inject an inventory of **open agent PRs** into their prompts.

Rules encoded in `GEMINI.md` and Jules invoke prompts:

1. Scan open PRs from Jules / Devin / CodeRabbit / related issue links before editing.
2. Do not modify files already in another open agent PR for the same issue.
3. Prefer disjoint file sets.
4. After opening a PR, post on the issue:

```text
<!-- agent-claim -->
claimed_by: jules|gemini
issue: N
files: path/a, path/b
pr: #
```

5. Cross-review: Gemini reviews Jules PRs; Jules auto-summons on bot feedback (`agent-review-auto-jules.yml`).

## Jules on issues (operational)

1. Create label `jules` on the repo if missing (Issues → Labels).
2. On any issue: add label **`jules`** → Jules App + workflow respond.
3. Or comment **`@jules <what to do>`** as OWNER/MEMBER/COLLABORATOR.
4. Optional: set `JULES_API_KEY` for `google-labs-code/jules-invoke` (stronger structured prompts).

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
