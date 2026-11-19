---
description: Factory QA — plan, back/front tests, execution and evidence for a task
argument-hint: <task-id> [--model role=value]
---
# Factory QA — Orchestrator of the QA factory (generic/config-driven)

Runs the complete QA pipeline for a task. **Contains nothing project-specific**:
all bindings (tracker, paths, stack, docker, branches) come from the project's `factory.config.md`.

> **SCOPE:** this command is the **orchestrator**; the 4 sub-agents are plugin workers in
> `workers/`: `qa-planner.md`, `qa-backend.md`, `qa-frontend.md`, `qa-runner.md`. Each STEP below
> delegates to the corresponding worker (the block here is the short instruction; the detail lives in the worker).

## Task ID: $ARGUMENTS

If no argument was passed, ask which task to test (format in `config.issue.id_regex`).

---

## STEP 0 — Load and validate config (MANDATORY, before anything else)

1. Read the project's **`factory.config.md`** (at `docs/factory.config.md` in the repo root).
   - If it does not exist: **STOP** — "Run `/factory:init` to create this project's config."
2. **Validate the mandatory keys** (list in `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`). If any of them is missing
   **or** has the value `TBD`: **STOP** and say exactly which key to fill in.
3. Confirm that `config.tracker.status.qa_gate` ≠ `config.tracker.status.in_qa` (distinct selectors).
   If they are equal: **STOP** — "qa_gate and in_qa need distinct selectors (see CONTRACT)."
4. Load the bindings. From here on **never** use a hardcoded value — always `config.<key>`.
5. **E2E driver:** `<name>` = first word of `config.stack.frontend.e2e` in lowercase (absent →
   `cypress`). Confirm that `${CLAUDE_PLUGIN_ROOT}/drivers/e2e/<name>.md` exists; otherwise **STOP** ("create the driver").
   The frontend and runner workers load it on their own.
6. **Tracker Driver:** load `${CLAUDE_PLUGIN_ROOT}/drivers/trackers/{config.tracker.driver}.md`. Every `tracker.<op>(...)` call
   below runs through that driver, as per `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`. The command does not know the tracker.

### Determine the initiative folder
- `task = tracker.fetch($ARGUMENTS)`
- If `task.parent_id` → `docs/initiatives/{normalized-parent-name}/`; otherwise → `docs/initiatives/$ARGUMENTS/`
- `mkdir -p`. **ALL sub-agents save here** — never in the `docs/` root.

### Status gate
- Confirm `task.logical_status == qa_gate`. If not, **STOP** and report (do not re-run a task already in QA).

**Output language:** write every artifact, tracker comment, MR/PR comment and message to the user in
`config.language` (e.g. `pt-BR`, `en`); if the key is absent, use the language the user is writing in. These
instructions are in English; the output is not.


**Models:** resolve each worker's model following the order in `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` → "Models per
role" (arg `--model role=value` → `config.models.<role>` → `config.models.default` → plugin default) and
pass it in the `model` parameter of **every** worker launch. Strip the `--model ...` from `$ARGUMENTS`
before using it as ID/initiative. Value outside `fable|opus|sonnet|haiku|inherit` → **STOP**.

---

## STEP 1 — QA Planner (sub-agent)

```
You are the QA Planner of {config.company}. Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/qa-planner.md`.
Task: $ARGUMENTS  |  Folder: docs/initiatives/{name}/  |  Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT}

