# Termux Fleet Swarm — AppID record

- **App ID:** 5560920
- **Slug:** `termux-fleet-swarm` (canonical — verified at creation; no bounce variant consumed)
- **Client ID:** Iv23lieRML2ZrPXEekgE
- **Owner:** timerloggedout-spec
- **Public:** true — https://github.com/apps/termux-fleet-swarm
- **Installation:** 177357774 (timerloggedout-spec, termux-monorepo ONLY)
- **Permissions:** actions write, checks write, contents write, issues write, pull_requests write, metadata read. No webhook (no URL — no hook attributes in the manifest). Events: none.
- **Created:** 2026-10-31 by the AppID lane via the App Manifest flow (owner GO 2026-10-31 16:53 PT via desk a440bcb2; final permission set = owner-approved restore incl. checks:write): manifest form POST in the owner's signed-in session (2FA-verify nudge skipped via GitHub's own deferral link; sudo Confirm access completed by the owner via GitHub Mobile), conversion POST /app-manifests/{code}/conversions, install consent. Private key + client secret = 0600 custody files in `custom.github-app-swarm/keys/` (pubkey fp `4550044eb59cadba4cad4fa666d4bfbe43f64e624fef2c98c84c96997d9dd23a`; rotation due 2027-05-01).
- **Role:** SWARM/provider workflow actor — workflows mint installation tokens as `termux-fleet-swarm[bot]` so swarm-generated events (PR creates, pushes, dispatches, issue creates/comments) are app-authored and trigger downstream runs, instead of parking as `action_required` under the GITHUB_TOKEN anti-recursion rule (B1, swarm doc `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md` §10–§11) or spending the operator PAT. Checks:write rides for swarm-stamped status on the Tribute lane family (app-scoped check runs can only be stamped by the owning app).
- **Actions minting (SEC-03):** secret `TERMUX_FLEET_SWARM_PRIVATE_KEY` + vars `TERMUX_FLEET_SWARM_CLIENT_ID` / `TERMUX_FLEET_SWARM_APP_ID` provisioned 2026-10-31 (sealed-box via PAT, names-only; verified present by read-back; repo secrets census 61 at check). Workflows mint via `actions/create-github-app-token` with the numeric APP_ID (5560920).
- **Scope honesty:** swarm tokens un-park only events generated WITH a swarm token; the pre-existing `action_required` pile (>=2666, swarm doc §10) is NOT retroactively released — stock clearance stays owner-UI. Provisioning != DISTRIBUTED: per-workflow mint adoption is the swarm lane's MIG-style work (first family #2750 delphi-ledger-feed-collect).
- **Verification (2026-10-31T23:56Z, firsthand via App JWT):** installations = 1 (selected), /installation/repositories = termux-monorepo only, installation bucket 5000/5000.
- **Avatar:** `avatar.png` in this package (six fleet bots in hexagon formation around a gold hub core, indigo/gold/teal), uploaded to GitHub 2026-10-31 — PNG 1600×1600, 737,350 B under the 1 MB logo cap.
