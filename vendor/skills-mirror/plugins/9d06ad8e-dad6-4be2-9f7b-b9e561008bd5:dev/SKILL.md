---
description: Factory DEV — takes a task from the backlog to the QA handoff
argument-hint: <task-id> [--model role=value]
---
# Factory DEV — Orchestrator of the DEV factory (generic/config-driven)

Takes a task from the backlog to the QA handoff: prepares the environment, implements through **isolated agents**
(`factory:dev-*`), reviews, validates and does the commit/handoff. **Nothing project-specific**: tracker, paths, stack,
branch and commit mechanics come from `factory.config.md`. Tracker through the ops of `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`.

> **You are the only one who talks to the tracker and to the human.** The workers are agents (`agents/dev-*.md` in the plugin):
> they have no tracker driver and no channel to ask questions. You resolve the task, pass the fields in the briefing and
> handle their `STATUS:` returns.

## Task ID: $ARGUMENTS
If empty, ask which task to process (format in `config.issue.id_regex`).

---

## STEP 0 — Preparation
1. **Config:** read `docs/factory.config.md`; validate the **DEV factory keys** (`${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`).
   Missing/`TBD` → **STOP**. Load `${CLAUDE_PLUGIN_ROOT}/drivers/trackers/{config.tracker.driver}.md`.
2. **Task + gate:** `task = tracker.fetch($ARGUMENTS)`. Status must be `backlog` or `in_progress`
   (otherwise → **STOP**/WARN: it may be rework or a return from QA). `name = task.parent_id ? kebab(parent) : $ARGUMENTS`;
   `DIR = docs/initiatives/{name}/`; `mkdir -p {DIR}`.
3. **Branch:** `BRANCH = task.branch` (driver-resolved; e.g. ClickUp = `CU-{clickup_id}`, shared between Stories
   of the same epic; PHCS = `{branch_prefix}{slug}`). Do **not** assume `{prefix}{id}`.
4. **Affected repos:** detect backend/frontend from the task body (paths/keywords from the conventions in
   `config.stack` + `config.workspace.repos`). None detected → **ASK** the human.
5. **Bring up the stack** if `config.docker.ensure_up: true` (`docker compose -f {config.docker.compose} up -d` + health in `config.env`).
6. **Stash WIP** in each affected repo (`git stash push -u -m "auto-stash {id}"`) — preserves it, does not discard it.
7. **Transition:** `tracker.transition($ARGUMENTS → in_progress)`.
8. **Branch in each affected repo:** `git fetch {config.git.remote}`; checkout `BRANCH` if it exists
   (local/origin), otherwise **create it from `config.git.dev_base`** (⚠️ `dev_base`, not `base_branch`).
9. **Output language:** write every artifact, tracker comment, MR/PR comment and message to the user in
   `config.language` (e.g. `pt-BR`, `en`); if the key is absent, use the language the user is writing in. These
   instructions are in English; the output is not.

### Common briefing (build it once; it goes into every agent's prompt)
```
task_id: $ARGUMENTS | config_path: docs/factory.config.md | initiative_dir: {DIR}
branch: {BRANCH} | repos: {affected, with each one's path}
task: type={task.type} parent_id={task.parent_id} complexity={task.complexity}
      depends_on={task.depends_on} description=<task body>
```


**Models:** resolve each worker's model following the order in `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` → "Models per
role" (arg `--model role=value` → `config.models.<role>` → `config.models.default` → plugin default) and
pass it in the `model` parameter of **every** worker launch. Strip the `--model ...` from `$ARGUMENTS`
before using it as ID/initiative. Value outside `fable|opus|sonnet|haiku|inherit` → **STOP**.

---

## PIPELINE (agents; each in its own context)
Base order: **tech-lead → developer(s) → [doc-sync] → code-review → self-test → [doc-sync]**.
**doc-sync** comes in at the point defined by `config.dev.doc_sync_order` (`before_review` or `after_self_test`).

**Return protocol** — every agent returns `STATUS:`. Handle it like this, always:
| STATUS | Orchestrator action |
|---|---|
| `OK` / `PASSED` / `APPROVED` | move on to the next step |
| `APPROVED_WITH_NOTES` | move on; carry the 🟡 into the final report |
| `REJECTED` / `FAILED` | back to the developer with the report; **counts 1 retry** (`config.dev.retries`) |
| `BLOCKED` | **STOP and ASK the human** using `blocked_reason` (the agent has no channel) |
| `UPSTREAM_BUG` | escalate to the human; does **not** consume a retry |

