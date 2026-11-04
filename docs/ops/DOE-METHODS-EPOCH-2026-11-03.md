# DoE methods of the epoch — definitions of record (2026-11-03)

Owner commission (2026-11-03): define the experiment methods
ACTUALLY IMPLEMENTED this epoch, from the epoch's receipts — not
aspirations. Each entry: {what it tests · design · verdict
criteria · where implemented}. A method whose execution has not
run is defined as its design discipline and marked as such;
nothing below claims a run the receipts do not show.

## 1. Replay-audit invariants method

- **Tests:** whether a scoring/settlement artifact enforces its
  own stated invariants when replayed deterministically from its
  records alone.
- **Design:** every invariant gets a NAMED check home in the
  artifact (B1 one expectation record per subject · B2 basis
  cited per position · B3 settlement only from the subject's
  record of record · B4 ledger-first, public render read-only ·
  B5 hidden winprob never imported — a numeric winprob/
  metrics_internal key anywhere in the inputs is a violation ·
  F1 §6.1 forecast timing: position ts < knowable ts, missing ts
  fails closed, knowable NOT_ESTABLISHED is listed, never
  silently passed). Acceptance is by EXERCISED fixtures, not
  code reading: post-outcome position ⇒ violation + INVALID/
  unscored + exit 1 · unprovable ts ⇒ fail-closed INVALID ·
  p = 0.5 exactly ⇒ ABSTAIN, excluded from N · a known valid
  position must score the exact hand-computed value (Brier
  control 0.04 for p = 0.8 on Y).
- **Verdict criteria:** live replay exit 0 ∧ all homes PASS on
  the real records ∧ every fixture behaves as designed. Any
  fixture surprise = the finding, reported, not smoothed.
- **Implemented:** moneyball `scripts/settlement/replay.py`
  (PRs #5/#7) · DoE audit PASS WITH FINDINGS (2026-11-03) ·
  findings implemented PR #12 merged b8a250e9043d (F1/B4/B5/F3)
  · DoE re-check PASS on firsthand fixtures incl. the Brier
  control · cosmetic dual-listing fixed PR #14 89e67dd44f97.

## 2. Two-leg corroboration census

- **Tests:** whether a decisive count or claim is true —
  operationalization of binding rule 9 (corroborated attribution
  only) as a counting method.
- **Design:** no number is reported from one leg. A custodian
  attestation is one leg; an INDEPENDENT read of the same
  records by a second seat is the other. The two must reconcile
  EXACTLY (counts, sums, field census); any mismatch is the
  finding. Feed↔ledger pairs reconcile the same way (feed census
  == ledger census, deltas stated, never absorbed).
- **Verdict criteria:** both legs agree to the unit, or the
  discrepancy is named with its size and owner. Single-leg
  numbers are labelled HELD/attested, never reported as counts.
- **Implemented:** wagering-book spot-verify (site feed ==
  book/ledger truth, sha-pinned, 2026-11-02) · pool census
  708→717 events (custodian attestation vs this seat's
  independent ledger read: 696 provisioned / 684 pools / members
  and B5 scans reconciled exactly, 2026-11-03) · G0 exit check
  (§4) ran as two independent replays with identical output.

## 3. Panel Judge Mirror 🪞

- **Tests:** what a competition's judging panel would reward,
  estimated without access to the panel — and whether the
  estimator itself discriminates.
- **Design:** two legs. BULL = mirror-jury construction
  (personas deliberate from the venue's published material).
  EKMAN = observable signals ONLY: every preference claim cites
  a receipted signal (podium history · public statements · role
  incentives · venue behavior); an uncited claim is fabrication
  and struck; a persona failing the citation rule does not sit.
  Grades: PERSON-GRADE only where identity + signals are
  receipt-established (carries test-③ effect estimates);
  VENUE-ARCHETYPE where the panel is not established, labelled
  on every output. Mirror scores are RECORDED FORECASTS, filed
  pre-outcome and scored at outcome publication (Brier/
  hit-rate). Every run reports DISPERSION across seats; a
  non-discriminating run files a NULL verdict on itself.
  Continuous improvement = LAYERING: the baseline stays citable
  and unedited; each material improvement to the freeze earns a
  new forecast layer showing score Δ + which basis term moved.
- **Verdict criteria:** forecast scored at judging close
  (2026-11-18 for D1) against placements of record; a run whose
  spread collapses to a constant is recorded as a null
  instrument reading, however good its prose.
- **Implemented:** spec PR #4584 merged 1add8357c157
  (`docs/ops/PANEL-JUDGE-MIRROR.md`) · layering PR #4587
  573fcc7be587 · baseline forecast pjm-2026-11-03-d1-studysprint
  (61.7/100, spread 10 — discriminates) · field-simulation
  companion F-N3 PR #4595 8c67f3992b8b · layers L2 PR #4600
  (65.0, sample content moved) · L3 PR #4612 (66.3, surfaces
  moved) · L4 PR #4619 (69.7, Strands depth moved). Layer L5 on
  the v1.0.0 cut; all layers score 2026-11-18. Alignment
  instrument (judge↔criteria fidelity) PR #4588 a4b4d85d0801.

## 4. G0 exit test

- **Tests:** whether a settlement pipeline works LIVE, end to
  end, on a real resolving subject — not on fixtures.
- **Design:** one full cycle on the first genuinely resolving
  subject: record of record updated → settlement stamped from
  that record ONLY (B3) → deterministic replay → scoring check
  by a seat that did not build the machinery. Every leg is
  named individually (open · escrow · settle · score · payout);
  a leg with nothing due is declared ZERO-DUE in the exit
  record, never silently passed. Retroactive positions are
  F1-invalid by construction, so the test cannot be gamed
  after the outcome is known.
- **Verdict criteria:** the cycle replays clean (exit 0, all
  invariant homes PASS) ∧ the exit record names every leg's
  state, including the unexercised ones and what they bind to.
- **Implemented:** moneyball DESIGN §9.5 · first cycle on D1-1
  (2026-11-03): coordinator RoR PR #4658 aea6201d87ed → Book
  settlement PR #4660 5d1c4a47b53c (Y; posterior {1.0, [1,1],
  n 1}) → two independent replays identical (settlements 0→1,
  scores {} — no positions existed on the subject) → report of
  record PR #15 9922d394b08c. DoE exit verdict: G0 CLOSED —
  PASS; escrow/payout legs zero-due and declared; the payout
  mechanics' first live exercise binds to POS-001 (D2-5).

