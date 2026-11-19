---
name: accelerate-status
description: Check whether the Accelerate AI Toolkit is connected to your WordPress site and able to fetch data. Diagnoses the specific failure layer if something is wrong.
license: MIT
category: diagnostics
parent: accelerate
---

# Accelerate — Connection status

Run a layered connection diagnostic on the Accelerate AI Toolkit. Check each layer in order and **stop at the first failure** -- report the specific problem and its fix, not a generic "run /accelerate-connect".

## Layer 1 -- Credentials

Use the Bash tool:

```bash
echo "WP_API_URL=${WP_API_URL:-NOT_SET}" && echo "WP_API_USERNAME=${WP_API_USERNAME:-NOT_SET}" && echo "WP_API_PASSWORD=${WP_API_PASSWORD:+SET}"
```

If any variable is `NOT_SET`, check whether credentials exist in `settings.local.json` but aren't loaded into the environment (common after upgrading from an older version of the toolkit):

```bash
python3 -c "
import json, os
path = '.claude/settings.local.json'
if os.path.exists(path):
    data = json.load(open(path))
    env = data.get('env', {})
    has_url = bool(env.get('WP_API_URL'))
    has_user = bool(env.get('WP_API_USERNAME'))
    has_pass = bool(env.get('WP_API_PASSWORD'))
    print(f'settings_local=FOUND url={has_url} user={has_user} pass={has_pass}')
else:
    print('settings_local=NOT_FOUND')
" 2>/dev/null || echo "settings_local=NOT_FOUND"
```

If `settings_local=FOUND` with all three values present but the env vars are still empty, the credentials are saved but the session needs a restart to pick them up:

```
❌ Credentials saved but not loaded yet
   Your site credentials are saved, but this session started before they were written.
   Fix: restart your agent session (close and reopen Claude Code). The credentials will
   load automatically on next start.
```

If neither env vars nor `settings.local.json` have credentials:

```
❌ Credentials not loaded
   Missing: [list which are missing, in plain English: "site address", "username", or "password"]
   Fix: run /accelerate-connect to set up your site credentials, then restart your agent session.
```

Stop here. Do not proceed to further layers.

**If all env vars ARE set**, confirm they aren't stale before trusting them. A terminal opened before the last `/accelerate-connect` run keeps exporting the old values, and an agent restarted inside that terminal re-inherits them — every layer below would then test the wrong address. Compare the live value against the on-disk sources:

```bash
LIVE="${WP_API_URL:-}"
FILE=$(sed -n 's/^WP_API_URL=//p' ~/.config/accelerate-ai-toolkit/env 2>/dev/null | tr -d '"')
LOCAL=$(python3 -c "
import json
print(json.load(open('.claude/settings.local.json')).get('env', {}).get('WP_API_URL', ''))
" 2>/dev/null)
echo "live=$LIVE file=${FILE:-none} settings=${LOCAL:-none}"
```

- **`settings` has a value and `live` differs from it** — the session started before the settings were written. Surface the "Credentials saved but not loaded yet" block above and stop.
- **`settings` is empty, `file` has a value, and `live` differs from it** — the shell environment is stale; restarting the agent in this terminal will never fix it:

  ```
  ❌ This session is using out-of-date connection settings
     Your saved settings were updated, but this session inherited older ones from a
     terminal that was opened before the update.
     Fix: open a new terminal window (or run `exec zsh`), then start a new agent session
     from there. Restarting in this terminal will keep loading the old settings.
  ```

  Stop here. Do not proceed to further layers.

- **`live` matches whichever on-disk source exists (or no on-disk source is found)** — proceed to Layer 2.

## Layer 2 -- Node.js connector

Use the Bash tool:

```bash
NPX_PATH=$(command -v npx 2>/dev/null)
NPX_VER=$(npx --version 2>&1 | head -1)
NPX_REAL=$(realpath "$NPX_PATH" 2>/dev/null || echo "$NPX_PATH")
echo "path=$NPX_REAL version=$NPX_VER"
```

Check both:
1. The version output looks like a semver number (e.g. `10.8.2`), not an error
2. The resolved path is inside a standard Node.js location (contains `node`, `npm`, `nvm`, `fnm`, `volta`, or is in `/usr/local/bin`, `/usr/bin`, or a Homebrew prefix)

If npx is missing, returns a non-semver version, or resolves to an unexpected location:

```
❌ Cannot start the site connector
   The toolkit uses a Node.js tool to connect to your site, but it doesn't appear to be
   available in your current shell -- another tool may be intercepting it.
   Fix: open a regular terminal and run `npx --version`. If it shows a version number there,
   see the troubleshooting section in the installation guide for how to fix this.
```

