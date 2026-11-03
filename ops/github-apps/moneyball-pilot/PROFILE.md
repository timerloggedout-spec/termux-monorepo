# Termux Fleet MoneyBall — AppID record

- **App ID:** 5602878
- **Slug:** `termux-fleet-moneyball` (canonical — verified at creation; no bounce variant consumed)
- **Client ID:** Iv23li4q4FnN7UOvJddY
- **Owner:** timerloggedout-spec
- **Public:** true — https://github.com/apps/termux-fleet-moneyball
- **Installation:** 178357694 (timerloggedout-spec, timerloggedout-spec/moneyball ONLY)
- **Permissions:** contents write, pull_requests write, issues write, metadata read. No webhook (no URL — no hook attributes in the manifest). Events: none.
- **Created:** 2026-11-03 by the AppID lane via the App Manifest flow — under the owner rule of record (2026-11-01 01:48 PT: build start for any competition entry ⇒ NEW dedicated repo + NEW AppID via the AppID lane; rule landed in-repo PR #3022), RepoStory pattern. Repo timerloggedout-spec/moneyball (id 1444884380, public, created 2026-11-03T22:08:54Z) created by the Web3 · MoneyBall seat; AppID ordered by the owner via main 2026-11-03 14:06 PT. Creation ran in the owner's signed-in session: GitHub interposed sudo Confirm access at the first manifest POST; the owner's GitHub Mobile approval cleared the session the same day and the resumed leg created the app (no credential was entered by any agent at any point). Private key + client secret = 0600 custody files in `custom.github-app-moneyball/keys/` (pubkey fp `3528599310cced1580e6af6c4903d9a79b1103ddd54330a0aacd3eef939b42d1`; rotation due ~2027-05-03).
- **Moniker:** `Actuary · MoneyBall` (canonical Actuary; aspect the Table; registry-issued 2026-11-03, docs/ops/AGENT-MONIKERS.md PR #4645; queued alt Kelly, mark K3lly; leet marks Actu4ry > 4ctuary; bounces actu4ry > 4ctuary NOT consumed).
- **Role:** per-entry fleet actor identity for the MoneyBall site entry (speculator market over fleet outcomes) — the entry's workflows/build actors mint installation tokens as `termux-fleet-moneyball[bot]` under their own identity and 5000/h bucket on moneyball. Fleet actor identity ONLY, not a product surface (The Book stays record in termux-monorepo; the site is the product surface).
- **Actions minting (SEC-03):** secret `TERMUX_FLEET_MONEYBALL_PRIVATE_KEY` + vars `TERMUX_FLEET_MONEYBALL_CLIENT_ID` / `TERMUX_FLEET_MONEYBALL_APP_ID` provisioned 2026-11-03 ON timerloggedout-spec/moneyball (sealed-box via PAT, names-only; verified present by read-back; moneyball secrets census 1 at check). Workflows mint via `actions/create-github-app-token` with the numeric APP_ID (5602878).
- **Scope honesty:** provisioning != adoption: moneyball workflows adopt the mint step as their own PRs (Web3 · MoneyBall seat owns the build; first tier-3 QUE dispatches were gated on this AppID landing).
- **Verification (2026-11-03T22:38Z, firsthand via App JWT):** installations = 1 (selected), /installation/repositories = moneyball only, installation bucket 5000 (4,999 remaining at check).
- **Avatar:** `avatar.png` in this package (green diamond field, gold ball with stitches, $ mark), uploaded to GitHub 2026-11-03 — PNG 460×460, 5,807 B under the 1 MB logo cap.
