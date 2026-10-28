# Challenge Coordinator Schema (v1)

The machine-readable source of truth for the challenge-entries lane is
**`ops/challenge/coordinator.json`**. The challenge log
(`docs/ops/CHALLENGE-ENTRIES-LOG.md`, §4) is the human view rendered
from the same state; this document defines the JSON's shape. Tooling
reads the JSON; people read the log. Where they disagree, the JSON is
corrected by PR and the log re-rendered to match — never the reverse
silently.

**Population rule:** current *verified* state only. Every fact carries
its evidence (a `source` on dates, a `source_url` on prize tiers, an
`evidence[]` on registrations and gates). Anything not verified from an
official page or a firsthand record is `NOT_ESTABLISHED` (dates, prize
sets) or `null` — never inferred, never reconstructed from plausibility.

## coordinator

| field | meaning |
|---|---|
| `role_moniker` | the Manager's coordination moniker (`challenge-entries-manager`) |
| `chat_id` | the Manager seat's side-chat id |
| `scope` | what the Manager owns (the lane + countdown-critical path) |
| `subs[]` | per-event sub-coordinators: `{suffix, event_id, chat_id}` — suffixes `-d1`..`-d5` on the Manager moniker (coordination identities, `docs/ops/AGENT-MONIKERS.md`); `chat_id` is null while a sub has no chat of its own |

## events[]

One object per packet (D0–D5), mirroring log §4.

