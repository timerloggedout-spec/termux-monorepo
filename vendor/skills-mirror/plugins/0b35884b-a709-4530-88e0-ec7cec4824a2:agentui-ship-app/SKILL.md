---
name: agentui-ship-app
description: Create, edit, build and ship an AgentUI app end to end with the agentui CLI — from `project create` to a live URL. Use when the user wants a new hosted app, internal tool, dashboard, portal or prototype; when they want to change an existing AgentUI project (sync → edit → push → build); when they ask to deploy, publish, rebuild, or "make it live"; or when they need serverless `/api` endpoints, app settings (login required, custom domain, home page), environments (staging vs production), secrets, or a shareable preview link.
---

# Ship an AgentUI app

## The mental model

A "project" in the CLI is one **workflow** on the platform (an `APP_V2` app). Its
components, pages, functions and entity schemas are server-side records. `sync` pulls
them down as plain files, `push` sends changes back, `build` makes them live.

**Push ≠ live.** A push only flags the app for a rebuild; the live app serves the
previous build until a rebuild runs. Close the gap deterministically with
`agentui build` (`--yes` on production) or `agentui project push --build`.

## Brand and project knowledge

When the workspace has a theme, the platform writes a **design package** into the app:
`brand.css` (the tokens, imported by the app) and `design/DESIGN.md` (the styling rules).
`sync` pulls them like any other file. Before styling a screen,
read `design/DESIGN.md` and use the classes it names; never paste colour values into
components. Also read `.agentui/WORKSPACE.md` (locale defaults, workspace instructions)
and `.agentui/PROJECT_KNOWLEDGE.md` (this app's standing requirements).

```bash
agentui design status --json               # current brand? which files did this app edit?
agentui design import <https-url|file> --save [--app]   # shadcn/tweakcn JSON or CSS → theme
agentui design sync --json                 # write the current brand into this app now
agentui design sync --force --yes          # also overwrite brand files this app edited
agentui project knowledge --json           # read Project Knowledge
agentui project knowledge --file notes.md  # replace it (--set "<text>", --clear)
```

Theme tokens in `brand.css` (`:root` / `.dark`) are rewritten on every theme change; rules
and custom variables you add there are kept. Change an app's colors with its theme, not by
editing token values. `design/DESIGN.md` is only rewritten if nobody edited it;
`design sync --force --yes` resets both files to the theme. `push --delete` never archives `brand.css` or `design/DESIGN.md`.

## New app

```bash
agentui project create --name "My App"      # creates the workflow AND scaffolds locally
cd my-app && cat AGENTS.md
```

Where it scaffolds: the current directory if empty, otherwise `./<project-name>`;
`--dir <path>` overrides, `--force` allows a non-empty directory, `--no-sync` creates
the project server-side only. `--workspace <id>` creates it in (and switches to)
another workspace.

Only `APP_V2` workflows can be created — legacy `APP`/`AUTOMATION`/`TOOL` types are
not executable end to end.

## Existing app

```bash
agentui workspace list && agentui workspace select <workspaceId>
agentui project list                  # the "Project ID" column IS the workflow id
mkdir my-project && cd my-project
agentui project sync <workflowId>     # pull it down
```

Cloned the repo from git and only missing the gitignored state files? Use
`agentui project init <workflowId>` — it writes `.agent.json` + `.agent-manifest.json`
and never touches your source files.

`sync` is 3-way-merge aware. If local edits would be overwritten it aborts and lists
the conflicts; re-run with `--theirs` (take server), `--ours` (keep local) or `--merge`
(write the server copy to `<path>.theirs` and leave your file alone).

## Project layout

```text
my-project/
├── .agent.json            # projectId (= workflow id), appId, environment  (gitignored)
├── .agent-manifest.json   # component ids, versions, codeHash per file     (gitignored)
├── AGENTS.md              # the platform's own build guide — READ IT
├── Layout.jsx             # optional app shell
├── components/*.jsx       # COMPONENT
├── pages/*.jsx            # PAGE        → routes
├── functions/*.jsx        # FUNCTION    → https://<app>/api/<name>
├── entities/*.json        # ENTITY      → real database tables
├── mcp/*.js               # custom MCP tools (see `agentui-mcp-tools`)
├── brand.css              # workspace brand tokens, generated — see "Brand and project knowledge"
├── design/DESIGN.md       # styling rules for this brand — generated
└── .agentui/              # WORKSPACE.md + PROJECT_KNOWLEDGE.md, refreshed by sync
```

`push` infers the component type from the directory and the name from the filename,
so creating `pages/Reports.jsx` creates a page called `Reports`. Never delete
`.agent.json` / `.agent-manifest.json` — they map local files back to server records.

Those four directories are the *typed* ones, not the whole story: the CLI walks the
entire tree, so shared code in `utils/`, `hooks/`, `context/` and nested paths like
`components/ui/Button.jsx` is pushed verbatim and `import … from "../utils/foo"`
resolves at build time. Anything outside a typed directory defaults to `COMPONENT`. The
project root's `index.html` ships too, but only when Custom index.html is enabled for
the project — and it is the only `.html` the CLI pushes.

**Before writing app code**, read `AGENTS.md` and pull the conventions from the
platform: `agentui skills list`, `agentui skills info <name>`,
`agentui packages list` (what you may import at runtime), `agentui guide new-project`.
Confirm the instructions are current with `agentui project instructions --check`.

## Edit → ship loop

```bash
agentui validate --all                 # the platform's own validator, server-side
agentui project push --dry-run         # exactly what would change
agentui project push --yes --build     # ship + rebuild + wait until live
agentui env status                     # this environment's URL + whether its build is fresh
```

`push` flags worth knowing:

- `--dry-run` — plan only, never changes server state (exempt from the prod guardrail).
- `--delete` — also delete components whose local files are gone. Off by default.
- `--yes` — required to push to production. **Ask the user before passing it.**
- `--build` / `--build-timeout <s>` — rebuild and wait (default 300s).
- `--no-create` — don't auto-create components for new local files.

The CLI packs operations into batches (50 ops / 1 MB each) and sends them in sequence,
so a large change does not need splitting by hand. Batches fail independently: read
`failed` in the result, not the exit code.

`agentui deploy` is `push` with a validation pass in front and deletions off: it
creates and updates, never deletes. Use it when you want the validator to gate the
ship; use `push` when you also need `--delete`. Neither one rebuilds — see below.

`agentui build` triggers the same rebuild the app's loading page does and waits for it.
**Building production needs `--yes`** — the same guardrail as `push`, because the build
is what actually puts the code in front of users. `--force` rebuilds from scratch,
`--no-wait` returns immediately, `--environment <name>` targets one environment. If the
build is already current it exits 0 with `upToDate: true`.

If the build half of `push --yes --build` fails, **do not just re-run the push** — with
the code already sent it reports "Nothing to push" and never rebuilds. Run
`agentui build --yes` on its own.

## Backend endpoints

```bash
agentui functions list
agentui functions invoke sendEmail --data '{"to":"a@b.c"}'
agentui functions logs <stepId>
agentui functions stats
```

`invoke` calls the deployed function the way a browser or webhook does
(`POST https://<app-domain>/api/<name>`). It **refuses to run when the app has unbuilt
changes** — run `agentui build --yes` first, or pass `--allow-stale` deliberately.

## Settings, environments, secrets

```bash
agentui project settings                              # every toggle the platform exposes
agentui project settings set requiresLogin false
agentui project settings set customDomain app.acme.com
agentui project settings set homePagePath Reports     # or pages/Reports.jsx; "none" to unpin
```

One key per invocation. Settings baked into the build only take effect on the next
**rebuild** — `agentui build` (`--yes` on production). `agentui deploy` will not do it
for you: with no code changes it exits immediately with "Nothing to deploy". Toggles include `requiresLogin`, `allowSelfSignup`, `ssoEnabled`,
`mfaEnabled`, `isFunctionAPIEnabled`, `isInstallableWebApp`, `isOfflineEnabled`,
`isCustomIndexHtmlEnabled`, `customDomain`.

Each environment is an **independent deploy with its own separate database**:

```bash
agentui env list
agentui env create staging
agentui env use staging
agentui env status                      # built / stale / building, served version
agentui env promote staging production --yes
```

Secrets: names and descriptions are visible, **values never leave the server**.

```bash
agentui secrets list
agentui secrets request STRIPE_API_KEY --description "Live key" --stdin   # value via stdin
```

When the value is the user's to supply and you should never see it, record the need
instead of asking for it:

```bash
agentui secrets request STRIPE_API_KEY --needed --description "Live key"
```

That registers the requirement and returns a link the user opens to fill it in from the
app's Secrets panel. Prefer it over asking for a key in chat.

Names are `UPPER_SNAKE_CASE`, 1–64 chars, values capped at 8 KB. Prefer `--stdin` or the
interactive prompt over `--value` so the secret stays out of shell history. **Scope is
this one workflow** — a sibling automation in the same app does not inherit the grant
(see ``agentui-automations``).

## Sharing it with the user

```bash
agentui project open                      # the editor, in the browser
agentui project open --preview --print    # the PRODUCTION app URL (see the warning below)
agentui open                              # what the project needs from a person, with links
agentui open setting ssoEnabled           # a link to one place in the web app (see below)
agentui project link                      # pre-authed LOGIN link to the preview, 7 days
agentui project link --scope iframe       # 1 hour, for embedding
agentui project icon logo.png --yes       # app icon → all PWA sizes + rebuild
```

`project open --preview` resolves the project's production/custom domain — it does not
consult `agentui env current`. **After building a non-production environment, do not
hand the user that URL**: take `previewUrl` from the `--build` output, or the
environment's own URL from `agentui env status`.

`agentui open <target> [value]` is how you point the user at a place in the web app —
a table, a setting, a panel, the box for a missing secret. Run `agentui open` alone for
the targets; an unknown table or setting is refused with the valid values.

A `project link` is a login token, not a pointer: anyone holding it acts as the user in
that workflow until it expires — hand it over only on a channel the user chose.

## Blueprints

`agentui blueprints list` / `info <id>` / `create <id>` — start from a starter template
instead of an empty app when one matches what the user asked for.
