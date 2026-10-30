# GitHub App pilot — Termux Fleet Collector

**Priority order (owner, 2026-10-29):**
1. **Self-directed, termux-monorepo allocation focus (FIRST).** Move scheduled
   collector reads off the owner PAT bucket (5000/h, shared fleet-wide — the
   bucket that walled the fleet 2026-10-28 and 2026-10-29) onto this app's
   installation token, whose bucket is independent. PAT is reserved for
   interactive publishes. This serves the automated revision-adaptive
   allocation process (`docs/ops/QUOTA-ALLOCATION-PLANNING.md`): the
   meta-pool gains a second, collector-dedicated bucket.
2. **Others can use it (ULTIMATE).** The app is PUBLIC: any other account
   can install it on their own repos and bring `termux-fleet-collector[bot]`
   into their own comments/PRs. Each foreign installation is that account's
   own bucket and responsibility. Designed-in from day one (public flag,
   read-only permissions) — exploited after the pilot proves out at home.

## Package (ops/github-apps/collector-pilot/)
- `manifest.json` — app definition of record (public, read-only, no webhooks).
- `PROFILE.md` — profile-page copy (github.com/apps/<slug>) + avatar spec.
- `avatar.webp` — profile picture.
- `scripts/github_app_token.py` — installation-token minter (openssl RS256
  JWT; key read from a local PEM path in env; token value never logged).
- `scripts/github_app_bucket_proof.py` — PAT vs app `/rate_limit` compare.

## Creation — programmatic (manifest flow; see docs/ops/GITHUB-APP-ROUTES.md)
Web computer use is an early-allowance workaround for single tests only;
the durable route is API-first:
1. `python3 scripts/github_app_manifest.py serve < ops/github-apps/collector-pilot/manifest.json`
   — serves the submission form on localhost and catches the result.
2. In any already-signed-in browser tab, open the localhost page and click
   Create once (the ONLY web-session step; GitHub has no REST create).
   GitHub redirects back with a one-time code; the tool converts it
   immediately (`POST /app-manifests/{code}/conversions`) and writes the
   bootstrap PEM + secrets to 0600 files — values never printed or chatted.
3. Install consent: open the returned `install_url`, select
   `termux-monorepo` only. Record App ID + installation ID in PROFILE.md.
(Equivalent manual form-fill values remain in `manifest.json` /
`PROFILE.md` for reference.)

## Proof protocol (bucket split)
1. Mint: `GITHUB_APP_ID=… GITHUB_APP_INSTALLATION_ID=… GITHUB_APP_KEY_FILE=…pem GITHUB_APP_TOKEN_OUT=/path/tok python3 scripts/github_app_token.py`
2. `GH_PAT_TOKEN=… GH_APP_TOKEN=$(cat /path/tok) python3 scripts/github_app_bucket_proof.py`
3. PASS = the app principal reports its own limit/remaining line, distinct
   from the PAT user's — then run one real collector read batch on the app
   token and confirm the PAT bucket's remaining is unchanged by it.

## Graduation criteria
- Proof PASS + one week of scheduled collector reads on the app token with
  zero PAT-bucket collector spend → collectors switch by default; PAT
  reserved for publishes.
- Then: per-role function apps on the same pattern (reviewer, publisher),
  each public, least-privilege; profile pages become the fleet's public
  identity cards for the collaborative monikers program.
