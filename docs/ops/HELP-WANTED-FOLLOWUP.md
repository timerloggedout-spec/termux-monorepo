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


## Feedback-first safety invariant (2026-10-18)

A stale nudge is permitted only when there is **no substantive maintainer feedback/review** in the observed thread and no known `CHANGES_REQUESTED` review. If feedback exists but predates our last marker, the next action belongs to our side: adapt the patch, validate the fix, or mark the work blocked. Do not ask the maintainer to repeat guidance that is already present.

New substantive comment/review feedback after the last marker remains eligible for `reengage` after the configured cooldown; `CHANGES_REQUESTED` after the marker retains priority. A trusted maintainer `APPROVED` review—including an empty-body approval—suppresses stale nudges but is not itself a request to re-engage. The policy is covered by `tests/test_help_wanted_followup_policy.py`.