| field | meaning |
|---|---|
| `id`, `name`, `host`, `platform` | event identity; `platform` is the registry platform_id |
| `also_platforms[]` | optional second platform (e.g. D2's `vultr` beside `lablab-ai`) |
| `official_url` | the official event page, or `null` when no canonical URL is in the record |
| `status` | `closed` \| `active` \| `registering` \| `upcoming` |
| `entrant_moniker` | canonical registry reference (e.g. `entrant{n0nAha}[platform:aha-io]`), or `null` |
| `dates{}` | `announced`, `reg_open`, `reg_close`, `build_start`, `build_end`, `submissions_open`, `deadline`, `judging_end`, `winners_at` — each either `{at, tz, source}` (ISO instant + IANA/America-Los_Angeles tz + where it was verified) or the string `NOT_ESTABLISHED` |
| `constraints[]` | hard rules, verbatim from the official page/rules |
| `gates[]` | `{id, label, blocks, owner, status (open\|cleared), evidence}` — enforced checks, per the lane's eligibility standard |
| `prizes{}` | `{status (ESTABLISHED\|NOT_ESTABLISHED), pool, tiers[{place, award, source_url}], notes}` — `pool`/`notes` optional; tiers verbatim amounts only |
| `opportunity_cost{}` | see Opportunity-cost section below — always populated per event |
| `registration{}` | `{state, evidence[]}` — platform join/registration state with its proof |
| `submission{}` | `{state (none\|draft\|submitted\|confirmed), at, confirmation_ref}` |
| `brief{}` | `{evidence_pack_ref, anchor_lines[]}` — the verbatim official-brief pack the concept generation anchors to |
| `projects[]` | see below |

## projects[] (nested per event)

| field | meaning |
|---|---|
| `id`, `name`, `one_liner` | project identity |
| `origin` | `oracle_proposal#<n>` \| `brief-first-gen` \| `hand-packet` |
| `brief_anchor` | the brief line/record the project derives from, or `null` |
| `status` | `candidate` \| `alternate` \| `picked_pending_freeze` \| `frozen` \| `in_build` \| `submitted` \| `questioned` \| `abandoned` \| `superseded` |
| `reason` | required in substance for `questioned` / `abandoned` / `superseded` (the ruling + date) |
| `superseded_by` | project id or `null` |
| `assets{}` | `{repo_dir, proposal_dir, demo_url, clips_url}` — each a path/URL or `null` |
| `decisions[]` | `{at, by, action, pr, sha}` — the audit trail; PR numbers + merge SHAs as recorded in the log |

Notes on current usage:

- Registry proposals that were never entries (D1's #43–#45) are recorded
  as projects with `status: abandoned` and a reason stating they are
  **not-entries** — the record exists so the taint ruling is auditable,
  not to make them candidates.
- A `questioned` project (D3's #42) keeps its full record and decisions;
  questioned is a review state, not a termination.

## opportunity_cost{} (per event, owner order 2026-10-28)

Opportunity-cost metrics sit alongside prizes/participants/judges/signals/podium/recruitment.

| field | meaning |
|---|---|
| `outcome` | `submitted` \| `not_submitted` \| `pending` — from `submission.state` + event status (closed+none = not_submitted; open window = pending) |
| `top_award{value, form, source}` | highest single award: numeric `value` in USD/credit-USD (null if NOT_ESTABLISHED), `form` verbatim, `source` = official source / verification record |
| `gross_foregone` | `top_award.value` if outcome=not_submitted, else 0 |
| `win_probability{estimate, basis{field_size, our_standing}}` | estimate = winning slots / field_size ONLY when field_size is verified from an official/public entrant count; otherwise null and field_size=NOT_ESTABLISHED. Never inferred. |
| `expected_value_foregone` | estimate × gross_foregone when estimate is established and outcome=not_submitted; null otherwise (pending/submitted = not yet / not foregone) |
| `non_monetary_foregone[]` | non-cash items foregone (backpack/badge/visibility/judge feedback), sourced from the award/rules |
| `computed_at` | date computed (YYYY-MM-DD) |

**D0 seed (verified):** AWS Weekend Challenge (Oct 23–26 PT), not_submitted, top award $200 total ($100 AWS credits + Builder Backpack, pool $1,000, top 5), field_size 40 (public project list exhausted 2026-10-26, no match for ours), estimate 5/40=0.125, gross_foregone 200, expected_value_foregone 25.0. **Correction 2026-10-28 (owner dispute, firsthand recheck):** official Awards list values EACH award at $200 ($100 credits + backpack implied $100); pool $1,000 = 5×$200, credits subtotal $500 — PR #2219's credits-only top value 100 / EV 12.5 superseded.

**DB (Neon, DB lane pattern):** sync rows carry `opportunity_cost` in events core; `challenge_events_current` exposes it and view `event_opportunity_cost` extracts outcome/gross/EV per event (schema.sql).

## derived (computed, never hand-written)

`next_deadline`, `countdowns[]`, `critical_path[]`, and
`counts{submitted, registered, in_build}` are computed from the events
above — countdown states by `scripts/challenge_entries/countdowns.py`
over the stored deadline instants (issue #1880's rule: computed, never
hand-typed). The block carries a `computed_at` stamp; a stale stamp
means the next refresh recomputes it, not that anyone edits the values.

## participants[] (nested per event) — other entrants, observed

Tracks ALL other participants per event, with their engagement
surfaces and persona profiles, from PUBLIC sources only.

| field | meaning |
|---|---|
| `id` | stable local id (event-scoped slug from the public team/project name) |
| `team_name` | as published on the source surface |
| `members[]` | public member names/handles as published; `NOT_ESTABLISHED` elements never invented |
| `platform_profile_url` | the participant's public profile on the event platform, or `null` |
| `project{}` | `{name, url, status}` — their public project (gallery/project page) |
| `persona{}` | `{bio, skills[], past_events[], past_wins[], public_links{github, devpost, linkedin, site, other}}` — public profile material only; any gap is `NOT_ESTABLISHED` (or `null` for a single link), never inferred |
| `engagement{}` | `{public_chats[{surface, url, handle, last_activity_at, notes}], touchpoints[]}` — where they are publicly reachable/active |
| `sources[]` | `[{url, fetched_at}]` — EVERY populated field traces to a listed source |
| `confidence` | `high` \| `medium` \| `low` — source quality/coverage for this record |

Rules (owner order, 2026-10-28):

- **Public sources only** — participant galleries, project pages,
  public profiles and posts. Nothing behind a login, nothing
  scraped against a platform's terms.
- **Sourced or NOT_ESTABLISHED.** Every field carries its source +
  `fetched_at`; gaps are recorded as `NOT_ESTABLISHED`, never
  inferred, never invented.
- **4n0n unlinkability untouched.** We observe other participants;
  nothing here links, names, or exposes OUR entrants — our own
  projects/personas never appear in `participants[]`.
- **Engagement is AUTONOMOUS (owner correction, 2026-10-28 —
  supersedes any draft-only/HITL-gate framing).** Outbound
  participant engagement (chats, forums, public channels) executes
  under the event's entrant moniker with NO draft/approval gate.
  Every touchpoint is logged — to the database mirror and to this
  JSON — as `{surface, at, content_ref}` in the participant's
  `engagement.touchpoints[]`. HITL pages are display surfaces only,
  never gates. Red lines unchanged: 4n0n unlinkability, no personal
  identifiers, credentials names-only.
- **Population schedule:** as each event's gallery opens — D4 at
  submissions open (Oct 30), D2 at build start (Nov 5), D5 at
  kickoff (Nov 17); D1/D3 from any public participant surface
  available now. Checked firsthand 2026-10-28: **D1's Projects tab
  is public** (signed-out) and is the population source — 1 project
  listed on day 1; its Participants tab is join-gated ("Join this
  hackathon to see its participants"; 323 joined per the page
  header) and is NOT a public source, so D1 tracking runs on
  Projects only. **D3 has NO public gallery** — submissions are
  form-only, so D3 participants populate from the winners/spotlight
  surface after Nov 13. `project{}` may also carry `repo_url` /
  `demo_url` when the project body itself publishes them (they are
  project links, not author-profile facts).

## judges[] (nested per event) + signals + recruitment (MoneyBall scope, owner 2026-10-28)

Participant tracking is a **MoneyBall lane for competitions**: the
same sourced-entity + time-series-signal + joined-view discipline
the fleet's MoneyBall weighting uses, applied to competitors and
judges.

**Judges** — `events[].judges[]`, same persona discipline as
participants:

| field | meaning |
|---|---|
| `id`, `name`, `org` | as published by the event/platform |
| `persona{}` | same shape as participants (bio, skills, past_events, past_wins, public_links) |
| `judging_history[]` | prior events judged, as published |
| `public_criteria[]` | their published judging criteria |
| `statements[]` | public statements (posts/talks) relevant to judging, each sourced |
| `sources[]`, `confidence` | as participants |

**Signals (time-series, per entity — participants AND judges):**
`signals.past_wins[]` = `{event, place, prize, project}`;
`signals.placements[]`; `signals.snapshots[]` = appended metric
snapshots `{at, fetched_at, source_url, comments_count, likes,
followers, project_engagement{}}`. Snapshots are APPEND-ONLY —
appended, never overwritten (the DB mirror's `participant_events`
rows carry them; the JSON carries the full series).

**Views (DB mirror):** prizes × competitors × profiles joined per
event — who won what, with what project, judged by whom
(`event_podium` view over the mirror, beside `participants_current`).

**Recruitment pipeline:** standout competitors/judges carry
`recruitment{candidate: true, pipeline_state}` with states
`identified → profiled → engaged → in_talks → collaborator`, or
`passed`. Engagement is autonomous (standing order above);
touchpoints logged as specified. Non-candidates carry
`recruitment{candidate: false, pipeline_state: null}`.

**Scoring (MoneyBall consumer pattern, landed 2026-10-28):**
evaluations use **moneyball-plane/v2** (`docs/schemas/moneyball-score.schema.json`,
validator `scripts/moneyball/moneyball_v2.py`; consumer mapping
`ops/moneyball/plane.json` consumers[0], PR #2211 — NOT the
ml/pipelines PR-triage scorer). Axes, sourced from the signals
fields: `track_record` .30 (past_wins + placements) / `momentum`
.25 (snapshots[] deltas) / `engagement_surface` .20 (public chats +
project engagement) / `composability_fit` .15 (persona skills vs
event themes) / `inverse_engagement_cost` .10. **Law: weights +
flag threshold are fixed at event intake, recorded in the event's
`moneyball{}` block in coordinator.json BEFORE any score is
published; never adjusted after seeing scores.** One v2 record per
(entity × event) evaluation, filed at
`ops/challenge-participants/scores/`, referenced from the entity's
`signals.moneyball_evaluations[]`. **Standout flag rule:**
`recruitment.candidate = true` requires composite ≥ the intake
threshold AND every axis `evidence_strength` in {evidenced,
limited} (an unverified axis cannot support a flag) AND a
v2-valid record. First evaluation (2026-10-28): D1
ladder-practice-sets composite **2.05** vs threshold 6.0, two axes
unverified → flag refused; the pre-pattern flag set in PR #2194
was corrected in the same landing (see the record's notes).

Population state at landing (2026-10-28): participants 0, judges 0,
candidates 0 across all events — no gallery has opened and no event
publishes named judges yet (D1: "a panel of AWS experts", unnamed;
D5: judges "to be announced during the Event" per its Contest
Rules). Entities populate on the schedule in the participants
section; judges populate when an event names them publicly.

## Required fields + surface contract (owner rule, 2026-10-28)

**Required information:** `prizes`, `dates`, `status`, and `gates` —
for every event, always populated in this JSON (a value, or
`NOT_ESTABLISHED` / an explicit state where unpublished). They are
never blank and never omitted.

**Named context surfaces** that must carry the required fields:

1. **Manager brief** — the ChallengeLane Manager's oversight surface
   (this JSON is its source; briefs drawn from it carry prizes,
   dates, status, and open gates per event).
2. **HITL web pages** — the countdowns dashboard
   (`apps/help-wanted-dashboard/countdowns.html`, via
   `challenge-countdowns-feed/v1.1`, whose entries carry `prizes`
   wired from this JSON by the feed collector).

On every surface, `NOT_ESTABLISHED` renders as `NOT_ESTABLISHED` —
an unpublished prize set or date is shown as such, never as an
empty field. A surface that drops a required field is a contract
defect, fixed on that surface.

## Update discipline

Changes land by PR (branch → PR → merge when gates pass), citing the
evidence for any state change. Status flips (a gate clearing, a spot
confirming, a submission landing) update the JSON and the log §4 view
in the same PR.

— Schema v1 landed 2026-10-28 by the challenge-entries lane under the
Challenge Management Manager's plan.
