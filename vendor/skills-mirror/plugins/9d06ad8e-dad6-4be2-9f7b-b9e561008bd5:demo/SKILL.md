---
description: Factory demo — sample project + Markdown kanban, then the PO factory on a sample initiative (no tracker, no MCP, no setup)
argument-hint:
- folder
---
# Factory demo — first run with zero setup

Builds a small **sample project** with a CodeBase map and a **Markdown kanban** as the tracker, writes its
`docs/factory.config.md`, and (if the user agrees) runs the **PO factory** on a sample initiative. Nothing
external is needed: no tracker, no MCP server, no code host, no Docker. The goal is to let the user see the
factory work in a few minutes and then point them to `/factory:init` for a real project.

**Output language:** write every file you create and every message in the language the user is writing in.
Set `language:` in the generated config to that language (e.g. `pt-BR`, `en`), so the PO run follows it too.

## FOLDER: $ARGUMENTS
Empty → `./factory-demo` (relative to the current directory). Call the absolute path `DEMO`.

---

## STEP 0 — Check the target
1. If `DEMO` exists and is **not empty** → **ASK** whether to use another folder name or stop. Never write
   into or delete an existing non-empty folder.
2. If the current directory is inside a git repository, mention that the demo will be a separate folder
   with its own `git init`, and suggest a path outside the repository if the user prefers.

---

## STEP 1 — Create the sample project
Create these files with the Write tool (contents translated to the output language; identifiers, paths,
config keys and YAML structure stay as written). Then run `git init -q -b main` inside `DEMO`.

### `DEMO/README.md`
Two short paragraphs: this is a demo project of the `factory` plugin (a notes app called **Notely**); the
`tasks/` folder is the kanban the factory writes to; how to run `/factory:po` again with another initiative.

### `DEMO/docs/codebase/README.md` — index
Notely: a web app where people write private notes. Links to `overview.md`, `backend/entities.md`,
`backend/routes-map.md`, `backend/services-map.md`, `frontend/pages.md`, `frontend/components-map.md`.

### `DEMO/docs/codebase/overview.md`
- Stack: NestJS 12 (ESM) + Prisma 7 + PostgreSQL 17 (backend, `backend/`); Next.js 16 + React 19 + MUI v9
  (frontend, `frontend/`); Vitest; Cypress for E2E.
- Architecture: Ports & Adapters (`domain/`, `application/`, `infrastructure/`) per module.
- Modules: `auth` (email + password, JWT in an httpOnly cookie), `users`, `notes`.
- Conventions: error codes `PREFIX_NNN` (e.g. `NOTES_001`); every query on `notes` is scoped by `ownerId`.

### `DEMO/docs/codebase/backend/entities.md`
| Entity | Fields | Notes |
|---|---|---|
| `User` | `id` (uuid), `email` (unique), `name`, `passwordHash`, `createdAt` | `backend/src/users/domain/user.entity.ts` |
| `Note` | `id` (uuid), `ownerId` → User, `title` (≤120), `body` (text), `archived` (bool), `createdAt`, `updatedAt` | `backend/src/notes/domain/note.entity.ts`; index `(ownerId, updatedAt)` |

### `DEMO/docs/codebase/backend/routes-map.md`
| Method | Route | Guard | Use case |
|---|---|---|---|
| POST | `/auth/login` | — | `LoginUseCase` |
| GET | `/notes` | `JwtAuthGuard` | `ListNotesUseCase` (owner only, paginated) |
| POST | `/notes` | `JwtAuthGuard` | `CreateNoteUseCase` |
| PATCH | `/notes/:id` | `JwtAuthGuard` + owner check | `UpdateNoteUseCase` |
| DELETE | `/notes/:id` | `JwtAuthGuard` + owner check | `ArchiveNoteUseCase` (soft: `archived=true`) |

### `DEMO/docs/codebase/backend/services-map.md`
Use cases in `backend/src/notes/application/` (one class per use case, injected `NotesRepository` port);
Prisma adapter in `backend/src/notes/infrastructure/prisma-notes.repository.ts`; no queues, no e-mail sender yet.

### `DEMO/docs/codebase/frontend/pages.md`
| Route | Page | Notes |
|---|---|---|
| `/login` | `app/login/page.tsx` | form → `POST /auth/login` |
| `/notes` | `app/notes/page.tsx` | list + search box; requires session |
| `/notes/[id]` | `app/notes/[id]/page.tsx` | editor with autosave |

### `DEMO/docs/codebase/frontend/components-map.md`
`NoteCard`, `NoteEditor`, `ConfirmDialog`, `AppShell` (top bar + user menu) in `frontend/src/components/`;
data access in `frontend/src/services/notes.service.ts` (fetch wrapper with the API base URL from env).

