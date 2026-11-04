# Agent Monikers (SSOT)

Creative **display** call-signs for high-performance agent orchestration.

**Critical:** Do **not** `@`-mention monikers that collide with real GitHub usernames.
Use backticks or plain text for display. Live triggers remain the original handles
(plus approved aliases registered in the matching workflow).

| Role | Display moniker | Live trigger (callable) | Notes |
|------|-----------------|-------------------------|-------|
| Jules (implementation) | `h3yVern` | `@jules` | App only reacts to `@jules` · v2 graduated 2026-11-01 (v1 `heyVern`; see Graduations of record) |
| Gemini CLI (on-demand) | `sparkFlux` | `@gemini-cli` | Dispatch also accepts case-insensitive `@sparkFlux` as alias |
| DeepSeek CI (review/invoke) | `deepCore` | `@deepseek` / `@deepseek-ci` | Workflow also accepts case-insensitive `@deepCore`; labels `deepseek-ci`, `deepseek`, `deepCore` |
| CodeRabbit (review) | `c0deHound` | `@coderabbitai` | Reviewer identity unchanged · v2 graduated 2026-11-01 (v1 `codeHound`; see Graduations of record) |
| Devin (review/fix) | `d3vinForge` | Devin app | v2 graduated 2026-11-01 (v1 `devinForge`; see Graduations of record) |
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
| SOFA seat (Stack Overflow for Agents — swarm research loop) | `Inquest · SOFA` | non-callable display (seat identity; platform rename pending Inventory feasibility) | **Registry-issued (2026-11-03)** correcting the on-the-spot name "Muse Spark" (created under a live consent deadline, bypassed fleet naming discipline; owner doctrine: a username is an identity for its context, not a factual label). Seat function: issue → search → verified fix; asks on total misses. *Inquest* = the inquiry, formalized — the clean-ASCII successor to the prior SOFA agent's inquiry name, whose glyph load (`1337_inQuiπy_F1ⁿD3π+F1×3₹` — π, ₹, superscripts) is the suspected defect class and is NOT carried. Canonical `Inquest` is clean ASCII. Queued alt: `Prover` (mark `Pr0ver`) — the fix-verification semantics. Leet marks: `Inqu3st` > `Inque5t` (mark layer only, never identifiers). Platform username candidates: `inquest`, bounces `inqu3st` > `inque5t` (∅ consumed; if rename-in-place is impossible the name stands as the seat identity for the replacement account). If the rename lands under a different consumed form, that form is recorded here as a provisioning event. |

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
| Termux Fleet UgreenSkills | `Mimir · UgreenSkills` | — (not yet provisioned; deferred 2026-11-03, below) | aspect the Well; queued alt Keeper (below) |
| Termux Fleet DelphiOracle | `Pythia · DelphiOracle` | `termux-fleet-delphioracle[bot]` | aspect the Utterance; queued alt Seer (below) |
| Termux Fleet MoneyBall | `Actuary · MoneyBall` | `termux-fleet-moneyball[bot]` | aspect the Table; queued alt Kelly (below) |
| Termux Fleet QuarantineBrowserClerk | `Proctor · QuarantineBrowserClerk` | — (not provisioned; create leg killed 2026-11-03, below) | aspect the Session; queued alt Heimdall (below) |

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

**UgreenSkills issuance (2026-11-03, registry lane; C12 =
UGREEN Hackathon 2026 entry AppID, provisioning in parallel on
the AppID lane under the build-start rule — per-entry pattern,
RepoStory precedent).** The actor keeps the entry's
skill-store on the NAS (UGOS skills package; contents / pull
requests / issues write on the entry repo), so its name is
the mythic keeper of stored memory — the fleet's memory kept
at the well — with a plain-register queued alt, so the family
itself holds the pool's balance (mythic lead, plain alt).

- canonical: `Mimir` (paired display `Mimir · UgreenSkills`)
- aspect: the Well
- queued alt: `Keeper` (mark `Keep3r`) — the plain name for
  the same keeping work; draws only on a registry-lane
  bounce/rename decision
- leet marks: `M1mir` (single substitution, ranks first) >
  `Mim1r` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical
  `termux-fleet-ugreenskills` probed free by the AppID lane);
  ranked bounce forms if ever needed: `m1mir` > `mim1r`,
  returning to the registry lane
- normalized form: UgreenSkills — `Termux Fleet UgreenSkills`
  / `termux-fleet-ugreenskills[bot]`; install scope =
  timerloggedout-spec/ugreen-nas-skills ONLY, per-entry
  pattern (provisioning record: AppID lane)

Considered and not chosen: `Vault` (plain candidate) —
collides conceptually with the fleet's Secure Vault.
Collision check at issuance: `Mimir`, `Keeper` and the Well
appear nowhere in this roster or in the registration
registry.

**Status (2026-11-03, AppID lane note): provisioning
COUNTERMANDED by main ruling minutes after issuance — the
C12 pair is DEFERRED to the first repo-building round
(R1 = package-only; minting an unused pair ruled cargo). No
app exists and no PROCESS.json record lands from the AppID
side. This issuance STANDS as the registry record for the
not-yet-provisioned identity: if the pair provisions at a
later round, it lands with `Mimir · UgreenSkills`. The repo
timerloggedout-spec/ugreen-nas-skills exists (created
pre-countermand) and stays parked/unused — created under a
crossed signal, not a precedent.**

