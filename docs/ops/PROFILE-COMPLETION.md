# Profile Completion — Adaptive Method

Reusable, parameterized procedure for finishing a fleet platform profile **on the
platform's own pages**. Proven 2026-10-29 on Devpost, AWS Builder Center, and Kiro
(accounts lane, chat 79a004f8). Any lane adapts it to a new platform by filling the
parameter table and adding one annex entry — the steps and rules do not change.

**Seams:** profile content comes from, and results return to, the SSOT
`docs/ops/PROFILE-REGISTRY.md`; identity assignment (which moniker/handle a profile
is created under) comes from `config/registration_monikers.json`; conduct rules are
`docs/ops/4N0N-REGISTRATION-PROTOCOL.md`. This doc owns the *method* only — it holds
no profile content of its own.

## Parameters (fill per platform before starting)

| Parameter | Meaning |
|---|---|
| `platform` | Platform name (matches the registry heading, e.g. `Devpost`) |
| `registry_ref` | The profile's heading in `docs/ops/PROFILE-REGISTRY.md` |
| `profile_url` | Public profile URL (completion is judged here) |
| `edit_url` | The platform's own edit/settings page |
| `signin_routes` | Ordered routes the account actually accepts (see Rule 3 — the account's linked IdP governs, not preference) |
| `prepared_avatar` | Registry-prepared avatar asset path, or `none` |
| `prepared_about` | Registry-prepared About/bio text, character-for-character, or `none` |
| `prepared_socials` | Registry-specified social links only |
| `owner_lane` | Lane that owns the profile (registry hierarchy) |

## Procedure

1. **Recon first, page-only.** Open `edit_url`. Produce the full field inventory:
   every field, its current value or EMPTY, forced vs optional, and any
   completion checklist the platform shows. Type nothing in this pass.
2. **Sign in on the account's own route** (Rule 3). Nothing is filled before the
   session is live.
3. **Fill from the registry SSOT, exactly.** Avatar asset, About text, and socials
   come from `registry_ref` — verbatim where the registry gives paste-ready text.
   Fields the registry does not cover stay untouched unless a Rule below forces
   a value.
4. **Save per page.** Some platforms validate page-by-page; a failed save can
   clear dependent selections (see Annex: Devpost) — re-check before re-saving.
5. **Verify on the public profile.** Completion = `profile_url` displays the
   fields. A form success toast alone is not completion.
6. **Record.** Registry + owning log updated by PR (PR number taken from the
   publish tool's own output; merge established by the PR-numbered commit in a
   master-history scan + landed content read on master). Carry the countdowns
   (issue #1880) in reports while the parent packet is open.

## Rules

1. **4n0n discipline.** Moniker only on third-party profiles. No cross-platform
   linkage: never reuse one moniker's avatar/character, or its bio text verbatim,
   on another platform; no social links beyond `prepared_socials`.
2. **Forced fields get the least-specific true value.** If a save hard-requires a
   field, supply the coarsest truthful value the form accepts (e.g. country
   before state before city) and record that it was forced. **Never invent PII**
   (birth dates, legal names, addresses stay empty).
3. **Sign-in route = the account's linked IdP.** Try the fleet Google route
   first; a platform may reject it because the account is linked to another IdP
   (see Annex: Builder Center). Switching IdP route is an owner-authorized step.
   Passwords enter only through Secure Vault cards — never chat, never files.
   **Pre-warn before any phone prompt** ("prompt incoming — phone in hand"),
   then relay the prompt number in one terse line the instant it is known.
4. **Forced real-name field = STOP.** If a save demands a legal First/Last name
   (or equivalent) that the profile's cryptic display name cannot satisfy, stop
   before saving and surface the exact fields to the owner. This is the 4n0n
   carve-out: the owner supplies values, chooses style-compliant substitutes,
   or drops the gated item. Never work around it.
5. **Moderation stops are surfaced, never silently rewritten.** If the platform
   rejects `prepared_about` in moderation, report the rejection verbatim. The
   fallback is an owner-ruled plain-language bisection (same meaning, leet →
   plain, symbol tails dropped), tried incrementally until it passes.
6. **No card, ever.** A payment/card demand anywhere in the flow is a BLOCK:
   stop and surface it as an owner item.
7. **Route selection is the owner's.** Where sign-up offers several routes
   (e.g. email / GitHub / a sponsor IdP), the owner's selection governs; a lane
   does not substitute its own preference for a route the owner picked.

## Failure taxonomy (stop + surface, with the prescribed note)

| Stop | Signal | Note to owner |
|---|---|---|
| IdP linkage | "already associated with … using X as its sign-in method" | Name the linked IdP; ask to authorize that route |
| Real-name carve-out | required First/Last (or State/Province) empty at save | List the exact required fields (Rule 4) |
| Moderation | "Moderation check failed" on save | Quote it; propose the Rule 5 bisection |
| Card block | any payment field | Stop; owner item (Rule 6) |
| Bot check | challenge resets for the agent browser but passes in the owner's own browser | Session-reuse angle; file/attach to a target brief rather than retrying in a loop |

## Annex — per-platform quirks (verified)

### Devpost (verified 2026-10-29)
- Edit pages: `/settings` (profile info) and `/settings/preferences_and_eligibility`.
- The Preferences save **hard-requires Location**; coarsest accepted value:
  `United States`. Occupation = Professional spawns a second required field,
  "Are you currently employed in tech?" (answer truthfully; fleet value: Yes).
- A **failed save clears the interest selections** — re-select before re-saving.
- Skill tags save lowercased/hyphenated (`github-actions`,
  `artificial-intelligence`, `machine-learning`); a space in a tag name can
  split it into an unintended extra chip — check the chips before saving.
- GitHub social + Website may already be populated from the connected account;
  leave LinkedIn/Twitter empty (Rule 1). Avatar: leave the default initial
  unless the registry prepares a Devpost-specific asset (Rule 1).

### AWS Builder Center (verified 2026-10-29)
- The Builder ID for the fleet email is **GitHub-linked**: Google sign-in is
  rejected by AWS itself ("already associated with an AWS Builder ID using
  GitHub as its sign-in method"). GitHub route (owner-authorized) completes via
  the existing GitHub session.
- Avatar: Profile → Update avatar; upload works and reflects on the public
  profile immediately.
- The registry's prepared leet About **failed AWS moderation twice**
  ("Moderation check failed. Please review your input and try again.") —
  Rule 5 case, pending owner ruling.
- Social links demand a full `https://` URL. The Edit-information save
  **hard-requires First name, Last name, State/Province** — Rule 4 carve-out,
  pending owner ruling. Display name + country are separate fields and were
  already set; do not touch them.

### Kiro (verified 2026-10-29)
- **No editable profile fields exist.** The account row (email, sign-in method,
  plan) is read-only; Appearance is a theme preference, not a profile field.
  Completion for Kiro = confirming this state; there is nothing to fill.

### lablab.ai (recon 2026-10-29; execution: challenge-entries lane)
- Sign-up routes: Email (magic link), GitHub, AMD. **No Google route.** The
  register form carries a Cloudflare check.
- The **AMD route creates a separate AMD account** behind its own profile-info
  form — it is an account creation of its own, not a lablab field. Route
  selection is the owner's (Rule 7).
- Profile completion + Discord connect are event prerequisites (per the
  platform's getting-started guide); public profiles show display name +
  handle, avatar/cover, Discord link, skill ratings.
- No card anywhere in the lablab path.

### Builder.io / Clips (verified 2026-10-27)
- Hosted Clips (clips.agent-native.com) account = Google sign-in only; **no
  username/handle or profile fields were offered** — nothing to complete.
  Remaining setup (storage connection) is build-time, in-app, not profile work.

## Adapting to a new platform (checklist)

1. Add the platform's row to the parameter table (from its registry entry).
2. Recon (Procedure step 1) and append an Annex entry: edit URLs, forced
   fields, save quirks, moderation behavior, IdP linkage — each marked
   verified with a date, or `not established`.
3. If the registry holds no prepared content for a field the platform demands,
   that is a **registry-prep flag** to the owning lane — not improvisation.
4. Run the procedure; record per step 6.
