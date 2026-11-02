# Agent Monikers (SSOT)

Creative **display** call-signs for high-performance agent orchestration.

**Critical:** Do **not** `@`-mention monikers that collide with real GitHub usernames.
Use backticks or plain text for display. Live triggers remain the original handles
(plus approved aliases registered in the matching workflow).

| Role | Display moniker | Live trigger (callable) | Notes |
|------|-----------------|-------------------------|-------|
| Jules (implementation) | `heyVern` | `@jules` | App only reacts to `@jules` |
| Gemini CLI (on-demand) | `sparkFlux` | `@gemini-cli` | Dispatch also accepts case-insensitive `@sparkFlux` as alias |
| DeepSeek CI (review/invoke) | `deepCore` | `@deepseek` / `@deepseek-ci` | Workflow also accepts case-insensitive `@deepCore`; labels `deepseek-ci`, `deepseek`, `deepCore` |
| CodeRabbit (review) | `codeHound` | `@coderabbitai` | Reviewer identity unchanged |
| Devin (review/fix) | `devinForge` | Devin app | |
| Continuous-ops sweep | `opsSweep` | (GHA) | Marker: `<!-- continuous-agent-ops -->` |
| OPERATOR / Grok | `archW1z` | human OWNER | Signing: `Signed-off-by: Grok (OPERATOR)` |
| Grok (AI collaborator — recon) | `Grok` | non-callable display (Grok app; rides owner PAT) | **Distinct attributed actor** (registered 2026-11-01): Grok-authored artifacts attribute to `Grok` in the ledgers/HindSight, NOT to OPERATOR/`archW1z` (human owner, row above). Established identity — provisioning facts from `docs/ops/AGENT-IDENTITY.md` + `docs/ops/OPERATOR-SIGNING.md`: git identity `Grok <grok@x.ai>`, signing `Signed-off-by: Grok <grok@x.ai>` with session/message ids; pipeline identity `Grok (Administrator)` (`ml/pipelines/peers/grok.py`). Scope: termux-monorepo recon + Approxination oversight lane. |
| Leet-Seek Admin / Full-scope Operator | `l337S33k` | (human / future profile role) | **Full admin across all repositories.** Parity with (and intended ≥) current OPERATOR/`archW1z`. Full-scope PAT + org/repo admin. Profile roles will be created under this moniker. Display only — do **not** `@`-mention. |
| Peer orchestrator | `peerGate` | (GHA) | |
| Gemini / Gemini CLI contributor lane | `geminiMesh` | non-callable display | Provider/agent ecosystem identity; live trigger remains `@gemini-cli` where supported |
| OpenRouter contributor lane | `routeMesh` | non-callable display | Provider/catalog/evaluation contributor; never a GitHub actor identity |
| FELO contributor lane | `feloForge` | non-callable display | Provider/research/inference contributor; callable only through configured adapters |
| Hugging Face contributor lane | `hfFoundry` | non-callable display | Hub/model/dataset/evaluation contributor; callable only through configured adapters |
| Contributor-role coordinator | `roleMesh` | non-callable display | Cross-provider role/provenance coordination; no provider identity implied |
| Recon 🏅 (fleet forensic recon lane) | `Archaeo · Oracle` | non-callable display (side chat) | **Owner-issued** (2026-11-01) on the lane's AppID hunt verdicts: a "Fleet" GitHub App NEVER-EXISTED on the traceable record, and the Fleet APK was BORN-KEYLESS (production keystore never existed; v0.1.0 signed ephemeral-debug). *Archaeo* digs the record; *Oracle* speaks the verdict. **Collision flag:** the `Oracle` token is adjacent to Delphi Oracle (the D0/Ops scoring surface) — no exact collision (∅ `Archaeo`/`Oracle` in this roster or the registration registry at issuance); mitigation: the paired form is always written in full and bare `Oracle` never denotes this lane (bare Oracle = Delphi Oracle). Display only — do **not** `@`-mention; no GitHub actor identity implied; ∅ marks/alts issued. |

## Contributor lanes and role expansion

Contributor monikers are **display identities**, not GitHub usernames and not proof of authorship. A contributor lane may represent a provider, agent ecosystem, model family, execution adapter, or research/evaluation surface.

