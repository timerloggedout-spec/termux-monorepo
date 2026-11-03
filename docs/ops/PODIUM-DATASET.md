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
  v1 = `2026-11-03.v1` (49 entities: 4 editions · 9 tiers · 6 judges ·
  30 projects · 0 conflicts · all-added baseline diff).

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
