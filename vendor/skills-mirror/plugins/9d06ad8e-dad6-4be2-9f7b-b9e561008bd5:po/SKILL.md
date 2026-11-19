---
description: Factory PO — initiative → research, codemap, blueprint and Epic+Stories in the tracker
argument-hint: <initiative> [--model role=value]
---
# Factory PO — Orchestrator of the PO factory (generic/config-driven)

Turns a roadmap **initiative** into a ready Epic + Stories in the tracker, through 4 isolated
sub-agents in sequence. **Nothing project-specific**: product, codebase, stack and tracker come from
`factory.config.md`. Tracker through the authoring ops of `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`.

## INITIATIVE: $ARGUMENTS
If empty, ask which initiative to process (e.g. "Yampi integration") or use the most recent
artifact in `docs/initiatives/<x>/`.

---

## STEP 0 — Load and validate config (MANDATORY)
1. Read `docs/factory.config.md`. Missing → **STOP** ("Run `/factory:init`").
2. Validate the **PO factory keys** (`${CLAUDE_PLUGIN_ROOT}/CONTRACT.md`): `product.{domain,personas}`, `docs_map.codebase`,
   `stack.{backend,frontend}`, and the tracker authoring keys (markdown→`tracker.{board_path,epic_folder,story_folder}`+`issue.id_format`; gitlab→`tracker.project_path`; github→`tracker.repo`). Missing/`TBD` → **STOP** saying which one.
3. Load the bindings (never a hardcoded value). Load `${CLAUDE_PLUGIN_ROOT}/drivers/trackers/{config.tracker.driver}.md` (used in step 4).
4. Initiative folder: `name = kebab-case($ARGUMENTS)` → `docs/initiatives/{name}/`. `mkdir -p`.
5. **Output language:** write every artifact, tracker comment, MR/PR comment and message to the user in
   `config.language` (e.g. `pt-BR`, `en`); if the key is absent, use the language the user is writing in. These
   instructions are in English; the output is not.


**Models:** resolve each worker's model following the order in `${CLAUDE_PLUGIN_ROOT}/CONTRACT.md` → "Models per
role" (arg `--model role=value` → `config.models.<role>` → `config.models.default` → plugin default) and
pass it in the `model` parameter of **every** worker launch. Strip the `--model ...` from `$ARGUMENTS`
before using it as ID/initiative. Value outside `fable|opus|sonnet|haiku|inherit` → **STOP**.

---

## PIPELINE (fixed order; each step = sub-agent via Task, isolated context)
Apply the **gate** after each step: validate the expected artifact; failed → **STOP** and report.

### STEP 1 — Researcher → `docs/initiatives/{name}/research.md`
```
Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/po-researcher.md`. Initiative: $ARGUMENTS | Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT} | Folder: docs/initiatives/{name}/
```
**Gate:** file exists with a comparison table + MVP recommendation (+ compliance check if `config.product.compliance` is non-empty).

### STEP 2 — Code Map → `docs/initiatives/{name}/codemap.md`
```
Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/po-codemap.md`. Initiative: $ARGUMENTS | Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT} | Folder: docs/initiatives/{name}/
```
**Gate:** mapped what already exists (via `config.docs_map.codebase`) + gaps + dependencies + risks.

### STEP 3 — Blueprint → `docs/initiatives/{name}/blueprint.md`
```
Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/po-blueprint.md`. Initiative: $ARGUMENTS | Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT} | Folder: docs/initiatives/{name}/
```
**Gate:** every feature has backend + frontend + error handling + testable acceptance criteria + complexity.

### STEP 4 — Tasks → Epic + Stories in the tracker
```
Read and follow `${CLAUDE_PLUGIN_ROOT}/workers/po-tasks.md`. Initiative: $ARGUMENTS | Config: docs/factory.config.md | Plugin: ${CLAUDE_PLUGIN_ROOT} | Folder: docs/initiatives/{name}/
```
**Gate:** Epic + Stories created (via `tracker.create_epic`/`create_story`), linked, and `tasks-report.md` lists the IDs.

> Researcher and Code Map *could* run in parallel, but the sequence is safer (the code map
> benefits from the research). Blueprint depends on both; Tasks depends on the blueprint.

---

## STEP 5 — Final report and handoff
```markdown
## PO Pipeline — {Initiative} — {date} — {config.project}
| Step | Status | Output |
|------|--------|--------|
| Researcher | ✅ | docs/initiatives/{name}/research.md |
| Code Map | ✅ | docs/initiatives/{name}/codemap.md |
| Blueprint | ✅ | docs/initiatives/{name}/blueprint.md |
| Tasks | ✅ | EPIC + N Stories |

### Stories created (handoff to the DEV factory)
| ID | Feature | Complexity |
### Next steps
1. PO: review blueprint + Stories.  2. DEV: start with the first Story (DEV pipeline).
```

## RULES
- STEP 0 always first; without a valid config (or with `TBD`), it does not run.
- Each sub-agent in its **own context** (Task). Fixed order: Researcher → Code Map → Blueprint → Tasks.
- Gate failed at any step → **STOP** and report; do not skip or invent a missing artifact.
- All intermediates in `docs/initiatives/{name}/` (traceability).
- Stories **are born in the tracker backlog** (markdown: `story_folder`; gitlab/github: open issue) — promoting them is the DEV factory's job.
- The factory **creates and organizes, it does not prioritize** the Sprint (human decision).
