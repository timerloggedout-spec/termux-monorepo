# Challenge Full-Spectrum OSINT

Owner scope (2026-10-28): "Everything — the project, event, competitor,
judges, etc." The tracking system (`ops/challenge/coordinator.json` +
Neon DB + opportunity ledger) covers all of it, **public sources only**,
every fact sourced + `fetched_at`, gaps `NOT_ESTABLISHED`.

## Surfaces

- **EVENTS** — organizer intel (`events[].organizers[]`), rules/prize
  changes, announcements, schedule shifts: watched by official-page
  snapshots (below); changes log as new snapshots, never edits.
- **PROJECTS** — ours (`events[].projects[]`) + competitors'
  (`events[].participants[].project{}`: public repos, demos, articles;
  engagement counts ride append-only `signals.snapshots[]`).
- **COMPETITORS/PARTICIPANTS** — persona profiles, past wins, signals (observation-only; recruitment is OUR TEAM ONLY per owner ruling 2026-10-28 — externals are never recruitment candidates)
  (CHALLENGE-SCHEMA.md participants section; MoneyBall v2 evaluations).
- **JUDGES** — profiles, orgs, public statements/criteria, judging
  history (`events[].judges[]`).
- **PRIZES** — verbatim tiers + changes (`events[].prizes{}`; page
  snapshots carry prize excerpts for diffing).

## Watch mechanism (recurring, GitHub-native per VM rule)

`scripts/challenge/osint_watch.py` + workflow
`.github/workflows/challenge-osint-watch.yml` (weekly Wed 08:17 UTC +
push on coordinator + dispatch; no VM execution):

1. Recomputes the coverage matrix → `ops/challenge/osint/coverage.json`.
2. Fetches each event's official public page, sha256-hashes its text,
   and **appends** a snapshot to `ops/challenge/osint/snapshots.json`
   only when the hash is new (a changed hash = prizes/rules/schedule
   changed on the official page; the snapshot carries a prize excerpt).
   Failed fetch appends nothing and warns.
3. Mirrors snapshots append-only into Neon (`osint_page_snapshots`,
   via `participant_event.py`) and proposes repo changes as a refresh
   PR (countdowns-feed pattern) — never commits directly.

## Coverage matrix (baseline 2026-10-28, collector firsthand)

| event | organizers | dates | prizes✓ | rules | our projects | competitors | judges | signals | recruitment | opp cost | page watch |
|---|---|---|---|---|---|---|---|---|---|---|---|
| STRANDS-DECIDER | 1 | 3 | 1 | 1 | 1 | — | — | — | — | OC-001 | ✓ |
| D0 | 1 | 1 | 5 | — | 1 | — | — | — | — | OC-002 | ✓ |
| D1 | 1 | 4 | 1 | 2 | 5 | 1 | — | 1 | 1 | OC-003 | ✓ |
| D2 | 2 | 3 | 3 | 4 | 1 | — | — | — | — | ✓ | ✓ |
| D3 | 1 | 5 | 5 | 3 | 2 | — | — | — | — | ✓ | ✓ |
| D4 | 2 | 4 | NOT_EST | 2 | 3 | — | — | — | — | ✓ | ✓ |
| D5 | 1 | 5 | 2 | 3 | — | — | — | — | — | ✓ | ✓ |

Legend: number = records populated; — = none yet / NOT_ESTABLISHED
(population follows the gallery schedule in CHALLENGE-SCHEMA.md:
judges populate when an event names them publicly; participants as
galleries open). Prizes column shows tier counts when ESTABLISHED
(D4 = NOT_ESTABLISHED, tiers TBD Oct 30). Baseline page snapshots:
7/7 official pages fetched 2026-10-28.

— Stood up 2026-10-28 by the challenge-entries-manager assistant seat;
entries lane (a33d3ca1) owns the source records, DB lane pattern
(e3055a9c) owns the store.
