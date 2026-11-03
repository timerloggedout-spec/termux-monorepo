# OSINT DISPATCH TEMPLATE — intake → atoms → sources → receipts → verdicts

`[MUSEai]@{role:{lane-moniker}}` · Tasking: {owner/manager order,
source chat or issue #, date} · Sibling: `SWARM-RESEARCH-TEMPLATE.md`
(defects/fixes); this template covers **observation dispatches** —
questions about the public record (participants · judges · projects ·
fields), answered with receipts or stamped NOT_ESTABLISHED.

**Amendment 1 (2026-11-03):** operator requirements from the
Recruitment/OSINT lane's live practice (D2 harvest PR #4484 ·
identity-gap PR #4497; ground-truth files under
`ops/challenge-recruitment/`) are folded into §§1–4 below —
where the operator's field record and this draft differed, the
field record governed (notably §2's yield ranking: judge names
lived on sponsor recaps, not event pages).

**Job:** given an OSINT question, return a **receipted record**:
every claim carries `{source · captured_at · collector}`, every gap
is stamped, every material finding is read both ways before it
stamps. Not a dossier of impressions — a record a second lane can
re-verify from the receipts alone.

**Research basis (2026-11-03):** fleet practice (PODIUM-DATASET.md
receipts/conflict discipline · participant-store rules) + the
awesome-osint corpus (jivoi/awesome-osint and adjacent lists) as the
tooling candidate pool + SOFA (queried at build time: OSINT
methodology = total miss, ∅ posts — this template therefore rests
on the fleet + web legs, and says so).

---

## Preflight (hard gates, before any collection)

1. **Charter check** — every source class the dispatch will touch
   has a crawl charter on file (public-only · stop on block ·
   never route around). No charter ⇒ charter first, collection
   second. A block mid-run ends that source's leg; it is recorded,
   not circumvented.
2. **Scope class** — the dispatch names its class:
   `participant/judge observation` (rails §6 apply in full) ·
   `event/field record` · `tooling/market`. Class is set at
   intake and cannot widen mid-run.
3. **Standing authority** — dispatches fitting this template fire
   on the lane's standing authority (owner order 2026-11-03: the
   system implements itself); anything outside the rails is a
   new ask, not a template run.

## 1. Intake

| Field | Content |
|---|---|
| Question | {the exact question, verbatim where possible} |
| Subject | {event · edition · project · person-as-published} |
| Scope class | {from preflight §2} |
| Consumer | {who reads the record + what decision it feeds} |
| Already known | {pinned dataset versions · prior records + their stamps — never re-derive a stamped gap} |
| Disambiguation | {venue · edition · dates} pinned BEFORE hunting — corpora mix near-identical editions (RAISE 2025 vs Agent Rush 2026); a hit from the wrong edition is a defect, not a lead |

**Entity/event field shapes (operator-proven, per record):**

- `event{slug, platform, url, window{kickoff_utc, deadline_local+tz}, field_size{participants_count, projects_count, as_of}}` — **three denominators, never conflated: joined / submitted-projects / tracked.**
- `entity{key, kind: participant|judge|team|project, persona?, org?, role_evidence}` — roles are evidence-backed, never assumed from a section heading.
- `project{repo_url, owner_login, created_at, pushed_at, stars, forks, topics[], readme_title, challenge_guess{value, confidence, basis}}`
- `judge{name, title, org, role: judge|mentor|speaker|POOL_UNRESOLVED, track?}` — event pages merge "Speakers, Mentors & Judges" with no per-person tags; an unsplittable pool stamps **POOL_UNRESOLVED**, never a forced split.
- `linkage{from_entity, to_entity, kind: same_team|same_owner|sponsor_recurrence|pool_recurrence, receipts[]}` — owner matches are **GitHub-login equality only**, never name similarity (an automated exact-owner-match pass runs across harvested sets).
- `gap{id, claim_missing, resolution_path, resolution_window}` — gaps are first-class records with a way out and a when, not footnotes.
- `dual_reading{threat, opportunity}` per screened entity (LENS doctrine) · `moneyball_axes` hooks (v2 keys, validator-bound).

## 2. Atoms → source classes

One atom = one source-class leg. Decompose the question, then map
each atom to the FIRST class that can answer it as observation:

Ranked by measured yield (operator record, 2026-11-03) —
work down the ranking; a lower class never overrules a higher
one's receipt:

| # | Source class | Answers | Identity strength |
|---|---|---|---|
| ① | **Event platform pages, full read** (lablab · Devpost · ETHGlobal · DoraHacks) | counters · criteria · tracks · pool sections · project/team pages | venue-native keys = strongest |
| ② | **Code hosts** (GitHub REST: /search/repositories · /users · /repos, via the PAT helper — API-only; browser GitHub search is RETIRED) | repos behind project claims · self-published profile links | strong when self-linked |
| ③ | **Partner/sponsor recaps + blogs** | **judge names + podiums lived HERE, not on event pages** (qubic.org pattern) | source-with-receipt |
| ④ | **Team/org own sites** | linkage chains (kairos-tek pattern) | source-with-receipt |
| ⑤ | **Web search** | discovery only — **every hit re-verified at source** before it is anything more than a signal | lead-grade only |
| ⑥ | **Third-party listings** (devhunt/competehub class) | corroboration only | never a sole source |
| — | **Web archives** (Wayback CDX) | rotated/removed pages · historical editions | lead-grade; verify (injected banners, incomplete captures) |

Every surface records `source_availability ∈ {PUBLIC,
COUNT_ONLY, JOIN_GATED, UNPUBLISHED, LOGIN_WALLED}` — absence
then reads as a ceiling, not as zero effort.

## 3. Tooling registry (per source class)

