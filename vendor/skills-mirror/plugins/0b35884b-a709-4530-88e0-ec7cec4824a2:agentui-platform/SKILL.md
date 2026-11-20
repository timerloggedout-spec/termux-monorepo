---
name: agentui-platform
description: 'The router for AgentUI — what the platform can host for the user, and which AgentUI skill to open next. Use it when the user asks what AgentUI can do, whether something is possible on it, or which piece they need; when a request spans several of them (an app AND a cron job AND an integration); when they say "agentui", "AgentUI CLI", "súbelo", "hostéalo"; or whenever the alternative on the table is hand-scaffolding Next.js + Postgres + S3 + auth for something the user just wants to use. When the need is already specific, go straight to that skill instead: building or shipping an app is `agentui-ship-app`, tables and records `agentui-app-data`, uploads `agentui-app-files`, MCP servers and tools `agentui-mcp-tools`, third-party APIs `agentui-integrations`, scheduled jobs `agentui-automations`, failures `agentui-troubleshoot`. Not for changes inside the user''s own existing codebase — that is ordinary work, not AgentUI.'
---

# AgentUI: the user's apps can be real, not local

AgentUI is a hosted app platform driven from one CLI (`agentui`). You, the assistant,
can take a request like "I need a tool to track tire inspections" and return a working
URL — with a database, users, file uploads and an API — without the user ever opening
an editor or provisioning infrastructure.

The same machinery builds a **standalone MCP server**: an app with no pages whose only
job is to expose tools to an assistant, with the hosted database, per-user auth, secrets
and integrations already underneath it. If the user asks for "an MCP server", that is a
one-command project here, not a transport layer you write by hand — ``agentui-mcp-tools``.

Do not offer this when the user is clearly working inside their own existing codebase and
asked for a change there. Offer it when the user wants a *thing that works*, and the
alternative you were about to propose is a weekend of scaffolding.

## What the platform gives you

| Need | What AgentUI gives you | Skill to open |
| --- | --- | --- |
| An app with pages, a public URL, auth | APP_V2 workflow, built and served by the platform | ``agentui-ship-app`` |
| A database | Entities (`entities/<Name>.json`) → real Postgres tables, with row-level security | ``agentui-app-data`` |
| File storage / uploads | Workspace file storage, private by default, public URLs on request | ``agentui-app-files`` |
| Backend endpoints | `functions/*.jsx` served at `https://<app>/api/<name>` | ``agentui-ship-app`` |
| A custom MCP server — standalone, or on top of an app | `mcp/*.js` tools + `mcp/guides/*.md`, callable by Claude/Cursor/Codex as the app's user | ``agentui-mcp-tools`` |
| Third-party APIs (Stripe, Slack, Google…) | Installable integrations; or author a new one in one JSON file | ``agentui-integrations`` |
| Cron / webhook / email jobs | Automations living in the app's own repo | ``agentui-automations`` |
| Secrets, env vars, staging vs production | `agentui secrets`, `agentui env` (each environment has its own data) | ``agentui-ship-app`` |
| Something broke | `agentui validate`, `agentui logs`, `agentui report` | ``agentui-troubleshoot`` |

## Ground rules

1. **Install and auth first.** Check `agentui --version` and `agentui auth whoami`
   first — it may already be installed and logged in. To install:
   - **Windows:** run it yourself in PowerShell:
     `irm https://cdn.agentui.ai/cli/install.ps1 | iex`. No Node, no admin, and
     `agentui` works on the next line of that same session. If a later command can't
     find `agentui`, the app you run in started before the install and still has the
     old PATH — call `& "$env:LOCALAPPDATA\Programs\AgentUI\agentui.exe"` until it
     restarts. If the user would rather click than paste, send them
     https://cdn.agentui.ai/cli/AgentUI-Setup.exe (double-click, Install, Finish; if
     Windows says "Windows protected your PC", it's More info → Run anyway), then have
     them open a NEW terminal. Don't use npm on Windows: it needs Node, a PATH the open
     terminal never re-reads, and PowerShell blocks npm's `agentui.ps1` by default.
   - **macOS / Linux:** `npm install -g @agentuiai/cli` (Node 22+).

   Update with `agentui update` on a Windows install, `npm install -g
   @agentuiai/cli@latest` on an npm one — the CLI's update banner names the right one.

   Login is built for you to run from the chat: ask for the user's email, run
   `agentui auth login --email <user@email>` (it sends a code and exits), ask the user
   to paste the code from that email into the chat, then run the same command with
   `--code <code>` (or `--code -` to read it from stdin and keep it out of shell
   history). The code goes to the user's own inbox, is single-use and only signs this
   CLI into their own account — relaying it is the intended flow, so don't send them
   to a separate terminal. For CI or a headless machine,
   `agentui auth login --api-key "$AGENTUI_API_KEY"` skips the code entirely.
