# Termux Fleet RepoStory — AppID record

- **App ID:** 5565297
- **Slug:** `termux-fleet-repostory` (canonical — verified at creation; no bounce variant consumed)
- **Client ID:** Iv23lir0OJoDVeqXSaRq
- **Owner:** timerloggedout-spec
- **Public:** true — https://github.com/apps/termux-fleet-repostory
- **Installation:** 177463385 (timerloggedout-spec, timerloggedout-spec/repo-story ONLY)
- **Permissions:** contents write, pull_requests write, issues write, metadata read. No webhook (no URL — no hook attributes in the manifest). Events: none.
- **Created:** 2026-11-01 by the AppID lane via the App Manifest flow — FIRST case under the owner rule of record (2026-11-01 01:48 PT: build start for any competition entry ⇒ NEW dedicated repo + NEW AppID via the AppID lane; competition fit gates claims only, never construction; rule landed in-repo PR #3022). Repo-Story build started 2026-11-01 (repo created 2026-11-01T08:38:46Z; Jules via desk issue #3018); request via Repo-Story manager 8cc20168. Creation ran in the owner's signed-in session with NO auth prompt surfaced (sudo window warm). Private key + client secret = 0600 custody files in `custom.github-app-repostory/keys/` (pubkey fp `e281ec13a6f4bd1bdf790bdf1c50be1bece27cf5070fbd428804b8acff9913b6`; rotation due 2027-05-01).
- **Moniker:** `Chronicler · RepoStory` (canonical Chronicler; aspect the Annals; registry-issued 2026-11-01, docs/ops/AGENT-MONIKERS.md PR #3027; queued alt Clio = candidate only, mark Cl1o; leet marks Chr0nicler > Chron1cler; bounces chr0nicler > chron1cler NOT consumed).
- **Role:** per-entry fleet actor identity for the Repo-Story competition entry — the entry's workflows/build actors mint installation tokens as `termux-fleet-repostory[bot]` under their own identity and 5000/h bucket on repo-story. Fleet actor identity ONLY, not a product surface (product surfaces = the entry's Action + pre-push hook + pinned Story, per the concept's Δ1).
- **Actions minting (SEC-03):** secret `TERMUX_FLEET_REPOSTORY_PRIVATE_KEY` + vars `TERMUX_FLEET_REPOSTORY_CLIENT_ID` / `TERMUX_FLEET_REPOSTORY_APP_ID` provisioned 2026-11-01 ON timerloggedout-spec/repo-story (sealed-box via PAT, names-only; verified present by read-back; repo-story secrets census 1 at check). Workflows mint via `actions/create-github-app-token` with the numeric APP_ID (5565297).
- **Scope honesty:** provisioning != adoption: repo-story workflows adopt the mint step as their own PRs (Repo-Story manager lane owns the build).
- **Verification (2026-11-01T10:29Z, firsthand via App JWT):** installations = 1 (selected), /installation/repositories = repo-story only, installation bucket 5000/5000.
- **Avatar:** `avatar.png` in this package (chronicler-bot with gold quill writing the annals, git-constellation behind, indigo/gold/teal), uploaded to GitHub 2026-11-01 — PNG 1600×1600, 628,938 B under the 1 MB logo cap.