### `DEMO/tasks/` — the kanban
Create empty folders with a `.gitkeep`: `tasks/epics`, `tasks/backlog`, `tasks/doing`, `tasks/qa`, `tasks/done`.

### `DEMO/docs/factory.config.md`
```yaml
---
project:  notely-demo
company:  Factory demo
language: <the user's language, e.g. pt-BR or en>

tracker:
  driver: markdown
  board_path: tasks
  epic_folder: epics
  story_folder: backlog
  backlog_folder: backlog
  status:
    backlog:     { folder: backlog }
    in_progress: { folder: doing }
    qa_gate:     { folder: qa, label: ready-for-qa }
    in_qa:       { folder: qa, label: in-qa }
    done:        { folder: done }
  labels: { approved: qa-approved, generated: factory-generated }

issue:  { prefix: "NOTE-", id_regex: '^NOTE-\d{3}$', id_format: 'NOTE-%03d' }

git:
  base_branch: main
  dev_base:    main
  protected:   [main]
  branch_prefix: { story: 'feat/', bug: 'fix/' }
  commit_format: '{type}({key}): {message}'
  remote: origin

workspace:
  root: .
  layout: single
  repos: { backend: { path: backend }, frontend: { path: frontend } }

stack:
  backend:  { framework: "NestJS 12 (ESM)", orm: Prisma 7, db: PostgreSQL 17, pkg: pnpm,
              test: "Vitest", build: 'pnpm --dir backend build', error_code_format: 'PREFIX_NNN' }
  frontend: { framework: "Next.js 16 + React 19", ui: "MUI v9", e2e: cypress,
              build: 'pnpm --dir frontend build' }

env:    { app_url: http://localhost:3000, api_url: http://localhost:4000 }
docker: { compose: docker compose, ensure_up: false, run: 'echo "demo: no test suite"' }

evidence:
  mode_var: EVIDENCE_MODE
  slowmo_var: SLOW_MO
  slowmo: 500
  resolution: 1920x1080
  artifacts: { videos: tests/videos, screenshots: tests/screenshots,
               backend_result: tests/backend.json, frontend_result: tests/frontend.json }

tests:
  dir: tests
  layout: { backend: 'tests/backend/{feature}', frontend: 'tests/e2e/{feature}' }
  roles: [user]

docs_map: { codebase: docs/codebase }

product:
  domain: "Personal note-taking web app"
  personas: [individual user, small team member]
  competitors: [Google Keep, Notion, Apple Notes]
  compliance: []

dev:
  developer_split: true
  doc_sync_order: after_self_test
  retries: 3
  commit: { by: pipeline, push: manual }
---

# Project notes
- Demo project created by `/factory:demo`. The backend and frontend folders are described in
  `docs/codebase/` but not implemented, so only the PO factory runs end to end here.
```

---

## STEP 2 — Show and offer the run
Show the created tree (`find DEMO -not -path '*/.git*' | sort`, trimmed) and explain in 3–4 lines: the config,
the CodeBase map, the kanban. Then **ASK** (AskUserQuestion):
- **Run the PO factory now** on the sample initiative **"Share a note with other users"** (translated to the
  output language). It runs 4 agents in sequence, including web research, and takes a few minutes.
- **Only create the project** — stop here and show how to run it later.

---

## STEP 3 — Run the PO factory (if chosen)
Treat `DEMO` as the **project root** for the whole run: every relative path (`docs/factory.config.md`,
`docs/initiatives/`, `tasks/`) is relative to `DEMO`, and shell commands run with `cd DEMO`.
Read and follow `${CLAUDE_PLUGIN_ROOT}/commands/po.md` with `$ARGUMENTS` = the sample initiative, adding
` | Project root: <DEMO>` to every worker prompt line, so each worker resolves its paths inside `DEMO`.
All gates and rules of the PO factory apply as written.

---

## STEP 4 — Wrap up
Report, in the output language:
1. What was produced: `docs/initiatives/<name>/{research,codemap,blueprint,tasks-report}.md`, the epic in
   `tasks/epics/`, the stories in `tasks/backlog/` (list their ids and titles).
2. What to look at first: the blueprint and one story file (the story body carries the full blueprint block).
3. Next step for a real project: open it and run `/factory:init`, then `/factory:po <initiative>`; DEV, QA and
   CR need a real codebase, a tracker (or this Markdown kanban) and, for QA, a way to run tests.

## RULES
- Never write outside `DEMO`; never touch an existing non-empty folder.
- No network access except the web research done by the PO researcher, and only if the user chose to run it.
- If any PO gate fails, stop and report as the PO factory says; the demo files stay in place.
