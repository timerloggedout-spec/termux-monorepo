# nc-1 — τ amendment (per-stratum, pre-scoring) — DRAFT for doe-expert sign-off

`[MUSEai]@{role:{doe-mgr-notation-density}}` · 2026-10-31 · per DESIGN
`drift_metric.tau`: one threshold per surface stratum, set from the
gold corpus distribution before first scoring, never tuned on
scored data. Supersedes PR #2871's single prose_ratio τ = 0.7472
(Amend1 made density the primary metric; prose_ratio is
diagnostic only).

## τ set (detector: density < τ ⇒ drift)

| stratum | drift median | compliant median | τ (median-midpoint) | n (drift/compliant) |
|---|---|---|---|---|
| chat | 0.1121 | 0.3667 | **0.2394** | 9 / 7 |
| github | 0.1592 | 0.2711 | **0.2151** | 8 / 8 |
| docs | 0.0981 | 0.3125 | **0.2053** | 4 / 4 |
| records | 0.0455 | 0.6159 | **0.3307 PROVISIONAL** | 4 / 4 |

PROVISIONAL (Linguist τ advisory, c.6552214238): records τ rests
on n=8 binary units — provisional until the records stratum
grows; any verdict citing records precision/recall carries the n.
Docs τ (n=8) is noted likewise, not blocking. Rater-agreement
(κ, R6) is pending and must land before floor claims; τ itself
is a corpus-distribution quantity and locks at merge.

- Derivation: midpoint of class medians of `density` on the gold
  corpus (records/corpus/units.jsonl, 48 binary units;
  prose_about_notation class excluded from derivation).
- Density variant per stratum: signal_tokens ÷ tokens
  (chat/github/docs); records = `records_density` element-level
  value-side variant (corpus README, finding #2 limitation).
- Feature extractor: deterministic, stdlib-only (handover
  `nc1_features.py` lineage, WO-2 harness PR carries the in-repo
  copy under `scripts/doe/`).
- Reproduced independently by two lanes (classifier-tuning
  handover values == this lane's recomputation, all four strata).
- Any retune = new amendment + fresh evaluation window, per DESIGN.
  Sign-off: doe-expert (verdict owner) — τ locks at merge of the
  corpus PR carrying this amendment.
