# Referral automation — free marketing stack (2026-10-27)

Lane: `[MUSEai]@{role:{marketing-channel}}` · Registry: `config/referral_programs.json`
Feed: `apps/help-wanted-dashboard/data/referral-feed.json` (built by
`scripts/referral/build_feed.py`) · Human registry: `docs/PARTNERS.md`
Census: `docs/ops/MARKETING-CHANNEL-CENSUS-2026-10-27.md` (PR #1889)

## Why

Owner order: get the free marketing going, high availability for fleet work and
hackathon starts. Everything in the public stack is **free, no credit card** —
cost to the visitor is a code entry; benefit is credits/tokens/access. Sizzle
first (benefit copy), steak underneath (the Value Derived board's as-if-paid
numbers prove it). Copy rule: benefit → proof → code. Never specs first.

## The stack (all free, no CC)

| Programme | Visitor gets (free) | Fleet gets per redemption | Pool |
|---|---|---|---|
| Muse | 1B tokens, redeem ≤48h of joining, never expires | **1B tokens per use, 30 uses left = up to 30B** | 1 live code (`VDP1DW`), no reserve — single-code programme, rotation impossible until a second code exists |
| Manus | free plan + invitation access | refer-a-friend credits (amount not firsthand) | link live (§1) |
| Cue | free early access | NOT ESTABLISHED | 1 live + 1 reserve |
| Migoo | invite signup + free daily points | NOT ESTABLISHED | 1 live + 2 reserve |
| CellCog | 200 free credits, no card | NOT ESTABLISHED | link live (§1) |

Muse terms are now firsthand (owner's in-app redeem screen, 2026-10-27):
48h window, both sides 1B, licence not money, non-transferable, **no expiration** —
this upgrades the census's community-reported terms.

## Automation (as automated as possible)

1. **Registry is the single input.** `config/referral_programs.json` holds
   programmes, mechanics, code pools, provenance. Owner supplies codes by
   screenshot in this lane; the lane lands them by PR. No other edit path.
2. **Feed is generated, never hand-edited.** `scripts/referral/build_feed.py`
   publishes exactly one live code per programme + reserve counts. Landing and
   dashboard consume the feed only (Web Design lane integrates; Dispatch Tree).
3. **Rotation — automated engine, named sensors.** AUDIT (2026-10-27): as
   originally written this step was a manual lane relay (report → issue →
   hand-flip). It is now an engine: `scripts/referral/rotate.py`, driven by
   the `referral-rotation` workflow (dispatch: programme, cell, source,
   uses-left). The engine flips the next reserve into the slot, marks the old
   code `exhausted`, rebuilds the feed, patches PARTNERS §1b, appends a
   `rotation_log` entry, and the swap lands as a PR; the landing re-renders
   from the feed. Rotation fires **before** exhaustion: at
   `rotation.threshold_uses_left` (5) on a sensor reading. Pool empty → live
   cell flips the programme to `code_pending`, cell_b empties just end that
   A/B cell, and a `referral:pool-empty` issue is filed automatically.
   **Detection is the one step that cannot be automated today**: no programme
   here exposes a redemption-count API or webhook (per-programme source is
   named in the registry, `rotation.detection_source`) — Muse = owner
   Invite-panel "uses left", Cue/Migoo = in-app invite screens. The sensor
   reading enters via workflow dispatch; everything downstream is automatic.
   Pool depth, by contrast, IS registry-provable: `pool_check.py` +
   weekly `referral-pool-watch` workflow (Tue 08:41 UTC) file a
   `referral:pool-low` issue the moment a live programme drops below its
   spare target — currently TRUE for Muse (0 spares) and Cue (0 spares).
4. **Replenishment ledger → Value Derived.** Every confirmed redemption is a
   session row candidate for `free-tier-value.json` (schema
   `3l0.free-tier-use-value.v1`): Muse 1B tokens ≈ 10 weeks of free allowance;
   dollar value NOT ESTABLISHED (estimates conflict) → recorded as unknown,
   never zero, per that feed's policy. Referral replenishment is how the free
   stack refills itself; the board is where the steak gets counted.
5. **Sync surfaces, in order:** registry → feed → PARTNERS.md → README banner →
   landing grid → YouTube post. A lane change is not done until all live
   surfaces match the feed.

## High availability

- **Hosting:** GitHub Pages + GitHub repo only. No card-gated infra, no single
  vendor free tier is load-bearing for the marketing surface itself.
- **Pool redundancy:** ≥2 codes per code programme where the platform issues
  them (Cue 2, Migoo 3 on hand). One published, rest in reserve — a burned code
  never takes the lane down.
- **Caps are ceilings, not surprises:** Muse referrer cap 20 is recorded in the
  registry; approaching it is a ledger event, not a discovery.
- **Mortality rule (fleet standard):** free programmes die or change terms
  routinely. Each programme carries its terms source + date in the registry;
  a dead programme exits the feed by status flip, and no critical fleet work
  may depend on a single free lane.

## Open blockers (named, minimal)

- **Muse** — RESOLVED 2026-10-27 19:47 PDT: owner supplied the live code from
  the Invite friends panel (30 uses left). Watch item: it is a single code with
  no reserve; at 0 uses the lane flips to `code_pending` and pings the owner.
- **Hark** — identity confirm (fleet surface vs Hark Pro) before anything lists.
- **Web Design** — feed integration + de-center build, sequenced on this PR.

## Channels + A/B test (owner, 2026-10-27)

Channels (registry `channels[]`): landing/repo (live) · YouTube (community
post live) · Facebook, X, TikTok, Instagram (owner-stated accounts; handles
NOT ESTABLISHED — never invented). Facebook connector check 2026-10-27:
managed Pages returned = 0 (empty result, not proof of none).

**Experiment `fb-pages-sizzle-vs-steak-1`** (registry `ab_test`): two Facebook
Pages, one per cell — A *sizzle* (benefit-first copy) vs B *steak*
(numbers-first, Value Derived proof). Code pools split per cell for clean
attribution (Cue W7AZA→A / 7RKCJ→B; Migoo uA3QYP→A / Du7Ehu→B, TSGDUJ
reserve; Muse's single code shared, attributed by landing param `?ch=fb-a|b`).
Metric: redemptions + landing clicks per cell. Decision rule: winner copy
becomes the default on X / TikTok / Instagram / YouTube after 10 attributed
redemptions or 14 days, whichever first.
4n0n: the two Pages never cross-link (isolation + test contamination).
Blocker: Page creation — the Facebook connector lists/publishes Pages but
has no create command; the owner creates the 2 Pages in Facebook, this lane
wires codes + copy per cell.

## Owner input needed — spare pool (terse, per programme)

- **Muse**: 1 spare code. Blocker question: does the Invite panel issue a
  second code before the first dies, or only after? If only after, rotation
  at 0 is: owner grabs new code → dispatch → swap is automatic.
- **Cue**: ≥1 spare code (both current codes are deployed in the A/B cells;
  pool = 0). If the app generates more invite codes, supply 1–2.
- **Migoo**: covered for one rotation (spare `TSGDUJ`); top up +1 when the
  pool-watch issue fires.
- **Manus / CellCog / Polsia / Grafana**: links, no code pool; rotation n/a
  unless a link is capped (none established).

## Facebook Pages — status + categories (2026-10-27)

Verified via the Facebook connector (pages list): **Dream In Production**
(fb-a) and **Receipts Count** (fb-b) exist. **Code, Not Card** (fb-c) hit
Facebook's "created too many Pages recently" limit at creation — owner
retries later; Page creation is owner-side by platform rule.

Category set per Page (primary first; apply in Page settings — categories
are the discovery/policy bucket, and the creation-flow defaults are wrong
for all three: none is a local business or a community):

| Page | Categories |
|---|---|
| Dream In Production (sizzle) | Personal Blog · Website · Science, Technology & Engineering |
| Receipts Count (steak) | Computers & Internet Website · Website · Personal Blog |
| Code, Not Card (mechanic) | App Page · Software Company · Computers & Internet Website |

If the picker shows a near-identical label, take the closest — the primary
category is the one that matters.

**Naming ruling (owner, 2026-10-27):** "Code, Not Card" — the negation is a
deliberate special test case, OUTSIDE the Positive Performance Psychology
Language Framing Structure. It is a feature, not a violation. Do not flag
it, do not rename it. (Recorded in the registry, ab_test.pages.fb-c.)
