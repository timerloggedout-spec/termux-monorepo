# StudySprint — developer-verification decision note

**Status: decision note only (app-package D, #4439).
No action is taken by this document.** It records the
options and a recommendation for the owner to rule on.

## The deadline that frames this

Android **developer verification**: from **30 Sep 2026**,
on certified Android devices in Brazil, Indonesia,
Singapore and Thailand, apps must be registered by a
verified developer to be installable — sideloading
included — with global expansion planned for 2027
(Android Developers Blog, via the app-package research
2026-11-03; post-blog mechanics — the advanced flow and
limited-distribution accounts — rest on secondary
reporting and are still moving, so exact requirements
should be re-read before acting).

What it does NOT change today: judging and testing are
unaffected (emulators and ADB installs bypass
verification), and the 0.1.x line's distribution —
GitHub releases + the landing page — works everywhere
until the rollout reaches a given region.

## The project's account reality

Student/hobbyist project, one owner, no organization,
no D-U-N-S, fleet has no credit card on file. The
signing identity is a committed DEV keystore (ruled,
#4222/#4340) — fine for sideload distribution with the
#4438 trust machinery, not a store identity.

## Options

1. **Stay sideload-only** (status quo). GitHub releases +
   trust block + reproducible builds. Zero cost, zero
   paperwork. From Sep 2026, installs on certified
   devices in the four named regions get harder; global
   expansion erodes the rest later.
2. **Limited-distribution (student/hobbyist) account.**
   Google's announced path for students and hobbyists:
   verification scoped to limited distribution (a capped
   number of devices) without the full developer-account
   apparatus. Fits this project's shape exactly — IF the
   final mechanics match the announcement (re-read at
   decision time).
3. **Full Play developer account (personal).** $25 +
   government-ID verification; new personal accounts also
   carry the 12-tester × 14-day closed-test requirement
   before production. Unlocks Play distribution and
   sidesteps verification entirely — at the cost of store
   review, policies, and a standing obligation the
   project does not otherwise need yet. Explicitly out
   of the app-package scope (no Play publishing) — would
   be its own owner decision.
4. **Organization account.** Needs a D-U-N-S number and
   organization verification. The project has no
   organization; not applicable.

## Recommendation

**Option 2 when its mechanics finalize; Option 1 until
then.** The limited-distribution path was designed for
exactly this account type, and the Sep 2026 date only
binds four regions — there is a full school year of
runway. Set a revisit trigger: re-read the official
verification terms at the first of (a) the limited
account's enrollment opening with published mechanics,
(b) any global-expansion date announcement, (c) the
project wanting distribution beyond hand-shared links.
Option 3 stays available at any time and nothing in the
current line (signing, packaging, trust machinery)
forecloses it — except one thing to know before ever
choosing it: a Play listing would need a NEW upload key
enrolled in Play App Signing; the committed DEV keystore
must never become a store identity (#4438 scope rule:
no silent rotation — a store key would be a deliberate,
documented, separate provisioning).
