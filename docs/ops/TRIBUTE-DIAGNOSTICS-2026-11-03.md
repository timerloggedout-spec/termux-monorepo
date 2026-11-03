# Tribute Diagnostics — Help-Wanted Lane (Z3π0 HELP-WANTED)

_Judged firsthand by the Optimizations & Implementation
Assurance seat, 2026-11-03, from live PAT reads of all 132
ledger PRs plus the lane's own published record. The lane was
PAUSED for this review; no outbound contact was made. Method:
per-PR truth = the live API state (state, merged flag,
merged_at, state_reason, CI rollup); ledger rows = the
generated status board (help-wanted/data/status.json,
generated 2026-11-03T22:32:28Z)._

## Verdicts

Truth cohorts over the 132-row ledger (125 truth-resolved;
7 evidence-gap rows: operator repositories + 1 unresolvable):

| cohort | count |
|---|---|
| open | 8 |
| merged | 20 |
| closed unmerged | 97 |
| evidence-gap | 7 |

- Ledger `foreign_open_count` = 8 = truth 8 (Δ 0 — healthy).
- The ledger's "closed 117" conflates merged + unmerged: its
  `state` field has no merged value (the generator read only
  the search API's open/closed state and never `merged_at`),
  so merges were understated in the lane's own presentation.
- Fail rate (closed unmerged / resolved) = 97/125 = 77.6%;
  merge rate 16%. Against the 2026-10-27 efficacy audit (PR
  #1736: merged 16 · closed-unmerged 63 · open 28 · gaps 7),
  the fail rate moved ≈ −2.1 points — no improvement trend.
- Closed-unmerged CI picture: 37 had CI runs; 9 had a failing
  check; 24 were all-success; 60 had zero CI. CI failure is
  not the driver.
- Timing: 67/97 closures within 7 days of filing; 20 closures
  on 2026-10-27 alone (a maintainer cleanup wave).
- Maintainer-negative screen (13-row stratified sample, 9
  with foreign comments): 4 explicit stake-placeholder
  rejections, verbatim — "this PR only adds a placeholder
  file and isn't a fix" (kiinshuk/kinshow#434 ·
  Nano-Collective/nanocoder#1749 · marrabld/omazone#72 ·
  GlassHaven/Haven#657, the last noting follow-ups came
  "from the automation, not a person"). One sampled PR also
  staked an issue already assigned to another contributor.

## Finding T-1 — timeliness leg NOT ESTABLISHED by non-delivery

The review requested the lane's own claim set (which filings
were replies inside what window) to test maintainer-response
timeliness. The set never arrived. The timeliness leg is
therefore recorded as a FINDING — NOT ESTABLISHED by
non-delivery — not as an oversight of the review.

## Recommendation of record

NO-RESUME in the current pattern. Resume stays the owner's
call. The prerequisites below were built as machinery in the
same pass, so a future resume inherits gates, not intentions.

## Resume prerequisites — built 2026-11-03 (this record's PR)

1. **Ledger `merged` state.** `scripts/ci/tribute_status.py`
   now reads `pull_request.merged_at` from the search items,
   maps it to a first-class `state: "merged"` (with
   `merged_at`), and publishes `foreign_merged_count`. The
   20 verified merges were backfilled into all three ledger
   copies (generated board, dashboard data, landing mirror):
   state flips 20/20, `foreign_merged_count` 20.
2. **Filing gate.** Verified already wired in
   `scripts/ci/tribute_contribute.py`: no patch ⇒ no PR
   ("stake-only PRs are retired"), and
   `tribute_system1.preflight_pr` blocks placeholder diffs at
   the point of filing. The assignment check likewise
   pre-exists in `preflight_candidate` (an issue assigned to
   anyone but the lane makes it ineligible, reason
   `assigned:<login>`) and is re-run at contribute time.
   Regression-pinned by `tests/test_tribute_gate.py` (8
   tests: merged mapping ×1, volume caps ×3, assignment
   ×2, placeholder ×2) so a future refactor cannot silently
   unwire them.
3. **Per-repo volume discipline.** New named config
   `scripts/ci/tribute_gate_config.json` (schema
   `tribute-gate/v1`): `max_open_prs_per_repo` 2,
   `max_filings_per_repo_per_24h` 3 — enforced by
   `volume_gate()` in `tribute_contribute.py` before any
   fork/clone work; a breach skips the filing with
   `contribute_skipped_volume_cap`. Missing config falls
   back to the same conservative defaults, never unlimited.

## Conditional resume gates (for the owner's call)

(a) the stake-placeholder class stays abolished at the gate;
(b) no filing on an issue assigned to another contributor;
(c) outcome reporting runs only on the merged-aware ledger;
(d) the volume caps hold. The 8 live open PRs are untouched
by this review and by the prerequisites build.
