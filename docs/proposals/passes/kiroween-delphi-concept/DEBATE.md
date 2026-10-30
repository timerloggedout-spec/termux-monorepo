# DEBATE record — kiroween-delphi-concept (stage 2b, calibration)

**Called:** by manager ruling 2026-10-30 (routed via the
challenge-entries lane), after round 1 tied. **Ran:** 2026-10-30,
ahead of the 2026-11-06 deadline. **Receipts:**
`cycle/FEEDBACK.json` (the stage outcome), `cycle/debate-ballots.json`
(the five revision ballots as supplied), `cycle/SYNTHESIS.json`
(the feedback they answer).

## Standing of this round

The variant freeze does **not** rest on this ballot. The manager
froze **skeleton-crew** on 2026-10-30 on the brief-author priors
(19/17/14), the profile points (3/2/2), and scope certainty — a
manager decision recorded by the challenge-entries lane; the
project repo (`timerloggedout-spec/skeleton-crew`) was created
in-period the same day (2026-10-30T23:55:28Z). Under the
superseding ruling this DEBATE round is **calibration-only**: it
tests whether a discriminating ballot, built from the record,
supports or contradicts the priors the freeze used.

## Why round 1 could not discriminate

The round-1 rubric scores generation-profile dimensions only
(evidenced ratio, unverified count, items, evidence sources,
dependency items). All three candidates are identical on every
one (1.0 / 0 / 3 / 2 / 0), so round 1 tied at 23.269 × 3 by
construction. The synthesis therefore preserved no discriminating
argument — the dimensions on which the candidates actually
differ were never scored.

## The revision ballots

Five ballots, one per panel role (`debate:<role>`, LOCAL_BASELINE),
each answering the synthesis with a `revision_reason` (intake
enforces rationale + evidence_refs + revision_reason). Each role
re-scores on five dimensions evidenced in the brief and the
generated proposals, combined as `score = clamp25( Σ w_d · f_d )`
with per-role weights `w` (each role's lens), features `f`:

| dimension | definition | skeleton-crew | frankenstein | resurrection |
|---|---|---|---|---|
| evidence | evidenced_ratio (profile) | 1.000 | 1.000 | 1.000 |
| breadth | evidenced points / max points | 1.000 (3) | 0.667 (2) | 0.667 (2) |
| plan | plan steps / max steps | 1.000 (7) | 0.857 (6) | 1.000 (7) |
| risk | min risks / risks | 0.667 (3) | 1.000 (2) | 1.000 (2) |
| certainty | central input named in the brief? | 1.0 (CMDB design) | 1.0 (PRs #1620/#1702) | **0.5 — corpse selection not recorded; its own brief item stays `planned`** |

Role weights (evidence / breadth / plan / risk / certainty):
OPERATOR .30/.20/.20/.20/.10 · builder .15/.15/.35/.25/.10 ·
reviewer .40/.30/.10/.00/.20 · Scout .20/.30/.25/.15/.10 ·
cost_auditor .20/.10/.20/.40/.10. The formula and features are
stated here and in the ballots' rationales so the round is
reproducible from the record alone.

## Outcome

The stage outcome (`cycle/FEEDBACK.json`) aggregates the five
revision ballots **with** the five retained round-1 rubric
ballots (the machinery's composition; 10 LOCAL_BASELINE ballots;
HUMAN_COLLABORATOR 0, MODEL_PROVIDER 0 — stated):

- skeleton-crew **23.288** · frankenstein **22.865** ·
  resurrection **22.481** → skeleton-crew > frankenstein >
  resurrection.

Revision ballots alone (same ledger weights): skeleton-crew
23.308 · frankenstein 22.462 · resurrection 21.692 — same order,
wider spread; the retained rubric half is tied and only dilutes
the margin.

## Calibration reading

Against the brief-author priors (skeleton-crew 1/19,
frankenstein 2/17, resurrection 3/14): **rank agreement 3/3,
deltas 0/0/0**. The first discriminating ballot this pass
produced supports the order the freeze was enacted on. Formal
calibration (stage 6) still runs against these same priors when
round 2 executes on the post-Nov-8 implementation evidence; this
debate is recorded as calibration evidence, not as the stage-6
record.
