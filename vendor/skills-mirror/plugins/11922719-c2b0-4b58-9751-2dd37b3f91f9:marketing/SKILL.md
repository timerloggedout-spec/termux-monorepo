---
name: marketing
category: Growth
description: "Why people choose, buy, sign up and stay, applied honestly: behavioral models, offers, pricing, trust, urgency, onboarding and growth loops for the apps and sites we build. Use when shaping a landing, pricing, signup or launch page, an offer or free tier, or asking \"why would anyone pick this\". Wording is plain-language; page structure is information-architecture.\n"
---

# Marketing — decide what moves a real person, then say only true things

Goal: find the one behavior a page, offer or flow has to cause, find what is stopping it, and
pick the few models that remove that obstacle. Every lever is used **honestly**: the customer
should still be glad they chose it after seeing exactly how the page was built.

Credit: the model catalog in [models.md](models.md) is a rewrite of the `marketing-psychology`
skill in `coreyhaines31/marketingskills` (MIT, Corey Haines). The reference files fold in
material from its `product-marketing`, `customer-research`, `competitors`, `competitor-profiling`,
`pricing`, `offers`, `paywalls`, `referrals`, `influencer-marketing`, `onboarding`, `signup` and
`launch` skills, rewritten with the manipulative parts left out. The procedure, honesty rules
and boundaries here are ours (see *Honesty check*).

## Where this skill stops

| The question | Goes to |
| --- | --- |
| Which behavior to cause, which obstacle to remove, which model, offer and price shape | **this skill** |
| The words on the page, tone, reading level | [plain-language](../plain-language/SKILL.md) |
| Which page a message lives on, section order, funnels, where each CTA goes | [information-architecture](../information-architecture/SKILL.md) |
| How it looks: hierarchy, color, type | [design-guide](../design-guide/SKILL.md) |
| Which metric proves it worked, dashboards | [data-analytics](../data-analytics/SKILL.md) |
| Generating options when nothing is chosen yet | [idea-refine](../idea-refine/SKILL.md) |
| A public site's SEO, structured data and launch checks | [public-site-checklist.md](../frontend/public-site-checklist.md) |
| Forms and overlays (signup fields, pop-ups, modals) | [forms-and-overlays.md](../frontend/forms-and-overlays.md) |
| Editing copy line by line | [copy-sweep.md](../plain-language/copy-sweep.md) |
| Moving or restructuring a site | [site-migration.md](../information-architecture/site-migration.md) |
| Measuring a small site, A/B tests, UTMs, consent | [site-measurement.md](../data-analytics/site-measurement.md) |
| Failed payments and subscription emails | [billing-recovery.md](../integrations/billing-recovery.md) |
| App store listings | [app-store](../app-store/SKILL.md) |
| Finding first customers, outreach | [first-customers](../first-customers/SKILL.md) |
| A demo video of the app | [demo-video.md](../design-assets/demo-video.md) |
| What a client actually sells, promises and calls things | that client's domain skill, when the project has one |

When a task spans several of these, settle this skill's decisions first (behavior, obstacle,
offer), then hand the wording and structure to the skills above. Copy written before the
offer is decided gets rewritten.

## Before you start: read what the project already says

1. **The project's positioning record.** Look for one in this order: the client's domain skill
   and the doc it routes to; a `docs/marketing.md` or `docs/positioning.md` in the repo; the
   repo's `.ai/PROJECT.md`. Use what it says about the audience, the offer and the promises;
   never contradict a recorded promise.
2. **No record yet?** Ask the six questions below in one gate (planning's front-loading rule),
   then write the answers to `docs/marketing.md` in the repo so the next page starts from
   them, using the template in [positioning-record.md](positioning-record.md). Do not guess an
   audience.
3. **`LEARNINGS.md` beside this skill, when your copy keeps one** — what has worked or been
   rejected before, per project. **`LOCAL.md`**, when your copy keeps one, names this
   workspace's domain skills and house rules.

## The six questions

1. **Who** is the one reader this page is for, and what are they doing right before they land?
2. **What single behavior** should they do next (book a call, start a trial, join a list, pay)?
3. **What do they already believe** about this problem, and about tools or firms like ours?
4. **Where are they** in the journey: unaware, comparing, or ready to decide?
5. **What stops them today?** Pick one: they don't see the value, they don't trust it, it looks
   hard or slow to start, it costs more than it seems worth, or there is no prompt to act now.
6. **What true evidence do we have?** Real reviews, real counts, real results, credentials,
   a guarantee we will honor. This list caps what the page may claim.

## Procedure

1. **Name the behavior and the obstacle** from questions 2 and 5. One of each. If the obstacle
   is "they never see the page", that's a traffic problem: say so and stop tuning the page
   (Theory of Constraints in [models.md](models.md)).
2. **Pick two or three models** from the diagnosis table. More than three in one page usually
   means none of them is doing the work.
3. **Turn each model into one concrete change**, the kind you could point at on a screen:
   "move the review count above the fold", "drop the signup form to email only", "make the
   middle plan the preselected one because it is what most customers need".
4. **Run every change through the honesty check** below. Rewrite or drop the ones that fail.
5. **Hand off** wording to plain-language and placement to information-architecture, carrying
   the behavior, the obstacle and the evidence list with you.
6. **Name how you'll know it worked**: one number and where it is read (data-analytics). If the
   site can measure it, change one thing at a time so the result points at a cause.
7. **When a change ships**, find the site, store-listing and changelog claims it made false (a
   new limit, a renamed plan, a removed feature, a price) and fix them in the same change.
   Changelog lines say only what is live for customers today ("You can now …"). This is an
   attended step: flag and fix with the change, never a scheduled job that edits copy alone.

## Diagnosis table

| Obstacle | Reach for |
| --- | --- |
| They don't see the value | Jobs to Be Done, contrast (before/after), framing, availability (a vivid real example) |
| They don't trust it | social proof, authority, pratfall (admit a real limit), reciprocity (give something useful first), liking/unity |
| It looks hard or slow to start | activation energy, Hick's law, default effect, Fogg (ability), goal-gradient, status-quo bias (make switching safe) |
| It costs more than it seems worth | anchoring against a real alternative, mental accounting, good-better-best, zero-price effect, regret aversion (guarantee) |
| No reason to act now | a true deadline or capacity limit, loss of a real benefit by waiting, a timely prompt (Fogg, EAST) |
| Too many choices | paradox of choice, recommend one "best for most", default effect |
| They signed up but didn't stick | IKEA effect, endowment effect, goal-gradient, Zeigarnik (show what's unfinished), peak-end |
| Growth has stalled | theory of constraints, local vs global optimum, feedback loops, compounding, exploration vs exploitation |