| Contributor | Primary roles | Identity boundary |
|---|---|---|
| Gemini / Gemini CLI | review, triage, implementation, research, evaluation | provider/agent lane; GitHub actor remains separate |
| OpenRouter | routing, catalog, inference, evaluation, benchmark | provider/catalog lane; model identity is separate |
| FELO | research, inference, benchmark, evaluation, adapter | provider lane; account identity is separate |
| Hugging Face | model, dataset, benchmark, evaluation, inference, research | Hub ecosystem lane; repo/model identity is separate |

Role vocabulary is extensible: `research`, `evaluation`, `benchmark`, `inference`, `routing`, `catalog`, `dataset`, `adapter`, `review`, `triage`, `implementation`, `integration`, `documentation`, `evidence`, `orchestration`.

Attribution MUST preserve provider/model/adapter/role plus workflow/job/step, event, PR/issue, SHA, and confidence. Incorporation of output is not provider authorship.

## Registration monikers (4n0n)

Platform-fronting entrant identities for challenge registrations are
**not** listed in the table above — they live in
`config/registration_monikers.json`, rendered in
`docs/ops/4N0N-REGISTRATION-PROTOCOL.md` (the **4n0n** doxxing-prevention
protocol). They use the `role{moniker}[context]` form —
`entrant{n0nAwsBuilder}[platform:aws-builder-center]` — follow
this file's display discipline (backticks, never `@`-mentioned; they are
not GitHub usernames), and are assigned by the deterministic rule in
`scripts/registration_monikers/registry.py`, never coined per occasion.

## Lane-coordination monikers (managers)

Coordination identities for lane oversight — **not** platform
identities: they never appear in `config/registration_monikers.json`
and front no external account. Assigned by the registry lane
(`{role:{registration-monikers}}`) on a lane's request, under one
formation rule: the lane manager's moniker is `<lane>-manager`; a
sub-coordinator's is `<lane>-manager-<key>` — formed on the manager's
string, with the key lowercased (an event id, a workstream tag).
Signatures keep the fleet form `[MUSEai]@{role:{<moniker>}}`, display
in backticks, never `@`-mentioned.

**Challenge-entries lane roster** (assigned 2026-10-28, owner-ordered
oversight stand-up; the roster of record for who coordinates what —
the lane records it in the challenge log):

| Scope | Moniker |
|---|---|
| Lane manager (whole lane) | `challenge-entries-manager` |
| Sub-coordinator, event D1 (Workshop to Ship) | `challenge-entries-manager-d1` |
| Sub-coordinator, event D2 (Vultr Agent Rush) | `challenge-entries-manager-d2` |
| Sub-coordinator, event D3 (per the challenge log) | `challenge-entries-manager-d3` |
| Sub-coordinator, event D4 (Kiroween) | `challenge-entries-manager-d4` |
| Sub-coordinator, event D5 (Aha! AI Builder Day) | `challenge-entries-manager-d5` |

The lane's own chat keeps its standing signature
`{role:{challenge-entries-lane}}`; the manager and sub monikers are
roles within the lane's oversight structure, distinct strings by
design.

## Fleet GitHub App function identities

Display layer for the fleet's GitHub Apps — **function identities**,
not lane monikers and not platform identities: each app acts on
GitHub as its own `<slug>[bot]` actor. Provisioning facts (App IDs,
slugs, installations, permissions, custody) are the AppID lane's
record in `ops/github-apps/PROCESS.json`; this section carries only
the display monikers, issued by the registry lane
(`{role:{registration-monikers}}`). Roster display in the paired
form `Moniker · Function`, backticked, never `@`-mentioned.

