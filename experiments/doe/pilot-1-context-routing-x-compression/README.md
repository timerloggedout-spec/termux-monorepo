# Pilot 1 — context routing × CedrLang compression (#1849)

First executed DoE family campaign. Design record: `DESIGN.json`
(this directory). Runner: `scripts/doe/run_pilot1.py`.

## Method (as executed)

- 2×2 blocked full factorial from `deepcli.observatory.doe.full_factorial`:
  routing [icm-guided, bounded-search] × representation [explicit, compressed].
- 8 source-grounded tasks (blocks: task family × difficulty stratum), each
  with predeclared required fragments that exist verbatim in its target doc.
- **icm-guided**: the retriever takes the task's target doc directly — the
  document the ICM map routes to (smallest authoritative source).
- **bounded-search**: keyword grep over `docs/**/*.md` +
  `.agents/skills/**/*.md`, ranked by keyword hits, top-1 doc wins
  (it can pick the wrong doc — that is the measured routing effect).
- **explicit**: context = retrieved doc as-is. **compressed**: context =
  retrieved doc round-tripped through CedrLang `compile_doc` →
  `decompile_doc`; input tokens counted on the compressed form actually fed.
- Answer extraction: first keyword-bearing line ±8 lines; if accuracy < 1.0,
  one fallback re-retrieval at ±20 lines (counted as rework).
- Accuracy = required fragments recovered / required (case-insensitive).
- One run = one `records/*.json`, conforming to
  `docs/ops/corpus/EXPERIMENT.schema.json` (family-adopted schema).
  `SUMMARY.json` holds per-arm aggregates + factorial effects
  (main effects + interaction on accuracy).

## Honesty limits

- Execution environment is **offline-deterministic** (see DESIGN.json):
  this proves the family pipeline — design record → executed runs →
  conforming records → surface results. It is not the live-dispatch
  variant of #1849 (dormant-until-config lane levels), which remains
  specified, not run, and needs a #1595-census quota statement first.
- The extractor is a deterministic fragment retriever, not an LLM;
  accuracy measures context recoverability under each arm, which is the
  pilot's declared primary outcome.
- Re-running the runner regenerates records; `observed_at` and
  `elapsed_ms` are run stamps and will differ. Everything else is
  deterministic at the pinned `base_sha` in DESIGN.json.