## 5. Pre-registered campaign design (Speculators)

- **Tests:** speculative-decoding token strategies (fork
  strategies vs baseline) on task performance.
- **Design:** the acceptance rule is fixed BEFORE any run and
  cannot move after: 12 cells (6 strategies × 2 verifiers) × 4
  tasks = 48 runs; acceptance = output-match rate ≥ 0.50 ∧
  speedup ≥ 1.20 ∧ margin ≥ 0.10; LOSSLESS GATE — a run with
  output_match ≠ true is disqualified regardless of speed.
  State admitted_design_only until its named automation runs
  (binding rule 5); every run record is instance-stamped
  (configured-instance identity) and lands as an EXPERIMENT
  record + summary.
- **Verdict criteria:** the pre-registered thresholds, read off
  the run records; no post-hoc threshold motion. 0/48 executed
  at this epoch's close — the method stands as implemented
  design discipline; its verdict awaits execution.
- **Implemented:** build PR #2671 5fe8481a0b36 · full DoE
  wiring PR #4066 b3ccc2a755da · paper|test wallets PR #4640
  ba726a65ba1f · allocation rule of record (method 7) in
  `experiments/speculators/token-strategies/DESIGN.json`.

## 6. MVT (multivariate testing) — co-source: MVT seat

- **Tests:** which combination of factor levels performs —
  several variables moved at once, read as a design, not as
  one-at-a-time tinkering.
- **Design:** MVT is nested UNDER DoE (leveling of record:
  roll-ups count DoE once). Variation comes from the family's
  operators (rnd v1: full_factorial / taguchi_l9 generators,
  randomized assignment); MVT's epoch work supplied the
  statistical-bounds method the whole pool program now stamps
  against: category shares as multinomial measurements over a
  declared window — Wilson 95% per-category bounds,
  Dirichlet–multinomial for joint statements, evidence floor
  N < 30 ⇒ NOT_ESTABLISHED, clamping disclosed with the
  pre-clamp share shown.
- **Verdict criteria:** per-design decision rules fixed in the
  campaign DESIGN (e.g. fb-pages-mvt-1: winner copy → default
  at 10 attributed redemptions ∨ window close); share claims
  may not be presented tighter than their bounds.
