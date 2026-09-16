# Credential exposure: committed browser profiles

**Status: open. Rotation required.**
Found while building the repo hygiene gate (`scripts/ci/repo_gate.py`). This is
the highest-severity finding in the repo and it is not theoretical — there are
live session cookies in the git index right now.

## What is committed

`git ls-files` tracks **607 files** belonging to four Chromium/Puppeteer user
data directories, of which **115** are credential or state stores:

| Tracked profile directory | Files | Notes |
| --- | --- | --- |
| `deepcli/browser-data/` | 136 | not matched by any `.gitignore` rule |
| `deepseek-cli/browser-data-account2/` | 157 | matched by `.gitignore` line 146, committed anyway |
| `deepseek-cli/browser-data-account2-clean/` | 169 | **contains live cookies** |
| `deepseek-cli/browser-data-account2-fresh/` | 145 | |

Sensitive store names present in each: `Cookies`, `Cookies-journal`,
`Login Data`, `Login Data-journal`, `Local State`, `Web Data`,
`Account Web Data`, `Trust Tokens`, `Session Storage/`, `Local Storage/`,
`IndexedDB/`.

## Confirmed live material

Read-only inspection of the committed SQLite files (row counts and host names
only — no values were decoded or printed):

```
deepcli/browser-data/Default/Cookies                        rows=0
deepseek-cli/browser-data-account2/Default/Cookies           rows=0
deepseek-cli/browser-data-account2-fresh/Default/Cookies     rows=0
deepseek-cli/browser-data-account2-clean/Default/Cookies     rows=5   <-- live
    hosts: .deepseek.com, chat.deepseek.com
    all 5 rows have a non-empty encrypted_value
```

`Login Data` tables are empty in all four profiles, so no saved passwords. The
exposure is **session cookies for a DeepSeek chat account**.

### Why "encrypted_value" is not protection here

These profiles were produced by Chromium under Termux. Chromium's `OSCrypt` on
Linux tries the Secret Service / kwallet first and falls back to a **hardcoded
password (`peanuts`) with PBKDF2-SHA1, 1 iteration, fixed salt** when no keyring
is reachable. Termux has no keyring. The `v10` prefix on those cookie values
means exactly that fallback was used, so the values are recoverable offline by
anyone with a copy of the file — which, because the file is in git, is anyone
with read access to the repository or to any clone, fork, or CI cache of it.

Treat the DeepSeek session as compromised.

## Immediate actions

1. **Rotate first, clean second.** Log out of *all* sessions on the affected
   DeepSeek account (account settings → sign out everywhere), then change the
   password. Untracking the files does not invalidate a token that already
   leaked.
2. **Untrack the profiles** (index only — your local files are kept):

   ```bash
   git rm -r --cached --quiet \
     deepcli/browser-data \
     'deepseek-cli/browser-data-account2' \
     'deepseek-cli/browser-data-account2-clean' \
     'deepseek-cli/browser-data-account2-fresh'
   git commit -m "security: untrack committed Chromium profiles (session cookie exposure)"
   ```

   `.gitignore` already covers `deepseek-cli/browser-data*/`; the missing rule
   for `deepcli/browser-data/` is added in the same change as this document.
3. **Purge from history if the repo is or may become public.** Untracking leaves
   the blobs reachable from old commits. All four directories entered in a single
   commit (`320c73b`), so the rewrite is narrow:

   ```bash
   git filter-repo --invert-paths \
     --path deepcli/browser-data \
     --path deepseek-cli/browser-data-account2 \
     --path deepseek-cli/browser-data-account2-clean \
     --path deepseek-cli/browser-data-account2-fresh
   ```

   This rewrites every commit SHA and requires a force-push plus a re-clone by
   every collaborator. Do not run it without deciding that first. If the repo
   stays private and the account is rotated, untracking is a defensible
   stopping point.

## Preventing recurrence

`scripts/ci/repo_gate.py` now hard-fails any PR that *adds* a path under a
browser-profile directory, with a dedicated `no-browser-credential-stores`
failure for the credential stores themselves. The existing 607 files are held by
two ratchet counters in `scripts/ci/baseline.json`:

```
tracked_browser_profile_files      607
tracked_browser_credential_stores  115
```

Both are allowed to go down and never up. After step 2 above, run
`python3 scripts/ci/repo_gate.py --write-baseline` so the counters drop to zero
and the door closes behind the fix.

## Root cause, and the durable fix

The automation in `deepcli/` and `deepseek-cli/` points Puppeteer at a
`userDataDir` that sits **inside the working tree**. Persisting a login between
runs is a reasonable goal; storing it next to the source is what makes it a git
problem. Point `userDataDir` outside the repo and derive it from the
environment:

```js
const userDataDir =
  process.env.DEEPSEEK_PROFILE_DIR ??
  path.join(os.homedir(), ".cache", "deepseek-cli", "profile");
```

That keeps the session on the device, survives `git clean -xdf`, and cannot be
committed by accident. Two of the four directories (`-clean`, `-fresh`) look
like manual "start over" copies — a single env-var-selected profile path removes
the need for those too.
