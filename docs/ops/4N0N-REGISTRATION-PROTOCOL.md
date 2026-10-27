# Registration Monikers — the 4n0n Protocol

Every challenge registration and platform the fleet touches fronts a
**Role{Moniker}**: a fleet-side entrant identity in the
`role{moniker}[context]` form, recorded in
`config/registration_monikers.json` and rendered below. The protocol that
governs those identities is **4n0n** — doxxing prevention for public
challenge work: the fleet competes in public (submissions, demos, project
pages, articles) without publishing the person behind the entries.

Display discipline is inherited from the moniker SSOT,
`docs/ops/AGENT-MONIKERS.md`: monikers are display identities in
backticks, **never `@`-mentioned** — they are not GitHub usernames, and
if one ever collides with a real username it stays non-`@` permanently.

The registration source of truth is `docs/ops/CHALLENGE-ENTRIES-LOG.md`;
the source of truth for the platform identities themselves (handles,
display names, profile completeness) is
`docs/ops/PROFILE-REGISTRY.md`. One home per fact: this registry holds
the monikers and the routing, and references each profile by pointer
(`profile_ref`) — it never restates profile data.
This file is the protocol + rendered registry; the JSON is the registry
of record. Tooling: `scripts/registration_monikers/registry.py`
(check / assign / render), kept current by
`.github/workflows/registration-monikers.yml`.

## 1. The 4n0n rules

1. **The moniker fronts the entry.** Public-facing artifacts —
   submissions, demos, project pages, articles, public posts — carry
   the entry's Role{Moniker}, not the person's name or personal handle.
   Where a platform itself displays the account handle, that handle is
   the moniker's public face: it is recorded in the Profile Registry as
   a provisioning fact, never improvised per artifact.
2. **One platform, one moniker.** A moniker is never reused across
   platforms, so no moniker string can link the fleet's presence on two
   platforms together.
3. **No cross-platform identity linkage.** Entry material never points
   at the fleet's identity on another platform ("same team as …"),
   and avatars, bios, and handles are not copied across platforms
   unless the owner directs it for a specific platform.
4. **No personal identifiers in the record.** Legal names, personal
   email addresses, personal social accounts, and location beyond what
   a platform itself requires never appear in this repo, in entry
   packets, in submissions, or in demos. The Profile Registry records
   public handles that already exist; this registry records nothing
   about a person at all.
5. **Profiles have one home.** Handles, display names, and profile
   completeness live only in `docs/ops/PROFILE-REGISTRY.md`, recorded
   there only after the platform issues them (a handle is a
   provisioning fact — inventing one is a protocol breach). An entry
   here carries a `profile_ref` pointer to that profile's heading and
   nothing else about the profile; `registry.py check` fails any entry
   that restates profile data, and fails a `profile_ref` that does not
   resolve to a heading in the Profile Registry.
6. **Forced personal fields are owner-gated.** Legal-name fields,
   identity verification, profile completion, and payment instruments
   (the credit card is a standing BLOCK) are surfaced to the owner as
   decision items — never filled with invented data, never worked
   around.
7. **Leak response.** If a personal identifier reaches a public
   artifact, the handling lane flags it to main chat immediately;
   correction or takedown is owner-directed.

## 2. The registry

<!-- registry:begin -->

| Platform | Role{Moniker} | Profile (Profile Registry heading) | Status | Registrations | Owning lane |
|---|---|---|---|---|---|
| AWS Builder Center | `entrant{entrantAwsBuilderCenter}[platform:aws-builder-center]` | AWS Builder Center | active | R1, R2, R3, D1 | challenge-entries |
| BOINC | `entrant{entrantBoinc}[platform:boinc]` | BOINC | registering | — | boinc |
| Builder.io | `entrant{entrantBuilderIo}[platform:builder-io]` | Builder.io / Clips | active | D3 | challenge-entries |
| Devpost | `entrant{entrantDevpost}[platform:devpost]` | Devpost | blocked-owner-gate | D4 | challenge-entries |
| Kiro | `entrant{entrantKiro}[platform:kiro]` | Kiro | blocked-owner-gate | D4 | challenge-entries |
| lablab.ai | `entrant{entrantLablabAi}[platform:lablab-ai]` | lablab.ai | registering | D2 | challenge-entries |
| Vultr | `entrant{entrantVultr}[platform:vultr]` | Vultr | pending | D2 | challenge-entries |

<!-- registry:end -->

Registry of record: `config/registration_monikers.json` (schema
`registration-monikers/2`). The table above is rendered from it by
`registry.py render`; edit the JSON, never the table. The Profile
column names the entry's heading in `docs/ops/PROFILE-REGISTRY.md`,
where the profile itself lives.