1. tracker.fetch($ARGUMENTS) — confirm logical_status == qa_gate
2. tracker.transition($ARGUMENTS → in_qa) + tracker.comment("starting QA")
3. Validate the task branch ({task.branch}) vs {config.git.base_branch}
4. Read the blueprint (task.description / tracker.read_blueprint)
5. git diff --name-only {config.git.base_branch}...{task.branch}   (ONLY list files)
6. Generate the plan → save to docs/initiatives/{name}/qa-plan-$ARGUMENTS.md
7. tracker.comment($ARGUMENTS, plan)
```
**Validation:** plan saved + posted + task in `in_qa`.

> Note: the diff uses `{task.branch}` (resolved by the driver), **not** `{prefix}{id}` — trackers such as
> markdown/ClickUp may derive the branch from `CU-{clickup_id}`, not from the key.

---

## STEP 2 — QA Backend + QA Frontend (IN PARALLEL)

**Backend:**
```
You are the QA Backend of {config.company}. Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/qa-backend.md`.
Task: $ARGUMENTS  |  Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT}
1. Read docs/initiatives/{name}/qa-plan-$ARGUMENTS.md
2. Project helpers: {config.tests.backend_helpers}
3. REAL code in {config.workspace.root}/{config.workspace.repos.backend.path}  (do NOT assume)
4. Compare plan × real code — document divergences
5. Create tests in {config.tests.layout.backend}  (framework: {config.stack.backend.test})
6. 1 scenario = 1 test; full cleanup in teardown
```
**Frontend:**
```
You are the QA Frontend of {config.company}. Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/qa-frontend.md`.
Task: $ARGUMENTS  |  Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT}
1. Read the plan
2. Project custom commands: {config.tests.frontend_cmds}
3. REAL code (routes/components) in {config.workspace.root}/{config.workspace.repos.frontend.path}
4. Table of real selectors BEFORE writing
5. Create E2E in {config.tests.layout.frontend}  (e2e: {config.stack.frontend.e2e})
6. 1 scenario = 1 test; cleanup via API in the after hook
```
**Validation:** both test files created.

---

## STEP 3 — QA Runner (Docker + Execution + Evidence)

```
You are the QA Runner of {config.company}. Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/qa-runner.md`.
Task: $ARGUMENTS  |  Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT}

PHASE 1 — Prepare:
1. git pull of branch {task.branch}; validate vs {config.git.base_branch}
2. Resolve tests dir: TDIR = (config.tests.dir == "auto" ? (qa-tests/ exists ? qa-tests : tests) : config.tests.dir)
3. Services online: curl {config.env.api_url} and {config.env.app_url}
4. Smoke ({config.tests.smoke_script} if defined; otherwise login + 1 endpoint via {config.env.api_url})
5. If it fails: tracker.comment(failure) and STOP

PHASE 2 — Execute:
6. cd {TDIR} && {config.docker.run}
7. Evidence: {config.evidence.mode_var}=true, {config.evidence.slowmo_var}={config.evidence.slowmo}, {config.evidence.resolution}
8. Collect videos/screenshots/logs

PHASE 3 — Report:
9. Report (table per scenario + metrics)
10. ALL PASSED → tracker.comment(report) + tracker.transition(→ done) + tracker.label(approved)
11. FAILED → for each failure: tracker.create_child_bug(task=$ARGUMENTS, title, body) + consolidated comment
12. Save to docs/initiatives/{name}/qa-report-$ARGUMENTS.md

PHASE 4 — Cleanup: tear down containers if applicable.
```

---

## STEP 4 — Final Report

```markdown
## QA Pipeline — $ARGUMENTS — {config.project}

| Step | Status | Output |
|------|--------|--------|
| Planner | ✅ | plan saved + posted |
| Backend | ✅ | X tests |
| Frontend | ✅ | Y tests |
| Runner | ✅/❌ | Z passed, W failed |

Result: ✅ DONE / ❌ W BUGS
- DONE → task in `done`, videos in the evidence, approved for merge
- BUGS → W bugs created (linked to $ARGUMENTS), task stays in `in_qa`
```

---

## TRACKER (driver-based — see `drivers/trackers/`)

This command does **not** map the tracker. It calls the 6 abstract ops (`fetch`, `read_blueprint`,
`transition`, `comment`, `create_child_bug`, `label`) of `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`; the driver in
`config.tracker.driver` translates them. Drivers: `jira`, `clickup`, `gitlab`, `github`, `markdown`.
**Adding a tracker = create `drivers/trackers/<name>.md` + set `tracker.driver`. Not a single line here changes.**

## RULES (generic)
- STEP 0 (load + **validate** config) always first; without a valid config, it does not run.
- Artifacts **always** in `docs/initiatives/{name}/`.
- Each sub-agent in its **own context** (Task). Backend and Frontend in **parallel**.
- Planner failed (status ≠ qa_gate) → **STOP**. Tests not created → **STOP** before the runner.
- Services offline / smoke failed → **do not run tests**, only comment.
- Bugs created **automatically** via `tracker.create_child_bug` (linked to the task, not to the epic).
- Always include time metrics in the report.
