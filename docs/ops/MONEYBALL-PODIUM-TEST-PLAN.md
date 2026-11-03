# MoneyBall — Podium-Dataset ML Test Plan (SPEC, pre-registered)

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` · **Owner GO:** 2026-11-03 09:17 PT (via main). **Status: SPEC ONLY — no test has run.**
**Review state: CLOSED (2026-11-03)** — Tests-LLM-Validation re-review: PASS WITH RESIDUAL CONDITIONS (per test); residuals mapped in the closure section at the end of this document. Earlier state: Tests · LLM Validation FORMAL review of record = **APPROVED WITH CORRECTIONS** (C1–C9; the formal review supersedes the same lane's earlier brief-level review where they differ — notably C2's frozen BINARY codebook + re-code supersedes the brief's ternary-handling gate). **Amendment #2 (this text) incorporates C1–C9; on its landing the review leg stamps the review closed and runs may proceed in sequence** (③ expected blocked-not-run unless judge↔track linkage is sourced).

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

## Review closure (2026-11-03) — residual dispositions

The re-review was written against amendment #1 (blob 7fd138ac) and crossed amendment #2 (PR #4500) in flight. Mapping, residual by residual:

- **① clarification (claim form + combination rule):** DISCHARGED in amendment #2 — primary claim = the ≥2-of-3 composite; cross-edition read = Fisher combined-p (named). ① remains BLOCKED on G1 double-tag + G4 controls, as held.
- **② descriptive · ③ blocked-not-run + pool-overlap descriptive · ④ qualitative inventory:** CLEARED as filed; may proceed on their artifacts.
- **⑤ conditional-cleared:** kills = {rank-range ≥4/6 · Kendall W < 0.5} (both in amendment #2). Remaining condition is a PRE-RUN FILING, not a spec item: the per-event published-rubric weights are filed as their own pre-registration artifact BEFORE any candidate is scored; inferred variant stays exploratory-labeled.
- **⑥ not cleared on amendment #1 text; amendment #2 discharges the C4 substance:** nested selection is binding in the filed plan (survival re-decided per origin on train editions only; in-sample rows stamped, gate read only under nested selection); k = podium slots in the predicted edition across tracks; unit = project-level membership; target fixed = project-level membership. ONE item remains for the ⑥ PRE-RUN FILING: the score choice (Brier ∨ hit-rate) is named there, before the run — the plan deliberately leaves the choice to that filing, and no ⑥ run is valid without it. ⑥ also waits on ① unblocking (no schedule cost).
- **Row-schema completion:** stratum + codebook_version are already in the filed C5 schema (amendment #2); they ride the first-row filing as required.

**Net state:** review CLOSED. Runnable now (on their artifacts): ② descriptive · ③ pool-overlap fallback (descriptive) · ④ theme inventory. Conditional: ⑤ (rubric-weights filing first). Blocked: ① (G1+G4) · ③ main test (judge↔track) · ⑥ (① unblocking + pre-run filing with named score).


## RESEQUENCE (owner, 2026-11-03 09:25 PT via main) — run-gating sits AFTER the OSINT results layer

The design closed ahead of the full harvest; feasibility stamps issued against the partial dataset of record may not survive the completed one. Therefore:

- **ALL runs HOLD** until the OSINT results layer passes = Swarm OSINT template first exercise + the scraping lane dataset build, both landed.
- On that pass, the feasibility stamps are **RE-ISSUED against the post-pass dataset of record** (new pin) before any test moves; the Tests leg verifies the re-issued stamps as the run gate.
- Stamps most likely to change: **③ blocked-not-run** (identity harvest may source judge↔track linkage) and **① field rows** (field harvest may fill the denominator).
- The DESIGN stays closed — this is stamp sequencing, not re-review.
- **LAYERING (owner correction, 2026-11-03 09:30 PT — "we layer"):** pre-pass stamps are NOT non-citable. Every stamp stays citable **with its dataset-version pin (its layer)**; run-gating reads the **CURRENT layer only**; a re-issued stamp is a new layer OVER the old, never an erasure — the same append-only pattern as the opportunity ledger (superseded entries remain; totals/verdicts run over the current layer). Citations of an older layer are valid history; gate decisions never read them.


- **Review-leg correction (Tests lane, 2026-11-03):** the per-test run clearances in the closure stamp are **PROVISIONAL, not live** — incl. ② descriptive, which also holds. The Tests leg post-pass stamp verification is the **formal gate** (not a follow-up); clearances issue from it. ③ and ① stamps evaluated against the partial record remain citable as their layer (per the layering rule above) but do not bind the gate, which reads the current layer only.

## Dataset v1 issued (scraping lane, 2026-11-03) — PRE-PASS pin + provisional stamps

- **Pin:** version `2026-11-03.v1` · sha256 `537981b874cb2bd3b0d53e3e0a73760e1b7db8690cba6a93d7bb1016eb1b60f8` · record `ops/podium/snapshots/2026-11-03.v1.json` (envelope `podium-dataset/v1`, PR #4501). This pin is the current dataset of record; per the resequence it is PRE-PASS layer — stamps below are provisional, citable with this pin, and re-issue as a new layer on the post-pass record (layering rule above).
- **Shape:** 55 entities · edition = stratum throughout · 30 projects (canonical URL per project, G5 ✓) · 6 judges + 6 judge-person entities (identity-stable, exact-name v1).
- **Feasibility stamps (v1, provisional):** podium_n per edition {ai-infra 13 · assemblyai 5 · nativebuilder 4 · alpaca 3 · ibm-bob 3 · vultr 0 (live)} — broader than the podium leg's n=11 read (crawl ⊃ leg sample); the re-issue reconciles. field_n = **null** (C1 gallery leg = v2; D2 gallery opens Nov 5) ⇒ ① stays blocked. Repeat judges observed = **0** (panels published for 1 of 4 crawled editions) + judge↔track linkage absent ⇒ ③ blocked-not-run stands. judge_comments 0 · community_comments 0, comments surface **NOT_ESTABLISHED** (∅ public comments in server-rendered pages; schema reserves the split) ⇒ ④ stays blocked/descriptive.
- **EGM guard (verified in their report):** ingest = lablab pages only + explicit drop-guard on the canonical stamp / RFP-EGM2- prefix; ∅ stamped items in v1.
- **Landing status (Tests-leg verification, 2026-11-03):** the v1 pin HASH-MATCHES at source (sha256 of snapshot content == plan pin; 55 entities; in-artifact stamps == this section) — but PR #4501 is OPEN (head c23ae1042964), so v1 resolves at PR-head only: corroborated at source, single-leg on surface = **HELD until #4501 merges**. "Issued" in this section reads as issued, not landed.
- **Hold unchanged:** OSINT layer pass = this build + Swarm OSINT template first exercise; runs wait for the pass + stamp re-issue + Tests-leg verification (the formal gate).


## Dataset v2 (scraping lane, 2026-11-03) — NEW CURRENT LAYER (v1 layer retained, citable)

- **Pin:** version 2026-11-03.v2 · sha256 b8a187aabc4b68ca8f987baae45ab633df78c52b9bd50c2b42e389072fb27995 · PR #4501 (open at issue; gates re-running) — same HELD-until-merge landing status as the v1 layer; the pin registers the layer, the merge lands it. Diff vs v1: +34 added · 9 changed · 0 removed. 89 entities; stratum preserved; conflicts 0. Per the layering rule, v1 stays citable with its pin; run-gating reads THIS layer.
- **Field rows LANDED (C1):** gallery surface = edition /live page (entries := gallery submissions). field_n {vultr 4 · alpaca 15 · assemblyai 11 · ibm-bob 13} — server-rendered anchors = LOWER BOUND if a gallery paginates client-side (stamped in the record). Editions without a field_n here remain null at this layer.
- **Stamps at this layer:** category x edition denominators = NOT_ESTABLISHED (categories not labeled on public surfaces) => test 2 stays descriptive. Editions with usable rubrics = 0 (no weighted criteria on crawled pages) => test 5 stays conditional on its published-rubric filing (the plan's named Agent Rush criteria are the anchor source, not the crawl). Repeat judges with attributable picks = 0.
- **Judge-track linkage: CLOSED as unsourceable from public pages** — the stamp (0 attributable picks) IS the deliverable per the plan fallback. Test 3 is blocked on LINKAGE, not on this dataset; only a non-public source changes that layer.
- **Gate state unchanged:** runs still HOLD — OSINT layer pass + Tests-leg verification of the current layer remain the formal gate. Test 1's remaining blockers at this layer: G1 double-tag re-code + editions lacking field rows.

