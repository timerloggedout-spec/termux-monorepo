# D3 Builder.io Agent-Native — Promo Plan ∧ Copy Set

`[MUSEai]@{role:{marketing-channel-d3}}` · lane = marketing sub-lane ↦ parent
`{role:{marketing-channel}}` (chat 81cbe17c) · build/submission owner =
entries lane a33d3ca1 ∧ manager `{role:{challenge-entries-manager}}`
(chat 9cb1c873) ∧ D3 seat 39fc8b89.
Status: ACTIVE — Beat A PUBLISHED 2026-10-31 (see §2); remaining
beats fire on evidence events, ¬ calendar alone.

## 1. Census (verified firsthand, 2026-10-31)

| Claim | Evidence |
|---|---|
| Project = ListingLens, pick FROZEN 2026-10-30 (manager-enacted) | coordinator.json@master `4ec62cb1e451` (PAT-API read 2026-10-31), D3.projects[listinglens].status=frozen |
| Deadline = Mon 2026-11-09T23:59-08:00 PT ⇒ supersedes Nov 2 read | coordinator D3.dates.deadline (Official Rules verbatim, read 2026-10-28; correction landed PR #2045) |
| Final weekend Nov 6–8; winners 2026-11-13 | coordinator D3.dates ∧ BUILD-BRIEF.md |
| Build = DONE: checkpoint build merged ∧ synced | PR #2616 merged `6ea0e52b0d95` ⇒ listinglens repo @`59c6c3b0427d`; Nov 1 checkpoint PASS early (manager relay 2026-10-31, verified vs coordinator provenance) |
| Polish = Nov 6–8 via provider dispatch (Jules), secondary ↦ D2 primary | manager relay 2026-10-31 ∧ coordinator schedule |
| Submission = none; registration = not required | coordinator D3.submission.state=none ∧ D3.registration |
| Gate D3-CLIPS-STORAGE = OPEN (blocks demo upload only); clips_url = ∅; ETA = NOT_ESTABLISHED | coordinator D3.gates; entries-lane in-app step; demo recording lands Nov 6–8 window |
| Surfaces: public repo + official event page ONLY; demo/social/project-page = ∅ | https://github.com/timerloggedout-spec/listinglens (public, API-verified) ∧ https://builder.io/hackathon |
| Prizes: pool $10,000 {Grand $5,000 / 2nd $2,500 / 3rd $1,500 / 4th $750 / 5th $250}, ≤1 cash/project | coordinator D3.prizes (Official Rules) |
| Judging: Usefulness∧Execution 40% / Creativity∧Design 20% / Innovation 20% / Agent-Native cleverness 20% | coordinator D3.brief ∧ BUILD-BRIEF.md |
| Channels available: FB Pages fb-a (id 1403768132822477) ∧ fb-b (1368017223068543) from campaign fb-pages-mvt-1 | experiments/marketing/fb-pages-mvt-1 records (PR #2705) |

∴ Constraints: (a) promotable surface = repo link ONLY until Clips
demo lands; (b) ∅ submitted/demo-live claims pre-evidence; (c) 4n0n
protocol ∀ public artifacts (∅ names, ∅ owner identity); (d) copy
generation delegated, this lane edits ∧ verifies (claim-level refs
per #1734); (e) notation per #320.

## 2. Beats (event-triggered)

1. **A Build-in-open** — FIRED ✓ 2026-10-31: parent channel call
   = fb-a (Dream In Production); published 2026-10-31T09:37:48 PT,
   post_id `122096301147538523`, visibility public (verified
   firsthand via facebook-cli `post read`):
   https://facebook.com/61596155692530/posts/pfbid05UUNPezsZaG3vrtGKAsXbaSW7rnSJ9XNBMPSSGHFjqDYVXctP2RosEHVpNLmVGBRl/
   Watch baseline @2026-10-31T09:38 PT: comments 0, reactions 0.
2. **B Final-weekend / polish** — fire: Nov 6–8 window opens ∧
   polish dispatch receipt exists. Includes Clips-demo link ONLY
   when clips_url is verified public (no-login viewable).
3. **C Submission** — fire: entries lane confirms submission via
   builder.io/hackathon/submit + receipt, ≤ Nov 9 23:59 PT.
   `[SUBMITTED_AT]` ∧ `[CLIPS_URL]` fill at that moment only.
4. **D Winners-watch** — fire: winners announced 2026-11-13
   (target date, Official Rules). Post outcome win ∨ loss.
5. **Audience/comment watch** — from Beat A: FB comments ∧ repo
   issues/stars ∧ Builder.io surfaces, checked per beat; build
   questions route ↦ entries lane, answered from evidence only.

## 3. Copy set (delegated generation; edited ∧ verified by this lane)

Edit note: delegated drafts said "build in progress" — corrected
∀ beats: checkpoint build DONE 2026-10-31, polish pending Nov 6–8.

### 3.1 Beat A — Build-in-open (FB Page, ~70 words)

> Building in the open: ListingLens, our entry for the Builder.io
> Agent-Native Hackathon.
>
> It's an app where people and agents work together — the agent
> does a real job, and you can view, edit, and act on its work
> instead of just watching it.
>
> Status, receipts-first: checkpoint build is merged and public.
> Not submitted yet. Public Clips demo lands in the Nov 6–8
> polish window.
>
> Deadline: Mon Nov 9, 2026, 23:59 PT.
> Repo: https://github.com/timerloggedout-spec/listinglens

Short variant (~40 words):

> Build-in-open update: ListingLens for the Builder.io
> Agent-Native Hackathon. People + agents working together, with
> a human interface to view, edit, and act on the agent's work.
> Checkpoint build merged, not submitted yet, Clips demo pending.
> Public repo: https://github.com/timerloggedout-spec/listinglens
> — deadline Nov 9, 23:59 PT.

### 3.2 Beat B — Final weekend (~58 words)

> Final weekend: Nov 6–8. ListingLens is in its last polish
> window for the Builder.io Agent-Native Hackathon.
>
> Focus is execution — the part judges weight most, at 40%: a
> working agent job, and a clean surface to view, edit, and act
> on what it produces.
>
> Still to close: public Clips demo recording, then submission.
> Deadline: Mon Nov 9, 23:59 PT.
> Repo: https://github.com/timerloggedout-spec/listinglens

### 3.3 Beat C — Submission template (~70 words; fire on receipt only)

> Submitted: ListingLens for the Builder.io Agent-Native
> Hackathon.
>
> Submitted at: [SUBMITTED_AT] — ahead of the Mon Nov 9, 2026,
> 23:59 PT deadline.
>
> ListingLens is built on the Agent-Native framework: an agent
> with a real job, and an interface where people can view, edit,
> and act on its work.
>
> Public demo — Clips: [CLIPS_URL]
> Public repo: https://github.com/timerloggedout-spec/listinglens
>
> Judging: Usefulness/Execution 40%, Creativity/Design 20%,
> Innovation 20%, Agent-Native cleverness 20%.

### 3.4 Beat D — Winners-watch template (~44 words)

> Results watch: ListingLens — Builder.io Agent-Native
> Hackathon.
>
> Our submission is in — demo and repo links are in the previous
> post. Prizes: $5k / $2.5k / $1.5k / $750 / $250 across five
> places.
>
> We'll post the outcome here as announced, win or not. Repo
> and Clips demo stay public either way.

### 3.5 Comment-reply templates

What is it?

> ListingLens is a people + agents app for the Builder.io
> Agent-Native Hackathon: the agent does a real job, and you get
> an interface to view, edit, and act on its work — not just a
> chat box. Public repo: https://github.com/timerloggedout-spec/listinglens

Tech stack?

> Agent-Native framework — built around `defineAction()` from
> `@agent-native/core`. That structure is what lets the agent's
> work show up as actions a person can view, edit, and act on.
> Code is public in the repo linked in the post.

Where can I try it?

> Honest status: there's no live demo to try yet — the public
> Clips demo records in the Nov 6–8 window (storage gate still
> closing). The public repo is here:
> https://github.com/timerloggedout-spec/listinglens — we'll
> drop the Clips link in this thread as soon as it's verified
> live.

## 4. Watch ∧ handoffs

- Clips gate closure ∨ submission receipt ⇒ entries lane relays
  ↦ this lane same-turn; Beat B/C fire ≤1 beat after evidence.
- ∅ coordinator.json edits from this lane (single-writer =
  entries lane); promo state lives in this file only.
- Media production = OUTSOURCE per owner order; ∅ fleet quota
  burn for media in these beats (text + repo link only).
