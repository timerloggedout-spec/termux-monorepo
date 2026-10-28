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
| Muse | 1B tokens, redeem ≤48h of joining, never expires | **1B tokens, cap 20 = up to 20B** | code pending (owner share code) |
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
3. **Rotation on exhaustion.** A code reported exhausted (visitor report, owner
   check, or in-app signal) → issue labelled `referral:exhausted` → lane flips
   the next reserve code to `live` in the registry, rebuilds the feed, PR merges,
   surfaces re-render. Pool empty → status `code_pending`, owner pinged once for
   a fresh screenshot. No silent dead codes: that is the availability failure
   mode this design exists to kill.
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

- **Muse share code** — the only missing input. Owner: Muse Settings → the
  *share/invite* view (the screenshot on file is the *redeem* view). On receipt:
  registry update + feed rebuild + PARTNERS row, one PR, same day.
- **Hark** — identity confirm (fleet surface vs Hark Pro) before anything lists.
- **Web Design** — feed integration + de-center build, sequenced on this PR.