### STEP 1 — Tech Lead (agent `factory:dev-tech-lead`) → `{DIR}/tech-lead-$ARGUMENTS.md`
Prompt = common briefing. **Gate:** artifact saved (impact map for a Story, root cause for a Bug) and
`scope` returned (`backend`/`frontend`/`both`).

### STEP 2 — Developer (agent `factory:dev-developer`) → code in the repos
Prompt = common briefing + `plan_path: {DIR}/tech-lead-$ARGUMENTS.md` + `scope` + `repo_path`.
- **`config.dev.developer_split: true`** and `scope == both` → launch **two instances in the same message**
  (one `scope: backend`, the other `scope: frontend`), running in parallel in separate repos.
- **`developer_split: false`** → one instance with `scope: both`.
- **Re-run** (after REJECTED/FAILED) → launch **only the `scope_to_fix`**, with `review_report` in the prompt.

**Gate:** `git diff --stat` consistent with the plan in each repo. The developer does **not** touch `docs/` nor commit.

### Doc Sync (position = `config.dev.doc_sync_order`) → `{DIR}/doc-sync-report-$ARGUMENTS.md`
Agent `factory:dev-doc-sync`; prompt = common briefing. If `config.dev.commit.by == doc_sync`, **it commits**
(code+docs + submodule pointer); otherwise it only edits on disk.

### STEP 3 — Code Review (agent `factory:dev-code-reviewer`, up to `config.dev.retries` attempts)
Prompt = common briefing + `plan_path` + `attempt` + `developer_notes`.
`REJECTED` → STEP 2 with `scope_to_fix` + `review_report`. `rerun_doc_sync: yes` → re-run doc-sync.
Retries exhausted → escalate and **STOP**.

### STEP 4 — Self Test (agent `factory:dev-self-test`, up to `config.dev.retries` attempts)
Prompt = common briefing + `plan_path`.
`FAILED` → STEP 2 with `scope_to_fix` + `failure`. Retries exhausted → escalate and **STOP**.
**Publish** the returned `self_test_section` on the task: `tracker.comment($ARGUMENTS, self_test_section)`
(or `tracker.append`, depending on the driver) — the agent does not write to the tracker.

---

## STEP 5 — Wrap-up (commit + handoff)
According to `config.dev.commit`:
- **`by: pipeline`**: selective commit in each affected repo with `config.git.commit_format`
  (`{key}`→$ARGUMENTS, prefix by `task.type` via `config.git.branch_prefix`). Doc-sync has already edited (not committed).
- **`by: doc_sync`** (PHCS): doc-sync has already committed code+docs and bumped the submodule pointer.
- **Push** according to `config.dev.commit.push`: `manual` → does **not** push (separate `/push` skill, after QA);
  `mr` → opens a Merge Request.
- **Transition:** `tracker.transition($ARGUMENTS → qa_gate)` (handoff to the QA factory).
- Restore the stashed WIP if desired (`git stash list | grep {id}`).

### Final report
```markdown
## DEV Pipeline — $ARGUMENTS — {date} — {config.project}
Type: {task.type} | Branch: {BRANCH} | Repos: backend/frontend | Status: backlog → in_progress → qa_gate
| Step | Status | Detail |
| 0 Prep · 1 Tech Lead · 2 Developer · Doc-Sync · 3 Review · 4 Self-Test · 5 Commit/Handoff |
Pending 🟡 caveats: {from APPROVED_WITH_NOTES}
Next: task in `qa_gate` → run the QA factory (`/factory:qa $ARGUMENTS`).
```

## RULES
- Each worker is an **agent** in its own context; the role body is its system prompt — do **not** repeat the
  role's rules in the prompt, pass only the briefing (task/paths/scope).
- **Only you** talk to the tracker and the human. `BLOCKED` from any agent = a question to the human, do not improvise the answer.
- Step failed `config.dev.retries`× → **STOP** and escalate. `UPSTREAM_BUG` does not consume a retry.
- The developer **NEVER** edits `docs/` (doc-sync does). The code-reviewer may request a doc-sync re-run.
- **NEVER** commit/branch on `config.git.protected`. **NEVER** `push --force` (`/push` uses `--force-with-lease`).
- The dev branch comes from `config.git.dev_base`; it may be **shared** (several commits accumulate) — see `issue.branch_field`.
- Push is not automatic when `commit.push == manual`. Moving `qa_gate → in_qa → done` is the QA factory's job.
- When in any doubt, **ask the human**.