The full model list, with what each one is and how it applies to a product or site, is in
[models.md](models.md). Read it when the table's name alone is not enough.

## Honesty check (every change passes all of these)

- **Every claim is true and checkable.** Each testimonial, star rating, customer count, logo,
  "featured in", result and credential traces to a real source we can show. A page is an
  external communication, and the visitor can't ask us what we meant. No source, no claim:
  no placeholder testimonials, stock-photo "customers" or rounded-up counts.
- **Urgency and scarcity are real.** A deadline exists only if the offer actually ends then; a
  "limited spots" line only if capacity is actually limited (a builder's real schedule). Never a
  countdown that resets, never "only 2 left" from a constant.
- **Every option is one a real customer would pick.** No decoy tier built to be bad value.
  Anchoring uses a real alternative (a real competitor price, the real cost of doing nothing,
  the plan above), never door-in-the-face (an inflated ask shown to make the real one look cheap).
- **Defaults serve the customer.** Preselect what most customers need, never a paid add-on, an
  auto-renewal they didn't choose, or a pre-ticked marketing opt-in.
- **Leaving is as easy as joining.** Cancel, export and unsubscribe are one clear step. Value
  can make people stay; friction may not. A cancel flow may offer a pause or a smaller plan,
  once, with cancel visible and one step: no forced survey, no expiring "stay" offer, no
  discount ladder.
- **Loss framing names a true cost.** "Every month on the old system costs you X hours" is fine
  if X is real. "Don't miss out!" with nothing behind it is not.
- **Respect the client's recorded voice and promises.** A small local trade business that
  promises straight answers doesn't get flash-sale tactics, whatever the model says.

If a change only works when the reader doesn't notice it, it fails. Say so plainly in the
review and offer the honest version.

Placeholder content during a build is fine only if it is visibly marked as a placeholder and
never ships. Before launch, grep for it.

## Reviewing an existing page

1. Answer the six questions from the page alone. Where the page doesn't answer one, that's
   finding #1.
2. Find the single behavior the page asks for. Two competing primary CTAs is a finding (hand
   placement to information-architecture).
3. Name the obstacle the page is failing on, from the diagnosis table.
4. Run the honesty check on every claim and lever already on the page.
5. Report: the behavior, the obstacle, at most five changes ranked by expected effect, and any
   honesty failures listed first.

## Common failure modes

- **Tactics before the obstacle.** Adding urgency to a page whose real problem is trust.
- **Every model at once.** A page stuffed with badges, timers, counters and pop-ups reads as a
  scam to exactly the careful buyer we want.
- **Copying a competitor's funnel** without knowing whether it works for them (survivorship
  bias). Ask what our reader needs.
- **Optimizing the page when the traffic is the bottleneck.**
- **Claims that outrun the evidence list.** The fix is more evidence (collect real reviews),
  not bolder wording.
- **A page with nothing new.** Before writing a page, write one sentence on what it adds that
  existing pages lack. If you can't, don't write it.
- **Gating what the visitor needs to decide.** A lead magnet (a guide, a checklist) asks only
  for an email and says exactly what they'll get and how often.

## Reference files

- [positioning-record.md](positioning-record.md): the `docs/marketing.md` template, evidence
  labels, competitor facts and customer-research tips.
- [pricing-and-offers.md](pricing-and-offers.md): value metric, first price, plans, offers,
  guarantees, honest urgency and in-app upgrade moments.
- [reviews.md](reviews.md): asking for reviews, platform rules, reusing testimonials, disclosure.
- [onboarding.md](onboarding.md): Minimum Path to Value, trial models, the aha moment, checklists.
