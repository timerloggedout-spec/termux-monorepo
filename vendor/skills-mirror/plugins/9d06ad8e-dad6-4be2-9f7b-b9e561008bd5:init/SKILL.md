---
description: Factory Init — generates the project's docs/factory.config.md (detects stack and tracker)
argument-hint:
- project-path
---
# Init Factory — Generator of `docs/factory.config.md` (generic/config-driven)

Detects the stack and the tracker of the project in the target directory and **generates a filled-in `docs/factory.config.md`**,
following the schema in `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`. It is the missing step: the `factory-*` commands say
"Run `/factory:init`" when the config does not exist. This command **creates** that config — it does not invent
values: whatever it cannot infer safely becomes **`TBD`** (with a comment explaining why), and the
final validation points back to each `TBD` for you to complete.

## TARGET: $ARGUMENTS
Project path. Empty → use the **cwd**. The config is always written to `<target>/docs/factory.config.md`.

---

## STEP 0 — Pre-check (MANDATORY)
1. Resolve `<target>` (arg or cwd). Confirm it is a repository (`<target>/.git` or a subfolder of a repo).
2. If `<target>/docs/factory.config.md` **already exists** → show its first 5 lines and **ASK**:
   overwrite, update only the `TBD`s, or abort. No clear answer → **STOP**.
3. Load `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` (source of the required keys) and the available drivers
   (`ls ${CLAUDE_PLUGIN_ROOT}/drivers/trackers/*.md`). Never write a key outside the CONTRACT schema.

---

## STEP 1 — Detect the stack (read-only)
Use `Glob`/`Grep`/`Read` (or an `Explore` sub-agent) on `<target>`. **Infer, don't guess** — without
clear evidence, mark `TBD`.

- **Language/framework/orm/test/build** (per repo):
  - `composer.json` + `artisan` → Laravel/PHP (orm Eloquent, test PHPUnit, pkg composer).
  - `package.json`: `@nestjs/*`→NestJS · `next`→Next.js · `@angular/core`→Angular.
    ORM: `prisma`→Prisma · `@mikro-orm`/`typeorm` likewise · `waterline`→Waterline.
    Test: `vitest`/`jest` (dev-deps); E2E: `cypress`→`e2e: cypress` · `@playwright/test`→`e2e: playwright`
    (the value picks the driver `drivers/e2e/<name>.md`; a tool without a driver → warn, as with the tracker).
  - `build`: read `scripts` in `package.json` (`build`/`lint`) or the artisan equivalents; fill in the
    real command (e.g. `pnpm build`). If you don't know the boot-check → `TBD`.
  - **Outside the list above → suggestion by evidence** (do not leave a silent `TBD`). Collect signals and pick the
    strongest candidate:
    - runtime `dependencies` (not dev-deps) whose package is a framework/ORM, cross-checked with `scripts.start`/`dev`
      (the binary called there is usually the framework) and with the `main`/entrypoint;
    - characteristic config files at the repo root (`*.config.*`, `.<name>rc`, `<name>-cli.json`,
      `config/`/`api/` folders with a typical structure);
    - outside Node: `pyproject.toml`/`requirements.txt`/`manage.py`, `Gemfile`, `pom.xml`/`build.gradle`,
      `go.mod`, `Cargo.toml` → the main dependency declared there.
    Write it as `TBD   # suggestion: "<Framework>" — evidence: <file:key>, <file:key>`. **At least 2
    independent pieces of evidence** to suggest; with only 1 → `TBD   # weak candidate: <name> (<evidence>)`;
    with 0 → `TBD   # no evidence`. The same rule applies to `orm`, `test`, `e2e` and `build`.
- **Package manager:** `pnpm-lock.yaml`→pnpm · `yarn.lock`→yarn · `package-lock.json`→npm · `composer.lock`→composer.
- **Layout / repos** (`workspace.layout` + `workspace.repos.{backend,frontend}.path`):
  `.gitmodules`→`monorepo-submodule` · `projects/*` or separate folders→`multi-repo` · a single app→`single`.
  Find the backend/frontend paths relative to `workspace.root`.
- **Docker:** `docker-compose.yml`/`compose.yaml` (root or per repo). Extract container/service names and
  ports for `docker.*` and `env.{app_url,api_url}`. No local stack that can be brought up → `docker.ensure_up: false`.
- **Git:** default branch (`git -C <target> symbolic-ref --short refs/remotes/origin/HEAD` or `git remote show origin`)
  → `git.base_branch`/`git.dev_base` (repeat the value if they coincide; **do not assume they are equal** — see CONTRACT).
  `git.remote` (default `origin`); `protected` = permanent branches you find (`main`/`master`/`develop`/`dev`/release globs).