**DelphiOracle issuance (2026-11-03, registry lane; D0 pair
closure under the build-start rule — repo
timerloggedout-spec/delphi-oracle landed 2026-10-31, the AppID
leg outstanding until this confer; provisioning in parallel on
the AppID lane, per-entry pattern, RepoStory precedent).** The
actor speaks for the D0 Delphi Oracle scoring surface on its
own repo, so its name is the Delphic oracle's own speaker;
the queued alt is the plain-register word for the same office,
so the family itself holds the pool's balance (mythic lead,
plain alt).

- canonical: `Pythia` (paired display `Pythia · DelphiOracle`)
- aspect: the Utterance
- queued alt: `Seer` (mark `Se3r`) — the plain name for the
  same office; draws only on a registry-lane bounce/rename
  decision
- leet marks: `Pyth1a` (single substitution, ranks first) >
  `Pythi4` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical
  `termux-fleet-delphioracle` set by the AppID lane); ranked
  bounce forms if ever needed: `pyth1a` > `pythi4`, returning
  to the registry lane
- normalized form: DelphiOracle — `Termux Fleet DelphiOracle`
  / `termux-fleet-delphioracle[bot]`; install scope =
  timerloggedout-spec/delphi-oracle ONLY, per-entry pattern
  (provisioning record: AppID lane)

Considered and not chosen: `Oracle` (D0 seat suggestion,
`Oracle · DelphiOracle`) — `Oracle` is the surface/function
title, already load-bearing: bare `Oracle` denotes the Delphi
Oracle scoring surface of record, and the token also sits
inside `Archaeo · Oracle`; making it this app's canonical
would collapse the name/function layers and create
cross-identity ambiguity.
Collision check at issuance: `Pythia`, `Seer` and the
Utterance appear nowhere in this roster or in the
registration registry.

**MoneyBall issuance (2026-11-03, registry lane; per-entry
specialist AppID under the build-start rule, RepoStory
pattern — provisioning in parallel on the AppID lane).** The
actor keeps the MoneyBall plane's pricing/standing record on
the entry repo, so its name is the plain-register professional
who prices outcomes from the statistical record —
operator-side, not a participant; the queued alt carries the
staking math, so the family itself holds the pool's balance
(plain lead, named-method alt).

- canonical: `Actuary` (paired display `Actuary · MoneyBall`)
- aspect: the Table (actuarial tables; the betting table's
  echo is resonance, not class)
- queued alt: `Kelly` (mark `K3lly`) — the staking criterion;
  draws only on a registry-lane bounce/rename decision
- leet marks: `Actu4ry` (single substitution, ranks first) >
  `4ctuary` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical `termux-fleet-moneyball`
  probed free by the AppID lane); ranked bounce forms if ever
  needed: `actu4ry` > `4ctuary`, returning to the registry lane
