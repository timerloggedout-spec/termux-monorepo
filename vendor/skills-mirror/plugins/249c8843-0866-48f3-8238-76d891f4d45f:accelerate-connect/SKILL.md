---
name: accelerate-connect
description: Connect the toolkit to your WordPress site. Set up credentials, generate an application password. Also triggered when the site connection is missing.
license: MIT
category: setup
parent: accelerate
disable-model-invocation: true
---

# Accelerate — Connect your site

Your job is to get the user's WordPress site talking to the toolkit. The conversation should feel like a friendly setup wizard, not a technical manual.

## What you're setting up

Three pieces of information need to land in `~/.config/accelerate-ai-toolkit/env`:

1. **Connection URL** (`WP_API_URL`) — the **full** WordPress MCP server URL, e.g. `https://their-site.com/wp-json/mcp/mcp-adapter-default-server` for sites running the MCP Adapter, or `https://their-site.com/wp-json/wp/v2/wpmcp` for legacy `wordpress-mcp` sites. The user only ever gives you the bare site address; this skill probes the site and saves whichever full URL responds.
2. **Username** — the WordPress username to authenticate as
3. **Application password** — a WordPress Application Password (not their login password)

Once those are set, the toolkit's WordPress connection (the `wordpress` MCP server) picks them up. **How** it picks them up depends on the agent: Claude Code reads the bundled `.mcp.json`, while Codex, Cursor, Gemini, GitHub Copilot, and Hermes each wire it a little differently. Step 7 handles that per agent. (Claude Code is the supported path; the others are in testing — if a connection doesn't come up, that's useful feedback.)

## The conversation

Walk the user through these steps one at a time. Wait for a response before moving to the next step. Be patient and don't assume technical knowledge.

### Step 1 — Welcome

Explain briefly what's about to happen, in plain language:

> "To connect your site, we need three things: your site's web address, your WordPress username, and a special password that only this toolkit will use. I'll guide you through generating that password in a moment. It takes about two minutes."

### Step 2 — Ask for the site URL

Ask:

> "What's the web address of your WordPress site? For example: `https://mysite.com`"

Accept whatever they give you and **normalise it to the site root**:
- Strip any trailing slash.
- If they pasted something ending in `/wp-json/...` or `/wp-admin`, strip that back to the site root and politely confirm (*"I'll use `https://mysite.com` as the site address — sound right?"*).
- If they gave you something with a content path like `https://mysite.com/blog`, confirm whether that's the correct WordPress root or whether the WordPress install lives at `https://mysite.com`.
- If they omitted `https://`, assume `https://`.

Keep the normalised site-root value (no path, no trailing slash) in working memory as `SITE_ROOT`. You'll combine it with the connector path detected in step 7b to build the full `WP_API_URL` saved in step 5.

### Step 3 — Generate an Application Password

Tell the user:

> "Now we'll create a dedicated password for this toolkit. This lets you revoke access later without changing your main login.
>
> 1. Open your site's admin area in a browser: `<their-site>/wp-admin`
> 2. Go to **Users → Profile** (or **Users → Your Profile**)
> 3. Scroll down to the **Application Passwords** section near the bottom
> 4. Type `Accelerate AI Toolkit` as the name
> 5. Click **Add New Application Password**
> 6. WordPress will show you a password that looks like `abcd efgh ijkl mnop`. Copy it exactly as shown, spaces and all.
>
> Let me know once you've got it."

If they report the Application Passwords section is missing, it usually means either:
- Their WordPress is older than 5.6 — tell them they need to update.
- The site is served over plain HTTP in production — Application Passwords require HTTPS. For local development they can set `WP_ENVIRONMENT_TYPE` to `local` in `wp-config.php` to bypass this. Suggest they ask their site administrator for help.

### Step 4 — Collect username and password

Ask:

> "Great. What's your WordPress username? And please paste the application password you just copied."

Collect both. The username goes into `WP_API_USERNAME`. The password goes into `WP_API_PASSWORD` **exactly as WordPress displayed it** — do not strip the spaces.

