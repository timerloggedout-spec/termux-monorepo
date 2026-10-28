# Marketing channel — referral surface census + offering verification (2026-10-27)

Lane: `[MUSEai]@{role:{marketing-channel}}` · Brief: Web Design PM lane, owner order 2026-10-27.
Scope: referral/offerings surface + marketing channel planning, under anon layers.
Build/deploy of the page itself executes in the Web Design Specialist lane at handover
(Dispatch Tree: prototype → shell integration). This lane owns offering verification,
listing content, anon-layer review, and the handover spec below.

Method: live GitHub API census via the PAT helper at action time (master, 2026-10-27);
program verification from firsthand / primary-adjacent web sources, cited per offering.
Referral tokens are referenced by location, never re-printed — names-only discipline.

## 1. Census — where the referral surface actually lives

There is no standalone referral page in this repo. The surface is three synced layers:

| Layer | Location | Role |
|---|---|---|
| Registry (SSOT) | `docs/PARTNERS.md` (this repo; consolidated from issue #574) | Active lanes §1, owned channels §2, pipeline §3, wallets §4, adding-a-partner procedure |
| Repo banner | `README.md` `partner-banner` markers (lines 72–88) | One badge per active lane, rows of three |
| Landing page | Separate repo `timerloggedout-spec/timerloggedout-spec.github.io`, `js/content.js` `partners.items` → https://timerloggedout-spec.github.io/#partners | Renders **active rows only**, mirrors PARTNERS §1 |

Site roles per `docs/ops/SITE-MAP.md`: the user-site root is MARKETING / REFERRALS;
`/help-wanted/` is ops, `/termux-monorepo/` is a thin project hub — neither is a referral twin.

### Active lanes on master (4, all three layers in sync)

| Partner | Mechanic | Offer (as listed) | Provenance |
|---|---|---|---|
| CellCog | invitation link | 500 bonus credits on first purchase | PARTNERS §1; README badge row 1; landing hero + card + footer |
| Polsia | `?ref=` link | 500 extra credits — PARTNERS itself flags "verify on signup" | PARTNERS §1; README row 1; landing card |
| Manus AI | invitation link (UTM-tagged) | invitation (no credit amount listed) | PARTNERS §1; README row 1; landing card |
| Grafana | referral code in sign-up URL | referral sign-up | PARTNERS §1; README row 2; landing card |

### CellCog's actual position

CellCog is the **anchor / first** active lane, not the page's subject — but the landing
layer is still CellCog-centric beyond the partners grid: brand line, hero headline + CTA
(the invitation link), trust line, and footer ("Powered by CellCog", CellCog terms/privacy
links) are all CellCog-only in `js/content.js`. De-centering that framing is a Web Design
build item in the handover spec (§4), not a registry change.

### Census findings / drift

1. **Runable — live referral link, absent from the registry.** `README.md` line 83 carries
   a bare `runable.cloud/?refer_code=…` link inside the banner block. It has **no row in
   PARTNERS.md, no badge, and no landing card**. Registry drift: either register it
   (PARTNERS §1 + badge + landing card, after program verification) or remove the stray link.
2. **Manus was queued as "to add" — it is already active** in all three layers (see §2).
   The queue item closes as already-landed; what remains is program-terms verification (§2).
3. **Polsia's offer is unverified by the registry's own admission** ("per #574 — verify on
   signup"); no public Polsia program-terms page was found in this pass either. Flag stays.
4. Owned channel: one YouTube community post lists the lanes (PARTNERS §2) — a fourth
   surface to keep in sync on any §1 change.
5. No referral/partner entry exists anywhere in the repo for Cue, Migoo, Hark, or Muse
   (code search 2026-10-27: Cue hits are unrelated provider-recon mentions; Migoo = 0 hits).

## 2. Verification pass — queued offerings

Verdict key: **ACTIVE** already listed · **VERIFIED** program exists, listable once a
fleet link/code is supplied · **INVITE-ONLY** access mechanic, no referral reward ·
**NOT ESTABLISHED** no program found from evidence (never assumed absent forever —
route per PARTNERS standing rule: direct contact / gifted-usage).

### Manus — ACTIVE; two distinct programmes, do not conflate

- *Refer-a-friend invitation* (the fleet's current link type): invitation link;
  third-party programme summaries report 500 credits to both sides.
- *Affiliate programme* (separate): invitation-only, run via Tapfiliate.
  Terms from Manus's own Tapfiliate programme ToS: **10% commission on referred
  subscription payments for up to 365 days; 1,000 free credits for followers via the
  affiliate link; monthly settlement, 30-day hold; $100 minimum withdrawal via PayPal;
  programmatic advertising (incl. Google Ads) and unauthorised discounting/cashback
  prohibited.** Eligible-plan names in those terms (Basic/Plus/Pro) are out of sync
  with current Manus pricing (Free/Pro/Team) — commission coverage by current plan
  needs confirmation before any commission claim is published.
- Action: none for listing (already active). The Tapfiliate lane is a **separate,
  invitation-only enrolment — owner-gated**; the fleet's invitation link earns no
  commission and must not be described as an affiliate link.

### Cue (by Manus) — INVITE-ONLY, no referral reward established

- Cue is Manus's personal-agent app (each agent gets its own email, phone number,
  wallet, cloud computer). Official source: Manus 2.0 announcement (manus.im, 2026-09-28):
  *"Cue is in early access and free to use with an invite code. You can start with
  MEETCUE, available to a limited number of early users on a first-come, first-served
  basis. Everyone who gets access also receives extra invite codes to share."*
- No affiliate programme, commission, or credit reward for sharing Cue codes was found
  in Manus's announcement, help centre, or coverage. The mechanic is access-gating only.
- Listing position: PARTNERS **§3 pipeline** (access code, not a tracked referral link;
  no attribution benefit to the fleet). `MEETCUE` is Manus's own public launch code —
  publishing it carries no fleet attribution and no anon cost. A fleet-personal share
  code (from an access holder's extra codes) is account-bound and **owner-supplied
  only, never invented**.

### Migoo (migoo.ai) — NOT ESTABLISHED

- Product: agentic "digital twin" platform (Gmail/Calendar integration, daily free
  points, paid points). Signup is invite-influenced: its privacy policy describes
  inviting others by email, and third-party boards circulate signup invite codes.
- **No referral or affiliate reward programme was found** — no programme page, no
  reward terms. Its ToS (§7) makes points account-bound, non-transferable and
  non-shareable absent written permission, which cuts against a public referral lane.
- Listing position: PARTNERS **§3 pipeline**, route = direct contact per the standing
  rule. Do not publish third-party invite codes as a fleet lane (provenance fails:
  they are strangers' codes, and reward attribution is unestablished).

### Hark — NOT ESTABLISHED + identity must be confirmed first

- Two different "Harks" are in play and must not be merged:
  (a) the fleet's internal agent surface named Hark (promptable tooling, proactive
  ops pushes — an internal surface, not a public product with a programme), and
  (b) **Hark Pro** by Hark Labs (hark.com; Brett Adcock; public launch 2026-10-06;
  free / $20 / $100 tiers).
- For (b): **no referral or affiliate programme was found** in launch coverage
  (TechCrunch-derived reporting, reviews, pricing write-ups). The only launch perk
  reported is a free paid tier for the first 100,000 sign-ups, with plan/duration
  terms not confirmed by the reporters.
- Owner item: confirm which Hark the queue means. If (a), there is nothing to list —
  an internal surface has no referral lane. If (b), verdict is NOT ESTABLISHED →
  §3 pipeline, direct-contact route.

### Muse (Meta) — VERIFIED: yes, a referral programme exists (owner question answered)

- **It is a programme of invite CODES, not links.** Launched 2026-09-16, announced by
  Meta / Alexandr Wang: a new user who redeems an existing user's invite code in
  **Settings → Redeem invite code within 48 hours of joining** receives **1 billion
  Muse tokens — and so does the referrer**.
- Terms as documented from Meta's own posts (no standalone official terms page has
  been published — community reporting is explicit about this, so treat fine print
  as provisional): referrer cap **20 friends** (up to 20B tokens; full-cap referrers
  get early access to new features); each code has a finite redemption cap
  (reported ~20–30) so public codes burn out fast; one redemption per new account;
  US + Canada, 18+; tokens are in-app usage credit, no cash value; referral pool
  reported as "never expires" in-app.
- **Provenance blocker (owner-gated):** the fleet's code is the owner's own Muse
  account code. It exists only in the owner's Muse Settings. It is **not in this
  repo and was not supplied to this lane**. The web is full of third-party Muse
  codes — using one would credit a stranger and misrepresent the lane; prohibited.
- Listing shape (new, for Web Design): a **code + instructions** entry, not an
  `href` card — code, "redeem within 48 hours of joining" warning, 1B-tokens-both-sides
  offer line. Because the cap is ~20–30 redemptions, a public landing-page posting
  will likely exhaust one code quickly; owner decides publish-and-rotate vs.
  not listing. Decision + code supply are the two owner inputs required.

### CellCog (baseline re-check)

- Invitation-link mechanic as listed; the 500-bonus-credits offer is stated in
  PARTNERS, the README blockquote, and the landing disclosure. No public CellCog
  affiliate/referral terms page was found in this pass (the public site states a
  200-free-credit start, a different mechanic). Programme terms therefore rest on
  the invitation itself — recorded as **listed, terms not publicly established**.

## 3. Anon-layer review (4n0n)

Protocol: `docs/ops/4N0N-REGISTRATION-PROTOCOL.md`; registry
`config/registration_monikers.json` (20 entries verified 2026-10-27).

1. **No overlap with the moniker registry.** None of CellCog, Manus, Polsia, Grafana,
   Runable, Cue, Migoo, Hark, or Muse appears in `registration_monikers.json`.
   Referral platforms are **not** challenge registrations; do not mint monikers for
   them without owner direction.
2. **The referral surface is an own surface** (landing repo + README + PARTNERS).
   Per the owner's own-surface rule (2026-10-27), own surfaces carry the full clue
   stack intentionally; third-party profiles stay isolated. Co-locating the partner
   lanes on one partners page is the existing owner-approved design (issue #574,
   DP-006) — it links the fleet's *partner accounts* to each other by design, which
   is the programme mechanic, not a 4n0n breach (4n0n governs person-identifying
   linkage; no personal identifiers appear in PARTNERS/listing copy — owner is
   recorded as the role "Marketing (Chloe)" only).
3. **Per-link rules for any new lane:** (i) token/code is single-purpose — never
   reused as an identity handle anywhere else; (ii) copy carries no personal name,
   handle, or cross-platform "same team as …" pointer beyond the partners-page
   co-location itself; (iii) codes that are account-bound and capped (Muse, Cue
   personal codes) are published only on owner supply + owner publication decision,
   because publication is irreversible and burns the cap; (iv) third-party codes
   found on the web are never listed — provenance fails and attribution would go
   to a stranger.
4. **Open related flag, unchanged by this lane:** the 4n0n public-registry exposure
   question is already carried by issue #1861 and is owner-directed there. Nothing
   in this census touches it; PARTNERS.md is a public-by-design registry and does
   not contain moniker-registry data.

## 4. Handover spec — Web Design Specialist lane

Registry-first order (per PARTNERS "Adding a partner"): PARTNERS.md → README banner →
landing `partners.items` → YouTube post. Build items:

1. **De-center CellCog on the landing layer**: hero/brand/footer in `js/content.js`
   become offering-neutral; CellCog remains one card in the partners grid + its
   PARTNERS anchor note. (Prototype → shell integration per Dispatch Tree.)
2. **Runable drift**: resolve per census finding 1 — register-and-badge it (after
   programme verification, separate ticket) or remove the stray README link.
3. **Pipeline rows**: add Cue, Migoo, Hark, Muse to PARTNERS §3 in a follow-up PR
   once the owner items below land; **not** §1 (no tracked fleet link exists for any).
4. **Muse entry type**: extend the partners item shape with a `code` variant
   (code + redeem instructions + 48-hour warning, no `href`); nav/sitemap/tests per
   the Dispatch Tree shell-integration pattern.
5. Nothing deploys from this lane; Web Design executes and reports PR + merge SHA.

## 5. Owner items (blockers, named)

1. **Muse**: supply the fleet's own invite code from Muse Settings, and decide
   publish-and-rotate (cap ~20–30) vs. do-not-list.
2. **Hark**: confirm identity — fleet internal surface vs. Hark Pro (hark.com).
3. **Manus affiliate**: whether to pursue the invitation-only Tapfiliate enrolment
   (commission lane) — separate from the existing invitation link.
4. **Cue**: whether to list Manus's public `MEETCUE` access code in §3 (no fleet
   benefit, pure access pointer) or wait for a fleet-personal share code.

## Sources (verification, 2026-10-27)

- Repo census: GitHub API via PAT helper — PARTNERS.md, README.md, SITE-MAP.md,
  project-pages-hub, landing repo `js/content.js` + tree, issue #574,
  registration_monikers.json (20 entries).
- Manus affiliate ToS: manus.tapfiliate.com programme terms (10% / 365d / $100 PayPal /
  1,000 follower credits, invitation-only).
- Cue: Manus 2.0 announcement, manus.im (MEETCUE, early access, extra codes to share);
  Manus help centre (Cue/Manus shared account, Cue phone-number subscription).
- Migoo: migoo.ai privacy policy (invite-by-email) + ToS §7 (points non-transferable);
  no programme page found.
- Hark Pro: launch coverage Oct 2026 (hark.com, tiers, first-100k perk, terms fuzzy);
  no programme page found.
- Muse: Meta programme announcement 2026-09-16 via Alexandr Wang / @meta.ai posts as
  documented in sourced programme write-ups (1B tokens both sides, 48h window,
  20-friend cap, no standalone terms page).
