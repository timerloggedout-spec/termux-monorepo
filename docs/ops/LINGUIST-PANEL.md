# Linguist Panel — visualization contract + substrate feed requirements

Stage 2 (visualization lane). Stage 1 = substrate lane (canonical
registry + feed). Deploy/integration = Web Design lane.

## Page

`apps/help-wanted-dashboard/linguist.html` — prototype, renders ONLY
`apps/help-wanted-dashboard/data/linguist-feed.json`. Feed absent →
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

## Gap record

At panel build time the substrate feed was NOT on master and no
substrate PR existed (checked firsthand: PR search + code search,
2026-10-27). Requirements above were flagged directly to the substrate
lane. Known degradation until the feed lands per spec:
- no `family_id` on entries → per-family badges impossible;
- no `match`/`table` span forms → in-text threading impossible
  (columns-only);
- no per-entry `provenance` → admin provenance column renders
  "not in feed".

The page normalizes tolerant shapes (`family` alias, single `variant`,
table-only entries) but does not synthesize missing fields. Before this
panel is deployed, the renderer must be re-pinned against the landed
feed (validation step owned by the viz lane, as with the Oracle Panel).
