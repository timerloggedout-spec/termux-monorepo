# MoneyBall — Podium-Dataset ML Test Plan (SPEC, pre-registered)

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` · **Owner GO:** 2026-11-03 09:17 PT (via main). **Status: SPEC ONLY — no test has run.**
**Review state:** Tests · LLM Validation FORMAL review of record = **APPROVED WITH CORRECTIONS** (C1–C9; the formal review supersedes the same lane's earlier brief-level review where they differ — notably C2's frozen BINARY codebook + re-code supersedes the brief's ternary-handling gate). **Amendment #2 (this text) incorporates C1–C9; on its landing the review leg stamps the review closed and runs may proceed in sequence** (③ expected blocked-not-run unless judge↔track linkage is sourced).

## Dataset facts of record (D2 podium leg, PR #4491)

- n = **11 placed projects** · ~4 events · 2nd/3rd placements mostly NOT_ESTABLISHED · per-track judges ∅ · comments anecdotal · **field rows = ∅** (podium only).
- **Dataset version pin (G6/C5):** dataset = the PR #4491 record (`ops/challenge/coordinator.json` podium leg; PR-head blob `150e7429e2ef05d2`). Every result row names this pin exactly; a record update re-pins by hash, prior rows keep theirs.
- Missingness is MNAR (winners publicized, losers not); every denominator states {observed / eligible + mechanism}.
- **Exclusion:** EGM instance-#2 test-stamped filings (canonical `EGM instance #2 TEST filing`, secondary `RFP-EGM2-`) never enter dataset-derived evidence.
- **Contamination (G5):** tags cite the **canonical project page URL** per project; lablab injected-module text is NEVER a feature source (Ariadne false lead precedent); Vortex IQ vs Unmask = disputed ⇒ excluded per Rule 9 until resolved.

## Dataset-build requirements (C1/C3/C8 — scraping-leg amendments)

