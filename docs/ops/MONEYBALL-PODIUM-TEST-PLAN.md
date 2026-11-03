# MoneyBall — Podium-Dataset ML Test Plan (SPEC, pre-registered)

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` · **Owner GO:** 2026-11-03 09:17 PT (via main). **Status: SPEC ONLY — no test has run.** Hypotheses + kill signals stamped BEFORE any dataset access.
**AMENDED PRE-REGISTRATION = PLAN OF RECORD (2026-11-03):** incorporates the Tests · LLM Validation design review (6fcaa7f8) wholesale — gates G1–G6 + per-test numeric kill signals + blocked/downgraded dispositions. The review's verdict was CONDITIONAL; this amended artifact is what the review leg re-reviews, and no test runs before that re-review clears.

## Dataset facts of record (D2 podium leg, PR #4491 — as reviewed)

- n = **11 placed projects** · ~4 events · 2nd/3rd placements mostly NOT_ESTABLISHED · per-track judges ∅ · comments anecdotal.
- **Dataset version pin (G6):** dataset = the PR #4491 record (`ops/challenge/coordinator.json` podium leg; PR-head blob `150e7429e2ef05d2`). Every result row names this pin exactly; a record update re-pins by hash and prior rows keep their pin.
- **Denominators (G4):** the dataset is podium projects only — there is NO field/control denominator in it. Missingness is MNAR (winners publicized, losers not). Every reported denominator states {observed / eligible + mechanism}.
- **Exclusion:** EGM instance-#2 test-stamped filings (canonical key `EGM instance #2 TEST filing`, secondary `RFP-EGM2-`) never enter dataset-derived evidence (owner ruling 2026-11-03).
- **Contamination (G5):** lablab explore-modules cross-inject descriptions (an Ariadne false lead entered and was refuted in-record). Rules: tags cite the **canonical project page URL** per project; injected-module text is NEVER a feature source; **Vortex IQ vs Unmask = disputed ⇒ excluded per Rule 9 until resolved**.

## Global gates (from the design review — bind all tests)

- **G1 TAGGING (blocks ①③④):** the P/E/H tags are single-tagger, ternary {yes · partial · no}, and "partial" carries the headline (P 10/11 ≥partial vs 5/11 strict-yes; H 1/11 strict). BEFORE any consumer test: a 2nd independent tagger on all 11 (n small ⇒ full double-tag), Cohen's κ per feature published, the "partial" rule frozen in writing, adjudication logged. **The coding rule is the result at this n.**
- **G2 NUMERIC KILLS:** every test files {statistic · α · kill threshold} pre-run (done per test below). A test that can't state its kill doesn't run.
- **G3 MULTIPLICITY:** ① is the sole PRIMARY test. All others are EXPLORATORY — the label rides every evidence row. (Alternative if the family ever claims jointly: Holm/BH across the family, pre-registered before the claim.)
- **G4 CONTROL GROUP (blocks ① as originally specced):** fix = harvest non-placed gallery projects per edition as controls (scraping-leg amendment), or ① downgrades to a within-podium descriptive tally (already done by the podium leg — not a validation test).
- **Rule 9 + significance (B5)** bind any probability/standing language; single-leg = HELD. The hidden metrics_internal winprob is not an input, output, or citation of this plan.
- **Book entry:** results enter the book as EVIDENCE ROWS in the relevant subjects' `expectation_record.evidence[]` only (B1), each {test_id · dataset_version (G6 pin) · n {observed/eligible + mechanism} · effect · exact_ci · verdict ∈ {supported, refuted, unresolved, blocked, descriptive} · primary_or_exploratory · kill_signal_state}.

## Tests (amended)

### ① Winner-pattern validation — PRIMARY — BLOCKED on G1 + G4 until controls + double-tag land
- **Question:** do podium projects show {proof-grounded (P) · enterprise-workflow (E) · approval-gates (H)} more often than field projects?
- **Pre-registered:** Fisher exact, **one-sided**; report **strict-yes and ≥partial codings side by side** (conclusions flip between them — H: 6/11 ≥partial vs 1/11 strict).
- **Kill (numeric):** corrected p > .05 **∨** OR < 2 ⇒ pattern claim DEAD, recorded as refuted.
- **Denominator:** podium n=11 observed; field = harvested gallery controls per edition (eligible + mechanism stated); until controls exist this test does not run as a validation.

### ② Room / crowding — REDUCED to descriptive
- Cells (category × edition) ≈ 1–3 podiums; per-category field denominators mostly ∅ ⇒ curves unfittable.
- **Form:** counts table only, ∅ curve claims — UNLESS per-category field sizes are harvested with the ① controls.
- **Gate (numeric):** < 3 editions with ≥ 2 categories carrying field+podium counts ⇒ stays descriptive permanently for this dataset version.

### ③ Judge-panel effects — CANNOT RUN on this dataset
- Per-track judge assignment is NOT_ESTABLISHED ∀ historic events (combined pools only); any judge↔shape link would be an ecological fallacy.
- **Fallback:** pool-overlap descriptive only. **Unblocks only** on judge↔track sourcing (new dataset leg, separately pinned). G1 would also gate the re-run.

### ④ Comment-signal — BLOCKED as inference
- ∅ corpus: a handful of public quotes, ∅ sampling frame, judge-vs-community unattributed in sources.
- **Honest form:** qualitative theme inventory with n = quotes-found stated. Theme coding is a 2nd tagging step ⇒ G1 applies if it ever upgrades to inference.

### ⑤ Ranking stability (D2 six candidates) — CONDITIONAL
- "Inferred rubric" from n=11 across 4 heterogeneous events = overfit ∧ circular. Conditions:
  - Rubrics come from **PUBLISHED criteria where they exist** (Agent Rush: Application of Technology / Presentation / Business Value / Originality), pre-registered per event; the inferred variant is labeled **exploratory-only** wherever reported.
  - **Metric (pre-registered):** Kendall's W + per-candidate rank range across rubrics.
  - **Kill (numeric):** any candidate rank-range ≥ 4 of 6 ⇒ verdict UNSTABLE, ∅ winner claim; the D2 slate ranking is labeled rubric-fragile wherever cited.

### ⑥ Backtested forecast — CONDITIONAL (gate for any forward use)
- ~4 editions ⇒ single-fold train≤3/predict-1 is anecdote; base rate brutal (P∧E ≥partial = 10/11 ⇒ a naive "shape wins" predictor is ≈ always right).
- **Required form:** leave-one-edition-out × 4 folds, scored **against a base-rate predictor** (Brier score or hit-rate, chosen pre-run).
- **Kill (numeric):** forecast ≤ base-rate predictor on the chosen score ⇒ leg OFF, no forward use.
- **Leakage:** tags were produced on ALL editions pre-split ⇒ per-fold blind re-tag, OR tags stamped as fixed features with a leakage caveat carried on the evidence row.
- **Target:** defined exactly pre-run (one of: winner-shape membership ∨ candidate rank) — no post-hoc target shopping.

## Sequencing + review (amended)

1. **G1 double-tag** (2nd tagger, κ published, partial rule frozen, adjudication logged) + **G4 control harvest** (scraping-leg amendment) — both land as dataset-leg artifacts with the G6 pin updated.
2. Tests-lane **re-review of this amended artifact** → clearance per test.
3. Run order: ① (primary, if unblocked) → ⑤ (published-rubric variant) → ⑥ (LOEO form) ; ② descriptive alongside; ③④ stay blocked until their sourcing exists.
4. Every verdict lands as a book evidence row (pinned) + report ↑main; killed/blocked legs are reported as such, never quietly dropped.
