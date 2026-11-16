# Pass record — strands-rfp-response (first live Oracle Method pass)

**Run:** 2026-10-27 · **Brief:** `brief.json` (this directory) ·
**Evidence:** `evidence.json` — 123 stamped items, 8 read-only API
calls · **Generator:** `scripts/delphi/generate_proposal.py --pass` ·
**Cycle:** `scripts/delphi/method_cycle.py`

## Candidates (n = 3, generated)

| Candidate | Concept |
|---|---|
| strands-rfp-response-kernel-first | Extend the merged offline kernel along the matrix's experiment order (E-05, E-01, E-03) |
| strands-rfp-response-collection-first | Build the DEBATE collection plane (ITEMS-003) so the panel is executable when entitlement lands |
| strands-rfp-response-packaging-first | Generalize the D0 Lambda packaging as the deployment shape, up to the account gate |

Candidate documents live in `docs/proposals/active/<candidate-id>/`
and are registered in `docs/proposals/registry.yaml`
(`author: oracle-method`).

## Outcome

- **Round 1 (cross-vote):** collection-first > kernel-first >
  packaging-first. Ballots: LOCAL_BASELINE 5 (panel-role rubric
  comparator); HUMAN_COLLABORATOR 0; MODEL_PROVIDER 0 — no human
  ballot was cast and model voting is disabled; both stated, not
  filled in.
- **Expectations recorded before implementation:**
  round-1-derived priors per class, plus brief-author priors
  (`BRIEF:delphi-lane`): kernel-first 1/19, collection-first 2/16,
  packaging-first 3/13.
- **Implementation round:** all three variants implemented offline
  in-repo and tested per proposal — 9 suites, 9 passed
  (`implementation/` holds the per-candidate records; code:
  `scripts/delphi/{kernel_experiments,ballot_collector,budget_breaker}.py`,
  tests: `tests/test_strands_pass_*.py`).
- **Round 2 (equalized evidence):** every voter scored from the
  identical per-proposal test-results bundle
  (sha256 in `cycle/BALLOT-round2.json`). Ranking held:
  collection-first > kernel-first > packaging-first.
- **Calibration:** LOCAL_BASELINE priors held within tolerance.
  The brief author's priors missed the top two (expected
  kernel-first first; the evidence ranked collection-first first) —
  rank deltas recorded in `cycle/CALIBRATION.json`, feeding the
  weighting/elo ledgers as designed.
- **Correction (2026-10-27):** the rankings above are a
  **tie-break order, not a score result**. The LOCAL_BASELINE scores
  tied exactly in both rounds (round 1: 23.269 for all three
  candidates; round 2: 25.0 for all three), with numerically
  identical evidence profiles on every scored dimension; the
  recorded order is `cross_vote.py rank()` sorting by
  `(-score, candidate_id)` over tied scores. Any reading of the
  order as an evidence preference (e.g. "broadest evidence base
  won") is withdrawn. The calibration rank deltas stand as
  arithmetic against the recorded order; under a tie, any strict
  prior order misses. The panel feed carries `ranking_basis`
  stating this per round.

## Specified not run

- **AWS deployment (ITEMS-007):** `specified_not_run` — card rule;
  no account exists and none was created.
- **Model panel (ITEMS-006):** `specified_not_run` — model voting
  disabled (`DELPHI_LLM_MAX=0`); the collection-first candidate is
  the build that makes it executable when a no-cost entitlement is
  validated.

## Ledger records

Ranked outcome and calibration appended to the outcome ledger
(issue #1487) as `delphi-generation-ballot v1` and
`delphi-generation-calibration v1` JSON comments; full receipts in
`cycle/` in this directory.