- **Implemented:** `docs/ops/POOL-SCOPE-METHODS.md` =
  pool-scope-methods/v1, PR #4689 a2ed0c67a57b (MVT seat) ·
  fb-pages-mvt-1 live since 2026-10-27 (fb-a/fb-b arms;
  verdict memo owed at its decision rule) · methods disputes
  route to the DoE seat per the method's own note. (Entry
  co-sourced with the MVT seat, 36e3433d; concurrence/
  correction invited on this text.)

## 7. Amendment-6 snapshot method (% discipline)

- **Tests:** whether a reported percentage is a measurement or
  a decoration.
- **Design:** a % is DYNAMIC — category-usage-driven,
  method-bounded; there is no fixed % table. A % may be
  reported ONLY as a snapshot stamped {at · window · method ·
  n · shares · bounds · clamped[]} whose method resolves to
  pool-scope-methods/v1 and whose allocation rule is recorded
  in the subject's DESIGN of record. A constant/bare % anywhere
  = defect. Unrecorded rule ⇒ the value renders
  NOT_ESTABLISHED, never a number. A snapshot rendered as
  current outside its stamped bounds = labelling breach.
- **Verdict criteria:** trace test — every rendered % resolves
  stamp → method → recorded rule; any break in the chain fails
  the surface carrying it.
