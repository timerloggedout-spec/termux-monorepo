# Termux Fleet Collector — GitHub App profile (github.com/apps/termux-fleet-collector)

- **Display name:** Termux Fleet Collector
- **Slug (auto from name):** termux-fleet-collector — VERIFY at creation; if taken, suffix `-tm` and record the real slug here (names are provisioning facts, never invented).
- **Bot author identity:** `termux-fleet-collector[bot]`
- **Description (profile page + manifest):** Fleet collector for timerloggedout-spec/termux-monorepo: scheduled quota readings, feed collection and evidence harvest on an ephemeral GitHub App installation token — its own rate-limit bucket, separate from the owner PAT bucket. Read-only pilot; part of the fleet's automated revision-adaptive allocation process.
- **Homepage:** https://github.com/timerloggedout-spec/termux-monorepo
- **Avatar:** `avatar.webp` in this directory (robot librarian + gauge). Upload at app Settings → Profile picture.
- **Visibility: PUBLIC — by design (owner goal, 2026-10-29).** The end state is that OTHERS can install these apps on their own repos and bring the bot identity into their own comments/PRs (`termux-fleet-collector[bot]` acting and mentionable there). A private app can only be installed on the owner's account, so the pilot ships public from day one. Public ≠ marketplace-listed: no listing, no review gate; anyone with the app URL can install, each installation = its own token + its own rate-limit bucket on THEIR account.
- **Permissions (pilot, read-only):** metadata / contents / pull_requests / issues / checks / actions = read. No webhooks, no events. Read-only is what makes public installation safe to offer: an installer grants reads on repos they choose, nothing else, revocable per-repo at any time.
- **Scope rule note:** this app is a FUNCTION identity (`collector`), not a lane-coordination moniker — AGENT-MONIKERS.md scope is untouched. If the pilot graduates, per-role apps follow the same pattern (function-named, least-privilege).
