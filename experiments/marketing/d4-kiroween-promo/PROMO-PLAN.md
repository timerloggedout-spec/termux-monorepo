# D4 Kiroween — Promo Plan ∧ Copy Set

`[MUSEai]@{role:{marketing-channel}}` · lane = marketing sub-lane ↦ parent
`{role:{marketing-channel}}` (chat 81cbe17c) · build/submission owner =
D4 seat `{role:{challenge-entries-manager-d4}}` (chat fefff1ad)
Status: PLAN — ∅ copy published yet; publication beats fire on evidence
events from the D4 seat, ¬ calendar alone.

## 1. Census (verified firsthand, 2026-10-31)

| Claim | Evidence |
|---|---|
| Project = skeleton-crew, FROZEN variant | coordinator.json@master sha `a576c0a38d4e` (PAT-API read 2026-10-31) |
| Repo public ∧ created in-period 2026-10-30T23:55:28Z | GitHub API `/repos/timerloggedout-spec/skeleton-crew` |
| Eligibility window 2026-10-30T09:00PT → 2026-12-04T14:00PT; gate D4-ELIGIBILITY = cleared | coordinator D4.dates ∧ D4.gates (rules §1) |
| Surfaces: GH repo ONLY; Devpost gallery unpublished, projects = 0; social/blog/demo = ∅ | coordinator D4.field_size (re-verified 2026-10-31T07:43Z) ∧ D4 seat census 2026-10-31 |
| Submission = none; registration incomplete; gate D4-ACCOUNTS = sole open gate (Devpost profile ✓, exact Kiro ID ∅, Kiroween registration incomplete) ⇒ 4,000-credit form blocked, deadline 2026-12-01T12:00PT | coordinator D4.gates ∧ D4 seat census |
| Build = scaffold only (HEAD `6b99cd4c0069`); build > 2026-11-08 via Desk ⇒ Jules-on-issues ⇒ monorepo PR/CI/merge ⇒ artifact sync | skeleton-crew README ∧ D4 seat census |
| Prize fit: Best Skeleton Crew $5,000 (category) ∧ Bonus Blog 2,000 credits ×100 ∧ Social Blitz 3-mo Kiro Pro+ ×5 | coordinator D4.prizes (rules §8) |

∴ Constraints: (a) promotable surface = repo link ONLY until a Devpost
project draft exists; (b) ∅ asset claims pre-build (demo/screenshots/
live URL exist post-build only); (c) Kiro-usage write-up = README stub
until build receipts land; (d) 4n0n protocol ∀ public artifacts
(∅ names, ∅ owner identity, neutral project voice).

## 2. Beats (event-triggered)

1. **Announcement** — fire: NOW (scaffold/freeze fact established).
   Channel: repo README link surface + social when a channel exists.
2. **Build-in-open** — fire: D4 spec-pack handoff (pre-Nov 8), then per
   build receipt (Jules PR merged / artifact sync verified by D4 seat).
3. **Blog** — draft in build window; fire: first real `/.kiro` hook/spec
   receipts exist (Bonus Blog target). Final sections fill post-build.
4. **Submission beat** — fire: D4 seat confirms submission on Devpost
   (≤ 2026-12-04T14:00PT). Bracketed links fill at that moment only.
5. **Audience/comment watch** — from first publication: Devpost comments
   ∧ repo issues/stars ∧ social replies, checked per beat; questions
   route ↦ D4 seat for build facts, answered from evidence only.

## 3. Copy set (drafted via delegated generation; edited ∧ verified by this lane)

### 3.1 Announcement post

> A skeleton crew, by design. 💀
>
> Skeleton Crew is being built for Kiroween 2026: a CMDB/reconciliation
> viewer run by a minimal crew of spec-first Kiro agents — ingest,
> reconcile, report — keeping fleet inventory honest against its sources.
>
> The shape: one `foundation/` plus two distinct apps — a conflict viewer
> and a stamped-report app. The public repo is live and the variant is
> frozen: https://github.com/timerloggedout-spec/skeleton-crew
>
> Created 2026-10-30, inside the submission period, as the eligibility
> rules require. Today it's scaffold only — the build starts after
> 2026-11-08, ahead of the 2026-12-04 14:00 PT deadline.
>
> Small crew. Full accountability. Build log to follow.
>
> #Kiroween #Kiro

