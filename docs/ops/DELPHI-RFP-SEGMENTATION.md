# Delphi RFP Segmentation — Improve-Cycle Context Options

Owner directive (2026-10-27): the `delphi:rfp` work sits in the DoE
lane for **iterative self-improvement + context-options
segmentation**. The label holds 70 open RFPs (live-derived census,
`scripts/delphi/rfp_census_observation.json`); without segmentation
they read as one flood. This doc is the segmentation record. Machine
config: `ops/delphi/rfp-segments.json`. Feed:
`scripts/delphi/rfp_segment_feed.py` → `delphi-rfp-feed.json` →
`delphi-rfp.html` (progress + status + criteria + questions +
outcomes per segment). Coordination: Delphi lane (gate, panel,
ledgers, scoring engine stay theirs — this segmentation does not
fork or re-derive them).

## The three classes

| Class | Count (census) | Segmentation | Comparison home |
|---|---|---|---|
| Research silos | 48 = 12 silos × (baseline + rnd/selected/control) | **One segment per silo** | Within segment only |
| Quota surfaces | 19 (18 in `surfaces.json` + fly.free_tier) | One class segment | Delphi gate + flywheel (existing) |
| Meta / process | 3 (#1572 intake, #1571 visualization, #1567 MVT-DoE/TLM) | Individual segments | Each on its own stated criteria |

## Research silos — the improve-cycle segmentation

Per `docs/ops/RESEARCH-SILO-DELPHI.md`, each silo runs its own
Proposal → Delphi → cycle stovepipe with **no cross-silo score
leakage**. The segmentation makes that mechanical:

- **Segment = silo.** Members: baseline (`research.<slot>`) +
  variants (`.rnd`, `.selected`, `.control`).
- **Cycle stages** (from `research-silos.json`): RFP improve-request
  → oracle + blind panel → award → validated output comparison →
  feature extraction → consensus implementation → flywheel.
- **Criteria = the three axes**: produced output results validated ·
  feature extractions · consensus implementation. These — not the
  gate score — are the comparison.
- **Gate = admission only.** Research ids are synthetic unsourced
  surfaces; the first baseline cycle returned a uniform parked /
  6.69-25 / not-converged (3 rounds) / recheck 2026-11-27 for all 12
  (record: #1487 comment 6459554998). Uniform by construction; it
  distinguishes nothing and is never presented as a result.
- **Questions** (per segment, in the feed): does the variant's output
  validate where the baseline's did/didn't · which features does each
  variant extract that the others don't · where do they converge on a
  consensus implementation, and where irreconcilably differ.
- **DoE reading**: each segment is a blocked comparison — silo is the
  block, variant is the treatment, baseline is the control arm. That
  is why this sits in the DoE lane: the improve cycle *is* a family
  design whose units are RFPs, and its records are the outcome
  ledger's, per segment.

Current status (census 2026-10-28): all 12 segments fully filed
(4/4 members); baselines gate-scored, axes pending as cycle stages;
variants filed, not started.

## Quota surfaces

The Delphi lane's home segmentation, untouched: sourced surfaces
with real fit/headroom/horizon, gate-scored, flywheel outcomes on
#1487 reweighting #1489. The feed lists membership and points at the
ledgers; it does not re-derive per-surface gate state.

## Meta / process

Three RFPs about the method itself. Each is its own segment and
context; judged on its own stated criteria. #1567 (MVT-DoE/TLM) is
the bridge to the DoE family's own validation work.

## Rules

1. Every open `delphi:rfp` issue belongs to exactly one segment; the
   collector emits `unassigned` rather than force-fitting.
2. Counts are census-derived at refresh time (snapshot + `read_at`),
   never carried forward.
3. Outcomes enter the feed only as recorded-outcome pointers to the
   ledger record — never transcribed scores without their source.
4. A new context (new silo, new surface, new class) enters by
   amending `ops/delphi/rfp-segments.json` / the source registries —
   the segmentation follows the registries, not the other way round.
