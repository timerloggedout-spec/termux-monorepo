# Challenge Full-Spectrum OSINT

Owner scope (2026-10-28): "Everything — the project, event, competitor,
judges, etc." The tracking system (`ops/challenge/coordinator.json` +
Neon DB + opportunity ledger) covers all of it, **public sources only**,
every fact sourced + `fetched_at`, gaps `NOT_ESTABLISHED`.

## Devpost expansion

The event-level lifecycle remains owned by this challenge OSINT lane. The global Devpost software directory is a separate discovery surface and requires its own adapter; the authenticated Devpost event connector does not expose general directory search. The proposed adapter boundary, BEFORE/DURING/AFTER lifecycle, directory schema, cadence, podium capture, and graph integration are specified in [`DEVPOST-OBSERVATORY-EXPANSION.md`](DEVPOST-OBSERVATORY-EXPANSION.md). That document is an architecture proposal; its proposed directory cadence is not configured until a workflow is deployed and observed.

## GitLab AI Hackathon source family

GitLab's AI Hackathon sources are tracked as a distinct public-source family,
separate from Devpost's global software directory and separate from the
existing event records. The source hierarchy, event distinctions, Discord
onboarding, reusable participant template, date discrepancies, and future-cycle
watch disposition are recorded in
[`GITLAB-AI-HACKATHON-OSINT.md`](GITLAB-AI-HACKATHON-OSINT.md).

The machine-readable URL inventory is
`ops/challenge/osint/gitlab-sources.json`. It records the supplied root group
and DevSecOps Flow subgroup, the Transcend and Project Templates subgroups,
the Participant Template project, the 312-project sibling Transcend catalog,
the archived October 2026 Transcend group, Devpost event/gallery/participants/
rules/resources pages, the GitLab Community Hackathon pages, and the official
Discord/documentation links. The sibling snapshot is
`ops/challenge/osint/gitlab-transcend-projects-2026-11-22.json`; the October
showcase snapshots contain 1,273 subgroups and 1,820 projects under
`ops/challenge/osint/gitlab-transcend-october-2026-subgroups-2026-11-22.ndjson` and `ops/challenge/osint/gitlab-transcend-october-2026-projects-2026-11-22.ndjson`.
The supplied DevSecOps Flow URL resolved to an **empty subgroup** at the
2026-11-22 observation; retain it as a URL-addressed subgroup source.

The February–March 2026 GitLab AI Hackathon and October 2026 Life After Code /
Transcend edition are closed. The next GitLab Community Hackathon is published
for **January 21–28, 2027 UTC** (candidate C17); owner onboarding, rule acceptance,
issue assignment, and contribution state: NOT_ESTABLISHED; Devpost
registration: NOT_REQUIRED. This URL inventory
is a source register; C17 is now included in the candidate-page observer.

The PICO Space Program (candidate C18) is open for submissions
**November 18, 2026–February 1, 2027**. The Devpost event page, rules, and
Luma kickoff listing are watched as separate sources. The November 24
kickoff is listed by Luma as 10:00 AM–12:15 PM PT; the supplied Discord
announcement ends at 12:00 PM PT, so the 15-minute discrepancy remains
explicit pending organizer clarification. Registration and participant
eligibility remain user-specific and are not written to this public file.

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
`.github/workflows/challenge-osint-watch.yml` (daily 08:17 UTC + push on
coordinator/watcher/doc changes + dispatch; no VM execution):

1. Recomputes separate admitted-event and pre-admission-candidate coverage
   matrices → `ops/challenge/osint/coverage.json`.
2. Fetches each record's `watch_sources[]` (or `official_url` fallback),
   sha256-hashes each page, and **appends** a snapshot to
   `ops/challenge/osint/snapshots.json` only when the same record kind,
   event ID, URL, and hash have not been observed (a changed hash = a
   source-page change; the snapshot carries the source label and excerpt).
   Failed fetch appends nothing and warns.
3. Mirrors snapshots append-only into Neon (`osint_page_snapshots`,
   via `participant_event.py`) and proposes repo changes as a refresh
   PR (countdowns-feed pattern) — never commits directly. Candidate
   snapshots remain pre-admission observations; they do not create event
   rows or participant records.

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
