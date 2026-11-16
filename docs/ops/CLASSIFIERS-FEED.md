# classifiers-feed/v1 — contract

Single-writer feed for the full classifier estate. Writer: the
tier1-classifiers steward lane ONLY (single-writer rule; other lanes
file deltas with the steward, they do not edit the feed).

- Artifact: `ops/classifiers/classifiers-feed.json`
- Generator: `scripts/classifiers/build_classifiers_feed.py`
  (the unit table lives in the generator; regenerate, never hand-edit
  the JSON).
- Baseline: `docs/ops/TIER1-CLASSIFIER-RECON-2026-10-28.md` plus
  steward-verified deltas since.

## Schema

Top level: `schema` (= classifiers-feed/v1), `generated_at`,
`generator`, `baseline`, `headlines` {estate_units, live, dormant,
dead, converged, multi_output}, `correction_note`, `honesty`,
`groups`, `units[]`, `observatory_quartet`, `gaps[]`.

Per unit: `id`, `name`, `group` (+ `group_name`), `state`
(live | dormant | dead — dormant covers code-only, never-run,
fail-last and parked), `converged` (bool) + `converged_basis`,
`outputs[]`, `pct_breakdown` {available, kind, label},
`winner` {available, kind, state}.

## Counting + honesty rules

- Unit = one recon row / one named system. CellCog is counted once
  (the recon lists it under both workflow triage and external
  surfaces).
- Converged requires ALL THREE: under the steward frame,
  definitions reconciled, and versioning with a comparison line.
- Byte-identical mirrors are not separate outputs; a distinct
  store/format (e.g. a Neon mirror) is a separate output.
- Class shares are SHARES, not confidences — the label travels with
  the data.
- Winner-% names MoneyBall winprob only. MoneyBall is PARKED
  (owner, 2026-10-28) and the feed shows that state.
- Headlines are recomputed from the unit rows at generation time,
  never copied from earlier reports. (2026-11-02: the first census
  headline overstated estate/live by +1 each; the feed's
  correction_note carries the recount.)