### Step 5 — Verify the environment and discover the connector URL

Before saving anything, run two quick checks. Both must pass before you can write a working configuration.

**5a — Verify npx is the real Node.js binary**

Use the Bash tool:

```bash
NPX_PATH=$(command -v npx 2>/dev/null)
NPX_VER=$(npx --version 2>&1 | head -1)
NPX_REAL=$(realpath "$NPX_PATH" 2>/dev/null || echo "$NPX_PATH")
echo "path=$NPX_REAL version=$NPX_VER"
```

Check **both** conditions:
1. The version output looks like a semver number (e.g. `10.8.2`), not an error or "Unknown command"
2. The resolved path is inside a standard Node.js location (the path contains `node`, `npm`, `nvm`, `fnm`, `volta`, or is in `/usr/local/bin`, `/usr/bin`, or a Homebrew prefix)

If npx is missing, returns a non-semver version, or resolves to an unexpected location, tell the user:

> "The toolkit needs a working copy of `npx` (part of Node.js) to connect to your site, but the `npx` in your current shell doesn't appear to be the standard Node.js version. This usually happens when another tool in your shell is intercepting the command.
>
> To check: open a regular terminal and run `npx --version`. If that works and shows a version number, your agent's shell has something overriding it. See the troubleshooting section in the installation guide for how to point the toolkit at the real `npx` binary."

If npx looks genuine, continue to 5b.

**5b — Probe the site to discover the connector URL**

Use the Bash tool to test the site's REST endpoints:

```bash
SITE="<the normalised site root from step 2>"
USER="<the username from step 4>"
PASS="<the application password from step 4>"

# The helper gives each request a 5-second connection limit and a 15-second
# overall limit. It gives curl the password through standard input, never argv.
WP_API_USERNAME="$USER" WP_API_PASSWORD="$PASS" \
  python3 scripts/connection.py probe --site "$SITE" --check accelerate
WP_API_USERNAME="$USER" WP_API_PASSWORD="$PASS" \
  python3 scripts/connection.py probe --site "$SITE" --check routes
```

Interpret the results in order:

**Is Accelerate installed?**

If `accelerate` is `404`: Accelerate isn't active on this site, or the Abilities feature isn't turned on. Tell the user:

> "I can reach your site, but Accelerate doesn't seem to be active or its Abilities feature isn't turned on yet. Check that the Accelerate plugin is installed and active in your WordPress admin, and that the Abilities feature is enabled (see the installation guide for instructions)."

Stop here. Do not save credentials.

**Which connector responds?**

Pick the connector URL using this priority — adapter wins when both respond, since `mcp-adapter` is the actively maintained route:

The adapter route is POST-only, so a `GET` against a working adapter returns `405` (route exists) — that's the expected healthy signal here, not `200`. Treat `405`, `200`, or `401` as "route exists".

| adapter | legacy | Action |
|---------|--------|--------|
| 405/200/401 | any | Set `WP_API_URL="$SITE/wp-json/mcp/mcp-adapter-default-server"`. Proceed to step 6. |
| 404 | 405/200/401 | Set `WP_API_URL="$SITE/wp-json/wp/v2/wpmcp"`. Proceed to step 6. |
| 404 | 404 | Stop. Accelerate is running but no MCP connector responded. Tell the user: *"Accelerate is running on your site, but the WordPress connector isn't responding. This usually means the MCP Adapter plugin needs to be installed or activated. Check with your site administrator or see the installation guide."* |
| Other | Other | Stop. Tell the user the site returned an unexpected response and suggest they check the URL is correct and the site is reachable in a browser. |

Keep the chosen full URL in working memory as `WP_API_URL`. You'll write it in step 6.

### Step 6 — Save credentials

Save credentials in **two places** so they work across all supported agents.

**6a — Claude Code settings (primary)**

This is what Claude Code reads when it starts the WordPress connector. Use the bundled helper from the toolkit directory to write the credentials into the project's `.claude/settings.local.json` (this file is gitignored and never committed):

