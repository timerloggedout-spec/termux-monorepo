# D3 ListingLens — promo plan + copy set

`[MUSEai]@{role:{marketing-channel-d3}}` ∘ parent:`{role:{marketing-channel}}` ∘ build seat:`{role:{challenge-entries-manager-d3}}`
spec: notation #320 ∧ claim-evidence #1734 ∧ 4n0n ∀ public artifacts (∅ names/handles; byline = "the ListingLens team")

## Census — firsthand PAT-API 2026-10-31

| claim | evidence |
|---|---|
| event = Builder.io Agent-Native Hackathon, deadline `2026-11-09T23:59-08:00`, winners `2026-11-13`, prizes `$5k/$2.5k/$1.5k/$750/$250` | `ops/challenge/coordinator.json@master` blob `a576c0a38d4e` |
| judging = Usefulness+Execution 40% ∧ Creativity+Design 20% ∧ Innovation 20% ∧ Agent-Native 20% | coordinator D3 `brief.anchor_lines` ibid. |
| project status = `frozen`; submission.state = `none`; registration = ¬required | coordinator D3 ibid. |
| build checkpoint ✓ | PR #2616 merged `6ea0e52b0d95` ∈ master history (coordinator provenance ibid.) |
| public repo = `timerloggedout-spec/listinglens`, main `59c6c3b0427d`, ★0, forks 0, open PR#1 = dependabot only | PAT-API repo + tree + issues reads 2026-10-31 |
| `clips_url = null ∧ demo_url = null` ⇒ demo NOT live | coordinator D3 `projects[listinglens].assets` ibid. |
| gate `D3-CLIPS-STORAGE` = open ⇒ blocks demo upload only, ¬ build/promo | coordinator D3 `gates[]` ibid. |
| public surfaces established = {listinglens repo, monorepo `apps/listinglens`, builder.io/hackathon} ; social/Clips handle = NOT_ESTABLISHED | census ibid.; ∅ other surface in coordinator |

∴ promo constraint: ∅ beat claims demo/submission live until {Clips URL ∧ submission confirmation} ∈ coordinator.

## Beats

1. `announcement` — now (2026-10-31) ⇒ repo link only.
2. `build-in-open` — polish window 2026-11-06→08 ⇒ 60s before/after (fixture: photo ↦ listing ↦ edit ↦ revision 2, prior immutable).
3. `submission` — 2026-11-09, pre-deadline ⇒ fires ONLY on submission confirmation; `[CLIPS_URL]`/`[REPO_URL]` placeholders until then.
4. `post-result` — 2026-11-13 winners ⇒ NOT_DRAFTED (outcome-dependent).

## Audience / comment watch

- watch: listinglens repo {issues, PR comments, stars/forks Δ} ∧ submission-beat replies on publishing surface (surface = NOT_ESTABLISHED ⇒ owner/parent picks at beat-1 fire).
- cadence: beat-days + 2026-11-09 + 2026-11-13; triage ⇒ factual Q = answer from README/coordinator; build defects ↦ D3 seat, ¬ fix here.
- metrics_internal NEVER renders publicly (fleet rule); report counts ↦ parent only.

## Copy set — delegated draft, edited + verified vs census ∀ claims

### 1. Announcement

Short: Introducing ListingLens: an indie seller photographs an item, and the agent drafts the whole listing — copy, price, and storefront layout. The seller edits every field before it ships. Built for the Builder.io Agent-Native Hackathon.

Long: ListingLens is in the build for the Builder.io Agent-Native Hackathon. An indie marketplace seller photographs an item, and the agent drafts the entire listing — descriptive copy, a pricing suggestion, and a storefront layout. Pricing is based on the median of comparables adjusted for condition, then charm-priced. Nothing is final automatically; the seller can view, edit, and act on every field before the listing ships. Built with `@agent-native/core` `defineAction()`, zod, and React, with the agent's work presented as a structured, editable package rather than a one-shot output. Code: https://github.com/timerloggedout-spec/listinglens — Submission deadline: Nov 9, 23:59 PT.

### 2. Build-in-open (2026-11-06→08)

Short: Build-in-open: in 60 seconds, a sample vase photo becomes a draft listing — then one seller edit creates revision 2, with the original untouched. ListingLens is in polish Nov 6–8, ahead of the Nov 9 submission deadline.

Long: Build-in-open update from the ListingLens team, Nov 6–8 polish window. The before/after takes about 60 seconds using the offline demo fixture. Before: a sample vase photo and basic item details. After: a complete draft listing — copy, a pricing suggestion calculated from the comparables median × condition and charm-priced, plus a storefront layout. Then the human step matters: the seller changes a field, and ListingLens produces revision 2 as a new version rather than overwriting the agent's original draft. That edit-and-review loop is the core of the design — the agent does the drafting work, the seller keeps control of every field.

### 3. Submission (2026-11-09; placeholders until confirmed)

Short: Submitted: ListingLens for the Builder.io Agent-Native Hackathon. One photo → listing copy, pricing, and layout the seller can edit field by field. Public demo: [CLIPS_URL] Code: [REPO_URL]

Long: ListingLens has been submitted to the Builder.io Agent-Native Hackathon. For indie marketplace sellers, ListingLens turns a single item photo into a complete draft listing: copy, a pricing suggestion based on the comparables median adjusted for condition and charm-priced, and a storefront layout. The seller reviews the agent's work in a React interface, edits any field, and generates a revised version — no field ships unreviewed. Built with `@agent-native/core` `defineAction()` and zod contracts, it directly addresses the judging mix: Usefulness and Execution 40%, Creativity and Design 20%, Innovation 20%, and Agent-Native use 20%. Watch the public demo (no login needed): [CLIPS_URL] Explore the code: [REPO_URL] — The ListingLens team

## Media

production = OUTSOURCE (∅ fleet quota); needs = {60s before/after screen capture ⇒ rides D3 Clips recording (gate above), 1× repo-README image}. ∅ media claimed ready.

## Open

- `D3-CLIPS-STORAGE` open ↦ entries lane / D3 seat.
- publishing surface for beats 1–3 = NOT_ESTABLISHED ↦ parent decision at fire time.
- D3 seat confer sent 2026-10-31 (submission `bbd1adc5`); correction, if any ⇒ amendment PR.