Edit note: delegated draft claimed "entered in Kiroween" — corrected
∵ registration incomplete (D4-ACCOUNTS open). ¬ published until parent
approves channel.

### 3.2 Build-in-open template

> Build-in-open: Skeleton Crew 🏗️💀
>
> Milestone: [milestone name]
> Done: [what was completed in this step]
> Proof: [link to commit / PR / screenshot]
> Next: [next milestone + target date]
>
> One foundation, two apps — `apps/conflict-viewer` and
> `apps/stamped-report` — driven by the specs, steering, and hooks in
> `/.kiro`. The crew stays minimal; the evidence doesn't.
>
> Repo: https://github.com/timerloggedout-spec/skeleton-crew
> Deadline: 2026-12-04 14:00 PT
>
> #Kiroween #BuildInPublic

### 3.3 Submission beat (template — fires only on confirmed submission)

> Submitted. 💀✅
>
> Skeleton Crew is in for Kiroween 2026, ahead of today's 2026-12-04
> 14:00 PT deadline.
>
> A CMDB/reconciliation viewer run by a minimal crew of spec-first Kiro
> agents — ingest, reconcile, report — keeping fleet inventory honest
> against its sources. One foundation, two distinct apps: a conflict
> viewer with an evidence-stamp detail view, and a stamped
> reconciliation report.
>
> Built in-period from a public repo created 2026-10-30:
> https://github.com/timerloggedout-spec/skeleton-crew
>
> [Demo: link] · [Devpost project page: link] · [Gallery: link]
>
> Small crew. Every claim stamped.
>
> #Kiroween #Kiro

### 3.4 Blog (Bonus Blog Prize) — outline ∧ intro

Working title: [Skeleton Crew: How Kiro Specs, Steering, and Hooks Run
a Minimal Crew]

Outline: (1) problem: inventory drifts, provenance lost; (2) constraint:
smallest crew that can ingest/reconcile/report; (3) specs first in
`/.kiro`; (4) steering = shared rules/evidence standards; (5) hooks fire
the checks [examples fill from actual build]; (6) two apps, one
foundation; (7) what the build proved ∧ didn't [post-build]; (8)
reproduce it: repo link ∧ structure tour [post-build].

Intro:

> Most inventory systems fail quietly: a record changes in one source,
> nothing changes in another, and by the time anyone notices, nobody can
> say which version was ever true. Skeleton Crew is a
> CMDB/reconciliation viewer built for Kiroween 2026 that takes the
> opposite approach — a minimal crew of spec-first Kiro agents that
> ingest from sources, reconcile what disagrees, and report only what
> they can stamp with evidence. There is no large team and no
> improvisation. Each agent's job is written down before it runs: specs
> in `/.kiro` define the work, steering files hold the crew to shared
> rules, and hooks fire the checks that keep the process honest. One
> foundation supports two distinct applications — a conflict viewer and
> a stamped-report app. This post walks through how that `/.kiro` setup
> drives the crew, [with examples drawn from the build itself as it
> progresses after 2026-11-08].

### 3.5 Devpost project page (fills when draft exists)

Tagline: A minimal crew of spec-first Kiro agents keeping fleet
inventory honest — every reconciliation, stamped with evidence.

Description: Skeleton Crew is a CMDB/reconciliation viewer run by the
smallest crew that can do the job: spec-first Kiro agents that ingest,
reconcile, and report. A shared `foundation/` supports two distinct
applications — `apps/conflict-viewer`, with an inventory list, conflict
matrix, and evidence-stamp detail view, and `apps/stamped-report`,
which produces a stamped reconciliation report. Specs, steering, and
hooks live in `/.kiro` and drive the crew's work. Public repo, created
in-period on 2026-10-30: https://github.com/timerloggedout-spec/skeleton-crew

## 4. Open items

- D4-ACCOUNTS closure (registration ∧ Kiro ID) — accounts lane owns;
  promo dependency = credit form ≤ 2026-12-01T12:00PT.
- Publication channel for beats 1–2 = NOT ESTABLISHED (∅ social surface
  exists today) ⇒ parent decides channel ∨ beats ride repo + Devpost only.
- Media (demo <3 min, screenshots) = build-window outputs, OUTSOURCE
  rule applies; ∅ fleet quota burn for media production.