```bash
python3 scripts/connection.py write \
  --settings .claude/settings.local.json \
  --env-file "$HOME/.config/accelerate-ai-toolkit/env"
```

Pass exactly three lines to the helper's standard input: the full connector URL chosen in step 5b, the username, and the Application Password. Do not put any of those values after the command. The helper preserves unrelated settings, writes both files atomically with mode `600`, and prints no credential values.

**This file is folder-scoped.** The connection works when Claude Code is started from this folder. Mention it briefly: *"One thing to know — this connection is tied to the folder we're in now. If you want to use the toolkit from a different folder later, run `/accelerate-connect` there and I'll re-link it in seconds, no password needed."* (The re-link path is in "If the user already has credentials" below.)

**6b — Backup env file (for Codex CLI and other agents)**

The same helper writes the standard env file for non-Claude-Code contexts.

**Important:**
- **Double-quote every value** in the env file. Application Passwords contain spaces. The helper handles this safely.
- Mode `600` is required — the helper establishes it before credential bytes are written.
- Do NOT echo the full password back to the user in chat after writing. Confirm by saying "Saved. ✓" instead.
- The `.claude/settings.local.json` file is automatically gitignored by Claude Code. Do not commit it.

### Step 7 — Wire the connection for your agent

The credentials are saved, but each agent reads them differently. If you don't already know which agent the user is in, ask. Then follow the matching branch. **Claude Code is the supported path; Codex, Cursor, Gemini, GitHub Copilot, and Hermes are in testing — if a connection doesn't come up for one of those, that's useful feedback to report.**

**Claude Code** — nothing more to do. The `.mcp.json` that ships with the plugin already reads the credentials you saved in `settings.local.json` (step 6a). Skip to step 8.

**Cursor** — Cursor configures MCP servers in `.cursor/mcp.json`. Write the WordPress server there (merged, non-destructive); it reads the credentials from the env file you wrote in step 6b:

```bash
python3 - <<'PY'
import json, os
path = os.path.join(os.getcwd(), '.cursor', 'mcp.json')
data = json.load(open(path)) if os.path.exists(path) else {}
data.setdefault('mcpServers', {})
data['mcpServers']['wordpress'] = {
    'command': 'npx',
    'args': ['-y', '@automattic/mcp-wordpress-remote@0.4.0'],
    'envFile': os.path.expanduser('~/.config/accelerate-ai-toolkit/env'),
}
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    json.dump(data, f, indent=2); f.write('\n')
print('Wrote', path)
PY
```

Like Claude's `settings.local.json`, this is folder-scoped — run `/accelerate-connect` again from another project to wire it there too.

**Codex CLI** — Codex configures MCP servers in `~/.codex/config.toml` (it does **not** read `.mcp.json`). Use the bundled helper after step 6; it merges only the `wordpress` block, locks the file to `600`, and never passes credentials on the command line:

```bash
python3 scripts/connection.py configure-codex \
  --config "$HOME/.codex/config.toml" \
  --env-file "$HOME/.config/accelerate-ai-toolkit/env"
```

Confirm it landed with `codex mcp list` (and `codex doctor` for a fuller config/auth/runtime health check). Also add the shell-profile line below (some Codex setups read the env from the shell too).

**Gemini CLI** and **GitHub Copilot** — the WordPress server is already declared in the manifest that ships with the toolkit (`gemini-extension.json` `mcpServers` for Gemini; the bundled `.mcp.json` for Copilot). There's no per-project file to write — they just need the credentials available as shell environment variables, so add the shell-profile line below.

**Hermes** — Hermes configures MCP servers separately from the plugin manifest. Point the user at `.hermes-plugin/README.md`, which has the exact `wordpress` server block to paste into their Hermes MCP config, then add the shell-profile line below.

**Shell-profile line (everyone except Claude Code — Codex, Cursor, Gemini, Copilot, Hermes):**

These agents read the credentials from the shell environment, so the env file must be sourced when the terminal starts. Add this line to the user's shell profile:

