# DeepSeek Session Capture Pipeline

This documents the actual working capture pipeline for `deepseek-cli`'s
webWrapper (reverse-engineered, WASM PoW + browser session cookies - no
official API key, by design). It was built and tested locally on a Termux
device before this repo existed on GitHub; this file makes it a documented
reference instead of ~30 similarly-named one-off scripts (`capture-*.cjs`,
`extract-*.cjs`, `deepseek-*.js`) that only make sense by reading each one.

## Why this needs a human step, and always will

DeepSeek's login flow sits behind an AWS WAF challenge and (per the scripts)
a passkey step. Both are designed to require a real browser completing a
real challenge - there is no way to script past that from a cloud sandbox
or a headless-only environment, and building something that tried to would
be the exact "reuse/automate around a security control" pattern this repo's
own `docs/CREDENTIAL-EXPOSURE.md` and `docs/proposals/AGENTIC-PERMISSIONS.md`
correctly refuse to do. The pipeline below is honest about that: step 1 is
manual and stays manual; steps 2-3 are what's actually automatable.

## The pipeline (as found, working, in `deepseek-cli/`)

**Step 1 - manual login, on-device (human required).**
`deepseek-manual-login-x11.js` launches a real, *visible* Chromium
(`/data/data/com.termux/files/usr/bin/chromium-browser`, i.e. Termux:X11)
against `chat.deepseek.com` with `userDataDir: './browser-data'`. A human
logs in (passkey) in that visible window, then Ctrl+C saves the profile.
This is the step that cannot be automated - it's also the step that, if its
*output* (the `browser-data` profile) gets committed to git, becomes exactly
the exposure documented in `docs/CREDENTIAL-EXPOSURE.md`. **Never commit
`browser-data/` or any `cookies*.json` - that directory should be
gitignored, not checked in.**

Separately, a browser extension (cookie-export format matches
EditThisCookie/Cookie-Editor's schema: `hostOnly`, `expirationDate`,
`sameSite`, etc.) can export the full cookie jar - including whatever AWS
WAF challenge cookie the browser picked up automatically during that same
session, no special handling needed - to a `cookies*.json` file. No
dedicated "WAF capture" script exists because none is needed: a real
browser session carries the WAF cookie like any other cookie.

**Step 2 - normalize + inject (automatable).**
`deepseek-debug3.js` picks the newest `cookies*.json` from a downloads
directory, normalizes the extension's export schema into Puppeteer's cookie
format (domain dot-stripping, `sameSite` casing, `expires`/`expirationDate`
mapping), and injects it into a headless Chromium profile. This part is
pure data transformation - no human interaction needed once a fresh
`cookies*.json` exists.

**Step 3 - extract the bearer token (automatable).**
`extract-account2-token-final.cjs` is the most-refined variant (after v1-v4
iterations, per the file names) - it launches headless, sets a specific
Firefox-on-Android user agent *before* setting cookies (found to matter),
navigates to `chat.deepseek.com`, confirms it didn't get redirected to
`/sign_in`, then reads `localStorage.getItem('userToken')` - the actual
Bearer token `deepcli`'s webWrapper needs.

## What's needed to make this replicable (forks/demos) and automated (us)

Not done in this pass - flagging as concrete follow-up work, not silently
deferred:

1. **Parameterize the hardcoded paths.** `CHROMIUM_PATH`,
   `DOWNLOADS_DIR` (`/data/data/com.termux/files/home/storage/downloads`),
   and account-specific filenames (`token_account2.txt`,
   `browser-data-account2-v2`) are hardcoded per-script. These should
   become CLI args or env vars so a fork/another user's device (different
   Termux install, different account slot) doesn't require editing script
   internals.
2. **Consolidate the ~30 `capture-*`/`extract-*` variants** in
   `deepseek-cli/` into the three canonical steps above, keeping the working
   logic from the "final"/"v4" versions and archiving (not silently
   deleting - they're debugging history) the superseded iterations under a
   clearly-labeled subfolder.
3. **Already done: `.gitignore` covers `browser-data*/` and `*cookies*.json`**
   repo-wide (lines 65, 121-122, 152, 190-192) - including a note that the
   ignore rule can't retroactively untrack the ~469 files already committed
   under `deepcli/browser-data/`. Untracking those (and any real history
   rewrite) is Tier 4 / Operator-only per `docs/CONSENSUS.md` -
   `docs/CREDENTIAL-EXPOSURE.md`'s remediation section is the place to
   track that, not this doc.
4. **Automate steps 2-3 end-to-end + the secret push**: a single script
   that, given a fresh `cookies*.json`, runs the normalize→inject→extract
   chain and then updates the `DEEPSEEK_COOKIES`/`DEEPSEEK_TOKEN_PRIMARY`
   GitHub Actions secret via the API - so the *only* manual step for
   refreshing a dead session is completing the login page once. Not built
   in this pass (needs the GitHub secrets libsodium-sealed-box encryption,
   which needs testing against a real repo before landing).

## Cross-references

- `docs/ops/DEEPSEEK-CI.md` - the CI-side secret contract (`DEEPSEEK_TOKEN_PRIMARY`, `DEEPSEEK_AWS_WAF_TOKEN`, `DEEPSEEK_COOKIES`, etc.)
- `docs/CREDENTIAL-EXPOSURE.md` - why the committed `browser-data/` is a finding, not a feature
- `deepcli/session_manager.py` - the consumer side that turns these captured values into request cookies/headers