- **Docs/conventions:** find the CodeBase folder (`docs/`, `docs/backend|frontend|shared`) → `docs_map.codebase`;
  conventions (`docs/conventions`) → `docs_map.conventions`.
- **Output language** (`language`): infer from the language of the README and of the recent commit messages
  (`git -C <target> log -20 --format=%s`) → a locale tag (e.g. `pt-BR`, `en`). Mixed or no signal → `en`
  as the default. It is always confirmed with the human in STEP 2.5.

---

## STEP 2 — Tracker (driver + mapping)
1. **Detect candidate:** remote contains `gitlab`→`gitlab` · `.gitlab-ci.yml` likewise · remote on `github.com` with issues enabled→`github` · kanban folder of MDs
   (e.g. `tasks/{todo,in-progress,em-qa,done}`)→`markdown` · known Jira project→`jira`.
2. **CONFIRM the driver with the human** (it is the highest-impact choice — do not decide alone if in doubt).
   A tracker that has no driver yet = create `drivers/trackers/<name>.md` (model B) — warn, do not improvise in the config.
3. Fill in the driver's keys (see CONTRACT) and the **logical status map**:
   - `gitlab` → `project_path`; status = `{state, label?}`; **`qa_gate` ≠ `in_qa`** (same `state` + distinct label).
   - `github` → `repo` (`owner/repo` from the remote); status = `{state: open|closed, label?}`, same distinct-label rule;
     `epic_type` only if the organization uses *issue types* (`gh api repos/{repo} --jq .has_issues` confirms issues are enabled).
   - `jira` → `cloud_id`, `project_key`; status = native name (`qa_gate:"PR"`, `in_qa:"Em QA"`, `done:"Done"`).
   - `markdown` → `board_path`, `epic_folder`, `story_folder`, `backlog_folder`; status = `{folder, label?}`;
     `issue.id_format` (e.g. `APP-%03d`). `qa_gate`/`in_qa` may share a folder if the label distinguishes them.
   - **Critical rule (CONTRACT):** `qa_gate` and `in_qa` MUST resolve to **distinct** selectors. If they collapse → `TBD`.
4. `issue.{prefix,id_regex}` (+ `id_format` for markdown; `branch_field` if the branch does **not** derive from the key).
5. `tracker.labels.approved` is required; the others (`needs_human`, `upstream_bug`, `generated`...) when the flow uses them.

---

## STEP 2.5 — Confirm suggestions (before writing)
If STEP 1 produced `# suggestion:`/`# weak candidate:` entries, **ask the human in a single round**
(`AskUserQuestion`, one question per key, up to 4 per round): option 1 = the suggestion (with the evidence in the
description), option 2 = the alternative candidate if there is one; "Other" lets them type. Always include
`language` in this round (option 1 = the detected value, option 2 = the other of `pt-BR`/`en`). Confirmed answer →
write the **concrete value** (no `TBD`). No answer / "don't know" → keep `TBD` **with the suggestion
comment** (STEP 0 of the factories shows the suggestion when it stops).

---

## STEP 3 — Generate `docs/factory.config.md`
`mkdir -p <target>/docs`. Write the YAML front-matter following the CONTRACT schema, **in this order** (omit blocks
that make no sense for the project, but keep the required ones). Every inferred value is written concretely; the rest is
`TBD   # why`. Skeleton:

```yaml
---
# ════════════════════ FACTORY CONFIG — <Project> ════════════════════
project:   <slug>
company:   <company>
language:  pt-BR               # output language of artifacts, comments and messages (e.g. pt-BR, en)

tracker:
  driver:   <gitlab|github|jira|clickup|markdown|...>
  # + driver keys (project_path | cloud_id+project_key | board_path+epic/story_folder)
  status:
    backlog:     <selector>    # only required for the DEV factory
    in_progress: <selector>    # same
    qa_gate:     <selector>    # DEV→QA handoff — DISTINCT from in_qa
    in_qa:       <selector>    # DISTINCT from qa_gate
    done:        <selector>
  labels: { approved: <label> }

issue:    { prefix: "<P->", id_regex: '<regex>' }   # +id_format/branch_field depending on the driver

git:
  base_branch: <origin/...>    # QA diffs against this
  dev_base:    <origin/...>    # DEV branches off this (may == base_branch — repeat it)
  protected:   [ ... ]
  branch_prefix: { story: 'feat/', bug: 'fix/' }
  commit_format: '<...>'
  remote: origin

workspace:
  root:   <abs or .>
  layout: <single|multi-repo|monorepo-submodule>
  repos:  { backend: { path: <...> }, frontend: { path: <...> } }

stack:
  backend:  { framework: "<...>", orm: <...>, db: <...>, pkg: <...>, test: "<...>", build: '<...>' }
  frontend: { framework: "<...>", ui: "<...>", e2e: <cypress|playwright|...>, build: '<...>', lint: '<...>' }
  arch_notes_doc: <...>

env:    { app_url: <...>, api_url: <...> }

docker:
  compose:   <docker compose | file>
  ensure_up: <true|false>      # false if the app is remote
  run:       '<test command>'
  # run_frontend: '<...>'      # present → back/front run separately

evidence:
  mode_var: EVIDENCE_MODE
  slowmo_var: SLOW_MO
  slowmo: 500
  resolution: 1920x1080
  artifacts: { videos: <...>, screenshots: <...>, backend_result: <...>, frontend_result: <...> }

tests:
  dir: <...>
  layout: { backend: '<...>', frontend: '<...>' }
  # backend_helpers / frontend_cmds / roles / seeder / smoke_script depending on the project

docs_map: { codebase: <docs...>, conventions: <...> }

product:                       # context for the PO factory
  domain: "<...>"
  personas:    []
  competitors: []
  compliance:  []

dev:                           # mechanics of the DEV factory
  developer_split: <true|false>
  doc_sync_order:  after_self_test
  retries:         3
  commit: { by: doc_sync, push: <mr|push> }

# models:                      # optional — omitted = plugin defaults (CONTRACT → "Models per role")
#   default: inherit           # level 1 fable · level 2 opus · level 3 sonnet
#   dev.developer: opus
---

# Project notes
- <quirks, inherited inconsistencies, "do not run X", etc.>
```

---

## STEP 4 — Validate and report (same criteria as STEP 0 of the factories)
1. Re-read the generated config and check the **required keys of `factory.config.md`** (CONTRACT):
   `project`, `company`, `tracker.driver`, `tracker.status.{qa_gate,in_qa,done}` (**distinct!**),
   `tracker.labels.approved`, `issue.id_regex`, `git.base_branch`, `workspace.root`,
   `workspace.repos.{backend,frontend}.path`, `tests.dir`, `tests.layout.{backend,frontend}`,
   `stack.backend.test`, `stack.frontend.e2e`, `env.{app_url,api_url}`, `docker.{run,ensure_up}`,
   `evidence.{mode_var,slowmo_var,slowmo,resolution}`, `evidence.artifacts.*`
   (+ driver extras: jira→`cloud_id,project_key`; markdown→`board_path`; gitlab→`project_path`; github→`repo`).
2. List, per factory, what is still missing for each one to run cleanly:
   - **PO:** `product.{domain,personas}`, `docs_map.codebase`, `stack.{backend,frontend}`, tracker authoring.
   - **DEV:** `tracker.status.{backlog,in_progress,qa_gate}`, `git.{dev_base,protected,branch_prefix,commit_format,remote}`,
     `workspace.{root,repos}`, `stack.*.build`, `docs_map.codebase`, `dev.*`.
   - **QA:** the `docker`/`evidence`/`tests` keys above (E2E configured? otherwise mark QA as deferred).
3. **Final report:**
```markdown
## Init Factory — {project} — {date}
Config: <target>/docs/factory.config.md  (created|updated)
| Block | Status |
|-------|--------|
| Detected stack | ✅ <summary> |
| Tracker | ✅ driver=<...> (or ⚠️ confirm) |
| Output language | ✅ <language> |
| Pending TBDs | <N> → <list of keys> |
| Suggestions | <N confirmed> written · <M pending> left as `TBD # suggestion` → <key: suggested value> |
### Ready to run
- PO: <yes | missing X>   · DEV: <yes | missing Y>   · QA: <yes | deferred: missing Z>
### Next step
- Fill in the TBDs and run `/factory:po` (or `/factory:dev`) on the project.
```

## RULES
- **Never invent** a tracker/branch/url value just to "close" the config — `TBD` with a reason beats a wrong value.
- A suggestion **is not a value**: it only becomes concrete with human confirmation (STEP 2.5); without it, it stays in the `TBD` comment.
- Only write keys from the `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` schema; tracker without a driver → warn (create `drivers/trackers/<name>.md`), do not force it.
- `qa_gate` and `in_qa` **ALWAYS distinct** (otherwise STEP 0 of the factories re-runs a task in progress).
- Detection is **read-only**; the only write is `docs/factory.config.md` (+ `mkdir -p docs`).
- When in relevant doubt (driver, base_branch vs dev_base, ensure_up, language), **ask** instead of assuming.
