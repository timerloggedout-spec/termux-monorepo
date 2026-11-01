# Notation-compliance detection — TEST report (2026-10-31)

Owner-ordered bounded TEST (via main). Instrument:
`scripts/notation/compliance_scorer.py` (heuristic v1, stdlib) +
`scripts/notation/test_compliance_scorer.py` (4/4 ✓). Frame: DoE
experiment nc-1 (PR #2865 merged d3bf60dae3, pre-registered) owns the
experiment design; this report = the L3 + L2 layer outputs its arms
consume. Mode: **report-only** (∅ gate wiring in this test).

## Method (heuristic v1)

Features per text: notation glyphs + cadence tokens /100w ·
prose-glue words /sentence · mean words /sentence · evidence refs
(#nnn, hex SHAs, run ids, URLs, paths, [MUSEai]) /100w. Composite
0..1; verdicts: ≥0.55 compliant · 0.40–0.55 borderline · <0.40 prose.

Pass criteria (set before scoring): C1 false-positive rate on
known-good lane output ≤10% · C2 prose-control detection ≥80% ·
C3 L2 sweep completes over ≥8 chats w/ ranking.

## L3 — GitHub surfaces (report-only)

- **Exemplars** (ENROLL filings on #1884, 2026-10-30+, spec-era lane
  comments): n=74, mean 0.786. Flagged 8 (11%): 7 borderline + 1 prose.
  At the prose threshold only: FP = 1/74 = **1.4%**. The borderline
  band concentrates in the earliest filings (several sym/100w = 0.0 —
  filed before the style spread) = part true drift, part band noise.
  This lane's own filing (comment 6520942443) = 0.867 ✓.
- **PR bodies** (20 most recent lane PRs w/ [MUSEai] bodies): mean
  **0.548**, 10/20 flagged. PR bodies = the prose-iest GH surface —
  summary paragraphs persist there while comments went dense. By the
  spec (∀ surfaces) these read as true drift, not FPs.
- **Controls**: synthetic prose paragraph → 0.100 prose ✓ detected.
  Issue #320 body → 0.746, #1734 body → 0.570: **not detected** —
  both are prose *about* notation / structured PR prose saturated w/
  symbols + refs. Construct limit of v1: density features cannot
  separate prose-about-notation from notation-as-connective-tissue.
- First-pass sampling lesson: pre-spec fleet comments (Oct 21–24)
  scored 0.627 mean — the fleet was already id-dense pre-formalization,
  so era alone ¬ a prose control.

## L2 — transcript sweep (first run)

9 chats × recent assistant turns (n=32 msgs), mean compliance:
viz-dispatch-tree 0.851 · doe-expert 0.767 · main 0.741 ·
delphi-oracle 0.738 · database 0.688 · challenge-entries 0.653 ·
challenge-mgmt 0.619 · web-design 0.427 · **tier1-steward (self)
0.413**. Worst-drifter pattern: the low outliers are owner-facing
long-form summaries (this lane's own chat reports incl.) + one
quoted-content case (entries relaying staged marketing copy verbatim
— quoted text ≠ lane voice; v2 must strip quotes/code fences).

## Verdict vs criteria

- C1: **PASS at the prose threshold** (FP 1.4%); borderline band =
  watchlist, ¬ verdicts (11% band-inclusive).
- C2: **FAIL for v1** on research/PR-prose controls (0/2); raw prose
  detected (synthetic ✓). ⇒ gate mode NOT justified; report-only +
  ranking is the supported mode — matching the order's sequencing.
- C3: **PASS** (9 chats ranked; feeds L1 as specced in nc-1).
- Overall: **report-only stack VIABLE; repo-gate check = premature.**
  v2 requirements: quote/code-fence stripping · symbol-function test
  (connective position vs mention) · claim↔ref adjacency (#1734
  proper) · per-surface thresholds (PR bodies ≠ comments).

Noise law honored: ∅ corrections posted anywhere by this test;
rankings route ↦ main only (L1 relay-validation decides drift events,
per nc-1).
