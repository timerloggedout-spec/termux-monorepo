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
  retrieved doc round-tripped through the CedrLang `compress` → `expand` pair
  (symbol substitution + stopword removal — lossy by design); input
  tokens counted on the compressed form actually fed.
- Answer extraction: the 3 densest keyword-bearing windows (±8 lines,
  ranked by keyword hits, disjoint); if accuracy < 1.0, one fallback
  re-retrieval with 6 windows (counted as rework). The extractor sees
  keywords only — never the required fragments it is scored against.
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

## Results (executed 2026-10-28, base 5ce1a9c2)

32 runs (8 tasks × 4 arms). Full aggregates + effects: `SUMMARY.json`.

| Arm | Mean accuracy | Mean input tokens |
|---|---|---|
| icm-guided / explicit | 0.9375 | 1051.6 |
| bounded-search / explicit | 0.8125 | 928.4 |
| icm-guided / compressed | 0.3125 | 981.8 |
| bounded-search / compressed | 0.3125 | 870.6 |

Factorial effects on accuracy: routing +0.0625, representation
−0.5625, interaction −0.0625.

**Verdict: threshold NOT met.** CedrLang compression (compress/expand
pair) cut input tokens only ~7% while destroying required-fragment
recovery (stopword removal + punctuation stripping break verbatim
source fragments). Routing choice barely mattered once the target doc
was reachable. Negative result preserved per the skill's rule 10 —
compression of routing-boundary context is not safe for
source-grounded tasks in its current form; the #1849 live variant
should not wake the compressed level until compression is
fragment-preserving.
