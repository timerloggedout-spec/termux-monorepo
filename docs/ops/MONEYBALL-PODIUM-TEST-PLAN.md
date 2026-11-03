# MoneyBall — Podium-Dataset ML Test Plan (SPEC, pre-registered)

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` · **Owner GO:** 2026-11-03 09:17 PT (via main). **Status: SPEC ONLY — no test has run.** Hypotheses + kill signals below are stamped BEFORE any dataset access (pre-registration discipline).

## Dataset (external leg — scraping lane build)

- **Source of record:** the D2 seat's podium leg (exercise record): per venue × edition — {editions · judges · placements · projects · comments (judge + community, distinguished)}.
- **Build owner:** scraping lane (their build; this plan consumes it, does not scrape).
- **Version pin (hard):** every result row carries `dataset_version` (content hash / version id issued by the dataset build). A result without the pin is not a result and does not enter the book.
- **Unit discipline:** edition is the stratum. No pooling across venues/editions without a per-stratum read first (strata never pooled — DoE conformity).
- **Exclusion:** EGM instance-#2 test-stamped filings (canonical key `EGM instance #2 TEST filing`, secondary `RFP-EGM2-`) never enter dataset-derived evidence (owner ruling 2026-11-03).

## Cross-cutting rules (bind all six tests)

- **Exact methods only** at this n: Fisher exact / permutation / exact CIs. No asymptotic claims. Every result stamps its n per stratum.
- **Small-n honesty:** a result that cannot distinguish its effect from noise is reported as UNRESOLVED, never dressed.
- **Rule 9 + significance (B5):** any probability/standing language from these tests requires corroborated evidence legs and the significance standard; single-leg = HELD.
- **Book entry:** results enter the wagering book as EVIDENCE ROWS — appended to the relevant subjects' `expectation_record.evidence[]` (never as parallel numbers, B1), each row {test_id · dataset_version · n · effect · exact_ci · verdict ∈ {supported, refuted, unresolved} · kill_signal_state}.
- **winprob boundary:** the hidden metrics_internal winprob is not an input, output, or citation of this plan.

## Tests

### ① Winner-pattern validation
- **Question:** do podium projects show {proof-grounded claims · enterprise-workflow fit · approval-gates} more often than field (non-podium) projects?
- **Method:** per-project binary feature coding (codebook fixed before coding); per feature: Fisher exact podium-vs-field per edition, odds ratio + exact CI; cross-edition consistency read.
- **Hypothesis:** ≥2 of 3 features show OR > 1 with exact CI excluding 1.0 in the pooled-consistent direction, and no feature reverses in ≥ half the editions.
- **Kill signal:** ∀ features CI includes 1.0, OR any claimed feature reverses direction in ≥ half the editions ⇒ pattern claim DEAD; recorded as a refuted evidence row.

### ② Room / crowding curves
- **Question:** how does podium share move with category entry count, per category per edition?
- **Method:** descriptive curve per category × edition {entries · podium slots · podium share}; elbow/non-linearity read visually + by segment split at the median crowding.
- **Hypothesis:** podium share declines with crowding, with a steeper decline past the median (elbow).
- **Kill signal:** podium share flat or rising with crowding in ≥ half the category-editions ⇒ crowding model DEAD; slate advice stops citing room size.

### ③ Judge-panel effects
- **Question:** do repeat judges (≥2 editions) reward a consistent project shape?
- **Method:** shape profile per project (the ① feature set + category); for each repeat judge, similarity between their editions' podium picks; permutation null (shuffled judge labels, 10,000 draws).
- **Hypothesis:** observed mean similarity > 95th percentile of the permutation null.
- **Kill signal:** similarity ≤ null median, or permutation p > 0.10 ⇒ no judge-effect claim; panel composition treated as noise in all downstream reads.

### ④ Comment-signal
- **Question:** do judge-comment themes predict placement beyond community-comment themes?
- **Method:** theme codebook fixed before coding; per theme: exact association with placement, computed separately for judge comments and community comments; incremental read = judge-side association among projects where community signal is held flat.
- **Hypothesis:** ≥1 judge theme carries an association with placement that community themes do not (incremental signal exists).
- **Kill signal:** judge themes add no incremental association (Δ ≈ 0 or negative ∀ themes) ⇒ comment-signal leg DEAD; comments used as color only, never as evidence.

### ⑤ Ranking stability (D2 six candidates)
- **Question:** is the D2 candidate slate's relative ranking stable under each edition's inferred rubric?
- **Method:** infer per-edition rubric weights from that edition's podium-vs-field feature contrasts (① machinery); score the six D2 candidates under each edition rubric; read Kendall's W + pairwise flips + top-3 membership changes across rubrics.
- **Hypothesis:** top-3 membership is identical under ≥ half the edition rubrics.
- **Kill signal:** top-3 membership changes in > half the edition rubrics ⇒ the slate ranking is RUBRIC-FRAGILE and must be labeled as such wherever the ranking is cited (including the D2 scoring return).

### ⑥ Backtested forecast (gate for any forward use)
- **Question:** can a model trained on editions ≤ n predict edition n+1 podium membership above base rate?
- **Method:** rolling origin over editions (train ≤ n → predict n+1, all n available); features = ① set + ② crowding + ③ panel where live; hit accounting exact vs the edition base rate.
- **Pre-registered hit criterion:** top-k precision (k = podium slots) exceeds base rate with exact CI excluding base rate, on ≥ 2 rolling origins.
- **Kill signal:** first full backtest misses the criterion ⇒ forecast leg stays OFF — no forward use, no exceptions, miss recorded as evidence. A pass on one origin is not a pass; the criterion is the gate.

## Sequencing + review

1. Dataset build + version pin (scraping lane) → dataset record lands; version cited back to this seat.
2. **Validation design review** with Tests · LLM Validation (6fcaa7f8) on this spec BEFORE any run — exact-test choices, codebook discipline, hit criteria.
3. Runs in order ① → ② → ③ → ④ (⑤ needs ①'s rubrics; ⑥ needs ①–④ survivors).
4. Each verdict lands as book evidence rows (dataset_version pinned) + a report ↑main; killed legs are reported as killed, not quietly dropped.