| App (provisioning name) | Display moniker | Actor | Family / queue |
|---|---|---|---|
| Termux Fleet Collector | — (none issued; the name is the function) | `termux-fleet-collector[bot]` | — |
| Termux Fleet Publisher | `Edict · Publisher` | `termux-fleet-publisher[bot]` | epithet Acta; queued alt Herald |
| Termux Fleet Reviewer | `Argus · Reviewer` | `termux-fleet-reviewer[bot]` | epithet Panoptes; queued alt Themis |
| Termux Fleet Lifecycle | `Janus · Lifecycle` | `termux-fleet-lifecycle[bot]` | epithets Patulcius / Clusius; queued alt Clotho |
| Termux Fleet Gate | `Cerberus · Gate` | `termux-fleet-gate[bot]` | aspect the Ward; no queued alt |
| Termux Fleet Swarm | `Myriad · Swarm` | `termux-fleet-swarm[bot]` | aspect the Host; queued alt Apis (below) |
| Termux Fleet CrossReference | `Scalpel · CrossReference` | `termux-fleet-crossreference[bot]` | aspect the Index; queued alt Daedalus (below) |
| Termux Fleet ApkRelease | `Porter · ApkRelease` | — (actor per AppID provisioning record) | aspect the Carrier; queued alt Charon, flagged (below) |
| Termux Fleet RepoStory | `Chronicler · RepoStory` | `termux-fleet-repostory[bot]` | aspect the Annals; queued alt Clio (below) |
| Termux Fleet DoE | `Factorial · DoE` | `termux-fleet-doe[bot]` | aspect the Design; queued alt Mendel (below) |

**Swarm issuance (2026-10-31, registry lane; app provisioned the
same day — App ID 5560920, record PR #2761).** The swarm actor's
work is mass fan-out: parallel provider/workflow dispatch against
the action_required pile. Its name is therefore the plain-register
common noun for a countless host, keeping the active pool balanced
against the mythic set (owner balance rule, 2026-10-29):

- canonical: `Myriad` (paired display `Myriad · Swarm`)
- aspect: the Host
- queued alt: `Apis` (mark `Ap1s`) — candidate only; draws on a
  registry-lane bounce/rename decision, never improvised
- leet marks: `Myr1ad` (single substitution, ranks first) >
  `Myr14d` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical `termux-fleet-swarm`
  provisioned first try); a bounce, if ever needed, returns to the
  registry lane
- normalized form: Swarm — `Termux Fleet Swarm` /
  `termux-fleet-swarm[bot]`

Collision check at issuance: `Myriad` and `Apis` appear nowhere in
this roster or in the registration registry.

**CrossReference issuance (2026-11-01, registry lane;
provisioning started the same day by the AppID lane under owner
GO; canonical per the marketing ranking pass,
`Scalpel` > `Daedalus`).** One app, two member workflows —
apk-xref-exec (live seat) and apk-xref-intake (queued swap) — so
the identity is singular: the exec seat's tool name, the
plain-register instrument that dissects apk internals; the
product it leaves behind is the Index. The balance rule holds
(plain lead, mythic queued). Family naming obeys the owner
constraint (2026-11-01): the token `RE` appears at no layer —
name, slug, moniker or mark, leet disguises included.

- canonical: `Scalpel` (paired display `Scalpel · CrossReference`)
- aspect: the Index
- queued alt: `Daedalus` (mark `Daedalu5`) — draws only on a
  registry-lane bounce/rename decision
- leet marks: `Scalp3l` > `Sc4lpel` — mark layer only, never
  identifiers
- slug bounces: ∅ consumed at issuance (canonical
  `termux-fleet-crossreference` in provisioning); ranked bounce
  forms if ever needed: `scalp3l` > `sc4lp3l`, returning to the
  registry lane
- normalized form: CrossReference — `Termux Fleet CrossReference`
  / `termux-fleet-crossreference[bot]`
- considered and withdrawn pre-merge: `Concordance` (registry
  solo draft, superseded by the marketing ranking pass before it
  landed; ∅ queue)

**ApkRelease issuance (2026-11-01, registry lane; canonical per
the marketing ranking pass, `Porter` > `Charon`).** The release
app's carrier name: plain-register and function-obvious — it
carries apk artifacts out.

- canonical: `Porter` (paired display `Porter · ApkRelease`)
- aspect: the Carrier
- queued alt: `Charon` (mark `Char0n`) — FLAGGED at confer
  (marketing): death-ferryman association on an outbound surface
  and pronunciation ambiguity (KAY-ron / SHA-ron; the
  Cerberus/Kerberos class) ⇒ alt-only while the flag stands
