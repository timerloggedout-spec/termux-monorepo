# OSINT DISPATCH TEMPLATE — intake → atoms → sources → receipts → verdicts

`[MUSEai]@{role:{lane-moniker}}` · Tasking: {owner/manager order,
source chat or issue #, date} · Sibling: `SWARM-RESEARCH-TEMPLATE.md`
(defects/fixes); this template covers **observation dispatches** —
questions about the public record (participants · judges · projects ·
fields), answered with receipts or stamped NOT_ESTABLISHED.

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

## 2. Atoms → source classes

One atom = one source-class leg. Decompose the question, then map
each atom to the FIRST class that can answer it as observation:

| Source class | Answers | Identity strength |
|---|---|---|
| **Event platforms** (lablab · Devpost · ETHGlobal · DoraHacks) | editions · tiers · placements · judge pools · project/team pages | venue-native keys = strongest |
| **Code hosts** (GitHub public) | repos behind project claims · self-published profile links | strong when self-linked |
| **Social** (public posts/profiles) | announcements · panel names in posts · engagement | source-with-receipt; weaker than the platform page |
| **Web archives** (Wayback CDX) | rotated/removed pages · historical editions | lead-grade; verify (injected banners, incomplete captures) |
| **Search / username** (search engines · username checks) | discovery of candidate surfaces | lead-grade only, never a row |

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

Every row: `{source_url · captured_at · collector}`; every fetched
page: `{url · http · bytes · sha256}` in the snapshot's source
list (the podium standard, generalized). Records are versioned
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
