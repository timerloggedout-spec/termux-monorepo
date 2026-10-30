# Pass record — kiroween-delphi-concept (D4 Kiroween concept pass)

**Run:** 2026-10-30 · **Brief:** `brief.json` (this directory) —
finalized against the official rules the day they published
(challenge-entries lane's firsthand rules read; residual stamp
PR #2535) · **Evidence:** `evidence.json` — 13 stamped items
(9 official-rules packet claims, 4 challenge-log packet claims) ·
**Generator:** `scripts/delphi/generate_proposal.py --pass` ·
**Cycle:** `scripts/delphi/method_cycle.py`

This record supersedes the stated record of 2026-10-27
(`stated_not_run`, n=3, no candidates). Generation and round 1 ran
in-period on 2026-10-30; the implementation stage is gate-held
(see Specified not run).

## Candidates (n = 3, generated)

| Candidate | Concept |
|---|---|
| kiroween-delphi-concept-skeleton-crew | CMDB / reconciliation viewer run by a minimal spec-first Kiro crew (ingest, reconcile, report); category-shaped as foundation + two applications in two repo folders |
| kiroween-delphi-concept-frankenstein | One new in-window project stitched from proven public patterns (Delphi receipts, fetch_evidence provenance, quota-panel display); patterns cross over, no pre-built project |
| kiroween-delphi-concept-resurrection | A dormant public spec picked from the repo's ops docs / proposal registry and rebuilt fresh in-window, original spec as baseline + resurrection report |

Candidate documents live in `docs/proposals/active/<candidate-id>/`
and are registered in `docs/proposals/registry.yaml`
(`author: oracle-method`). All three candidates generated fully
evidenced (unverified points: 0 of 3 / 2 / 2); deadlines resolved
from the evidence, not asserted.

## Outcome

- **Round 1 (cross-vote): TIE.** All three candidates scored
  **23.269** (LOCAL_BASELINE, 5 panel-role rubric ballots) on
  identical scored profile dimensions (evidenced_ratio 1.0,
  2 evidence sources, 3 items each). The recorded
  `ranked_outcome` order (frankenstein, resurrection,
  skeleton-crew) is the `rank()` tie-break by candidate id —
  **not an evidence preference and not a winner**. No variant is
  frozen by round 1; the discriminating evidence is the
  implementation round (post-Nov-8 builds).
- **Ballots by class:** LOCAL_BASELINE 5; HUMAN_COLLABORATOR 0;
  MODEL_PROVIDER 0 — model voting is disabled
  (`DELPHI_LLM_MAX=0`) and no human ballot has been cast; both
  stated, not filled in. The owner's HUMAN_COLLABORATOR ballot
  and a DEBATE / revision round against the synthesis remain
  open as one decision point.
- **Expectations recorded before implementation:**
  round-1-derived priors per class, plus brief-author priors
  (`BRIEF:challenge-entries-lane (brief author)`, in
  `expectations.json`): skeleton-crew 1/19, frankenstein 2/17,
  resurrection 3/14. Calibration runs against these when round 2
  executes.
- **Facilitator synthesis issued** (`cycle/SYNTHESIS.json`) from
  the round-1 rationales; score spread 0 per candidate — no
  material disagreement to report.

## Eligibility

The generated concept proposals are not the competition project
and do not trip the eligibility gate. The brief's gate is stamped
from the official rules (s.1): the Submission Period opened
**Oct 30, 2026, 9:00 AM PT** (the rules prevail over the Devpost
dates page's 1:00 PM PT, corrected in the brief by both lanes'
stamps). Project creation timestamps must land in-period;
build work starts after Nov 8 per owner sequencing; deadline
Dec 4, 2026, 2:00 PM PT.

## Specified not run

- **DEBATE / revision round:** `specified_not_run` — callable
  against the synthesis, not automatic; no revision ballots
  supplied.
- **Implementation, evidence equalization, round 2,
  calibration:** `specified_not_run` — no per-proposal test
  results exist; the D4 build sequence runs after Nov 8 and a
  variant freeze precedes it. Round 2 opens on the equalized
  implementation evidence when the builds land.
- **Model panel ballots:** `specified_not_run` — model voting
  disabled (`DELPHI_LLM_MAX=0`).

## Ledger records

Round-1 ballot record appended to the outcome ledger (issue
#1487) as a `delphi-generation-ballot v1` JSON comment at run
time. Calibration appends when round 2 runs; full receipts in
`cycle/` in this directory.