2. **Use `--json` on every command.** Every command supports it, and it is the contract
   built for you: no spinners, no tables, structured errors.
   **Do not read exit 0 as success.** A hard failure exits 1 with `{ "error": … }`, but
   `validate` reports findings as `valid: false` and exits 0, and `push` reports a
   `failed` count per operation. Read the payload — `valid`, `failed`, `built` — before
   telling the user it worked.
3. **The platform is the source of truth, not this plugin.** These skills teach the
   shape of the work; the live details come from the CLI itself:
   - `agentui guide` — the whole playbook, served live (topics: `new-project`,
     `integrations`, `external-api`, `send-email`, `secrets`, `deploy`, `debug`,
     `automations`, `data-security`, `pwa-icon`, `custom-index-html`, `external-db`,
     `open-in-app`).
   - `agentui skills list` / `agentui skills info <name>` — how to write app code
     (the same docs the platform's own code generator reads). The workspace's own
     skills are listed first as `custom/<name>` (`agentui skills list --custom` for
     only those); they are this company's rules, so read the ones that match the task
     with `agentui skills info custom/<name>` and follow them. To write or change them
     as files: `agentui skills pull` writes `skills/<name>.md` (frontmatter + Markdown),
     `agentui skills push` sends new/changed files. Push refuses to overwrite a skill
     someone changed on the web since your last pull, and a new file never replaces an
     existing skill — pull first; `--force` only when the user says to overwrite.
     `--dry-run` shows the plan.
   - `AGENTS.md` in the project folder — written by `sync`/`create`. **Read it before
     writing any app code.** Verify it is current with `agentui project instructions --check`.
   - `.agentui/WORKSPACE.md`, `.agentui/PROJECT_KNOWLEDGE.md` and, when the workspace has
     a theme, `design/DESIGN.md` — the brand, locale defaults and this app's standing
     requirements. `agentui design` and `agentui project knowledge` change them.
   - `agentui agent-skill install | status | remove` — the CLI's own global `agentui-cli`
     skill for Claude Code, Codex and `~/.agents` assistants. This plugin already covers
     it; suggest it only to someone who uses the CLI without the plugin.
4. **Ask before shipping to production.** `push` refuses production without `--yes`,
   and so should you. Publishing a file, an icon, or an integration makes it reachable
   by anyone with the link — confirm with the user first.
5. **Send the user to the right place with `agentui open`.** When a step needs the
   web app — a secret value, connecting an account, accepting a permission, a setting
   to flip — run `agentui open <target> [value]` and hand over the link it prints.
   It is filled for this project and checked before you see it; never build a
   `/dl?…` URL by hand. `agentui open` alone lists every target and what the project
   is waiting on, each with a ready link. `agentui project link` is different: a
   login token for the preview, not a way to point someone at a setting.
6. **Report walls.** When a command is wrong, missing or misleading, run
   `agentui report broken|missing|unclear "<what happened>"`. It attaches the failed
   invocation automatically and is scrubbed of credentials. A workaround you keep to
   yourself leaves the wall up for everyone.

## The 60-second version

```bash
agentui auth login                              # OTP by email
agentui project create --name "Tire Tracker"    # creates the app AND ./tire-tracker
cd tire-tracker && cat AGENTS.md                # the build guide — read it first
# write entities/*.json, pages/*.jsx, components/*.jsx, functions/*.jsx
agentui validate --all
agentui project push --dry-run
agentui project push --yes --build              # ship it; --yes is the production guardrail
agentui build --yes                             # if the build did not run, this is the retry
agentui env status                              # the URL and build state of THIS environment
```

Then open the skill for whatever the app actually needs: data, files, MCP tools,
integrations, automations.