- **Implemented:** owner % RULE (2026-11-03 15:38 PT) ·
  allocation rule recorded in token-strategies-1's DESIGN
  (PR #4708 1e58afce0a93: this campaign NOT_ESTABLISHED —
  full-factorial, arms carry no allocation — family rule
  stated) · arm pool ledger events carry `split:
  NOT_ESTABLISHED` verbatim (×4) · pools feed carries the
  stamps in-feed (moneyball PR #38 4ea84b78ae16).

## 8. QUE-plane experiments (admission / ordering as treatments)

- **Tests:** whether the dispatch plane's admission and
  ordering choices change lane outcomes — the queue itself as
  the treatment.
- **Design:** the lane population of record is the
  dispatch-tree feed (32 QUE lanes at census). Admission =
  which slice of the pool a lane's work draws from and in what
  fallback order (allocations.json claims: primary slice,
  fallback none, leftover-only); ordering/timeboxing
  (priority_timebox tiers) = the pressure treatment. Both are
  operated as recorded variables — a lane's slice and tier are
  stamped, so outcomes can later be read against them.
- **Verdict criteria / establishment bound:** implemented this
  epoch as operating discipline + census (32 que-lane pools
  provisioned from the feed); a CONTROLLED admission
  comparison (same work under varied admission) is
  NOT_ESTABLISHED this epoch — no verdict is claimed for
  admission effects, only the instrumentation that makes one
  possible.
- **Implemented:** allocations claim machinery (comment-quality
  slice claim #1884: primary [github pool], fallback none,
  leftover-only) · priority_timebox model of record (D1
  PR #4126; slate rollout PR #4130) · QUE census leg of the
  pool program (PR #4688 7a63b56870bd).

## The cycle, as practiced this epoch

The stages every method above actually moved through:

1. **Pre-registration.** Criteria are fixed BEFORE the artifact
   exists: the EGM instance-#2 decision rule, the census's four
   criteria, the G0 terms, the Speculators thresholds, the
   target-table tests. A check invented after seeing the
   artifact is not a check.
2. **Build by a seat that is not the evaluator.** Swarm/
   Speculators-build/MoneyBall build; DoE defines and judges;
   Delphi's gate build was routed the same way (builder ≠
   evaluator) after the shape-alone verdict.
3. **Firsthand verification.** The oracle is master history +
   landed content read back; decisive mechanisms are EXERCISED
   (fixtures run, replays executed, feeds re-counted), never
   trusted from a lane's report — a report is input, not
   evidence.
4. **Corroboration.** A second independent leg must agree
   before a result is of record (method 2). One leg = HELD.
5. **Verdict of record.** PASS / PASS WITH FINDINGS / FAIL with
   severity, filed where the work lives, with the honesty
   remainders named (zero-due legs, unexercised shapes,
   NOT_ESTABLISHED cells).
6. **Registration.** The verdict and any new method version
   enter the family register (this file's home: DOE-FAMILY)
   under rule 8's backfill doctrine — methods are versioned,
   and a version change re-scores history.
7. **Layering / re-run.** On material change, the instrument
   re-runs as a NEW layer over the frozen baseline (mirror
   L1→L4; census regens 1→5; target table r1→r2) — the curve
   is the evidence; earlier layers are never edited.
8. **Closure or next review point.** Each thread closes with
   its next trigger named (a count, an incident, a date:
   CMP-2 at 6 routed ∨ first incident; mirror at the freeze;
   payout leg at POS-001) — nothing is left "ongoing" without
   the event that reopens it.

Cadence as practiced: same-turn within a dispatch (a check
fires the turn its trigger lands); epoch layering against the
wall (D1 freeze 2026-11-04 23:59 PT); verdict flow is one-way —
lane report → verification → verdict → registration — and a
verdict, once of record, is corrected by a new entry, never
edited in place.

## Iteration — definition of record (owner addition, 2026-11-03)

An **iteration** is one numbered pass at a stated done-condition,
inside a series that shares a higher done-condition.

- **Opens** when all three exist: a trigger of record (a landing,
  a defect verdict, a material change, an owner's order) · an
  owning seat · a done-condition stated before the work runs.
  Activity without a done-condition is not an iteration; it is
  motion, and the epoch's records refuse it that name.
- **Closes** when its done-evidence verifies firsthand — a PASS,
  a landed PR read back on master, a scored result — by a seat
  other than the producer where the seats differ (self-verified
  closures disclose it), OR when it is superseded BY NAME, with
  the superseding iteration cited. A failed iteration closes as
  a failure and stays in the record: the failures are why a
  later PASS means anything.
- **Numbering is append-only.** A reopened item gets a NEW
  iteration number; an old one is never resurrected or edited.
  Corrections land as later iterations, not revisions.

**Composition.** Iterations compose into a **cycle**: the series
taken together against its shared done-condition (submission
readiness, a curve completed at the freeze, a full-scope
reconciliation). Cycles compose into the **epoch**: the set of
cycles running under one wall and theme — this epoch is bounded
by the D1 freeze (2026-11-04 23:59 PT) with its scoring tail at
judging close (2026-11-18). An epoch closes when its cycles
close, or when their remainders bind forward BY NAME as named
openings of the next epoch (the G0 payout leg → POS-001; the
mirror layers → their 2026-11-18 scoring).

**The epoch's concrete instances:**

- **StudySprint parity slate** — owner order (MAKE IT HAPPEN,
  no inter-iteration pauses): it-1 = 0.2.0 (#4414) · it-2 =
  0.3.0 (#4415) · it-3 = 0.4.0 (#4416, term-expansion component
  stamped in) · it-4 = 0.5.0 (#4417). Each opens on the prior
  iteration's green and closes on gate + evidence; the slate is
  one cycle aimed at the submission wall. The #4276 defect ran
  its own iteration series inside it: 0.1.1 (device FAIL) →
  0.1.3 (#4412), closed only when BOTH legs verified (emulator
  gate + owner device smoke).
- **Panel Judge Mirror layers 1–4** — each layer is one
  iteration of a single forecast: baseline (61.7) → L2 (65.0,
  sample content) → L3 (66.3, surfaces) → L4 (69.7, Strands
  depth). A layer opens on a named trigger (a proof closing, a
  release advancing, a content landing), closes when its
  forecast files with the Δ and the moved basis term stated;
  L5 opens on the v1.0.0 cut. The layers compose into the
  improvement curve — the mirror's cycle — which closes at the
  freeze and scores 2026-11-18.
- **Census rounds** — provisioning rounds (base program, 161
  entities → Amendment 1 DoE umbrella +49 → … → Amendment 5
  arms + loops, 693 pools) and their render rounds (feed
  regens 1→5 · target table r1→r2). A round opens on a scope
  amendment landing and closes on reconciliation: counts exact
  between legs, deltas named, NOT_ESTABLISHED cells carried
  with reasons. The census cycle closes when the last class
  and the last render leg verify.
- **Strands proof runs 1–4** — four iterations of one
  done-condition (a fetch→plan tool chain executing on the
  live model, receipted). Runs 1–3 did not close it; run 4
  (run 41708224556) PASS closed the series. The failed runs
  remain in the record as the series' evidence — attempt 4's
  gate record carries the repro RED beside the PASS.
- Cadence instances, same shape at smaller grain: the Delphi
  gate's silent hourly sweeps converging a filing over several
  rounds (RFP-D1-7, ~31 min) are iterations of a scoring cycle
  whose done-condition is a converged ledger posting.
