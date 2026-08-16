# Secrets & keys — continuous ADE contract

**Agent: Grok** · Profile: https://x.com/grok  
Device: BLU B160V Termux · Aligns with GitHub PR **#18 Sentinel** (0o700 dirs / 0o600 files)

## Hard rules

1. **Never commit** API keys, PATs, cookies, or session material to git.
2. **Presence-only** checks in code (`os.environ.get(...)`) — never log or write the value.
3. **Fail closed** if a secret-bearing directory cannot be locked down (chmod OSError → abort before read/write).
4. **B160V**: no always-on process that holds secrets in RAM longer than a single session.

## Environment variables (skyhook / Jules)

| Variable | Purpose | Where set |
|----------|---------|-----------|
| `JULES_API_KEY` or `GOOGLE_JULES_API_KEY` | Jules API / dispatch | Termux env, CI secrets, or host agent — **not** in repo |
| `SKYHOOK_HOME_REPO` | Default `timerloggedout-spec/termux-monorepo` | Optional override |
| `SKYHOOK_DEFAULT_BRANCH` | Default `master-staging` | Optional |
| `SKYHOOK_PACKAGE_BRANCH` | Default `feature/skyhook` | Optional |
| `SKYHOOK_PREFER_STAGING` | Prefer staging gate (`1` default) | Optional |
| `JULES_API_BASE` | Override API base URL | Optional |

`skyhook/bridge/config.py` only records **whether** a Jules key is present (`jules_api_key_present: bool`).  
`skyhook/bridge/http_client.py` reads the key only at request time and never persists it.

## Sentinel alignment (PR #18)

When #18 lands on `master-staging`:

- Credential / config directories → **0o700**
- Token / session files → **0o600**
- `mkdir(..., mode=0o700)` + `os.chmod`; **do not** swallow `OSError`

skyhook doctor (offline) should eventually assert permission bits on known paths **if they exist**, without requiring secrets to be present.

## Where secrets live (recommended)

| Surface | Pattern |
|---------|---------|
| Local Termux | `export` in a **gitignored** shell profile fragment, or `termux-keystore` / file under `~/.config` with 0o700 parent |
| GitHub Actions | Repository **Secrets** / **Variables** — inject only into job env |
| Jules cloud sessions | Jules project / host secrets plane — phone stays free of long-lived key material |
| Linear / Notion | No API keys in page bodies; use integration connections |

## MCP / long-lived services

See `MCP_HOSTING.md`. Do **not** keep a Termux MCP (or any secret-bearing HTTP server) alive 24/7 on B160V. Prefer:

- Jules API via stdlib HTTP (presence key only when invoking)
- On-demand stdio-SSH for device control
- Hosted GitHub MCP / cloud Workers for non-device tools

## Agent checklist before push

- [ ] No `JULES_API_KEY=...` or PAT literals in diff
- [ ] No `.env` with real values committed
- [ ] Commit message includes Agent + Profile + Signed-off-by
- [ ] Target branch respects gate: package work on `feature/skyhook` → PR to `master-staging`

## Related

- `DEVICE_B160V.md` — hardware constraints
- `MCP_HOSTING.md` — no durable Actions MCP server
- GitHub #18 / Linear TER-19, TER-20 — Sentinel land
- `SIGNATURE.md` — Grok attribution