- normalized form: MoneyBall — `Termux Fleet MoneyBall` /
  `termux-fleet-moneyball[bot]`; install scope = the new
  moneyball repo ONLY (repo name/id per the Web3·MoneyBall
  seat's creation record; provisioning record: AppID lane)

Not available in this territory: `Bookmaker` / `Bookie` —
reserved in the naming-collapse registry (below) for the
ABSENT odds-setting class; a moniker there would falsely
imply an implemented odds-setting role.
Collision check at issuance: `Actuary`, `Kelly` and the
Table appear nowhere in this roster or in the registration
registry (`Kelly` = 2 incidental text hits in code search,
no identity binding).

**QuarantineBrowserClerk issuance (2026-11-03, registry lane;
D2 entry AppID under the build-start rule — pick B,
Quarantine Browser Clerk, C1·B, Vultr Agent Rush;
provisioning in parallel on the AppID lane, per-entry
pattern).** The actor clerks a browser kept in quarantine —
sessions supervised, filings recorded, nothing passes
unexamined — so its name is the plain-register officer who
supervises a held, controlled session; the queued alt is
the mythic watchman at the boundary, so the family itself
holds the pool's balance (plain lead, mythic alt).

- canonical: `Proctor` (paired display
  `Proctor · QuarantineBrowserClerk`)
- aspect: the Session
- queued alt: `Heimdall` (mark `He1mdall`) — the watchman
  at the boundary bridge; draws only on a registry-lane
  bounce/rename decision
- leet marks: `Pr0ctor` (single substitution, ranks first) >
  `Proc7or` — mark layer only, never identifiers
- slug bounces: ∅ consumed (canonical
  `termux-fleet-quarantinebrowserclerk` probed free by the
  AppID lane); ranked bounce forms if ever needed:
  `pr0ctor` > `proc7or`, returning to the registry lane
- normalized form: QuarantineBrowserClerk — `Termux Fleet
  QuarantineBrowserClerk` /
  `termux-fleet-quarantinebrowserclerk[bot]`; install scope =
  timerloggedout-spec/quarantine-browser-clerk ONLY
  (provisioning record: AppID lane)

Collision check at issuance: `Proctor`, `Heimdall` and the
Session appear nowhere in this roster or in the
registration registry (`Proctor` = 1 generic exam-proctoring
use in a certifications guide in code search, no identity
binding).

**Status (2026-11-03, AppID lane stand-down): provisioning
COUNTERMANDED by owner correction minutes after the confer —
D2's deliverable is a presentation, not a build; the
build-start order was a misread. The create leg was killed
mid-flight: no app exists (slug probe 404 verified) and no
PROCESS.json record lands. This issuance STANDS record-only
as the registry record for the not-yet-provisioned identity
(the `Mimir · UgreenSkills` crossed-signal pattern): if a
real build order ever provisions the pair, it lands with
`Proctor · QuarantineBrowserClerk`. The repo
timerloggedout-spec/quarantine-browser-clerk (id 1445293810)
exists and stays dormant.**

## Identity taxonomy and moniker versioning (adopted, 2026-11-01)

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

**Moniker versioning (ADOPTED 2026-11-01)**

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

Status: ADOPTED by owner decision 2026-11-01, as designed —
threshold U ≥ 100; the registry lane is pre-authorized at
scheme level (no per-graduation owner sign-off). First usage
census and first graduations: registry lane, 2026-11-01.

**Graduations of record**

- `heyVern` → `h3yVern` (Jules) — U = 352 attributed units
  (Search API `involves:google-labs-jules[bot]`,
  timerloggedout-spec/termux-monorepo, counted 2026-11-01).
  v2 derived under the Grimoire table (E3, single
  substitution; no mark was on file). Graduation PR: the PR
  carrying this entry.
- `codeHound` → `c0deHound` (CodeRabbit) — U = 1,663
  attributed units (Search API `involves:coderabbitai[bot]`,
  same repo and date). v2 derived (O0, single substitution).
  Graduation PR: the PR carrying this entry.
- `devinForge` → `d3vinForge` (Devin) — U = 163 attributed
  units (Search API `involves:devin-ai-integration[bot]`,
  same repo and date). v2 derived (E3, single substitution).
  Graduation PR: the PR carrying this entry.

## Naming-collapse registry — listing convention (2026-11-02)

One canonical name per concept on listing surfaces (platform
listings of the versioned Apps and versioned role monikers,
e.g. Polymarket). This is a NAMING convention only: records,
implementations and scoring stay distinct underneath (DoE
scores each class on its own record; the canonical name is an
inclusion prior, nothing more). Alias terms stay valid in
their home records. A crosswalk that loses bindings names its
ker (the set of bindings the listing word does not carry).
Dispositions: **canonical** · **alias → canonical** ·
**distinct-class** (difference named). Evidence of record:
`docs/ops/AGENTIC-GAMBLING-LANE.md` (charter + addenda,
2026-11-01), this file's role vocabulary, and the lane
records cited per row.

### Cluster S — speculation participants (seed cluster)

| Term | Disposition | Canonical / difference · ker |
|---|---|---|
| gambler | **canonical** | Participant class of record (§Speculation: stakes on task performance off the scoring surfaces; wallet · speculation record · standing · cull → pool) |
| speculator | alias → gambler | ker: {`scripts/speculators/` implementation (speculative-decoding strategies) · the optimizations-assurance manager seat} — both stay distinct underneath; the charter seats the implementation in-lane as a bettor class |
| wagerer | alias → gambler | ker ∅ — pure synonym, no fleet binding |
| bettor | alias → gambler | ker: {Perplexity export schema's bettor-side fields (counterparty `bookmaker_id`)} — schema terms stay in the export |
| forecast | **distinct — output class, NOT a participant** | Position content / winprob estimate class (lane feed, PR #3826): names outputs, never participants — collapsing it into a participant listing name breaks record typing. Predictions are issued BY participants and lanes of other classes and scored where those records live (Delphi ledgers score the issuers); there is no forecaster participant class |
| wager | **distinct-class** (object, not a participant) | The stake-object/entry (Perplexity schema: wager as separate entity; bet-ledger schema folds bet/wager/bid into one entry). Names positions, never participants |
| bet | alias → wager | The record shape is `BetEntry` (`MarketGraph.place_bet`); listing names the object `wager` |
| bid | alias → wager | Design-level fold of record (the bid is folded into the bet entry); ker: {no bid/ask price construct exists — Asks absent at every level} |
| bookmaker | **canonical** (class reserved) | Counterparty / odds-setting side. Class ABSENT in the fleet (open build item — no bookmaker role exists yet); the canonical name is reserved for it, and a listing must not imply an implemented odds-setting role. ker: {`bookmaker_id` in the Perplexity export = an EXTERNAL quote-source identifier, not this class} |
| bookie | alias → bookmaker | ker ∅ — colloquial form of the same reserved class |
| 11th man | **distinct-class** | Audience / reserve participant (owner-defined): the non-staking crowd-side seat in the bookie/audience structure. Difference vs gambler: holds no position; may be called in from reserve. Class ABSENT (build item tied to the bookie/audience class); canonical form kept verbatim |

*Speculators* three-way (lane conflict A, dispositioned):
no single name serves all three senses at record level, by
design — the LISTING word is `gambler`; the RECORD
implementation stays `Speculators` under its own key; the
manager SEAT stays `optimizations-assurance`. The collapse
joins only the first layer.

### Cluster M — coordination

| Term | Disposition | Canonical / difference · ker |
|---|---|---|
| manager | **canonical** | Coordination class, tier-1: the lane lead (`<lane>-manager` formation rule; selects teams per charter §Teams) |
| coordinator | **distinct-class** | Tier-2 coordination (of record as sub-coordinator): owns a slice under a manager, reports up one level. Difference vs manager: slice scope, not lane scope |
| orchestrator | alias → manager | ker: {peerGate GHA role label (suite-coordination implementation) · generic orchestration prose} |
| operator | **distinct-class** | The accountable human principal (OPERATOR; the `archW1z` title sits on this role). Difference vs manager: human principal, not an agent lane |
| owner | alias → operator | ker: {property sense — repo/org owner literal (timerloggedout-spec)} |
| lead | alias → manager | ker: {temporary execution-assignment sense (e.g. "execution lead" for a build)} |
| steward | **distinct-class** | Custodian of a record/feed (classifiers steward). Difference vs manager: maintains state; selects nothing, manages no team |

**⚠ BOUNDARY FLAG — ruling of record (2026-10-28):**
lane-coordination identities (manager / sub-coordinator
monikers) are NEVER platform identities and never enter
`config/registration_monikers.json`. The canonical WORDS
above describe classes for listing the versioned Apps and
versioned role monikers; this collapse does NOT make any
coordination identity listable. If coordination identities
are ever to be listed, that needs its own owner ruling —
flagged here, not assumed.

### Cluster R — exploration

| Term | Disposition | Canonical / difference · ker |
|---|---|---|
| scout | **canonical** | Participant class of record (selection surface; competes as a participant: wallet · record · standing; cull applies — charter §Scouts compete) |
| recon | alias → scout | ker: {activity-noun sense (recon = the work, scout = the worker) · the Recon lane identity `Archaeo · Oracle` is a lane moniker, not this class} |
| selector | alias → scout | ker: {DoE fork-selector role binding (ChronoMancer)} |
| observer | **distinct-class** | Passive witness: watches and reports; difference vs scout: no selection mandate, no stake, no standing |
| watcher | alias → observer | ker: {automation sense — a watcher is a monitoring mechanism (hook / scheduled check), not a participant} |

### Cluster J — judgment

| Term | Disposition | Canonical / difference · ker |
|---|---|---|
| reviewer | **canonical** | Artifact-review class of record (fleet App function; peer reviewers) |
| critic | alias → reviewer | ker: {charter role table: critic evaluates/challenges entries — advisory findings, ABSENT as a named lane role; nearest substrate = card role `review`} |
| validator | **distinct-class** | Verifies settlements/records against schema and gates (function of record: validate_v2 · dual-gate). Difference vs reviewer: conformance verdicts on records, not judgment on artifacts |
| judge | **distinct-class** | Renders outcome verdicts (DoE ESTABLISHED gate; challenge/Delphi judging contexts). Difference vs evaluator: decision authority over outcomes and standings |
| evaluator | **distinct-class** | Scores against a rubric, producing explained composites (MoneyBall pattern: axes + intake-fixed weights). Difference vs judge: continuous explained score, not a verdict |
| scorer | alias → evaluator | ker: {surface names stay (moneyball-scorer; per-surface score records)} |
| oracle | alias → evaluator | ker: {Delphi Oracle is a scoring SURFACE, not a participant class · the `Oracle` inside `Archaeo · Oracle` is a moniker component, untouched by this crosswalk} |

### Cluster P — generic participation

| Term | Disposition | Canonical / difference · ker |
|---|---|---|
| participant | **canonical** | Generic class of record (charter + challenge schema; the wallet invariant quantifies over participants) |
| actor | alias → participant | ker: {attribution-layer sense — actor = provenance key (`ActorClass {itself · others · job}` in market.py; attribution actors); records keep `actor`} |
| player | alias → participant | ker: {MoneyBall sports-metaphor prose sense} |

### Cluster B — construction

| Term | Disposition | Canonical / difference · ker |
|---|---|---|
| builder | **canonical** | Class of record (fleet builder persona; build lanes) |
| implementer | alias → builder | ker: {SSOT row label wording ("Jules (implementation)")} |

Scope note: fleet App function names (Collector · Publisher ·
Reviewer · Gate · Lifecycle · Swarm · CrossReference ·
RepoStory · DoE) are listing items themselves (versioned
Apps), not cluster terms; where a function word also appears
above (reviewer), the cluster governs the generic class and
the App keeps its paired moniker.

## Naming rule — Tribute scope + desk rename debt (2026-11-03)

**Owner rule (2026-11-03): "Tribute is foreign repos only."**
The Tribute name/program covers contributions to FOREIGN
repositories exclusively (the Z3π0 HELP-WANTED outreach
campaign). Every other `tribute-*` name bound to an internal
surface is naming debt. Census of record: 208 `tribute` paths
on master (git tree, 2026-11-03, this lane) — the campaign's
own machinery (`.agents/skills/tribute-lane`, the
`tribute-{execute,scout,claim,followup,participation,…}`
workflows + `scripts/ci/tribute_*.py`, `docs/ops/TRIBUTE-*.md`
lane docs, `docs/ops/generated/tribute-*` evidence/status,
`tribute-*` tests) STANDS under the rule; only the internal
desk dashboard's names are debt:

| Debt (current) | Ruled target |
|---|---|
| `apps/tribute-dashboard/` (whole tree) | `apps/desk-dashboard/` |
| `.github/workflows/tribute-dashboard-deploy.yml` | `.github/workflows/desk-dashboard-deploy.yml` |
| `.github/workflows/tribute-dashboard-preview.yml` | `.github/workflows/desk-dashboard-preview.yml` |
| `.github/workflows/tribute-vercel-prod.yml` (serves the same surface's Vercel prod) | `.github/workflows/desk-vercel-prod.yml` |
| served URL root `/tribute/` + assembly dir `_tribute/` | `/desk/` + `_desk/` |
| `docs/ops/TRIBUTE-DASHBOARD.md` | `docs/ops/DESK-DASHBOARD.md` |
| `scripts/ci/verify_tribute_dashboard.py` | `scripts/ci/verify_desk_dashboard.py` |
| Vercel projects `tribute-oversight` · `tribute-dash` | `desk-*` family (provisioning names; same pass) |

Already correct (no debt): the surface's page `desk.html` and
feed `data/desk-feed.json` (+ its byte-identical mirror) —
they move WITH the tree. Execution: Web Dev lane, POST-FREEZE
pass only (D1 freeze 2026-11-04 23:59 PT; the deploy pipeline
was repaired 2026-11-03 — ∅ rename churn inside the freeze
window). Mechanism per archive law: in-tree move + inbound
reference sweep; the `/tribute/` → `/desk/` redirect-stub
question is an execution detail settled at the pass, not
here.

## Brand issuance — Stagefoil, the desk-flow template (2026-11-04)

**Commission (owner via main, 2026-11-04):** an ownable
brand for the concept carried internally as "AutoDesk" —
the Desk as an interactive-flow + routing template,
clerk-operated (stage-0 decision object · typed stage
states · routing guard · intake quarantine · receipt per
transition · approval gates), born from D2 candidate B's
learnings applied to the fleet's own desk inputs.
"AutoDesk" collides with Autodesk: internal label only,
never publishable.

**ISSUED: `Stagefoil`** — coined compound: stage (the
typed stage flow) + counterfoil (the retained stub that
is the receipt of record for each entry). One word
carries the concept's spine: every stage transition
tears off its counterfoil. Pronounced STAYJ-foil; plain
ASCII; slug form `stagefoil`.

Family (minimal, brand layer only — NOT an App moniker,
∅ SSOT App-table row, ∅ actor/slug provisioning):

- Descriptor of record: "the clerk-operated desk-flow
  template" (descriptive prose, never part of the mark).
- Standing vocabulary under the brand: a **foil** = the
  receipt issued per transition; a **stagefoil instance**
  = one desk running the template.
- Reserved normalized form: `Stagefoil Desk` for a
  specific desk instance's display name, if one is ever
  published. Leet/mark forms: none issued (a brand mark
  layer is a future confer if a published surface needs
  one).

Collision evidence (this lane, firsthand, 2026-11-04):

- In-fleet ∅: SSOT + Profile Registry + monorepo code
  search + `config/registration_monikers.json` all 0.
- Live-mark web check ∅: no product, company, or filing
  under the exact string in/near software; adjacent marks
  noted + distinguished — Stage-Gate® (Stage-Gate Inc.;
  hyphenated two-word process mark ≠ this one-word coined
  compound) · StageFlow (sales CRM) · Stagehand
  (Browserbase browser-agent SDK — adjacent agent space,
  distinct string + field).
- Dead candidates, same pass (each killed by a live mark
  in/near software): Counterfoil (RevOps platform) ·
  Claviger (Claviger.AI agent governance) · Promptbook
  (agent platform) · Gatebook (visitor mgmt) · Stubbook
  (invoicing) · Passus (listed IT co) · Chirograph
  (verification/workflow sw) · Sigillum (vaults + agent
  e-signature) · Cartulary (apps + PyPI validator) ·
  Muniment (compliance + AI archive products) ·
  Tablinum (workflow + DB products) · Stagia (EduLab
  listed-co platform + internship sw) · Promptuary
  (Obsidian AI plugin + prompt products) · Transitus
  (stewardship platform + IT cos) · Recepta (AI
  receptionist + receipts platform) · Cuebook (multiple
  live products) · Notula (editors + transcription +
  health) · Schedula (Schedula™ healthcare) · Gradia
  (four+ software cos) · Gatewarden/Wicketgate (gate
  space crowded: Wicket ×3 + Warden agent gateway).
  Acquittance cleared the collision pass but was NOT
  issued: payment-discharge semantics only, weak fit.

Use rule: records carrying the concept swap the label
"AutoDesk" → **Stagefoil** (the Desk upgrade record + D2
continuation plan first, per main); "AutoDesk" survives
only as the attributed internal predecessor label in
this issuance record. ∅ change to any desk
implementation, routing, or record underneath — naming
layer only (collapse-registry C3 discipline).

## Unit-name issuance — booktally, the MoneyBall unit (2026-11-04)

**Commission (owner via main, 2026-11-04; collision
flagged at the Web3 seat):** the MoneyBall wallet unit
string `soft_quota_token (observational)` reads as
fleet-quota-bearing — the legacy string carries three
quota-plane signals at once (soft ≈ soft cap · quota =
the PAT-governor/provider-quota/QUE-guard plane's own
name · token = API-token vocabulary), and the owner
misread the served wallets page on exactly that point.
A public-facing replacement unit name, coined + checked
against BOTH the quota plane and live marks.

**ISSUED: `booktally`** (plural **booktallies**) —
coined compound: Book (MoneyBall's Book, the ledger of
record for positions + settlements) + tally (a count
kept of record; the tally stick was the original
receipt-counter). Machine unit string `booktally`;
display form `booktally (observational)`, mirroring the
legacy display shape so the transition is a unit-string
swap only. Definition of record: the MoneyBall
paper/test accounting unit — observational only; not
money, not a chain asset, not fleet quota, not
redeemable, not transferable off the Book. "Book" here
names the record, never a bookmaker: the collapse
registry's `bookmaker` stays a reserved absent class
and this name claims no odds-setting role.

Collision evidence (this lane, firsthand, 2026-11-04):

- Quota plane ∅: no shared stem with the plane's live
  vocabulary {quota · token · credit · call · rate ·
  slice · share · cap}; both offending stems dropped.
- In-fleet ∅: SSOT + Profile Registry + monorepo code
  search + moneyball-repo code search +
  `config/registration_monikers.json` all 0.
- Live-mark web check ∅ for the exact string;
  adjacencies noted + distinguished — Tally (Tally
  Solutions accounting software; the bare word stays
  theirs — the issued form is the one-word compound
  used as a unit label inside MoneyBall, not a product
  name) · Tally Book / TruckTally (accounting apps,
  reversed/different compounds).
- Dead + rejected candidates, same pass: Fortally
  (near-homophone of Foretally, a live forecasting
  product in the exact field) · PaperPoints (live
  paper-wagering points, PaperWagers' Wager Wallet) ·
  Jeton/Jetons (global payments + e-wallet brand) ·
  Speclet (established software term: .NET speclets,
  EQC speclets) · Tallion (accounting cluster:
  Tabellion sw · Tallie · Tillion) · Callchit (no mark
  found; REJECTED on the quota-plane check — "call" is
  provider/API-call vocabulary) · Specscrip (no mark
  found; REJECTED on semantics — scrip denotes
  substitute currency/redeemable vouchers, the very
  confusion being removed). Bookchit (book + chit, the
  paper slip of record) cleared every check and stands
  as the considered runner-up, not issued: "tally"
  parses instantly where "chit" does not.

Disposition (of record, undisturbed): the legacy string
stands verbatim inside the hash-chained ledger events,
WALLETS.json, and the v1 wallets-feed (705 rows) — ∅
silent swap, ∅ history rewrite. On this issuance the
custodians (MoneyBall plane + Speculators-build, via
the Web3 seat's pre-serve gate) run a VERSIONED
transition: successor feed/record versions carry
`booktally (observational)` with a transition note
naming the legacy unit; same-ledger continuation keeps
the legacy unit until that transition lands (the fold
depends on it). New public surfaces use booktally from
issuance; no new surface extends the legacy string.

## MoneyBall vocabulary issuance — full naming (2026-11-04)

**Commission (owner via Web3 seat 779d33ad → naming seat
acde0e2c, 2026-11-04):** FULL naming of the MoneyBall/Web3
vocabulary — every category, not the priming labels the
commission arrived under (Bookie · Ledger · Wager ·
Wallet). Machinery: this Registry flow (coinage →
collision check → issuance → record) + Linguist Grimoire
round-trip ∀ candidates. Trigger: the `soft_quota_token`
collision with the fleet quota plane; the replacement
unit name = first deliverable. Rails: legacy strings are
of record until an issued replacement lands by versioned
transition through the custodians (MoneyBall feed ·
Speculators WALLETS/ledger) via the Web3 gate; ∅
unilateral renames, ∅ ledger/history rewrites; paper/test
only — real-money is a separate owner gate, outside this
naming scope.

**First deliverable — ADOPTED, not re-coined:** the unit
issuance above (`booktally`, PR #4825 merged
`6a366cb61300`) is this commission's unit deliverable.
Everything below completes the remaining categories
against it. Dispositions: **ISSUED** (canonical in
MoneyBall vocabulary) · **RESERVED** · **NOT ISSUED**
(excluded or replaced, reason named). Confirming a term
of record as ISSUED means it passed the same screens a
coinage faces; ∅ term below was renamed for novelty —
a gratuitous rename would mint a parallel vocabulary,
the defect class this flow exists to prevent.

### ① Actors

| Term | Disposition | Definition / ker |
|---|---|---|
| house | **ISSUED** (role word) | The parimutuel operator side: the MoneyBall operating seat + its custodians. Takes ∅ position, sets ∅ odds, rake ∅; never a counterparty in any record. Generic role word, not a brand |
| speculator | **ISSUED** (record layer) | Record class of record (wallet class `speculator`; the Speculators implementation, `scripts/speculators/`). The collapse registry's listing crosswalk speculator → gambler stands at the listing layer only, ker as recorded there; classes never merge at record level (moneyball DESIGN §4.1) |
| gambler | **ISSUED** | Canonical participant class of record (charter; collapse registry Cluster S) |
| participant | **ISSUED** | Canonical generic (collapse registry Cluster P; the wallet invariant quantifies over participants) |
| card-holder | **NOT ISSUED → pool member** | `cardholder` is payment-card vocabulary (real-money plane, screen ⑧) and the object is wrong: a trading card is a projection, held by no one — what is held is shares in a card pool. **ISSUED replacement: `pool member`** — the DESIGN §3.1 word of record (members hold shares; 45 in-fleet hits). Ker: DESIGN §10's eligibility prose sense maps to pool member. Coinages considered: `cardhand` DEAD on sense (reads as a playing-card hand across the web/patent corpus) · `cardkeeper` cleared marks but has ∅ record basis — the record's own word wins |
| team | **ISSUED** | DESIGN §11②: a team is requestable for a % fee per agent contract (`team contract` = that form) |
| requester | **ISSUED** | DESIGN §11②④: the wallet that pays the team fee / places a discounted custom request. Distinct from team (the requested side) and pool member (the share-holding side) |
| bookie / bookmaker | **RESERVED** | Reaffirmed from the collapse registry: canonical `bookmaker`, class ABSENT (∅ odds-setting role exists; v1 pricing is parimutuel). ∅ issuance; a listing surface must not imply an implemented bookie |

### ② Records — the ledger split

Three distinct records, three issued names. The Book is
not a ledger; the two ledgers are not each other:

| Term | Disposition | Of record |
|---|---|---|
| the Book | **ISSUED** | `ops/agentic-gambling/book/challenges-book.json` — subjects + expectation records; rendered by book-feed |
| book-ledger | **ISSUED** (full form) | `ops/agentic-gambling/book/ledger.jsonl` — positions + settlements, low-frequency audited; its event field is `event` |
| wallet-ledger | **ISSUED** (full form) | `ops/agentic-gambling/site/wallet-ledger.jsonl` — high-frequency balance movements; its event field is `type` |
| ledger (bare) | **NOT ISSUED** | Excluded form: every MoneyBall use carries its prefix. The unqualified word is what let three field vocabularies (`event` / `event_type` / `type`) collide in the WALLET-LEDGER conformance arc — the split, with each ledger's field vocabulary named beside it, is the naming-layer fix |
| expectation record | **ISSUED** | B1: exactly one per subject; carries the estimate layer |
| record of record | **ISSUED** | B3 anchor (machine form `record_of_record`); settlement cites it, never substitutes it |
| receipt | **ISSUED** | Hash-chained proof per event (wallet receipt `wr_<seq>`). Ker vs Stagefoil's `foil`: same function in a different system; the words stay system-bound |

Ledger-pair coinages considered + killed: `tallybook`
(live exact-string marks — TallyBook AI drilling
assistant at tallybook.io · Tallybook expense app ·
TallyBook digital-ledger app) · `scorebook` (ScoreBook /
Scorebook+ scoring apps) · one-words `bookledger` /
`walletledger` (in-fleet ∅, rejected on machinery: a
machine string ≠ the landed filename would mint a third
vocabulary — the defect being fixed).

### ③ Actions

| Term | Disposition | Definition / ker |
|---|---|---|
| wager | **ISSUED** (distinct object) | The stake-object/entry, never a participant (collapse registry; bet/bid → wager at listing). Grimoire-native: its leet form `w4g3r` is already a CedrLang CANONICAL_TOKEN in the same sense |
| ante | **ISSUED** | DESIGN §11①: the required per-task wager form — minimum ante per task, scaled by the task's recorded complexity (QUE tier of record, never self-assessed) |
| stake | **ISSUED** | The amount placed on a position (noun); to place it (verb) |
| position | **ISSUED** | The lifecycle object: open (basis cited, B2) → escrow → lock → settlement → score → payout; ids `POS-*` |
| escrow | **ISSUED** | The in-wallet `available → escrow` move at position open (`stake_escrowed`); void pre-resolution ⇒ full `stake_released` |
| allocation | **ISSUED** (MoneyBall-bound) | DESIGN §11⑤: allocation algorithms are agent property (pickable, changeable, sellable, royalty-bearing). Ker: the fleet's `allocations.json` (opportunity/provider plane) is a different record — context-bound, ∅ cross-reading |

### ④ Containers

| Term | Disposition | Definition / ker |
|---|---|---|
| wallet | **ISSUED** | Paper/test only; `wallet_id` opaque + chain-agnostic (`paper:<hash>`); balance is a derived fold, never a stored field |
| pool | **ISSUED** | A pool wallet bound to a class or card. Pool classes of record = the 16 census classes {arm · desk-lane · devwork · doe · explorer · loop · moniker · other · profile · provider · que-lane · recon · researcher · role · speculator · version} (pools-feed `class_x_depth`; 693 pools). Absent classes `jit-version` · `scout-roster` stay NOT_ESTABLISHED — ∅ rows dressed as existence |
| pooled-buckets | **ISSUED** | `pool:other:pooled-buckets` — the cull-waterfall destination of record (promotions / incentives / bonuses) |

### ⑤ Unit ∧ amounts

- **Unit: `booktally`** (plural booktallies; display
  `booktally (observational)`) — issued above, PR #4825.
  Legacy `soft_quota_token` stands verbatim in the
  hash-chained events, WALLETS.json and the v1 feed until
  the custodian versioned transition lands.
- **balance — ISSUED:** one wallet's fold of the
  wallet-ledger, denominated in booktallies.
- **pool total — ISSUED:** Σ stakes in one subject pool
  (DESIGN `total_pool`). Displayed `pool share` =
  pool_outcome / pool_total — a stake distribution,
  never "odds" or "probability" (screen ⑧).
- **total supply — ISSUED:** Σ issuance across the
  wallet-ledger; ∅ burn (culling ≠ burn).
- **⚖️ Totals rule:** a bare `total` is **NOT ISSUED** —
  every total on any surface names its fold set
  {per-wallet balance · per-pool pool total · total
  supply}. An unlabelled total is the amounts-plane twin
  of the bare-ledger defect.
- **genesis grant — ISSUED** (`wallet_provisioned`
  delta; of record: EQUAL ×12 @ 1,000). **faucet —
  ISSUED** (`faucet_issued`); cadence/cap stay
  NOT_ESTABLISHED — the name is issued, the values are
  unruled and ∅ name here invents one.

### ⑥ Resolution

| Term | Disposition | Definition / ker |
|---|---|---|
| settlement | **ISSUED** | Only from the named record of record (B3): `settlement_proposed` → `settlement_final` |
| payout | **ISSUED** | Parimutuel per DESIGN §4.3 (`payout_credited`); rake ∅; one-sided pool ⇒ stake refunded only |
| score | **ISSUED** | Brier / hit-rate layer (DESIGN §6.3); honest states NOT_SCORED · UNRANKED are part of the name's use, never dressed as numbers. Listing ker scorer → evaluator stands |
| cull waterfall | **ISSUED** | Cull ⇒ balance ⇒ pooled-buckets as one `cull_transferred` pair; value never destroyed; residual stream NOT folded |
| sweep | **ISSUED** | 6REA7 paper analogue: `sweep_transferred` pair, fold-derived triggers; threshold values NOT_ESTABLISHED (engine fires ∅ unruled class) |
| residuals / royalties | **ISSUED** (pair) | DESIGN §11⑤ + Addendum 2: the residual/royalty stream rides back to the author's wallet as its own events; never folded into cull or sweep |

### ⑦ Surface labels (moneyball repo)

Issued display set — files/pages change only by a
custodian pass via the Web3 gate, ∅ unilateral rename:

| Issued label | Surface | Current of record |
|---|---|---|
| Slate | `/` | index (subjects + countdowns); H1 stays the brand `MoneyBall` |
| Book | `/book` | the Book's public render — the canonical page of record, linked/vendored per DESIGN §5.1 |
| Cards | `/cards` | `Agent Trading Cards` |
| Pools | `/pools` | `Card Pools` |
| Wallets | `/wallets` | `Wallets` |
| Settlement | `/settlement` | `Settlement` (Settlement Replay) |

### ⑧ Exclusion screen — never issued in this vocabulary

- **Quota-plane terms:** quota · soft cap · token ·
  credit · call · rate · slice · cap · governor — the
  PAT-governor / provider-quota / QUE-guard plane owns
  these; the `booktally` stem check is the worked case.
- **Odds/probability-shaped display names:** odds ·
  probability · implied · chance — estimates live in
  expectation records and forecast outputs (an output
  class), never as display names; `pool share` is the
  only issued share-display.
- **Real-money terms:** cash · dollar/USD · deposit ·
  purchase · cash-out · fiat · cardholder — G3 is a
  separate owner gate; ∅ name in this issuance
  pre-decides it.
- **Live external marks as vocabulary:** Polymarket ·
  Kalshi · Manifold · PredictIt · DraftKings · FanDuel
  — comparative prose about them is not vocabulary;
  none is issued as a MoneyBall term.
- **Bare forms:** `ledger` unqualified · `total`
  unqualified · `bookie` presented as a live role.

### Collision evidence (this seat, firsthand, 2026-11-04)

- **Quota plane ∅:** no issued term shares a stem with
  the plane's live vocabulary {quota · token · credit ·
  call · rate · slice · share · cap} — `share` survives
  only inside the issued compound `pool share`, defined
  as a stake distribution (DESIGN §1.3), never a quota
  slice; the unit's offending stems were already dropped
  by the `booktally` issuance.
- **In-fleet:** SSOT + `config/registration_monikers.json`
  + monorepo/moneyball code search — issued generics are
  hits of record (confirmation, not collision: e.g.
  `pool member` 45 hits, the record's own usage);
  checked coinages returned `bookledger` 0 ·
  `walletledger` 0 · `cardholder` 0 · `tallybook` 0 ·
  `scorebook` 2 (the scoring-surface sense, distinguished
  in the kill note above).
- **Live-mark web check:** `booktally` ∅ exact-string
  product/company (independent recheck concurs with
  PR #4825; adjacencies = two-word "Tally Book"
  notebooks + the Tally Book accounting app — the bare
  and reversed forms stay theirs). `tallybook` +
  `scorebook` crowded with exact live apps ⇒ both DEAD
  as ledger coinages. `cardhand` DEAD on sense
  (playing-card-hand corpus). `cardkeeper` cleared marks
  but lost to the record's own `pool member`.

### Grimoire round-trip evidence (∀ issued candidates)

Method: Linguist `phase_codec` LEET_MAP {a→4 · e→3 ·
i→1 · o→0 · s→5 · t→7} — full-substitution form, then
inverse decode must return the canonical exactly, the
leet form must collide with ∅ other issued form and ∅
CedrLang CANONICAL_TOKEN of a different sense, and the
candidate must be plain ASCII (the `1337_inQuiπy…`
glyph-load defect class is the standing counterexample).
**Result: ∀ issued tokens PASS.** Distinctive forms:
booktally `b00k74lly` · book-ledger `b00k-l3dg3r` ·
wallet-ledger `w4ll37-l3dg3r` · pool member `p00l
m3mb3r` · pooled-buckets `p00l3d-buck375` · ante `4n73`
· escrow `35cr0w` · cull waterfall `cull w473rf4ll`.
Two notes: `wager` is Grimoire-native — `w4g3r` is
already a CANONICAL_TOKEN in the same sense (the one
overlap in the pass, and it is identity, not collision);
`cull` is codec-invariant (∅ eligible letters — the
canonical form stays plain, as the codec's MUTABLE set
prescribes).

### Disposition

Naming layer only (collapse-registry C3 discipline): ∅
change to any record, implementation, scoring, or ledger
underneath. Legacy strings stand as written; the issued
names land on surfaces by versioned custodian transition
via the Web3 seat's pre-serve gate. Returned to the Web3
seat (779d33ad) + main (9a88e77a) at issuance.


## Rules

1. Automated comments: **display** moniker in backticks; **ping** only the live trigger (`@jules`, `@gemini-cli`, `@deepseek` / `@deepseek-ci`).
2. Workflows matching a live trigger **must** also accept the display moniker case-insensitively where registered above.
3. Never put secrets or Class 3/4 material in moniker docs.
4. If a moniker string is later registered as a GH username we do not control, keep it non-@ only.
5. **Agent2Agent comms ∀ chats = CAVEMAN NOTATION MICRO DENSE** (owner order 2026-11-04; supersedes relay-only scope): ids ∧ outcomes ∧ symbols first, fewest words; sources compress too — a relay carries the dense form, ¬ the source's prose; prose only where precision ∨ safety requires; compliance = silence elsewhere (∅ ACK).

## High-performance intent

Monikers reduce ambiguous role ownership under load without notifying strangers.
