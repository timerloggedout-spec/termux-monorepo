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

## Results (collected 2026-11-03, ledgers on the six issues)

ALL SIX filings: **effective 9.12 / 25 - award parked -
converged round 1 - veto false**, with the IDENTICAL
per-role vote profile {OPERATOR 9 - builder 9 - reviewer
12 - Scout 15 - cost_auditor 3}:

| cell | issue | substance | shape | effective |
|---|---|---|---|---|
| A1 | #4297 | #4231 FSRS drift (verified, measured) | full/embedded | 9.12 |
| A2 | #4298 | same substance | full/referenced | 9.12 |
| A3 | #4299 | same substance | sparse | 9.12 |
| B1 | #4300 | #4213 empty release assets (verified-strong, blocks-use) | full template | 9.12 |
| B2 | #4301 | #4225 parity.md version drift (verified-weak, polish) | full template | 9.12 |
| B3 | #4302 | FALSE claim (refuted below) | full template | 9.12 |

- ARM A spread (shape varies, substance constant): 0.00.
- ARM B spread (substance varies, shape constant): 0.00.
- B3 sits exactly ON the B1-B2 band (a single point).

## Decision-rule verdict

Pre-registered rule: "B3 effective within/above the
B1-B2 band => rubric reads shape alone, proven; B3 >=2
pts under B2 => a substance channel exists." B3 = B1 =
B2 = 9.12. **VERDICT: the Delphi rubric, as instrumented,
reads SHAPE ALONE - proven under the pre-registered
rule.** No role's vote moved for any manipulation:
not for a measured scheduler-integrity defect, not for
a blocks-use release failure, not for a polish item,
and not for a claim that is flatly false.

Corroborating pattern: RFP-D1-7 (#4240) and RFP-D1-8
(#4281) also scored exactly 9.12 with the same profile,
and the earlier copy filings #3695/#3696 scored
8.54 = 8.54. Every observed score in this series is a
constant of its filing-shape class (filer + template
class), not a function of content: two shape classes,
two constants {9.12, 8.54}.

## B3 refutation (published, per REFUTED discipline)

B3's claim - "the shipped APK declares the INTERNET
permission and loads remote content" - is FALSE,
verified firsthand before filing: AndroidManifest.xml
@master contains ZERO <uses-permission> elements;
MainActivity loads only file:///android_asset/web/
index.html. The rubric awarded this refuted claim the
identical score and profile as a verified blocks-use
defect. B3 stands published as REFUTED; it never
converts (TEST quarantine stands).

## Blinding disclosure

Panel voters were blind to the cell structure, arms,
and hypotheses. They were NOT blind to test status:
every filing carried the instance TEST stamp (required
for the quarantine). The stamp demonstrably did not
affect scoring either - the six scored identically to
this filer's genuine filings (D1-7/D1-8).

## Rubric amendment proposals (priced from this measurement; for the Delphi lane via main)

- P1: a SCOREABLE VERIFICATION-RECORD FIELD in the
  filing shape {oracle, evidence_refs, verdict} that the
  panel is instructed on - today the filing shape gives
  the panel no substance channel to read.
- P2: ORACLE RESOLUTION AT SCORING TIME - the gate
  resolves cited evidence (issue / file / API) before
  voting, so a filing whose central claim resolves
  FALSE is mechanically distinguishable from a verified
  one (B3 is the existence proof of the gap).
- P3: PER-ROLE RATIONALE DISCLOSURE in the ledger -
  identical profiles across unlike filings should be
  detectable in-line, not by running an experiment.
- P4: a FILER-BLIND SUBSTANCE PASS - a second scoring
  pass over a shape-stripped substance summary, reported
  alongside the shape score until the two converge.

This instance changes no gate behavior; proposals route
to the Delphi lane via main. Instance #2 CLOSED.

## Disposition (Delphi lane, via main, 2026-11-03)

The rubric operator accepted the shape-alone verdict
UNQUALIFIED. Root cause of record: the gate was
instrumented for provider-surface RFPs, where parsed
shape genuinely is the substance; generalized to all
filings, the substance channel is simply missing.

- **P3 ADOPT, FIRST** (near-zero cost): per-filing vote
  profile rendered on the #1474 board + in-line collision
  flags on identical profiles.
- **P1+P2 ADOPT AS ONE GATE CHANGE:** a scoreable
  verification-record field citing RESOLVABLE REFS ONLY
  (PR / run / receipt ids, never prose), scored ONLY
  through P2's oracle resolution at scoring time.
  <=10 citations per filing, hash-cached, resolution
  results inside the hash inputs. Outcome classes:
  verified / contradicted / unresolvable / unreachable;
  infra-failure = neutral-and-stated. ACCEPTANCE TEST:
  a B3-replica fixture scores >=2 pts below its
  shape-only band. Reuse the D0 kernel's fetch_evidence
  resolution pattern.
- **P4 ADOPT AS SHADOW:** a deterministic substance
  score beside the shape score, never merged; inputs =
  P1/P2 tallies only, no free-text rubric; filer-blind.
  Convergence criterion (registered): last-20 cohort,
  median |shape - substance| <= 2.0 AND identical-profile
  rate < 10%. Awards stay shape-governed until
  convergence + a separate promotion ruling.
- **QUARANTINE GUARD (operator requirement):** the
  gate's recheck must SKIP filings carrying the instance
  #2 test stamp (canonical key: body contains "EGM
  instance #2 TEST filing"), so the instrument change
  never silently re-scores the quarantined six.
- Ownership: spec + acceptance review = Delphi seat;
  build routed by DoE (builder != evaluator) via
  route+claim in the EGM pattern.
