# Linguist Panel — visualization contract + substrate feed requirements

Stage 2 (visualization lane). Stage 1 = substrate lane (canonical
registry + feed). Deploy/integration = Web Design lane.

## Page

`apps/help-wanted-dashboard/linguist.html` — prototype, renders ONLY
`apps/help-wanted-dashboard/data/linguist-panel-feed.json`. Feed absent →
explicit absent state; no mappings are invented in the page.

Surface (owner MUSTs):
- all mapped versions of a text: side-by-side columns (original + one
  column per enabled family) AND in-text mode (highlighted spans,
  click a span → threaded mapped versions across families);
- toggles per mapping family on/off;
- badges: per family "N in text"; per span, count of families hitting it;
- admin view: browse/search all mappings, provenance visible per entry.

## Feed requirements (sent to substrate lane 2026-10-27)

Schema (working name `linguist-feed/v1`):
`{schema, generated_at, honesty_rules, gaps, data:{families[], entries[], sample_texts[]}}`

- `families[]`: `{id, label, kind (cipher|leet|compression|notation|other), description, provenance}`
- `entries[]`: `{id, family_id, source, variants[], direction (forward|reverse|both), provenance {source_path, detail}, round_trip_verified (bool|null — null, never omitted, when unverified), granularity (char|token|phrase), table {from:to} for char-level maps, match (literal span form) where applicable}`
- `sample_texts[]`: `{id, text, note}` — real repo texts only.

## Gap record — CLOSED by re-pin (2026-10-27)

Stage-2 was built before the substrate feed landed; the census lane
(cb34a236) verified 4 mismatches against the landed feed
(`linguist-panel-feed/v1`, PRs #1864/#1868). All fixed in the re-pin:
- G1 path: `./data/linguist-panel-feed.json`.
- G2 wrapper: feed is FLAT (top-level families/entries/sample_texts);
  renderer reads `feed.data ?? feed`.
- G3 tables: char maps are `family.table` as `[{from,to}]` (2 families);
  renderer hoists to an object (array `to` -> first variant) as a
  synthetic per-family char entry for transforms/spans.
- G4 direction: logic uses `direction_panel` (both/forward transform;
  reverse/null = match/admin only, no column). Notation families
  (direction_panel null) render spans + admin, never transform columns.

Layers (census spec): layer = `family.kind` (cipher/compression/leet/
notation/other); two-level toggle — layer master (tri-state) ∧
per-family checkbox. Count-only families (`entries_included=false`,
archwiz 7,287) render a disabled toggle + "count-only — not enumerated"
badge and never produce spans/columns.

Acceptance verified in tests/test_linguist_page.py against the landed
feed + a real-shape fixture sim: (a) all layers off -> no columns/spans,
admin still browsable; (b) leet-only -> char transforms from family
tables; (c) notation-only -> spans+admin, no transform columns;
(d) feed-absent state retained on fetch failure.
