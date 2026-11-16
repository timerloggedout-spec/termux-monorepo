# EGM Evaluation — Findings Tested as RFPs

**`egm-evaluation` v0** — registered 2026-11-03 under DoE
governance (see `docs/ops/DOE-FAMILY.md`, Method versions).
Owner order 2026-11-03: run an Elephant-Goldfish-style
evaluation of the landed D1 UI surfaces; the opinions are
evaluated AS RFPs — in this schema the opinions get TESTED.

## The gap this closes

Upstream EGM tests its machinery (reviewers produce
findings; the pipeline files them) but never its FINDINGS.
The D1 precedent shows the same gap from the other side:
the Delphi gate rubric scores a filing's FIELDS {problem ·
scope · done-evidence · rubric mapping · gantt}, not the
substance (#3695/#3696: effective 8.54, converged r1, veto
false — identical scores because the parsed surfaces were
identical, "not a merit tie"). A finding nobody verified is
a claim at face value — exactly what rule 9 forbids for
weight-bearing use. This run tests both: machinery AND
findings.

## Objects of record

- **Goldfish** = cold reviewers (Viz + Web Design seats,
  dispatched by main): zero build context, artifacts only.
  Their memory-lessness is the method — they see the
  surface a first user sees.
- **Elephant** = the shipped artifacts of record, the
  oracle every claim is checked against:
  - TUI v0.1.0 — PR #4161 merged `5653241db3a4`
  - WebApp (PWA) v0.1.0 — PR #4162 merged `46518482875c`
  - APK v0.1.0 — PR #4163 merged `c84b8b213505`
  (issues #4092/#4093/#4095 closed)

## Pipeline (pre-registered before any finding arrives)

1. **CLAIM intake.** Every goldfish finding enters as a
   CLAIM, stamped {finding id · surface · reviewer seat ·
   claim text · alleged location in the artifact}. No
   finding skips intake; no finding is scored at intake.
2. **VERIFICATION leg.** Each claim is checked against the
   elephant by an oracle, in this order of authority:
   (a) the artifact source at its merged SHA — does the
   alleged blind spot exist in the build? (b) the served
   surface (PWA served pages) — does it manifest live?
   (c) an executable test where the claim is testable.
   Verdicts: **VERIFIED** (defect exists as alleged) ·
   **PARTIAL** (exists, scope differs — the claim is
   RESTATED to the verified scope before proceeding) ·
   **REFUTED** (the artifact contradicts the claim).
   The verification record {oracle · evidence · verdict}
   attaches to the claim permanently.
3. **RFP conversion.** Only VERIFIED and PARTIAL-restated
   claims become RFPs, in the delphi:rfp field shape
   {problem · scope · done-evidence · rubric mapping},
   carrying their verification record INTO the filing — the
   done-evidence dimension scores against it, which is how
   this run repairs the fields-not-substance gap inside the
   existing machinery instead of beside it.
4. **SCORING.** The existing Delphi machinery, unchanged
   for comparability with the precedent: voter roles
   {OPERATOR · builder · reviewer · Scout · cost_auditor},
   effective score /25, veto flag, converged rounds, shadow
   bar 15.0. Two pre-registered additions, both recorded on
   the RFP itself, never applied silently:
   - **severity class** from the verification leg:
     {blocks-use · degrades-use · polish};
   - **reviewer calibration**: REFUTED claims score the
     REVIEWER, not the book — reviewer accuracy =
     (VERIFIED + ½·PARTIAL) / total claims, recorded as a
     posterior input on the reviewer seat (this is the
     findings-tested leg; a goldfish that cries blind spots
     the elephant does not have is itself a measured
     result).
5. **AWARDS.** Award recommendation ↑ main = score-ranked
   within severity class (severity stated, bar unchanged —
   no post-hoc overrides: a blocks-use RFP under the bar is
   reported as under-bar with its severity named, and main
   decides). Awards become build items routed under the
   claim convention (route+claim, no form-only filings) —
   precedent: RFP-D1-6 = issue #4156 → build batch.

## Discipline

- Design is pre-registered: dimensions, oracles, and the
  award rule are fixed HERE, before findings arrive.
  Anything changed after findings land is a v1 amendment
  with the change + reason stated (no silent refits — the
  anti-p-hacking rule of the parent frame applies to the
  evaluator first).
- REFUTED findings are published in the scored set as
  REFUTED, never dropped — the set reports the reviewers'
  hit rate alongside the RFP scores, or it has tested
  nothing.
- Scores cite the precedent scale (8.54 = the D1 copy RFPs)
  so this run's numbers are comparable on arrival.
