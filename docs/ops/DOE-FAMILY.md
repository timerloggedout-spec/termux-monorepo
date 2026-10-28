# DoE Family — MVT Is One Member, Not the Whole

Owner direction (2026-10-27, issue #1865): DoE becomes a **family**.
MVT is one member, not the whole. This document is the family's
structure record; `docs/ops/MVT-DOE-ATES-SEPARATION.md` remains the
ownership spec for the surfaces.

## Members

| Member | Kind | State | Primary home |
|---|---|---|---|
| MVT campaigns | member (existing) | active practice | MVT surface (`mvt.html` / `mvt-feed.json`) — the DoE surface carries a pointer only, never the payload |
| Pilot 1 — context routing × CedrLang compression (#1849) | campaign | admitted (design record committed); executed — see campaign dir | `experiments/doe/pilot-1-context-routing-x-compression/` |
| Pilot 2 — dispatch topology × quota policy (#1850) | campaign candidate | proposal only — **not admitted** (no design record, no run evidence) | issue #1850 |
| Future design classes | campaign types | taxonomy in `docs/ops/DOE-TAXONOMY.md`: implemented generators today = full factorial + Taguchi L9 (fractional orthogonal array); fractional factorial, Plackett–Burman, sequential = skill-named, no generator; foldover, central composite, Box–Behnken, RSM, mixture, split-plot, Latin hypercube = candidates. Randomized assignment (`mvt_shuffle`) is an assignment mechanism, not a design class | DoE surface |

## Family-level shared

- **Experiment record schema** — `docs/ops/corpus/EXPERIMENT.schema.json`
  ("DOE/MVT Experiment Record", schema_version 1.0). Primary home is the
  MVT surface per the separation spec; the family **adopts** it: every
  family campaign run emits one record conforming to it, validated in
  tests (`tests/test_doe_family.py`). One dispatched/executed run = one
  record = one observation.
- **Feed sections** — `doe-feed.json` carries, per member: designs /
  campaigns / results. A member with no results renders its state
  exactly (design-only, proposal-only), never a borrowed result.
- **Intake rule** — a campaign joins the family only with a committed
  **design record + run evidence** (EXPERIMENT-conforming records).
  Proposals alone don't count.
- **Evaluation doctrine** — parallel lanes under a shared capability
  contract; scoring distinguishes execution status → task outcome →
  correctness → integration → regression → resource cost (multivariate-doe
  skill outcome model); 🍒-pick customizations are recorded as new
  cohort/version, never silently folded into a running design (skill
  rule 12).

## Binding rules (from #1865 + separation spec)

1. One primary home per record. Cross-surface references are citations
   (pointer + label), never copied payload.
2. The Delphi cycle record's presentation on this surface is REQUIRED
   with full payload + `owner_surface: delphi` — and is never counted
   or relabeled as a DoE campaign result.
3. DoE's own results come only from family campaigns' committed records.
4. Counts are live-derived at report time.

## Campaign layout

```text
experiments/doe/<campaign-id>/
  DESIGN.json    # design record: hypothesis, factors/levels, blocks,
                 # outcomes, execution environment, quota note
  records/       # one EXPERIMENT.schema.json-conforming JSON per run
  SUMMARY.json   # aggregates + factorial effects, produced by the runner
  README.md      # method, honesty limits, how to re-run
```

Runner: `scripts/doe/run_pilot1.py` (deterministic, offline; re-running
regenerates records + summary — `observed_at`/elapsed are run stamps).