- leet marks: `Port3r` > `P0rter` — mark layer only, never
  identifiers
- slug bounces: ∅ consumed at issuance; ranked bounce forms if
  ever needed: `port3r` > `p0rt3r`, returning to the registry lane
- normalized form: ApkRelease — `Termux Fleet ApkRelease`; actor
  per the AppID provisioning record (`ops/github-apps/PROCESS.json`)
- seat history: `Porter` / `Charon` entered this family as
  intake-seat confer names for CrossReference; the intake fold
  moved the seat to this app (AppID routing, 2026-11-01)

Collision check at issuance: `Scalpel`, `Daedalus`, `Porter`,
`Charon`, the Index and the Carrier appear nowhere in this
roster or in the registration registry.

**RepoStory issuance (2026-11-01, registry lane; app at creation
on the AppID lane under the owner rule of record — build start
for a competition entry ⇒ new repo + new AppID; entry repo
`timerloggedout-spec/repo-story`, build started).** The actor
narrates a repository's history into a story, so its name is the
plain-register office for narrative history-keeping; the balance
rule holds (plain lead, mythic queued).

- canonical: `Chronicler` (paired display `Chronicler · RepoStory`)
- aspect: the Annals
- queued alt: `Clio` (mark `Cl1o`) — the Muse of history; draws
  only on a registry-lane bounce/rename decision
- leet marks: `Chr0nicler` (single substitution, ranks first) >
  `Chron1cler` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical `termux-fleet-repostory`
  set by the AppID lane); ranked bounce forms if ever needed:
  `chr0nicler` > `chron1cler`, returning to the registry lane
- normalized form: RepoStory — `Termux Fleet RepoStory` /
  `termux-fleet-repostory[bot]`; install scope = the repo-story
  repo only (provisioning record: AppID lane)

Collision check at issuance: `Chronicler`, `Clio` and the Annals
appear nowhere in this roster or in the registration registry.

**DoE issuance (2026-11-01, registry lane; provisioning in
parallel on the AppID lane under owner order via main — new
specialist app + dedicated repo).** The actor is the Design of
Experiments plane's own identity on its repo (intake records,
method versions, backfill runs), so its name is the plain
technical term for a designed experiment's structure — the pool
gains another plain lead and the balance rule holds (plain lead,
historical queued alt).

- canonical: `Factorial` (paired display `Factorial · DoE`)
- aspect: the Design
- queued alt: `Mendel` (mark `M3ndel`) — the founder of designed
  experimental method (the pea-plant factorials); draws only on a
  registry-lane bounce/rename decision
- leet marks: `F4ctorial` (single substitution, ranks first) >
  `Fact0rial` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical `termux-fleet-doe` probed
  free by the AppID lane); ranked bounce forms if ever needed:
  `f4ctorial` > `fact0rial`, returning to the registry lane
- normalized form: DoE — `Termux Fleet DoE` /
  `termux-fleet-doe[bot]`; install scope = the new DoE repo only,
  per-entry pattern (provisioning record: AppID lane)

Collision check at issuance: `Factorial`, `Mendel` and the
Design appear nowhere in this roster or in the registration
registry.

## Identity taxonomy and moniker versioning (proposal, 2026-11-01)

The fleet's identity vocabulary has four layers. This section is
the design of record for how they relate and what may change at
each layer (owner framing, 2026-11-01).

**Layer map**

