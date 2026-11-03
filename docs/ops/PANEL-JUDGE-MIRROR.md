# Panel Judge Mirror 🪞 — Experiment Layer Spec (v0)

Owner directive 2026-11-03: "replicate the known judges
as our own panel judge mirror system (TV show BULL &&
Lie To Me — Paul Ekman, actual science)". Registered in
`docs/ops/DOE-FAMILY.md` (Method versions). Sits in the
Podium test-plan family (SYSTEM-REVIEW-2026-11-03): the
mirror is the instrument test ③ (judge-panel effects)
uses where real attribution is disclosure-blocked.

## Concept

A mirror panel: simulated replicas of known judges that
pre-score our entries the way the real panel plausibly
will. Two method legs:

- **BULL leg — mirror-jury construction.** Personas are
  assembled from evidence; a mock panel of personas
  deliberates over a submission and surfaces
  objections/enthusiasms PER PERSONA (the jury-service
  read: who objects, to what, how strongly, and what
  would move them).
- **EKMAN leg — observable signals only.** Personas are
  modeled from OBSERVABLE SIGNALS, never vibes: the
  judge's receipted podium history (what they actually
  picked), public statements/writing, role/employer
  incentives, venue behavior. EVERY preference claim in
  a persona cites its signal. A preference claim with no
  cited signal is not a persona element — it is a
  fabrication and is struck at build review.

## Inputs

Fed through the challenge_opportunity_pipeline:
podium-dataset judge rows · competition-import
receipts · the known set today = the RAISE pool
(Debnath · Cochrane + ~40 pool rows; POOL_UNRESOLVED
portions flagged and never silently resolved) · venue
patterns for D0/D1 (panels unpublished — see Grades).

## Grades (honesty rails, binding)

- **PERSON-GRADE** — only where identity AND signal are
  established by receipts: a named judge, with per-claim
  cited signals. Person-grade mirrors may carry
  effect estimates for test ③.
- **VENUE-ARCHETYPE grade** — where the panel is
  NOT_ESTABLISHED. D2 is the standing case:
  PANEL_PUBLICLY_UNNAMED, registered as gap **GAP-J1**.
  Archetype personas are built from venue patterns
  (published criteria, weights, prior editions' outcomes)
  and are labeled archetype-grade ON EVERY OUTPUT.
  No fabricated named judges; no invented preferences —
  an archetype's preferences are the venue's published
  criteria wearing a seat, and say so.
- **Mirrors are MODELS.** Every mirror verdict stamps
  {grade · evidence basis · model} and never presents
  as the real judge's view, prediction guarantee, or
  inside knowledge.

## Persona schema

```
persona {
  persona_id            # stable id
  grade                 # person | venue-archetype
  identity              # person: {name, role, employer} as receipted
                        # archetype: {venue, seat_pattern}
  gap_flags             # [GAP-J1 | POOL_UNRESOLVED | ...]
  signals[] {           # EKMAN leg: observable only
    type                # podium_history | statement | writing |
                        # incentive | venue_behavior | venue_criteria
    ref                 # resolvable receipt (issue/PR/URL of record)
    observed            # what the signal actually shows
  }
  preference_claims[] { # each claim cites >= 1 signal ref
    claim, signal_refs[], strength: weak|moderate|strong
  }
  model { builder, version, built_at }
}
```

A persona failing the citation rule (any preference
claim with empty signal_refs) is INVALID and does not
sit on a panel.

## Experiment shape (DoE discipline)

- Mirror scores are **RECORDED FORECASTS** (test-⑥
  machinery): filed BEFORE the real outcome, scored
  when real placements publish — Brier score per
  probability forecast, hit-rate per categorical call.
  Leave-one-edition-out (LOEO) evaluation across venues
  as n grows.
- Test ③ consumption: person-grade mirror panels carry
  the panel-effect ESTIMATES (does this panel-shape
  reward X?); archetype-grade output stays DESCRIPTIVE
  (a structured self-assessment against venue criteria)
  and never enters effect estimates.
- **Shape-constant warning (binding self-check).** A
  mirror panel that scores everything alike carries no
  signal (the Delphi lesson, EGM instance #2). Every
  run reports its DISPERSION (per-persona spread +
  cross-subject spread when run on >1 subject); a run
  whose personas do not discriminate files a NULL
  verdict on itself in its own record.
- Forecasts live in
  `experiments/doe/panel-judge-mirror/forecasts/`
  (append-only; a forecast is never edited after the
  outcome publishes — corrections are new records).

## First subjects

- **D1** — post-freeze self-assessment vs the field
  SWOT; the Gate-1 screen simulated. (First run below:
  venue-archetype — the D1 panel is unpublished.)
- **D2 slate candidates** — archetype-grade (GAP-J1);
  the pre-pick mirror read is ONE advisory input beside
  the ⛏️ charter, never binding.

## Continuous improvement — forecast layering (owner, 2026-11-03)

"Must continuously improve 🎯" — applied to the mirror:
the first run on a subject is a BASELINE, not a verdict.
While the subject's improvement window is open, the
mirror RE-RUNS on each material improvement landing;
every re-run files as a new forecast LAYER (append-only;
the baseline stays citable, never edited). Done only
when the window closes (for D1: the Nov 4 23:59 PT
freeze).

Re-run triggers (D1 line, coordinated with the D1 seat):
1. Strands proof closes (run-3 receipt with tool chain)
   ∧ any stamp upgrade;
2. 0.2.0 cuts green + the release of record advances;
3. the v1.0.0 cut.

Each layer's record shows the IMPROVEMENT CURVE against
the baseline: panel score delta + WHICH basis term
moved — Strands depth · sample content · surfaces (or
"no basis term moved" when a re-run is flat, which is
itself the datum). Layers score against the same
outcome when it publishes; the curve is the improvement
evidence, the Brier score is the calibration evidence.

## Measured quantity: judge↔criteria alignment (owner probe, 2026-11-03)

When a venue's placements publish, compute the
ALIGNMENT READ for that venue:

- winners' coded features (coded under the FROZEN
  codebook — the podium shape taxonomy as frozen for
  the test plan; no re-coding to fit the outcome) vs
- the venue's VERBATIM rubric/requirements (the
  spec/import of record — the issuer's own text, never
  a summary).

The read answers two things: (1) does the picked set
OVER-INDEX on the stated criteria (which criteria the
winners actually saturate), and (2) where does it
DEVIATE — the taste terms: winner features the rubric
never mentions, and stated criteria the winners
collectively ignore.

Filing + consumption:
- Filed PER VENUE as a dataset layer (podium dataset)
  at the placements-publication moment. Capture legs:
  D0 = capture #4547; D1 = its judging close
  (2026-11-18). Each layer cites {placements ref ·
  codebook version · rubric import ref}.
- Mirror input: the read yields a venue-level
  **criteria fidelity** parameter consumed by
  archetype seats (how literally this venue's outcomes
  track its stated criteria — archetype personas weight
  their venue-criteria preferences by it).
- **Per-judge fidelity: only where picks become
  attributable. Today that count is 0 — do not
  manufacture.** (Venue-disclosure-bound, per the
  system review's hardened C1-D1.)
- Test-plan join: the alignment read is EVIDENCE for
  test ① (winner patterns) and test ⑤ (rubric
  sensitivity) in the Podium test plan.
- Resequence gate: alignment RUNS obey the resequence
  gate — intake stamps re-issue first; this section
  registers the quantity and its hooks, it does not
  itself fire a run.
