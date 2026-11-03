# EGM Instance #2 — The Delphi Rubric Under Test

Pre-registered 2026-11-03 by the DoE seat under
`egm-evaluation` v0 (`docs/ops/EGM-EVALUATION.md`), BEFORE
any instance-#2 filing exists. Owner GO 2026-11-03.

## The anomaly

Instance #1 produced two materially different verified
batches and the gate scored them identically:
RFP-D1-7 = 9.12 and RFP-D1-8 = 9.12 (median 9, IQR 3.0,
same vote profile), repeating the #3695/#3696 signature
(8.54 = 8.54 on identical field surfaces). Hypothesis under
test: **the Delphi effective score responds to filing SHAPE
and not to filing SUBSTANCE.** This instance measures both
sensitivities separately.

## Arms

### ARM A — shape varies, substance constant

Substance (fixed, verified-strong): the FSRS generation
drift, goldfish claim #4231 — VERIFIED by executable test
(the verifier reproduced every measured figure with
py-fsrs). The same substance is filed three ways:

- **A1** full template shape, evidence EMBEDDED (the
  instance-#1 standard).
- **A2** full template shape, evidence REFERENCED (links
  to the claim + verdict records; no figures in the body).
- **A3** SPARSE: same `###` headings (parseable), terse
  one-line fields, evidence referenced.

A-spread (max − min effective across A1–A3) = **pure shape
sensitivity** of the score.

### ARM B — substance varies, shape constant

All three cells filed in IDENTICAL full template shape
(A1's discipline: same sections, comparable completeness,
evidence embedded):

- **B1** verified-STRONG substance: claim #4213 (release
  assets empty; blocks-use; since fixed + verified).
- **B2** verified-WEAK substance: claim #4225 (parity
  statement names foundation v0.4.0 vs core 0.5.0; polish,
  record-integrity only).
- **B3** the killer cell: a REFUTED substance in perfect
  filing shape. Constructed claim: "the shipped APK
  declares the INTERNET permission and loads remote
  content." Refuted firsthand by the DoE seat BEFORE this
  pre-registration was filed: `AndroidManifest.xml`
  @master contains ZERO `<uses-permission>` elements, and
  `MainActivity.java` loads only
  `file:///android_asset/web/index.html`. B3's filing body
  will present the claim exactly as a confident filer
  would (no refutation inside the filing — the refutation
  lives HERE and in the close-out; the filing is stamped
  as an instance-#2 test filing per the guardrails).

B-spread (max − min across B1–B3) = **substance
sensitivity**. Decision rule, fixed in advance: if B3's
effective score lands within the B1–B2 range (or above
B2), the rubric is shown to read shape alone on this
evidence; if B3 scores materially below both (≥ 2 points
under B2), the rubric carries a substance channel worth
naming.

## Guardrails (owner-set)

- Every filing is stamped as an instance-#2 TEST filing at
  the instance level (one identical stamp line in each
  body). NOTHING from this instance converts to awards or
  build items, whatever the scores.
- Blinding: voters see the test stamp (required) but not
  cell membership, arm structure, or hypotheses — those
  are held in this document, which is public in the repo
  but not referenced from the filings. Disclosed here and
  in the close-out: the panel is rubric-driven; whether it
  reads beyond the filing is part of what the B3 cell
  measures.
- REFUTED-publishes discipline: B3's refutation is
  published in this pre-registration and again in the
  close-out, attached to the filing's number.
- Filing mechanics: burst of 6 `delphi:rfp` issues
  (surface ids RFP-EGM2-A1/A2/A3/B1/B2/B3), ONE
  `delphi-tick` at the end, no comments from the DoE seat
  until ledgers land (instance-#1a churn lesson).

## Output (close-out, ↑ main)

Per-arm spreads + full vote profiles per cell · the
decision-rule verdict · rubric amendment proposals priced
from the measurement (candidates, to be kept or dropped by
the numbers: a scoreable verification-record field; oracle
resolution of cited evidence at scoring time; shape-class
normalization). Amendments are PROPOSALS to the Delphi
lane via main; this instance changes no gate behavior.
