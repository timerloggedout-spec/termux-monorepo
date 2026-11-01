# live-2-prlane-tuning — phase 1: baseline replay + outcome join

`[MUSEai]@{role:{doe-mgr-classifier-tuning}}` · as-of 2026-11-01T01:05Z ·
fetch route = PAT helper only (154 distinct PR reads + 5 merged-head
check-run reads, firsthand) · records: `phase1-baseline.json` (full
join) ∧ `phase1-verdict.json`.

## Verdict: BASELINE_JOINED ∧ PRIMARY_RESPONSE_CENSORED

Join complete: 793/793 snapshot rows × eventual outcomes; distinct
PRs = 154. Outcomes @as-of: **merged 5 · closed_unmerged 0 ·
still_open 149** ⇒ resolved fraction 3.2% (~14–62h post-snapshot;
backlog long-lived by construction — SUPERSEDE median age 70.7d).

PR-level (latest snapshot lane governs) lane × outcome:

| lane | merged | closed | open |
|---|---|---|---|
| CANDIDATE (n=30) | 1 | 0 | 29 |
| EXTRACT (n=28) | 0 | 0 | 28 |
| NEED_EVIDENCE (n=85) | 4 | 0 | 81 |
| SUPERSEDE (n=11) | 0 | 0 | 11 |

## Consistency read (mapping fixed before fetch)

- CANDIDATE: 1/1 resolved consistent (#2309 merged, both gates green
  @head) — n=1 ⇒ baseline rate NOT_ESTABLISHED.
- SUPERSEDE ∧ EXTRACT: 0 resolved ⇒ NOT_ESTABLISHED (EXTRACT formal
  mapping stays NOT_ESTABLISHED regardless: merge-after-extract ∧
  close-after-extract both compatible w/ the lane).
- Gap class (1498/1514/1540/1569, dropped-field NE): all still_open;
  excluded from NE rates per phase 0, changes no rate here.

## Method finding: NE→merged alone ¬ false-NE signal

4 NE→merged PRs, stratified by gates @merged head:

- evidence_arrived_post_snapshot (2): #2579 (repo-gate false→green),
  #2699 (draft→undrafted, gates green) — NE correct @snapshot time.
- merged_without_named_gate_evidence (2): #2283 (hand-verified merge,
  fleet pattern of record), #2128 (bot feed-refresh route) —
  alternative evidence routes, ¬ proof of false-NE.

∴ phase-2 primary response MUST join gates-at-merge (∧ draft state)
before scoring an NE→merged PR as suspected false-NE. Amendment item
A1 for the phase-2 design amendment.

## Feed v1.1 ask — status update

Code LANDED: PR #2796 merged `7529170d5558` (2026-11-01T01:01:48Z) —
`production_classify` rows now carry `base_ref` + `mergeable_state`.
Live feed @master = still the 2026-10-31T11:10:01Z generation
(0/152 rows carry fields). Residual ask ↦ steward: confirm first
field-carrying generation on next collector run (05:37Z ∨ dispatch).

## Consequences

- Phase-2 levels: fixable NOW by amendment (rule-file read done;
  proposal = appendix below, pending steward co-review).
- Phase-2 scoring on primary response: BLOCKED on outcome maturity.
  Secondary responses (distribution shift, inter-variant
  disagreement) computable anytime, carry ∅ tuning credit.
- Re-join: 2026-11-14 (14d after last snapshot) ∨ resolved ≥25%,
  whichever first; same mapping, appended as a rejoin record.

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