1. **Field sampling (C1):** field projects per edition = **all gallery submissions** for that edition (entries := gallery submissions, NOT approved registrants — the two counts differ, cf. D2 field 2,302 approved vs gallery). If volume forces sampling: a stated random sample with the seed recorded in the dataset record. No silent selection.
2. **Feasibility stamps (pre-run, published in the dataset record):** per edition {podium n · field n} (C1) · {# repeat judges with attributable picks} (C3) · {# projects with judge comments · # with community comments} (C8) · category×edition denominator counts (C7) · count of editions with usable ⑤ rubrics (C9).
3. **Judge↔track sourcing (C3):** the only leg that can unblock ③; separately pinned if it lands.

## Codebook (C2 — frozen here, supersedes prior tag handling)

- The podium leg's P/E/H tags **predate this codebook** (single tagger, ternary) — reusing them would void "codebook fixed before coding" in fact. **All coding is redone** from canonical project pages under this frozen **BINARY** codebook (`codebook_version: podium-codebook/v1`):
  - **proof-grounded (P):** the project page presents verifiable execution evidence (live demo / repo / run output) for its central claim — yes/no.
  - **enterprise-workflow (E):** the project targets an organizational workflow with named roles/approvals/integrations — yes/no.
  - **approval-gates (H), STRICT:** a formal pre-action approval step is a described mechanism (a human or policy gate that must approve before the system acts) — yes/no. The loose "human in the loop somewhere" reading is a DIFFERENT feature and is not coded (podium-leg contrast: strict H = 1/11, loose = 6/11 — the test result is whichever definition is frozen; frozen = STRICT).
- **Double-tag:** all 11 podium projects + an equal-sized field sample, two independent taggers; Cohen's κ per feature published in the plan record; adjudication logged. Theme coding (④) double-codes a sample under the same discipline.

## Evidence-row schema (C5 — final)

`{test_id · dataset_version · stratum (edition id; n as per-stratum map for per-edition tests) · effect · exact_ci · verdict ∈ {supported, refuted, unresolved, blocked, descriptive} · family ∈ {primary, exploratory} · codebook_version · kill_signal_state}`

**blocked ≠ killed:** kill = evidence AGAINST the hypothesis; blocked = no test existed (missing linkage/corpus). The book carries the distinction.

## Tests (amended #2)

### ① Winner-pattern validation — PRIMARY claim (C6)
- **The primary claim is the composite:** ≥2 of 3 features {P · E · H-strict} associate with podium placement. No family-wise claim is made across tests; ②③④ rows are exploratory-labeled.
- **Statistic:** Fisher exact, one-sided, per edition; cross-edition read by **Fisher combined-p** (named combination rule — no silent pooling; strata rule intact).
- **Kill (numeric):** combined corrected p > .05 **∨** OR < 2 ⇒ claim DEAD (refuted row).
- **Feasibility:** runs only when C1 field rows + feasibility stamps exist per edition; per-edition podium n ≈ 1–3 ⇒ per-edition Fisher ≈ 0 power — the combined-p read is the test, per-edition numbers are reported as strata, not claims.

### ② Room / crowding — descriptive-first (C7)
- **The median-split IS the test** (podium share below/above median crowding per category); any visual curve is color only, never evidence.
- Category×edition denominator counts published pre-run; **cells < 6 ⇒ verdict UNRESOLVED** (small-n rule). Entries := gallery submissions (pinned definition, C1).
- Stays descriptive unless ≥3 editions carry ≥2 categories with field+podium counts.

### ③ Judge-panel effects — expected BLOCKED-NOT-RUN (C3)
- Judge→track/pick attribution is NOT_ESTABLISHED; "their editions' podium picks" presumes the missing linkage — the statistic is undefined on current sources.
- Permutation mechanics (if linkage ever lands): 10,000 draws, **shuffle WITHIN edition×track strata**; kill = similarity ≤ null median ∨ p > 0.10.
- **Feasibility stamp decides:** {# repeat judges with attributable picks} = ∅ or < 3 ⇒ ③ recorded **blocked** (not killed, not run). Fallback until then: pool-overlap descriptive.

### ④ Comment-signal — BLOCKED as inference on current corpus (C8)
- Feasibility stamp {# with judge comments · # with community comments} pre-run; the "community held flat" stratification empties cells at this n ⇒ **downgraded to per-source associations only** (judge-side and community-side reported separately, no conditional claim).
- Δ is defined pre-coding: **Δ = Δ log-OR (judge vs community) per theme**; kill = Δ ≤ 0 ∀ themes ⇒ no incremental signal.
- Theme codebook = second codebook ⇒ C2 double-coding on a sample applies. Qualitative theme inventory (n = quotes-found stated) is the current honest output.

### ⑤ Ranking stability (D2 six candidates) — CONDITIONAL (C9)
- **Anchor ranking:** the published-criteria rubric (Agent Rush 2026: Application of Technology / Presentation / Business Value / Originality) is the reference read, pre-registered. Inferred per-edition rubrics = sensitivity spread, exploratory-only.
- Editions where features are constant within podium contribute ∅ rubrics (unidentified) — the count of **usable rubrics is stamped**; inference from podium n ≈ 1–3 is acknowledged as the bound.
- **Metric:** Kendall's W + per-candidate rank range across rubrics.
- **Kills (numeric, either fires):** any candidate rank-range ≥ 4 of 6 **∨** Kendall's W < 0.5 ⇒ RUBRIC-FRAGILE label fires wherever the slate ranking is cited (incl. the D2 scoring return); ∅ winner claim.

### ⑥ Backtested forecast — gate for any forward use (C4)
- **Selection leakage fix (binding):** feature survival is re-decided **within each origin on train editions only** (nested selection). Any row computed otherwise is stamped `feature_selection: in-sample` and the gate criterion below applies ONLY under nested selection.
- **Definitions (exact, pre-run):** prediction unit = **project-level podium membership** in edition n+1; **k = the number of podium slots in the predicted edition (across tracks)**; target = project-level membership (not winner-shape, not candidate rank — fixed here).
- **Form:** leave-one-edition-out × 4 folds vs a base-rate predictor (Brier or hit-rate chosen pre-run); fallback feature set if ③ blocked = ① + ② features only.
- **Hit criterion (unchanged, brutal):** top-k precision > base rate with exact CI excluding base rate on ≥ 2 origins, under nested selection.
- **Kill:** forecast ≤ base-rate predictor, or first full backtest misses the criterion ⇒ leg OFF, no forward use; miss recorded as evidence.
- **Tag leakage:** per-fold blind re-tag, OR tags stamped as fixed features with a leakage caveat on the evidence row.

## Cross-cutting (unchanged)

Exact methods only · small-n honesty (UNRESOLVED is a verdict, not a failure to hide) · Rule 9 + significance (B5) on any probability language · winprob never an input/output/citation · results enter the book ONLY as evidence rows (schema above) · killed AND blocked legs reported as such ↑main.

## Sequencing

1. Dataset-build amendments land (field rows + feasibility stamps + pin update) — scraping leg.
2. C2 re-code under `podium-codebook/v1` (double-tag, κ published).
3. Review leg stamps the review closed on this amendment.
4. Runs in sequence ① → ② → ⑤ → ⑥; ③④ remain blocked/descriptive until their sourcing exists.
