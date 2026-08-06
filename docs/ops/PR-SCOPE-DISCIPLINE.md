# PR Scope Discipline — Agent Mandatory

> **Status:** LIVE (2026-08-06)  
> **Agent:** Grok  
> **Trigger case:** PR #42 carried `src/db.py` (Bolt SQLite/FTS) inside an agentic CI/CD workflow PR

## The problem this doc fixes

Long-lived feature branches accumulate **unrelated commits**. When the branch is opened as a PR titled for one intent (e.g. “Gemini CLI workflows”), reviewers correctly flag app-code defects that have **nothing to do** with that intent.

**Canonical example:** [PR #42](https://github.com/timerloggedout-spec/termux-monorepo/pull/42) titled *feat(agentic-cicd): free-tier Gemini CLI…* also contained:

| Path | Actual origin | Belongs in |
|------|---------------|------------|
| `src/db.py` | Jules Bolt: SQLite `executemany` + FTS5 | Focused Bolt PR |
| `termux-multi-agent/src/db.py` | Same | Focused Bolt PR |
| `termux-multi-agent/dashboard.py` | Jules Palette / Bolt telemetry | #45, #46, #65, #66 |
| `cli-synthegration/synthegration_index.py` | Hash-width / blob path work | Separate extract PR |
| `.jules/bolt.md`, `.Jules/palette.md` | Agent journals | Optional / with matching work |
| ChatGPT proposal dumps, wiki, AGENTS copies | Docs promotion | Docs-only PR |

**Rule:** Title, body `### Changes`, and `Implements:` must match the **diff that is in scope**. Everything else is either split out or explicitly listed under `### Non-goals / Out of scope` with pointers to the correct PR.

## Hard rules for every agent (Jules, Gemini, Devin, Grok, CodeRabbit, humans)

1. **One intent per PR.** Workflows ≠ app performance ≠ security Sentinel ≠ dashboard UX.
2. **Branch from `master-staging`** for integration code. Workflow-only activation may land on `master` only when `issue_comment` events require default-branch presence — still keep the *diff* minimal.
3. **Before opening or expanding a PR**, run mentally:
   - Does every changed path serve the PR title?
   - If not → new branch from clean base, or document as out-of-scope and do not “fix” those review threads on this PR.
4. **Do not fix out-of-scope review findings on the wrong PR.** Reply on the thread: “Out of scope for this PR; tracked on #N / new extract.”
5. **Cite `Implements: <ITEM-ID>`** (e.g. `CE-22`). Free-text is not an ID.
6. **Scan open agent PRs** before editing shared files (`<!-- agent-claim -->` protocol).
7. **Prefer focused Jules PRs** already open over stuffing more into #42:
   - Bolt telemetry: #45, #66
   - Palette dashboard UX: #46, #65
   - Sentinel perms: #44
   - curl_cffi Termux fallback: #63

## Resolution path for PR #42 (CE-22)

**In scope (keep / merge when gates green):**

- `.github/workflows/gemini-*.yml`
- `.github/workflows/agent-jules-on-issues.yml`
- `.github/workflows/agent-review-auto-jules.yml` (if intentional for this stack)
- `.github/workflows/agent-feedback-linear-sync.yml` (if intentional)
- `GEMINI.md`, `docs/AGENTIC-CICD-FREE-TIER.md`, `docs/AGENTIC-BUILDERS-VS-REVIEWERS.md`
- CE-22 row in `docs/proposals/active/chatgpt-critical-eval/ITEMS.md`

**Out of scope (do not expand #42 to fix these threads):**

- `src/db.py` / `termux-multi-agent/src/db.py` — FTS5 portability, shared-conn rollback, FTS de-dup → **Bolt extract**
- `cli-synthegration/synthegration_index.py` — blob path vs text, hash width migration → **separate PR**
- `termux-multi-agent/dashboard.py` — rich hard-fail, pulse UX → **#45/#46/#65/#66**
- Case-collision `.Jules` vs `.jules` → consolidate spelling in a docs/hygiene PR

**Operator options:**

A. **Trim** `feature/agentic-cicd-gemini-free` to workflow+docs only (new clean branch preferred).  
B. **Leave** app commits on the branch but mark them Non-goals; land app work via focused PRs; merge only when conflicts on workflow paths are resolved.  
C. **Close** #42 after promoting workflows to `master` (already partially done) and open a thin follow-up for remaining workflow fixes only.

## Checklist for agents opening a PR

```text
[ ] Title matches primary intent
[ ] Implements: ITEM-ID present
[ ] Base is master-staging (or justified master for default-branch workflows)
[ ] Every file in the diff is listed under Changes OR under Non-goals with redirect PR
[ ] Open agent PRs scanned — no silent file overlap
[ ] Review threads on out-of-scope paths answered with “not this PR”
[ ] Gates: repo_gate + termux_smoke when code lands on master-staging
```

## Related docs

- `AGENTS.md` — hard rules
- `docs/PR-SUMMARY-PROCESS.md` — body skeleton
- `docs/AGENTIC-BUILDERS-VS-REVIEWERS.md` — Jules builds, Gemini reviews
- `docs/ops/AGENT_AUTO_RESOLVE.md` — bot feedback → Jules

Signed-off-by: Grok <grok@x.ai>