For zsh / bash (`~/.zshrc` or `~/.bashrc`):
```bash
[ -f ~/.config/accelerate-ai-toolkit/env ] && set -a && . ~/.config/accelerate-ai-toolkit/env && set +a
```

For fish (`~/.config/fish/config.fish`):
```fish
if test -f ~/.config/accelerate-ai-toolkit/env
    while read -l line
        set -l pair (string split -m 1 '=' -- $line)
        set -gx $pair[1] (string unescape --style=script -- $pair[2])
    end < ~/.config/accelerate-ai-toolkit/env
end
```

This removes the double quotes used by the shared env file and decodes its escaped values before exporting them.

(Cursor reads the env file directly via `envFile`, but the shell-profile line is still the simplest way to make the same credentials available everywhere.)

### Step 8 — Restart the agent session (advice differs by agent)

Getting this wrong sends the user into a restart loop that never picks up the new values, so match the advice to how their credentials load.

**Claude Code** (credentials come from `settings.local.json`, re-read every session start):

> "One last step — close this Claude Code session and start a new one. The connection settings load at startup, so they'll kick in next session. When you're back in, run `/accelerate-status` to confirm everything works."

**Codex, Gemini, Copilot, Hermes, or any agent using the shell-profile method from step 7:** restarting the agent is **not** enough. The agent inherits its environment from the terminal, and the terminal keeps whatever values were exported when it was opened — restarting the agent in the same terminal re-inherits the old values every time. Tell them:

> "One last step — open a **new terminal window** (or run `exec zsh` in this one) so the new connection settings load, then start a fresh session there. Restarting in the same terminal won't pick them up. When you're back in, run `/accelerate-status` to confirm everything works."

This matters most when **updating** existing credentials (new password, new site, or the old bare-root address being upgraded to the full connector URL): every already-open terminal keeps exporting the stale values until it reloads its profile.

## Things to watch for

- **Don't skip the chmod.** Credentials must not be world-readable.
- **Don't write the env file anywhere else.** The `.mcp.json` in the plugin root expects `WP_API_URL`, `WP_API_USERNAME`, and `WP_API_PASSWORD` as environment variables, sourced from the `~/.config/accelerate-ai-toolkit/env` path.
- **`WP_API_URL` is the full connector URL.** It must include the `/wp-json/...` path discovered in step 5b. Never save just the site root — the toolkit's status check will flag it as stale and tell the user to rerun this skill.
- **Don't embed credentials in the plugin folder.** Never write to a `.env` or `env` file inside the repository; it must go in the user's home directory.
- **Never show the full password in chat output after writing it.** It's fine to show the first and last four characters for confirmation (e.g., `abcd **** **** mnop`), but never the whole string.

## If the user already has credentials

Check the **on-disk sources**, not just the live shell environment — the shell can hold stale values exported by a terminal that was opened before the last update:

```bash
echo "live=${WP_API_URL:-NOT_SET}"
sed -n 's/^WP_API_URL=//p' ~/.config/accelerate-ai-toolkit/env 2>/dev/null | tr -d '"' | sed 's/^/file=/' || true
python3 -c "
import json
print('settings=' + json.load(open('.claude/settings.local.json')).get('env', {}).get('WP_API_URL', 'NOT_SET'))
" 2>/dev/null || echo "settings=NOT_SET"
```

Route on what you find:

- **All present and agreeing** — already configured. Suggest `/accelerate-status` to verify it works. Offer to overwrite if they want to connect a different site.
- **Env file has credentials but this folder's `settings.local.json` doesn't** — they set up the toolkit in a different folder. Offer to re-link: *"You've already connected [site] from another folder — want me to link it here too? Takes a second, no password needed."* If yes, read all three values from `~/.config/accelerate-ai-toolkit/env` and write them into `.claude/settings.local.json` using the step 6a snippet, then send them through step 8. Do not ask for the password again.
- **Live value differs from an on-disk value** — the shell environment is stale. Don't re-collect anything; give them the step 8 advice for their agent (for shell-profile users: new terminal window or `exec zsh`, then a fresh session).
