# Help-wanted follow-up (automation)

**Status:** LIVE · refined 2026-09-23

## What it does

Polls **all open foreign PRs** authored by `timerloggedout-spec` (not only `review:changes_requested`).

| Action | Trigger |
|--------|---------|
| `changes` | `CHANGES_REQUESTED` **after** our last follow-up marker |
| `reengage` | Maintainer comment/review **after** last marker + ≥`REENGAGE_HOURS` (default 18) |
| `stale_nudge` | PR idle ≥`STALE_IDLE_HOURS` (default 72) + cooldown |
| `skip` | No new signal / still in cooldown |

Each non-skip posts a comment with:

- Thread / review excerpt
- **CONTRIBUTING.md** recon (if present in foreign repo)
- URLs extracted from thread + docs

## Scripts

- `scripts/ci/help_wanted_followup.py`
- `scripts/ci/help_wanted_foreign_recon.py`

## Cadence

`help-wanted-followup.yml` — cron `17 */2 * * *` + `repository_dispatch`.

Agent-Identity: Grok (Administrator)
