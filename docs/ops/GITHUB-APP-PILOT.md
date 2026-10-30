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

## Owner creation steps (account-level; ~5 min)
1. github.com → Settings → Developer settings → GitHub Apps → New GitHub App.
   Fill from `manifest.json`: name "Termux Fleet Collector", homepage =
   repo URL, description = PROFILE.md text, permissions = the six reads,
   uncheck webhook Active, check "Anyone can install" (public) — or use the
   manifest flow with `manifest.json` verbatim.
2. Create → note the **App ID** (a provisioning fact; record it in PROFILE.md).
3. Private keys → Generate → download the PEM. **Vault it, never chat it:**
   store via the fleet vault pattern (names-only in chat: key id + last-used).
4. Profile picture → upload `avatar.webp`. Verify the slug on the profile
   page; record the real slug in PROFILE.md if it differs from the guess.
5. Install App → on timerloggedout-spec → select `termux-monorepo` only →
   note the **installation ID** (record in PROFILE.md).

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