Stop here.

## Layer 3 -- Normalise the saved URL

Before reaching out to the site, classify what's stored in `WP_API_URL`. The toolkit now saves the **full** connector URL (e.g. `https://example.com/wp-json/mcp/mcp-adapter-default-server`), but older installs may still hold the bare site root.

Use the Bash tool:

```bash
python3 - "$WP_API_URL" <<'PY'
import sys
from urllib.parse import urlparse, urlunparse
raw = sys.argv[1].rstrip('/')
parsed = urlparse(raw)
path = parsed.path or ''
if path.endswith('/wp-json/mcp/mcp-adapter-default-server'):
    shape = 'full_adapter'
    root = urlunparse(parsed._replace(path=path[:-len('/wp-json/mcp/mcp-adapter-default-server')]))
elif path.endswith('/wp-json/wp/v2/wpmcp'):
    shape = 'full_legacy'
    root = urlunparse(parsed._replace(path=path[:-len('/wp-json/wp/v2/wpmcp')]))
elif path in ('', '/'):
    shape = 'bare_root'
    root = urlunparse(parsed._replace(path=''))
else:
    shape = 'unknown'
    root = raw
print(f"shape={shape} root={root}")
PY
```

Use the printed `root` value as `SITE_ROOT` for every check below. Use the printed `shape` to decide whether to nudge the user about a stale config in Layer 7.

If `shape=unknown`, treat it as a bare-root for the curl checks but stop after Layer 7 with:

```
❌ Connection address looks invalid
   The saved site address has an unrecognised path. The toolkit can't tell which
   WordPress connector to use.
   Fix: run /accelerate-connect to re-detect the right address.
```

## Layer 4 -- Site reachability

Use the Bash tool:

```bash
python3 scripts/connection.py probe --site "$SITE_ROOT" --check site
```

The helper stops each request after a 5-second connection limit or 15-second overall limit.

If the response is not `200`:

```
❌ Cannot reach your site
   URL: [SITE_ROOT, without showing the variable name]
   Fix: check that the address is correct and the site is reachable in a browser.
```

Stop here.

## Layer 5 -- Authentication

Use the Bash tool:

```bash
python3 scripts/connection.py probe --site "$SITE_ROOT" --check auth
```

If the response is `401` or `403`:

```
❌ Authentication failed
   Your application password was rejected by the site. It may be wrong, expired, or revoked.
   Fix: run /accelerate-connect and generate a fresh application password.
```

Stop here.

## Layer 6 -- Accelerate installed

Use the Bash tool:

```bash
python3 scripts/connection.py probe --site "$SITE_ROOT" --check accelerate
```

If the response is `404`:

```
❌ Accelerate not found on your site
   Your site is reachable and your credentials work, but Accelerate doesn't appear to be
   active or the Abilities feature isn't turned on yet.
   Fix: check that Accelerate is installed and active in your WordPress admin, and that
   the Abilities feature is enabled. See the installation guide for instructions.
```

Stop here.

## Layer 7 -- Connection address

Use the Bash tool:

```bash
python3 scripts/connection.py probe --site "$SITE_ROOT" --check routes
```

Decide the outcome from `shape`, `adapter`, and `legacy`:

- **Full URL saved (`shape=full_adapter` or `shape=full_legacy`) and the matching route responds (`405`, `200`, or `401`)** — healthy, proceed to Layer 8. (The adapter route is POST-only, so a `GET` returns `405` when it exists — that's the expected healthy signal, not `200`.)
- **Full URL saved but the matching route returns `404`** — the connector that was working at setup time has gone away. Surface:

  ```
  ❌ WordPress connector not responding
     Accelerate is running but the connector address saved during setup no longer responds.
     Fix: run /accelerate-connect to re-detect the connector address.
  ```

- **Bare-root saved (`shape=bare_root`) and `legacy` responds (`405`/`200`/`401`)** — legacy `wordpress-mcp` site, still healthy. Proceed to Layer 8 silently.
- **Bare-root saved (`shape=bare_root`), `legacy` is `404`, but `adapter` responds (`405`/`200`/`401`)** — saved config is stale. The bundled client falls back to the legacy route for bare-root values, so traffic is hitting a `404`. Surface:

  ```
  ❌ Saved connection is out of date
     Your site uses a newer WordPress connector than the one the toolkit was set up against.
     Fix: run /accelerate-connect to re-detect the right address. (One-time fix.)
  ```

- **Both routes `404`** —

  ```
  ❌ WordPress connector not responding
     Accelerate is running but no WordPress connector responded.
     Fix: check with your site administrator, or see the installation guide for setup details.
  ```

Stop here unless the outcome above said to proceed.

## Layer 8 -- Live tool availability

Check whether the `mcp__wordpress__mcp-adapter-execute-ability` tool is available in this session.

If it is not available but all previous layers passed:

```
❌ Site is reachable but the connector isn't running in this session
   Your credentials and site are fine, but the background connector process hasn't started.
   Fix: restart your agent session (close and reopen Claude Code or Codex). The connector
   starts automatically when the session begins. If you've already restarted and it still
   fails, open a new terminal window first — an old terminal can feed every new session
   out-of-date connection settings.
```

Stop here.

## Layer 8b -- Accelerate version

This is a **non-blocking** check. Unlike every layer above, it never stops the flow -- if it finds a problem it records a single warning line and continues to Layer 9. If it finds nothing, it stays completely silent.

Sites running a version of Accelerate older than the minimum below have a server-side bug that breaks entry-page ranking data. The deployed version is detectable from the homepage without touching the site's settings.

The minimum supported version is **4.2.0**. (Maintenance: bump `MIN_VERSION` below when the floor changes.)

Use the Bash tool:

```bash
MIN_VERSION="4.2.0"
DETECTED=$(curl -s --connect-timeout 5 --max-time 15 "$SITE_ROOT/" 2>/dev/null | grep -oE 'accelerate\.[0-9][0-9a-z.]*\.js' | head -1 | sed -E 's/^accelerate\.(.*)\.js$/\1/')
if [ -z "$DETECTED" ]; then
  echo "version=none"
else
  OLDER=$(printf '%s\n%s\n' "$MIN_VERSION" "$DETECTED" | sort -V | head -1)
  if [ "$DETECTED" != "$MIN_VERSION" ] && [ "$OLDER" = "$DETECTED" ]; then
    echo "version=$DETECTED status=older"
  else
    echo "version=$DETECTED status=ok"
  fi
fi
```

- **`version=none`** — the version couldn't be determined (homepage doesn't embed the marker, a custom build, or a development version string). Skip silently: no warning, no mention. Proceed to Layer 9.
- **`status=ok`** — the site is on a supported version. Proceed to Layer 9 silently.
- **`status=older`** — record this warning line and carry it into the final summary, then proceed to Layer 9:

  ```
  ⚠️ Your site is running an older version of Accelerate ([DETECTED version]). Some analytics
     views (like entry-page rankings) won't work until it's updated.
     Fix: ask whoever maintains your site to update the Accelerate plugin.
  ```

When the remaining layers all pass, render the healthy status from Layer 9 as normal, then append this warning line beneath it.

## Layer 9 -- Live data check

If all layers pass, do all three of these in order:

1. **Count the Accelerate surface.** Call `mcp__wordpress__mcp-adapter-discover-abilities` and count the returned entries whose `name` starts with `accelerate/`. Ignore the `mcp-adapter/*` wrapper tools — those are transport, not capabilities.
2. **Smoke-test a read.** Call `accelerate/get-site-context` with `blocks: "none"` to grab basic site info. On an older site that rejects `blocks`, retry once with `include_blocks: false`.
3. **Smoke-test a second read.** Call `accelerate/get-audience-fields` as a capability ping.

Present the healthy status using the dynamic count from step 1:

```
✅ Connected to [site name]
   URL: [site URL]
   Accelerate capabilities available: [count from step 1, e.g. "42"]
   Ready for questions.
```

**Fallback:** if step 1 (`discover-abilities`) errored but both smoke tests in steps 2 and 3 succeeded, the connection is still healthy — surface success without the count line rather than guessing or printing `3`:

```
✅ Connected to [site name]
   URL: [site URL]
   Ready for questions.
```

If a smoke test fails with a permission error:

```
⚠️  Connected to [site name] with limited access
   URL: [site URL]
   Your account doesn't have permission for some features. Analytics and testing require
   a WordPress role that can edit content (e.g. Editor, Author). Some admin actions
   (stopping tests, broadcasts, exports) require an administrator role.
   Ask your site administrator to check your role.
```

## Output rules

- Keep the final output to **one status block** -- whichever layer you stopped at.
- Use ✅, ❌, or ⚠️ as the status indicator.
- Always include a **Fix:** line with a specific action.
- **Never show raw HTTP status codes, curl output, variable names (WP_API_URL etc.), or technical terms (endpoint, MCP, API, connector plugin) to the user.** The bash commands use these internally; the messages shown to the user must be plain English.
- This is a diagnostic, not a report. Be concise.
