# Podium dataset — crawl / ingest / store

[MUSEai]@{role:{scraping-tools}} — owner requirement 2026-11-03
("excellent crawling ingesting data store systems") for the D2
exercise record + MoneyBall test plan.

## Purpose

The podium/field dataset behind D2 (Vultr Agent Rush, lablab.ai) and
MoneyBall's test plan: **external, receipted evidence** about lablab
editions — judges · placements · projects · comments — crawled from
the venue itself, so podium claims can be triple-sourced against
`ops/challenge/coordinator.json` (the internal record) instead of
resting on one lane's reading (cf. the Ariadne/Unmask correction).

## Pipeline

```
lablab.ai public pages ── podium_crawl.py ──> podium-snapshot/v1
  (server-rendered HTML,     (stdlib, no login)   {sources w/ sha256,
   no session)                                     rows w/ receipts}
        │
        └─ podium_ingest.py ──> podium-dataset/v1 (versioned, in repo:
             dedupe by content hash · conflicts kept, never merged ·
             diff vs previous version = change detection)
        │
        └─ podium_load.py ──> SQL ──> Neon podium_* tables
             (append-only; current views; secrets by name only:
              LANE_EVENTS_DATABASE_URL / NEON_API_KEY)
```

- **Crawl surfaces (v1, public):** `/ai-hackathons` (edition index),
  `/ai-hackathons/<slug>` (edition core, prize tiers, Speakers/Mentors
  & Judges cards), `/apps/recent-winners` (winning project cards:
  medal icon = placement, card URL = edition/team/project keys).
  Repeat crawls through the live window (D2 field moves daily to
  Nov 8) via `.github/workflows/podium-crawl.yml` (dispatch + daily).
- **Login-gated surfaces** (own team/submission state) are a later leg
  via the lane's login-capable routes; v1 is public-only by design.
- **Comments:** no public comments surface found in recon of the
  server-rendered pages (2026-11-03); schema reserves `kind=comment`
  and the leg lands when a surface (app/API) is verified — not faked.
- **Receipts:** every row carries `{source_url, captured_at,
  collector}`; snapshot sources carry `{url, http, bytes, sha256}`.
- **Conflicts:** same entity+field with differing values (across
  sources or across versions) ⇒ `conflicts[]` in the dataset and a
  `podium_conflicts` row. Display value = first seen; nothing is
  silently merged or overwritten (store is append-only, enforced by
  trigger, same pattern as `ops/challenge-participants/schema.sql`).
- **Snapshots:** `ops/podium/snapshots/<version>.json` in the monorepo
  is the citable record; every consumer pins a dataset version.
  v1 = `2026-11-03.v1` (55 entities: 4 editions · 9 tiers · 6 judges ·
  6 judge-persons · 30 projects · 0 conflicts · all-added baseline
  diff), sha256 `537981b874cb2bd3b0d53e3e0a73760e1b7db8690cba6a93d7bb1016eb1b60f8`.

## Store

`ops/podium/schema.sql` — `podium_crawls` (batch) ·
`podium_observations` (append-only, verbatim fields + receipts) ·
`podium_conflicts` · views `podium_current`, `podium_by_edition`.
Same Neon lane-events project/route as the participant store; the two
join on edition slug ↔ coordinator event (mapping = consumer's job,
values are never copied across silently).

## Consumers

- **D2 exercise record** (entries lane): pins `2026-11-03.v1`+;
  re-crawls append versions through Nov 8.
- **MoneyBall test plan**: reads `podium_by_edition` / pinned snapshot.
- **Validation lane**: reviews the tagging step (project tech_tags and
  placement attribution from feed cards are heuristic — medal icons
  mark category placements on the winners feed; edition podium truth
  requires the triple-source join, which is the point of the store).

## Known v1 limits

- Feed-card placement = the medal shown on the card (category-level on
  multi-category editions); 2 alpaca cards carry no medal ⇒ placement
  null, kept as observed.
- Edition `dates_seen` is raw text evidence (pages carry stray dates);
  authoritative windows stay with coordinator.json until a dated
  source joins — a deliberate conflict surface, not a gap to paper over.
- Judges parse = (name, title) pairs from the section; org is not
  consistently on the card and is left null rather than guessed.

## MoneyBall alignment (test plan PR #4492, seat cd195597)

- **Version pin:** consumers pin `version` + dataset sha256; a record
  update re-pins by hash, prior rows keep theirs (plan G6/C5).
- **Stratum:** edition is never pooled away — entities are keyed per
  edition; aggregates are consumer-side.
- **Judge identity:** `judge_person` entities key judges by normalized
  name across editions (exact-name v1; fuzzy linkage = Splink leg in
  the tool slate) for repeat-judge detection (test ③). Judge↔track
  linkage is NOT in lablab public pages — separately pinned if sourced.
- **Feasibility stamps** ride every dataset (`feasibility{}`): per
  edition {podium_n · field_n · judge_comments · community_comments} +
  repeat-judge count. v1: field_n = null (gallery leg below),
  comments = 0/0 (surface NOT_ESTABLISHED).
- **EGM exclusion:** EGM instance-#2 test-stamped items (canonical
  `EGM instance #2 TEST filing`, secondary `RFP-EGM2-`) are excluded
  by an ingest guard; v1 sources are lablab pages only, so nothing
  stamped can enter — the guard binds any future source widening.