Fleet stack is bound first; the awesome-osint corpus is the
candidate pool for additions, and the scraping lane's find-tools
slate (login-capable free scraping tools goal) is **pulled by
reference, never duplicated here**.

| Class | Fleet tool of record | Chartered additions |
|---|---|---|
| Event platforms | `scripts/podium/podium_crawl.py` (stdlib, receipted) + the podium-crawl workflow | per-venue crawler legs as venues charter (Devpost first per the podium research record) |
| Code hosts | GitHub API via the PAT helper (public data) | code-search surfaces from awesome-osint §Code Search |
| Social | platform connectors (read legs) | — |
| Web archives | Wayback CDX + snapshot fetch | archive-diff tooling only with the false-mismatch caveat stamped |
| Search / username | browser search | username-check tools (sherlock-class; awesome-osint §Username Check) — **lead generation only**, output never enters a record unconfirmed by a class-1/2 source |
| Extraction | trafilatura-class for page bodies | per the podium tools ranking |
| **Fetcher router** | **per-domain method binding** — plain HTTP (curl) hits Cloudflare 403 on lablab.ai; the working route there is the text-extraction fetch (browser.open class). The router, not the operator's memory, carries which fetcher serves which domain | bindings added on first proven failure |
| **Payload-embedded counters** | named extraction pattern: platform pages may be JS/client-rendered with counters in the embedded page payload (e.g. `initialParticipants`) invisible to naive scrapers — record WHICH method extracted each counter | — |

A tool joins the registry when a dispatch needed it, its charter
passed, and its output carried receipts. Novelty is not a criterion;
fit is (public · no card · Actions-runnable · receipted).

## 4. Skills / competency binding

An OSINT run must be able to do all of these; the binding names
where the fleet already has each — a dispatch that cannot bind a
competency does not fire until it can:

| Competency | Fleet home |
|---|---|
| Crawl + receipt (bytes · sha256 · source stamp) | scraping-tools lane · podium pipeline |
| Ingest discipline (append-only · conflicts kept, never merged) | podium ingest + participant store |
| Identity discipline (venue keys > self-links > leads; collisions named) | podium research record (identity ceiling) |
| Archive verification (capture completeness, banner artifacts) | this template §2 + research record (d) |
| Dual-valence reading (§5) | MoneyBall plane practice |
| Statistical honesty (denominators · MNAR · exact methods at small n) | podium test plan + research record (c) |
| Template research method (for new source classes) | SWARM-RESEARCH-TEMPLATE.md |
| Fetcher router (§3) | scraping-tools lane |
| Receipt validator — unreceipted claims rejected at write time | ingest tooling |
| Gap registrar — gaps as first-class records with windows (§1) | Recruitment lane practice |
| Denominator guard — the 3-count separation (§1) | Recruitment lane practice |
| Coordinator hand-off — single-writer: packets OUT, never direct writes into another lane's store | fleet coordination protocol |

## 5. Dual-valence readings (mandatory)

Every material finding is stamped with BOTH readings before it
enters a record. Examples of record:

- A judge's public praise of a project → engagement signal ∧
  partiality risk for that pairing.
- A team's prior podium → capability signal ∧ field-compression
  (the same names recur; the denominator is smaller than it looks).
- A missing panel → venue opacity ∧ **not** evidence about the
  judges themselves. Absence stamps the venue, never the person.

A finding whose second reading was not considered is a draft,
not a record row.

## 6. Scope rails (participant/judge class — hard)

- **Observation only.** Public sources; no accounts created for
  collection, no login-gated participant data in v1 legs, no
  contact, no engagement of any kind from a collection identity.
- **Our own projects are never participants** (no-stacking rule);
  our monikers appear only as hosts/authors where the venue
  itself prints them.
- **Gaps are NOT_ESTABLISHED, never filled** — by inference, by
  cross-venue name matching, or by archive leads. A lead is a
  pointer to a future observation, filed as a lead.
- **Persons are stamped as published** — names/roles exactly as
  the venue prints them; no enrichment from breach data, email
  hunting, or people-search aggregators (those awesome-osint
  sections are out of scope for this fleet, permanently).
- **Stop on block.** Rate limits, robots walls, and 403s end the
  leg with the block stamped. Never route around.

## 7. Receipts standard

Every claim: **`{source_url, captured_at_utc, method,
quote_or_locator}`** (operator shape) — method names the actual
extraction (HTTP fetch · text-extraction fetch · payload-embedded
· API), because the method is part of the evidence. Every fetched
page also carries `{url · http · bytes · sha256}` in the
snapshot's source list (the podium standard, generalized).
Counters carry `as_of` + a drift class — same-day reads of 2302
vs 2308 are BOTH preserved, never averaged. Search hits enter
labelled **SIGNAL**, never as verified facts. **Commit emails
are NEVER recorded.** Public sources only. Records are versioned
and pinned by consumers (`<date>.v<n>` + sha256); a re-run appends
a version, never edits one. Conflicts between sources are kept
as conflicts with both receipts — display value = first seen,
resolution only by a receipted act.

## 8. Verdicts + filing

The record closes with, per atom: **RESOLVED** (receipts) ·
**PARTIAL** (what resolved, what did not, why) · **NOT_ESTABLISHED**
(the ceiling, named: never-published · blocked · no-surface).
Gaps and defects discovered en route file as capture issues the
same turn (the capture rule). Consumers pin the record's version;
a verdict that later evidence overturns is corrected in the open,
in a new version, with the superseded stamp kept.

---

*First live exercise: `docs/ops/OSINT-DISPATCH-EXAMPLE-D2.md` —
today's D2 identity-gap + podium harvest re-run through this
template (2026-11-03).*
