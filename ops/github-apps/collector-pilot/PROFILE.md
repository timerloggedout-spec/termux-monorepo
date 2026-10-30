# Termux Fleet Collector — GitHub App profile (github.com/apps/termux-fleet-collector)

- **Display name:** Termux Fleet Collector
- **App ID: 5535733** · **Client ID: Iv23liKMLj976ok6Cn3D** (provisioning facts, recorded at conversion 2026-10-30T02:17Z)
- **Installation ID (timerloggedout-spec): 176747357** — termux-monorepo only.
- **Slug (VERIFIED at creation):** termux-fleet-collector — profile https://github.com/apps/termux-fleet-collector
- **Bot author identity:** `termux-fleet-collector[bot]`
- **Description (profile page + manifest):** Fleet collector for timerloggedout-spec/termux-monorepo: scheduled quota readings, feed collection and evidence harvest on an ephemeral GitHub App installation token — its own rate-limit bucket, separate from the owner PAT bucket. Read-only pilot; part of the fleet's automated revision-adaptive allocation process.
- **Homepage:** https://github.com/timerloggedout-spec/termux-monorepo
- **Avatar:** `avatar.png` in this directory (robot librarian + gauge), uploaded to GitHub 2026-10-29 via Settings → Upload a logo. The package's earlier `avatar.webp` was removed 2026-10-30: GitHub's logo control rejects WebP and caps logos at 1 MB — PNG only.
- **Bucket-split proof (2026-10-30T02:18Z, PASSED):** app bucket limit 5000 / remaining 5000 while the PAT bucket read limit 5000 / remaining 0 in the same minute — buckets fully independent. First installation token minted via scripts/github_app_token.py (openssl RS256), installation reads scoped to termux-monorepo only.
- **Visibility: PUBLIC — by design (owner goal, 2026-10-29).** The end state is that OTHERS can install these apps on their own repos and bring the bot identity into their own comments/PRs (`termux-fleet-collector[bot]` acting and mentionable there). A private app can only be installed on the owner's account, so the pilot ships public from day one. Public ≠ marketplace-listed: no listing, no review gate; anyone with the app URL can install, each installation = its own token + its own rate-limit bucket on THEIR account.
- **Permissions (pilot, read-only):** metadata / contents / pull_requests / issues / checks / actions = read. No webhooks, no events. Read-only is what makes public installation safe to offer: an installer grants reads on repos they choose, nothing else, revocable per-repo at any time.
- **Scope rule note:** this app is a FUNCTION identity (`collector`), not a lane-coordination moniker — AGENT-MONIKERS.md scope is untouched. If the pilot graduates, per-role apps follow the same pattern (function-named, least-privilege).
