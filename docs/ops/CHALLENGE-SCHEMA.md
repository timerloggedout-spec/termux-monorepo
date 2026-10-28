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

## derived (computed, never hand-written)

`next_deadline`, `countdowns[]`, `critical_path[]`, and
`counts{submitted, registered, in_build}` are computed from the events
above — countdown states by `scripts/challenge_entries/countdowns.py`
over the stored deadline instants (issue #1880's rule: computed, never
hand-typed). The block carries a `computed_at` stamp; a stale stamp
means the next refresh recomputes it, not that anyone edits the values.

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