- **Coding contamination (G5):** project rows carry the canonical
  project page URL; feature coding is redone from those pages under
  `podium-codebook/v1` by the consumers — card text here is evidence,
  not features.

## Amendment v2 (2026-11-03, MoneyBall plan amendment #2)

Dataset `2026-11-03.v2` (sha256 `b8a187aabc4b68ca8f987baae45ab633df78c52b9bd50c2b42e389072fb27995`,
diff vs v1: +34 added · 9 changed · 0 removed) adds: **field rows**
(per-edition `/live` gallery anchors — entries := gallery submissions;
vultr field already 4 on day 1, alpaca 15, assemblyai 11, ibm-bob 13)
∧ expanded feasibility stamps {repeat judges with attributable picks
= 0 · judge↔track linkage NOT_ESTABLISHED (stamp = the deliverable) ·
category×edition denominators NOT_ESTABLISHED · editions with usable
rubrics = 0}.

## Next version scope (v3)

- **Field rows (C1):** per edition, ALL gallery submissions (entries :=
  gallery submissions, not approved registrants). D2 gallery opens
  Nov 5 (participant-store record); concluded editions' galleries
  first, D2 on open. If volume forces sampling: stated random sample
  with the seed recorded in the dataset record.
- **Comments leg:** if an app/API comments surface verifies, rows land
  as kind=comment with author_kind {judge|community} distinguished (C8).

## Tool slate (FIND TOOLS leg, 2026-11-03)

Gate rule: a tool that cannot carry per-row receipts
`{source_url · captured_at · collector}` through its data flow fails
the core requirement regardless of other merits. Verdicts:
BUILD (ours) / ADOPT (integrate) / HOLD (later) / SKIP.

### Crawl
| tool | verdict | why |
|---|---|---|
| podium_crawl.py (stdlib) | **BUILD — shipped** | receipts native; change detection via ingest diff; SSR pages |
| Crawl4AI (Apache-2.0, self-host) | **ADOPT next** | JS-heavy + login-session leg; hooks-auth documented; diff = external (our ingest) |
| api-anything (MIT, eval 2026-11-03) | ADOPT candidate | replay tier-1 + heal for learned APIs; browser tier needs direct egress (Actions) |
| Crawlee (Apache-2.0) | HOLD | SessionPool/login handlers solid; overlaps Crawl4AI leg |
| TinyFish Fetch/Search | adjunct | public fetch; envelope-level receipts only (wrapper stamps rows); key-blocked |
| Firecrawl changeTracking | SKIP (core) | only native per-field diff, but paid + snapshots vendor-held; receipts ⚠️ stamped at ingest |
| changedetection.io (Apache-2.0) | SKIP | real diff engine but daemon-shaped (VM/Actions unfit) + page-text model = **row receipts fail**; tripwire pattern reference only |

### Ingest
| podium_ingest.py | **BUILD — shipped** | exact-hash dedupe + conflicts preserved + receipts, to spec |
| Splink (MIT) | **ADOPT (v3 leg)** | Fellegi-Sunter fuzzy dedupe/linkage on DuckDB/Postgres; explainable match weights = the link itself is receipted; receipts ride our tables |
| dedupe (MIT) | SKIP | active-learning labelling fights automation; upstream inactive since 2024-08 |
| OpenRefine (BSD-3) | SKIP | interactive; provenance is operation-level, not per-row |
| frictionless (MIT) | HOLD | contract gate at ingest later; dataset-level metadata only |

### Store
| Neon Postgres (provisioned) | **KEEP — primary** | append-only + views; receipts are columns; participant-store pattern live |
| git snapshots in repo | **KEEP — record** | versioned, hash-pinned, citable (dataset_version) |
| DuckDB | ADOPT | query scratchpad over snapshots; Splink's backend; no native versioning (convention: dated immutable exports) |
| lakeFS / DVC | SKIP (now) | true data-versioning, unjustified ops weight at this scale; revisit if snapshots outgrow repo |

### Identity resolution
| judge_person exact-name (ours) | **BUILD — shipped** | deterministic, receipted; variants gap |
| Splink | **ADOPT (v3)** | calibrated probabilistic person linkage; band adjudication, never auto-merge below threshold |
| Maigret (MIT) | ADOPT (candidate-gen) | 3,000+ site handle sweep + profile extraction; existence ≠ identity — feeds Splink only; wrapper stamps receipts |
| Sherlock / socialscan | SKIP (evidence) | URL/boolean lists, no metadata/timestamps; too weak as linkage truth |

### Feature tagging
Constraint: MoneyBall C2/G5 — coding is redone from canonical project
pages under frozen `podium-codebook/v1` by consumers; this pipeline
supplies text (title/tagline/tags + canonical URL), tagging tools are
draft/assist only, and any tag used as evidence carries its own
receipt (model id + prompt + codebook version as collector).
| bart-large-mnli zero-shot (HF, local) | HOLD | $0, multi-label native; pending validation-lane design review |
| LLM APIs (Mistral verified live; Gemini vault) | ADOPT (adjudicator) | low-confidence band only; pin model + temp 0, record both per tag |
| sklearn TF-IDF OneVsRest / spaCy textcat | LATER | cheapest once a few hundred checked tags exist to train on |
| KeyBERT | SKIP (classifier) | keyword extraction, no governed label set; tag suggestion only |
