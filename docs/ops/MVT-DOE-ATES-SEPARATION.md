# MVT / DoE / ATES — Surface Separation Spec

The dashboard surfaces landed braided (PR #1741 MVT, PR #1742 DoE,
2026-10-27): the MVT feed carried the ATES harness block and the ATES
fixtures; the DoE feed carried the Delphi cycle's implementation record
as its "executed comparisons". This spec assigns every record exactly
one home surface. Everything cross-surface is a **citation** — a pointer
with a label — never a copied payload.

## The three surfaces, as their records define them

### ATES — the orchestrator harness

The machinery that executes arms under discipline. Records:

- `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md` §MVT — the seven hard
  invariants of the minimum viable test cohort (abstention availability,
  wrong-commit penalty, required-fragment preservation, distractor
  isolation, deterministic execution failure, isolated SPAWN behavior,
  actor/critic private-context isolation).
- `.github/workflows/ates-orchestrator-benchmark.yml` — the
  deterministic benchmark: on changes to the evaluator, fixtures or
  ATES docs it runs the orchestrator suites, evaluates
  `scripts/ci/evaluate_orchestrator_benchmark.py` over the fixtures,
  and asserts the deterministic verdicts (pass case PASS; leak case
  FAIL_DETERMINISTIC, net_score 0.0). Trace contract:
  `docs/ops/ATES-ORCHESTRATOR-TRACE.schema.json`.
- `.github/workflows/ates-phase-b-run-receipt.yml` — run receipts: on
  completion of "Continuous agent ops" it emits a metadata-only receipt
  (`scripts/ci/emit_ates_run_receipt.py`; no head_commit, no html_url)
  and publishes it as a 30-day Actions artifact.
- `.github/workflows/agent-mvt-experiment.yml` — the execution vehicle:
  candidate and baseline refs checked out independently, measured,
  recorded; `contents: read` only; its header states it NEVER mutates
  refs.
- `tests/fixtures/ates/orchestrator_mvt.json` — two synthetic boundary
  cases (`mvt-boundary-pass`, `mvt-boundary-leak`). Fixtures, not
  results.

### MVT — multivariate testing as practiced

The practice of running simultaneous arms and recording experiments.
Records:

- `docs/ops/corpus/EXPERIMENT.schema.json` — the experiment record
  contract (the schema's own title is "DOE/MVT Experiment Record").
- The experiment loop's experiment-facing record: dispatch inputs
  (candidate_ref, baseline_ref, experiment_id, suite, compare_only),
  its state, and its run receipts (0 runs observed — defined, not run).
- `.github/workflows/team-mvt.yml` — Team MVT: simultaneous provider
  lanes over an issue/PR target (528 runs observed at the 2026-10-27
  snapshot in `scripts/dashboards/workflow_observations.json`).

### DoE — design of experiments

The design discipline: which arms, which factors, which rules. Records:

- `deepcli/deepcli/observatory/doe.py` — the methods library
  (full_factorial, taguchi_l9, mvt_shuffle).
- `.agents/skills/multivariate-doe/SKILL.md` — the default agent-team
  factor space and the 12 design rules.
- The ATES doc §DoE — the first factorial slice (routing × actor_critic
  × abstention × spawn × judge, with primary/secondary outcomes): a
  design defined inside the harness doc.
- `docs/proposals/active/model-selection-market/DSPY-DOE-LANE.md` —
  the DSPy optimizer lane. Design only, not run.

## Ownership rules

1. **One primary home per record.** A feed emits payloads only from its
   own surface's records (feed `sources` lists name them).
2. **Cross-surface = citation.** References travel in a feed's
   `citations` array: `{surface, record, label, note}` — where the
   record lives and why it matters here. The cited surface's data
   payload never appears in the citing feed.
3. **Joint files split by section, not by copy.** The ATES doc is one
   file holding two surfaces' records: §MVT (invariants) belongs to
   ATES, §DoE (the factorial slice) belongs to DoE. `EXPERIMENT.schema.json`
   is a shared record contract whose primary home is MVT — the loop
   emits records in its shape and Team MVT is the practice that fills
   it; ATES and DoE cite it. `doe.py`'s docstring ("DoE helpers for MVT
   campaigns") names a consumer, not an owner: the library is DoE's,
   MVT cites it as its design source.
4. **No borrowed results.** A surface with no results says so in its
   `gaps`. Defined-but-not-run renders as exactly that, on the surface
   that owns the definition.

## The Delphi record

`docs/proposals/passes/strands-rfp-response/cycle/IMPLEMENTATION.json`
is owned by the Delphi surface and rendered on the Oracle Panel. The
DoE feed no longer inlines its per-candidate results as
`executed_comparisons`; it carries one citation entry, labeled as a
Delphi record. It is not a DoE campaign and contributes no DoE results.

## Feed shapes after separation

| Feed | `data` keys |
|---|---|
| `ates-feed.json` (new) | doc, invariants, invariant_note, workflows (benchmark / run-receipt / experiment-loop vehicle), fixtures, trace_schema, citations → MVT, DoE |
| `mvt-feed.json` | method, experiment_record_schema, experiment_loop, team_mvt, citations → ATES, DoE |
| `doe-feed.json` | methods_library, skill, first_factorial_slice (with executor citation), dspy_lane, citations → Delphi |

Collector: `scripts/dashboards/surface_feeds.py`
(`collect_ates` / `collect_mvt` / `collect_doe`). Contract:
`docs/ops/DASHBOARD-SURFACE-FEEDS.md`. Agreement and the separation
boundaries are pinned by `tests/test_surface_feeds.py`.

## Page consequences (Web Design lane)

The feeds land first, against this spec; the pages re-render from them:

- `mvt.html` drops its harness and fixtures sections — they move to a
  new `ates.html` consuming `ates-feed.json` (unified nav + sitemap
  gain ATES).
- `doe.html`'s executed-comparisons table becomes a citation card
  pointing at the Delphi record on the Oracle Panel.

Until that re-render lands, those two sections cannot render from the
separated feeds. That is the known, intended handoff state of this
spec — not a defect in the feeds.