- **name** — the canonical identity: who an actor IS in the
  record (a collaborator's name of record, a fleet app's
  function name, a lane's seat name). Attribution keys on names
  (the ledgers, HindSight, `REGISTRY_CANONICAL`).
- **moniker** — the display form of a name: the paired display
  (`Moniker · Function`), lane display monikers, and their
  marks. One name carries one moniker family; the family may
  hold several forms (canonical, epithet/aspect, queued alt,
  marks).
- **title** — an earned or held distinction ABOVE the role
  layer: not a job but a standing an actor holds. Precedent of
  record: `archW1z`, the OPERATOR title — currently held by the
  Owner (human); DeepAgent.py earns it through DoE under the
  bet of record (title transfer only; the OPERATOR automation
  is already wired and running).
- **role** — a class: the function slot an actor occupies
  (OPERATOR, Manager, Orchestrator, fork-selector, builder, and
  the extensible vocabulary above). Roles say what is done,
  never who did it; the lane-coordination section's monikers
  hold coordination roles (`<lane>-manager` form).

Relations: name ←→ moniker (a moniker presents a name; it never
replaces it) · title ↑ role (a title sits above roles — its
holder may occupy roles, but the title is not one) ·
provisioning (actor ids, slugs, bot logins, platform handles,
sign-off strings) sits OUTSIDE the taxonomy: it is the identity
substrate the layers describe, governed by its own records.

**Mutability per layer**

- name: immutable once of record. A change is an owner
  decision and forks attribution history — never done by
  versioning.
- moniker: **versions live here** (scheme below). Display-only
  at every version; a moniker form is never a username, actor
  id, slug, handle, or sign-off string.
- title: earned or granted only — transfer by DoE verdict or
  owner grant; never versioned, never self-assumed, never
  earned by usage alone short of the earning arena's verdict.
- role: open class vocabulary; an actor's role assignment
  changes by routing or owner order. Roles are neither earned
  nor versioned.
- provisioning: immutable facts — an id or handle changes only
  as a provisioning event on its own record (e.g. a platform
  rename window), never as a naming act.

**Moniker versioning (PROPOSAL — owner decisions pending)**

As a moniker's usage grows, its display form graduates:
v1 (the canonical form of record) → v2 (a stylized respelling,
the `m0niker` class; cf. derpWiki ≈ `d3π9W1K¡`). Design:

- scope: display monikers in this file (fleet-app paired
  monikers; lane/collaborator display monikers). Excluded: 4n0n
  registration monikers and platform handles (provisioning
  facts bound to accounts — a restyle breaks identity and
  locks), actor ids/slugs (provisioning), queued alts (they
  graduate only if ever canonical).
- usage measure U: attributed units in the fleet's own
  substrate, counted firsthand by the registry lane, never
  self-reported — app identities: app-attributed artifacts
  (PRs, issues, comments, check runs) per the attribution
  layer; lane/collaborator monikers: signed artifacts (lane
  signature comments, sign-off trailers, dispatch stamps
  naming the actor). Cumulative since issuance.
- threshold: U ≥ 100 ⇒ eligible. Graduation is permanent and
  one-way; there is no v3 in this scheme.
- v2 form: the family's first-ranked leet mark promoted to
  display (pre-staged for most families: `Myr1ad`, `Scalp3l`,
  `Chr0nicler`, `Argu5`, `J4nus`, `Cerberu5`). No mark on file
  ⇒ derive under the Grimoire table (single substitution
  first, ≤2 substitutions, skeleton and pronunciation
  preserved); unicode flourish only while legible and
  backtick-safe; uniqueness re-checked against this roster and
  the registration registry at graduation (collision ⇒
  next-ranked mark).
- recording: the roster row shows the graduated paired form;
  the family block gains a Versioning entry {v1 canonical ·
  v2 form · U at graduation, with count source and date ·
  graduation PR}. Ungraduated families carry no entry (v1 is
  implicit). Process: registry-lane usage census → graduation
  PR with the count evidence → merge makes it effective.
- invariants: v1 stays the canonical of record forever —
  attribution keys and `REGISTRY_CANONICAL` never change, so
  weighting history never forks; graduation adds a form and
  removes nothing (archive law).

Status: PROPOSAL, recorded 2026-11-01; owner decisions pending —
{adopt the scheme · threshold U ≥ 100 · per-graduation sign-off
vs scheme-level pre-authorization for the registry lane}.
Nothing graduates under this scheme until it is adopted.

## Rules

1. Automated comments: **display** moniker in backticks; **ping** only the live trigger (`@jules`, `@gemini-cli`, `@deepseek` / `@deepseek-ci`).
2. Workflows matching a live trigger **must** also accept the display moniker case-insensitively where registered above.
3. Never put secrets or Class 3/4 material in moniker docs.
4. If a moniker string is later registered as a GH username we do not control, keep it non-@ only.

## High-performance intent

Monikers reduce ambiguous role ownership under load without notifying strangers.