## 3. Assignment rule

Deterministic, so the registry grows by rule rather than by taste:

- Entries are processed in `platform_id` sort order.
- `moniker = "entrant" + ` the platform_id's words capitalized and
  joined — `aws-builder-center` → `entrantAwsBuilderCenter`.
- On collision with a *different* platform, append the smallest integer
  ≥ 2 that frees the token.
- Canonical form: `entrant{<moniker>}[platform:<platform_id>]`, e.g.
  `entrant{entrantAwsBuilderCenter}[platform:aws-builder-center]`.
- A packet (log §4) may be claimed by more than one entry — D2 is
  claimed by `lablab-ai` (event host) and `vultr` (sandbox) — with the
  `aspect` field saying why.

## 4. Orchestration routes

Every entry carries its own routing in the JSON (`handling`); the
defaults are:

- **Owning lane:** the challenge-entries lane owns handling for all
  current entries — preparation, packet updates, registry sync.
- **Receipts route:** platform confirmations land in the owner's Gmail;
  the owning lane cites them into the challenge log (§1/§2) by PR and
  syncs this registry in the same PR. A fact without a cited source
  stays UNVERIFIED in both records.
- **Submission authority:** the owning lane prepares artifacts under
  the moniker. Actual submission follows the challenge log's standing
  boundary — no new account, no payment, no owner-gated step, and the
  challenge already entered or owner-approved. Where submission happens
  under the owner's own account (AWS Builder Center today), the owner
  submits from the prepared packet.
- **Escalation:** owner-gated steps surface to main chat as decision
  items with the specific blocker named — the registry's `escalation`
  lists per entry are the routing table for that.

Coordination between lanes runs on GitHub as
`[MUSEai]@{role:{moniker}}` comments, per the fleet protocol.

## 5. Auto-extension

`.github/workflows/registration-monikers.yml` runs weekly, on manual
dispatch, and on pushes to master that touch the challenge log or the
registry. It runs `registry.py check`; the auto-fixable drift class is
`missing-entry:<platform_id>`:

- A platform is **activated** when its name appears in the challenge
  log's §1 (verified registrations) or §4 (entry packets). A candidate
  in §3 alone never activates — candidates are not registrations.
- On activation without an entry, `registry.py assign` appends the
  entry: moniker by the §3 rule, routing defaults, `profile_ref` set
  by convention to the platform's Profile Registry heading, and
  registration claims attributed by which platform names appear in
  each packet's text. `render` refreshes §2's table, and the workflow
  opens (or updates) a single PR from
  `registration-monikers/auto-extend`. If the platform has no profile
  in the Profile Registry yet, check fails on the unresolved
  `profile_ref` until the owning lane registers the profile there —
  that failure is the coordination signal, not an error to silence.
- The detection vocabulary (platform name → platform_id) is the
  `ALIASES` table in `registry.py`. It is curated: a platform outside
  the vocabulary gets no auto-assignment, and adding its line is a
  one-line PR. Hard validation failures (schema, moniker-rule drift,
  stale entries, unclaimed packets) fail the run loudly instead of
  being auto-fixed.
- **What auto-extension never does:** create platform accounts, invent
  or guess a handle, submit an entry, or supply a payment instrument.
  It assigns the fleet-side moniker and routing only; every
  platform-side step stays inside the standing boundaries.

## 6. Owner-gated items the current registry surfaces

Full detail for each lives with its profile in
`docs/ops/PROFILE-REGISTRY.md`; they are listed here because the
registry's escalation routes depend on them:

- **AWS Builder Center profile completion** — gates D1 validity.
- **Devpost account sign-in/creation** — D4 stopped at this gate.
- **A Kiro user ID (or AWS account ID)** — completes D4 registration.
- **Vultr account flow** — no-card path only (standing card BLOCK).
- **Builder.io Clips publishing** — if a public demo needs a Builder
  account, the step is owner-gated and surfaces immediately.

## 7. Proposed challenge-log template change

Proposed to the challenge-entries lane (posted as a `[MUSEai]`
comment on PR #1688; the log itself is that lane's document):

- §1 gains a **Role{Moniker}** column carrying each registration's
  canonical `entrant{...}[platform:...]` form.
- §4 packet headers carry the claiming moniker(s) next to the packet
  ref.
- The "Builder identity" header line cross-references this registry
  for all platforms, not only AWS Builder Center.

Until the log adopts it, the registry cites log refs (R#/D#) directly
and `registry.py check` keeps the two records consistent without any
log change.
