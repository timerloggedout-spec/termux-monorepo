# Challenge Full-Spectrum OSINT

Owner scope (2026-10-28): "Everything — the project, event, competitor,
judges, etc." The tracking system (`ops/challenge/coordinator.json` +
Neon DB + opportunity ledger) covers all of it, **public sources only**,
every fact sourced + `fetched_at`, gaps `NOT_ESTABLISHED`.

## Discovery sources — new-opportunity intake

The discovery layer must search more than already-known event pages. **Devpost is now an explicit candidate-discovery source**, not an exclusive source and not the final record of truth:

- **Devpost directory:** https://devpost.com/hackathons — scan public, upcoming/open listings; use online/in-person, status, length, interest tags, host and public/invite-only filters to widen and narrow the candidate set.
- **Devpost AI category:** https://devpost.com/c/artificial-intelligence — focused AI challenge discovery.
- **Per-event Devpost pages and rules:** verify eligibility, dates/time zones, project originality, required technologies, submission fields, judging, prizes and updates before admission.
- **Other discovery lanes remain in scope:** sponsor/organizer pages (including AWS Builder Center and direct Google/Atlassian/Mozilla program pages), lablab.ai, MLH, HackerEarth and Devfolio. These are alternatives/complements; a directory listing is a lead, not verified event truth.

**Automation boundary (important):** the current scripts/challenge/osint_watch.py watches official URLs already present in coordinator.json; it does not crawl the global Devpost directory or discover new events by itself. C17 / SLAY HACKS is a firsthand-verified candidate intake from the Devpost directory and its event/rules pages on 2026-11-16. A recurring directory-discovery collector remains a separate implementation task. Every candidate must carry discovery_source, sources[] and fetched_at; unresolved eligibility stays a hard hold, not an inferred pass.

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

## Recurring Devpost directory collector

`scripts/challenge/devpost_discovery.py` scans pages 1–5 of both the public Devpost hackathon
directory and AI category on a daily GitHub Actions schedule (10 bounded
page requests with a short inter-request pause). Source failures are retained
in each run receipt; if all pages fail, the previous feed is left untouched. It writes
`ops/challenge/discovery/devpost-directory.json`, a deduplicated, timestamped
lead feed. Each record carries source URLs, first/last seen, a title-keyword
triage heuristic, and explicit `UNVERIFIED_LEAD` / `NOT_ESTABLISHED`
states. The score is a search-order hint only—not fit probability, eligibility,
or expected value.

The collector never writes `coordinator.json`, promotes candidates, registers,
submits, or creates wagering-book subjects. Event pages and rules must be
verified before a separate governed admission. Existing human review notes and
verification states survive later scans. A run with both sources unavailable
fails without replacing the last good feed.

The directory scan currently covers Devpost's general directory and AI
category. lablab.ai, MLH, HackerEarth, Devfolio, and sponsor/organizer pages
remain complementary discovery sources recorded in the feed as not yet
automated; they are not falsely reported as crawled by this collector.
