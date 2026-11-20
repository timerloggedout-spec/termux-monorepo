---
description: Factory CR — code review of a task's MRs/PRs with a human gate
argument-hint: <task-id> [--model role=value]
---
# Factory CR — Orchestrator of the Code Review factory (generic/config-driven)

Receives a task id, discovers the MRs/PRs linked to it, reviews each one, **shows the findings and
waits for the human verdict (approve/reject + why)**, comments on the MR **and** on the task, and moves the status:
approved → advances; rejected → returns. **Nothing project-specific**: tracker, code host, stack,
branch and status come from `factory.config.md`. Task through the ops of `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` (tracker); MR through SCM ops (`${CLAUDE_PLUGIN_ROOT}/drivers/scm/<driver>.md`).

> **Safety invariant:** this factory is **read-only on git** — it uses `glab/gh mr diff` and, at
> most, `git fetch`+`git diff` against remote refs. **It NEVER checks out nor changes a local branch.**

## Task ID: $ARGUMENTS
If empty, ask which task to review (format in `config.issue.id_regex`).

---

## STEP 0 — Preparation
1. **Config:** read `docs/factory.config.md`; validate the **CR factory keys** (see `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` → "Required
   keys of the CR factory"). Missing/`TBD` → **STOP**. Load `${CLAUDE_PLUGIN_ROOT}/drivers/trackers/{config.tracker.driver}.md` **and**
   `${CLAUDE_PLUGIN_ROOT}/drivers/scm/{config.scm.driver}.md`.
2. **Task + gate:** `task = tracker.fetch($ARGUMENTS)`. **Keep `previous_status = task.logical_status`** (for rollback).
   Status must be `review_gate` (otherwise → **WARN** and ask whether to proceed anyway; it may be rework).
3. **Output language:** write every artifact, tracker comment, MR/PR comment and message to the user in
   `config.language` (e.g. `pt-BR`, `en`); if the key is absent, use the language the user is writing in. These
   instructions are in English; the output is not.


**Models:** resolve each worker's model following the order in `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` → "Models per
role" (arg `--model role=value` → `config.models.<role>` → `config.models.default` → plugin default) and
pass it in the `model` parameter of **every** worker launch. Strip the `--model ...` from `$ARGUMENTS`
before using it as ID/initiative. Value outside `fable|opus|sonnet|haiku|inherit` → **STOP**.

---

## STEP 1 — Discover the MRs
1. `mrs = scm.find_mrs(task)` (S1): links in the body/comments **+ fallback** by `scm.branch_convention`;
   filters `target == config.scm.mr_target`; excludes the twin `scm.exclude_branch_suffix`. Warn if it came from the fallback.
2. For each MR, `scm.mr_view` (S2): **skip** the `merged`/`closed` ones (record as skipped, no CR).
3. **No open MR at all** (nothing found, or all merged/closed): do **NOT** move the status. Inform the user,
   offer to enter MRs manually; if none, finish leaving the task in `previous_status`.
4. Only when there is ≥1 open MR: `tracker.transition($ARGUMENTS → in_review)`.

---

## STEP 2 — Review each MR (isolated sub-agents per MR)
For each open MR, launch **both workers in parallel** (same message, their own contexts):
1. `Read and follow ${CLAUDE_PLUGIN_ROOT}/workers/cr-reviewer.md. MR: {repo}!{iid} | Task: $ARGUMENTS | Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT}`
   → reads the diff (S3, read-only), derives the checklist from `config.stack` + conventions in `config.docs_map.codebase`,
   and returns findings (🔴 Critical / 🟡 Important / 🟢 Suggestion / 📄 Doc) per file:line.
2. `Read and follow ${CLAUDE_PLUGIN_ROOT}/workers/cr-security.md. MR: {repo}!{iid} | Task: $ARGUMENTS | Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT}`
   → dedicated security pass over the same diff; returns only **HIGH/MEDIUM** with confidence ≥0.7,
   each with an exploitation scenario. Mapping: **HIGH → 🔴**, **MEDIUM → 🟡**.

Consolidate both returns per MR, deduplicating: if both point to the same `file:line`, keep
**the highest severity** and the security description (which carries the exploitation scenario).
`0 HIGH · 0 MEDIUM` is a valid result — record the pass as done, do not omit it.

---

## STEP 3 — Present the findings (consolidated)
Show the user, per MR, the findings table + summary. **Do not decide on your own.** Format:
```markdown
## Code Review — Task $ARGUMENTS — {config.project}
### MR {repo}!{iid} — {title}  ({source_branch} → {target_branch})
| Sev | File:line | Description |
| 🔴/🟡/🟢/📄 | ... | ... |
### Summary: N critical · M important · … + positive points
### 🔒 Security: N HIGH · M MEDIUM (or "no findings") — with exploitation scenario on the HIGHs
```

## STEP 4 — Human verdict (mandatory GATE)
Use `AskUserQuestion`:
- **Default recommendation:** Reject if there is ≥1 🔴 (or a 🟡 that the user confirms as blocking); otherwise Approve.
  **Every security HIGH is 🔴** — highlight it in the recommendation, with the exploitation scenario.
- Options: **"Approve"** / **"Reject"**. **Capture the "why"** (the user's reason — it goes into the comments).
- Never advance/return without an explicit answer.

## STEP 5 — Comment (MR + task) and move the status
With the verdict + reason:
1. **On each MR** (`scm.mr_comment`, S4): post the CR (verdict + included findings + the human's reason).
2. **On the task** (`tracker.comment`): post the consolidated summary (MRs reviewed/skipped + verdict + reason + actions).
3. **Transition:**
   - **Approved** → `tracker.transition($ARGUMENTS → review_approved)` (+ `tracker.label(approved)` if configured). **Advances.**
   - **Rejected** → `tracker.transition($ARGUMENTS → review_returned)`. **Returns.**
4. Tell the user the final status and the links of the posted comments.

### Final report
```markdown
## Factory CR — $ARGUMENTS — {date} — {config.project}
MRs: {reviewed} reviewed, {skipped} skipped | Verdict: {APPROVED|REJECTED} — "{reason}"
Status: {previous_status} → in_review → {review_approved|review_returned}
Comments: {MR links} + {task link}
```

## RULES
- **Read-only on git:** never `checkout`/branch switch/commit. Diff always via `mr diff` or `git diff` against a remote ref.
- **The human gate is mandatory** (STEP 4) — the factory reviews and recommends; **the human is the one who approves/rejects**, with a reason.
- Only move to `in_review` if there is an open MR; no MR → leave it in `previous_status` (rollback) and handle it with the user.
- Comment **in both places** (MR and task). Focus on real problems, not style (the linter takes care of that).
- Each MR in its own sub-agents (isolated context): `cr-reviewer` **+** `cr-security`,
  launched in parallel. When in any doubt, **ask the human**.
- Suite failure/error caused by a pre-release bug (not by the MR's code) → does not count as 🔴; flag it as `upstream_bug`.
