# Podium dataset & test systems — swarm research record

`[MUSEai]@{role:{optimizations-assurance}}` · Tasking: owner order
2026-11-03 09:19 PT via main ("Research everything necessary with
what we have — identity gaps && expand + improve — find tools") ·
Template: `docs/ops/SWARM-RESEARCH-TEMPLATE.md` · Companion legs:
the fleet record (PODIUM-DATASET.md · MONEYBALL-PODIUM-TEST-PLAN.md ·
PR #4513 system review) and the DoE concept review (parallel;
findings cross-fed).

**Preflight:** SOFA read+write legs LIVE (agent Inquest, 10 scopes,
verified at run time). Fleet record beats SOFA on conflict (template
rule); web-derived items are labelled unverified until a crawl
charter verifies them.

## 0. State of record (fleet evidence, firsthand)

- Dataset v1 pinned: 55 entities (4 editions · 9 tiers · 6 judges ·
  6 judge-persons · 30 projects), sha256 537981b8…; the analysis cut
  is n = 11 placed projects over ~4 events (test-plan pin, PR #4491).
- A v2 snapshot (89 entries) exists inside PR #4501 **uncited** — it
  needs its own pin layer before any consumer may cite it (gap G1).
- Tests: 6 designed, review closed, **0 cleared to run** — held for
  the OSINT/pipeline pass. Test ③ (judge panel) is descoped to a
  descriptive census: per-track judges ∅, judge↔outcome linkage ∅.
- The dataset today supports **composition shares only** — field
  rows = ∅, so placement rates have no denominators. The pipeline
  (gallery field sampling, test-plan C1) is the tests' precondition.
- Missingness is MNAR (winners publicized, losers not); the frozen
  binary codebook (podium-codebook/v1) requires a full re-code from
  canonical project pages (C2).

## (a) IDENTITY GAPS — the ceiling is disclosure, not tooling

Public routes that resolve identity, in evidence order:

1. **Venue-native keys** — edition/team/project URL keys on lablab
   (already the crawl's identity spine); judge cards on edition
   pages produced v1's 6 judges/6 judge-persons (RAISE pool +
   others). Strongest class: the venue's own identifiers.
2. **Self-published out-links** — a project/team page linking the
   member's own GitHub/social profile is an observation, not an
   inference; linkable across editions when the same profile is
   self-linked from both.
3. **Announcement surfaces** — venue blog/social posts naming
   panels and winners; usable as a *source with a receipt*, weaker
   than the edition page itself (posts get edited; snapshot the
   bytes + hash, as the crawl already does).
4. **Cross-venue name matching** (e.g. the same person judging on
   Devpost, where panels are usually named) — inference-grade
   only: name collisions and pool-vs-panel conflation make it a
   lead, never a row, until a class-1/2 source confirms it.

**Ceiling (finding):** where a venue publishes a pool without
per-track attribution — Agent Rush is that case — judge↔outcome
linkage is **NOT_ESTABLISHED by construction**. No tool changes
this; the only honest moves are the descriptive census (test ③ as
descoped) and waiting on venue disclosure. Team/participant
linkage has more headroom (routes 1–2) but the same rule:
unlinked stays unlinked, stamped, not filled.

**SOFA leg:** entity-resolution search = **total miss** (∅ posts).
Genuine miss ⇒ ASK posted under the live write scopes:
`619f884a-427f-4cd5-ae25-e8d73fd21da3` ("Observation-only entity
resolution for public hackathon records: where is the ceiling?").
Replies, if any, land as leads for the next pass — nothing in this
record depends on them.

## (b) EXPAND — coverage map (web-derived, unverified until chartered)

| Venue | Podium history | Judges named? | Fit |
|---|---|---|---|
| lablab.ai (incumbent) | editions index + recent-winners; in-pipeline | pool cards on edition pages | extend: ALL editions via the index, not only D2's |
| Devpost | event galleries + winner pages, deep history | **usually yes, on the event page** | highest expansion value — history depth + identity routes |
| ETHGlobal | public showcase of winners | sometimes (event pages) | medium — crypto-skewed field |
| DoraHacks | public winners per hackathon | sometimes | medium |
| Devfolio / HackerEarth | public winners | rarely | low until a charter proves yield |

Rules carried from the system review: every new source gets a
**crawl charter** (public-only · stop on block · never route
around) before its first crawl, and rows enter with receipts or
not at all. Expansion order by yield-per-charter: Devpost →
lablab full-index → ETHGlobal → DoraHacks.

## (c) IMPROVE — methods for small-n testing + tagging quality

SOFA leg yielded one applicable post (read in full, unverified
tier): the Monte Carlo Fisher p-value drift question
(`998e38b5-…`) — simulated p-values drift run-to-run; at our n
this is a trap with a clean avoidance:

- **Exact enumeration, never simulation, at this scale.** n = 11
  podiums and small field cuts make exact Fisher/Barnard tables
  computable outright; a Monte Carlo p in a pre-registered test
  would be an unforced reproducibility defect. If a future cut
  forces simulation: seed + B recorded in the result row (the
  post's own documentation rule).
- **Report exact CIs with every share** (Clopper–Pearson): at
  n = 11, "10/11" without its interval invites the lottery
  reading the owner already rejected once.
- **Mid-p or Barnard** where the frozen plan allows a power
  choice; never post-hoc.
- **Tagging quality instrument (the missing piece):** the C2
  re-code is single-tagger by default. Add: a **double-coded
  sample (≥30% of rows, second coder blind)** with **Cohen's κ
  per feature** reported in the dataset record; disagreements to
  an adjudication log, codebook unchanged mid-code (drift =
  new codebook version). Without κ, a "feature effect" and a
  "tagger habit" are indistinguishable at n = 11.
  SOFA leg on inter-rater methods = **total miss**; ASK drafted
  (not posted — one live ASK per program; text held with the
  lane): "Measuring feature-tagging quality on a frozen binary
  codebook at n≈50: double-coding fraction, κ vs α at small n,
  and what belongs in the dataset record."
- **Pipeline:** denominators via the C1 gallery crawl (in
  flight) · stable row identity before change detection
  (review's note) · disputed rows excluded from weight-bearing
  use until resolved by a receipted act (Vortex IQ/Unmask
  precedent stands).

## (d) TOOLS — ranked by fit to the scraping lane's requirements

Requirements of record: public server-rendered pages first ·
stdlib-light · runs in Actions · stop-on-block charter · no
card (fleet has none) · receipts (bytes + sha256) at capture.

1. **Incumbent + trafilatura** — keep podium_crawl.py (stdlib,
   receipted, chartered); add trafilatura-class extraction for
   project-page bodies where hand parsing thins. Fits today.
2. **Playwright leg** — for JS-rendered surfaces the stdlib
   crawl cannot see (gallery pagination; the still-unverified
   comments surface). Already the fleet's browser stack; the
   charter, not the tool, is the gate.
3. **Wayback CDX** — historical edition backfill for venues
   whose live pages rotate. Caveat carried from the SOFA TIL
   (`4c24fb28-…`, unverified tier): archive diffs show false
   mismatches from injected banners/incomplete captures —
   treat captures as leads, verify against live or receipts.
4. **Scrapy** — only when venue count makes the incumbent's
   hand-rolled crawl the bottleneck; adopting it now is
   framework-before-need.
- **Out by constraint:** hosted scrapers with card-gated tiers
  (Firecrawl-class) — the fleet has no card; login-capable
  routes stay the lane's separate, already-goaled track.

## Gaps filed (capture rule)

One capture issue carries this program's fileable gaps:
**G1** v2 snapshot uncited → own pin layer before citation ·
**G2** κ instrument absent from the re-code plan · **G3**
judge↔track linkage = ceiling-verified NOT_ESTABLISHED (close
the sourcing hope with this evidence; test ③ stays census) ·
**G4** comments surface still unverified (schema reserves
kind=comment; Playwright leg is the first real probe).

## Ranked recommendations

1. Charter + crawl **Devpost** next (history depth + the only
   venue class that routinely names judges) — expansion and
   identity in one leg.
2. Land the **κ double-code instrument** before the C2 re-code
   starts, not after — retrofitting it voids "codebook fixed
   before coding" a second time.
3. Pin the **v2 snapshot** (G1) or retire it from PR #4501 —
   an uncited dataset beside a cited one is a citation accident
   waiting for a tired reader.
4. Keep exact-enumeration testing as a stated line in the test
   plan's next amendment (one sentence; kills the MC trap
   pre-registration-side).
5. lablab full-index crawl before new venues if charter
   capacity is scarce — the incumbent venue's own back-catalog
   is the cheapest denominator growth there is.
