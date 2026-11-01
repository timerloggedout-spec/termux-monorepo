# live-2-prlane-tuning — phase 1: baseline replay + outcome join

`[MUSEai]@{role:{doe-mgr-classifier-tuning}}` · as-of
2026-11-01T01:05-01:13Z (two fetch passes) · fetch route = PAT helper
only (157 distinct PR reads + merged-head check-run reads, firsthand)
· records: `phase1-baseline.json` (full join) ∧ `phase1-verdict.json`.

## Verdict: BASELINE_JOINED ∧ PRIMARY_RESPONSE_CENSORED

Join complete: 945/945 snapshot rows (8 snapshots) × eventual
outcomes; distinct PRs = 157. Outcomes @as-of: **merged 6 ·
closed_unmerged 0 · still_open 151** ⇒ resolved fraction 3.8%
(backlog long-lived by construction — SUPERSEDE median age 71.3d).

PR-level (latest snapshot lane governs) lane × outcome:

| lane | merged | closed | open |
|---|---|---|---|
| CANDIDATE (n=31) | 1 | 0 | 30 |
| EXTRACT (n=28) | 0 | 0 | 28 |
| NEED_EVIDENCE (n=87) | 5 | 0 | 82 |
| SUPERSEDE (n=11) | 0 | 0 | 11 |

## Consistency read (mapping fixed before fetch)

- CANDIDATE: 1/1 resolved consistent (#2309 merged, both gates green
  @head) — n=1 ⇒ baseline rate NOT_ESTABLISHED.
- SUPERSEDE ∧ EXTRACT: 0 resolved ⇒ NOT_ESTABLISHED (EXTRACT formal
  mapping stays NOT_ESTABLISHED regardless: merge-after-extract ∧
  close-after-extract both compatible w/ the lane). Suspected
  false-S cases = 0.
- CANDIDATE-still-open-old watch (age ≥40d, DESIGN stratum): EMPTY —
  30 CANDIDATE still-open, max snapshot age 12.1d (addendum record).
- Gap class: snapshots 1–7 = {1498, 1514, 1540, 1569} (dropped-field
  NE, phase 0); snapshot 8 self-describes in-row — members
  {1498, 1514, 1540, 1541, 1569} (base_ref ≠ master; 1541 new, cue/
  base, repo-gate also false). All still_open; excluded from NE
  rates, changes no rate here.

## Snapshot 8 + feed v1.1 — CLOSED

First field-carrying generation landed: feed 2026-11-01T01:02:29Z
(commit `102db9aa480d4`, blob `5b5b2137ec63`), 152/152 rows carry
`base_ref` + `mergeable_state` (steward PR #2796). Extracted in this
PR as `snapshots/feed-2026-11-01T010229Z.json` + INDEX row (point 8,
counts 30/28/83/11). Replay w/ in-row fields (updated
`reconstruct()`, companion PR) = **EXACT 152/152** — 0 mismatches,
counts reproduced; snapshots 1–7 keep the recorded-gap fallback.
Cross-check: PRs absent from snapshot 8's open list vs 1–7 ==
exactly the then-merged 5.

## Method finding: NE→merged alone ¬ false-NE signal

5 NE→merged PRs, stratified by gates @merged head:

- evidence_arrived_post_snapshot (2): #2579 (repo-gate false→green),
  #2699 (draft→undrafted, gates green) — NE correct @snapshot time.
- merged_without_named_gate_evidence (3): #2283 (hand-verified
  merge, fleet pattern of record), #2128 (bot feed-refresh route),
  #2797 (fleet-publisher bot route) — alternative evidence routes,
  ¬ proof of false-NE.

∴ phase-2 primary response MUST join gates-at-merge (∧ draft state)
before scoring an NE→merged PR as suspected false-NE. Amendment
item A1 for the phase-2 design amendment.

## Consequences

- Phase-2 levels: fixable NOW by amendment (rule-file read done;
  proposal = appendix below, pending steward co-review).
- Phase-2 scoring on primary response: BLOCKED on outcome maturity.
  Secondary responses (distribution shift, inter-variant
  disagreement) computable anytime, carry ∅ tuning credit.
- Re-join: 2026-11-14 ∨ resolved ≥25%, whichever first; same
  mapping + `scripts/doe/prlane_outcomes.py`, appended as a rejoin
  record.

## Appendix — phase-2 factor-level proposal (PENDING steward co-review)

Read from rule files @master (¬ invented):

| factor | source | levels |
|---|---|---|
| ancient_days | `supersede_rules.is_ancient(days=40.0)` | 30 · **40 control** · 60 |
| extract_files | `minesweeper_rules.files_over_extract_threshold(40)` | 25 · **40 control** · 60 |
| gates_posture | `classify_pr` gates rule (both required) | **both control** · repo-gate-only |

Fixed (¬ factors): draft ∨ dirty ∨ base≠master ⇒ NE (hard blockers);
title-token vocabularies (pulse/minesweeper) = vocabulary, ¬ thresholds.
Full factorial = 3×3×2 = 18 cells (control included). Regression
margin + A1 response amendment land w/ the amendment, after steward
co-review. Phase 3 (decide/laya weights) untouched by this record.
