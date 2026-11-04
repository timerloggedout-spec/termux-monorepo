# Proofs directory — INDEX (coverage map of record)

**Directory of record** for DoE proofs (owner amendment,
2026-11-03): `experiments/doe/proofs/`. This INDEX is the
coverage map, living here as the directory's index; the wiring
(entry → experiment · data layers · oracle run · verdict) is
`MANIFEST.json` beside it. Proof ARTIFACTS stay in the Lean
home (`research/nse-023/examples/`, where the oracle compiles
them) and enter this directory by citation/provenance — no
silent moves. An entry missing its data-layer refs reads
INCOMPLETE, exactly like a missing proof.

# Proof coverage map — experiments of record × proof status

Owner standing requirement (2026-11-03): **for every experiment
of record in the repo, DoE creates its proof.** Registered as a
standing duty of the reviewer seat. The pattern is packet
E001.lean: statements first · proofs where decidable · ∅ hidden
sorry · what resists named as OPEN STATEMENTS · the verdict
read from the oracle run's artifact, never the job color.

**Register rule (from 2026-11-03): an experiment without its
proof reads INCOMPLETE in the register.** INCOMPLETE is a
statement about proof coverage, not about the experiment's
other evidence — several INCOMPLETE rows below carry strong
non-Lean evidence (tests, reconciliations, verdicts), and the
map says so per row. Proof ≠ evidence; the requirement adds
the proof leg, it does not demote the others.

Status classes: **proved** (Lean artifact + oracle run PASS of
record) · **proved-fragment** (theorems landed in an artifact;
the run, or the unformalized remainder, still owed — the owed
part is named) · **statements-only** (claims formalized as
statements; no proof discharged) · **open** (no Lean artifact
yet). Enumeration source: DOE-FAMILY register + DOE-METHODS-
EPOCH-2026-11-03 + CMP register, at 2026-11-03.

## The map

| Experiment of record | Proof status | Artifact / owed |
|---|---|---|
| Settlement machinery (wagering book B1–B5/F1; G0 cycle) | **proved-fragment** | E001.lean §1 (PR #4729): predicates + the audit's fixtures discharged by decide incl. Brier control 1/25. Owed: oracle run 41746401168 verdict (in flight); B3 authenticity + leg independence OPEN in E001 §5 |
| Amendment-6 snapshot method (% discipline) | **proved-fragment** | E001.lean §2: Snapshot shape + validity, floor both directions proved. Owed: Wilson/Dirichlet bound correctness — Mathlib leg (E001 §5 referent) |
| The cycle / iteration / generation / epoch shapes | **proved-fragment** | E001.lean §§3–4: stage transitions + trace validity (G0 + layered traces), iteration opening rule, cull-record shape, epoch freeze bound — all by decide. Owed: nothing structural; richer traces as cycles accumulate |
| Pool-scope census (693 pools; counts + reconciliation) | **open** | Counts proved by two-leg reconciliation (non-Lean evidence of record). Owed: the count arithmetic as decidable list computation over the ledger (gap E006) |
| EGM instance #2 (Delphi rubric reads shape alone) | **open** | Verdict of record rests on filed scores (6 filings, identical 9.12 profiles; spreads 0.00). Fully decidable arithmetic — first gap item (E002) |
| EGM instance #1 (claim → verification → conversion) | **open** | Verdicts of record: 26 claims → 25 V / 1 P / 0 R; calibration arithmetic decidable. Rides E002's machinery |
| Speculators token-strategies-1 | **open** | Acceptance predicate (≥0.50 ∧ ≥1.20 ∧ ≥0.10 + lossless gate) pre-registered in DESIGN; 0/48 runs. Statements formalizable now; discharge awaits run records (E003) |
| Routed-dispatch protocol (rule 7: sets-of-3, n-floor 3, cap 12) | **open** | Protocol of record in DOE-FAMILY binding rule 7; stamp corpus live. Arithmetic of set/cumulative accounting formalizable (E004) |
| Panel Judge Mirror (forecasts L1–L4 + F-N3 field sim) | **statements-only** | EKMAN adequacy + dispersion stated OPEN in E001 §5. Scoring (Brier/hit-rate over L1–L5) discharges at judging close 2026-11-18 (E005); F-N3's simulation claims are assumption-labelled by design |
| Certifications value matrix (Bayesian record conformity) | **open** | Conformity verdict of record (CONDITIONAL PASS → PASS on amendment) on 33–34 records; the record-shape predicates formalizable like E001 §2 |
| ATES improvement frame (coverage over selected set S / Sⁿ) | **open** | Frame v0.5 of record; K1–K10 conformity clauses are predicates awaiting formal statement |
| fb-pages-mvt-1 | **open** | Decision rule of record (10 redemptions ∨ 2026-11-10); verdict memo owed at the rule — proof rides the memo's arithmetic |
| live-1-wave-framing (2×2) | **open** | DESIGN of record (PR #2809); decision rule n≥16 ∧ ≥4/cell ∨ 2026-12-04 — formalizable as a predicate over the cell counts when they land |
| live-2-prlane-tuning | **open** | Phase verdicts of record; the phase-3 variance precondition is a stated inequality awaiting its inputs |
| live-3-phrases-deepseek | **open** | Ruling (i-a) authored (PRs #2856/#2857, owners' review); cells re-cut to rule-7 sets on landing — proof follows the re-cut |
| cb-1-chronomancer-emission | **open** | admitted_design_only; dispatch gate unmet — no claims to prove yet beyond the gate predicate |
| lab-1 | **open** | NO-GO/defer of record; re-trigger conditions are the formalizable content |
| nc-1-notation-compliance | **open** | τ values locked (provisional for records stratum); verdict no_selection of record; run-003 gated on three named rulings |
| util-1-provider-rotation | **open** | Cull rule stated (arm < pooled−0.25 @ n≥8); window open (24 stamps ∨ 2026-12-01) — the rule is a predicate; no trigger yet |
| bf-1-backfill-methods | **open** | Method versioned + audited of record; corpus significance NOT_ESTABLISHED — the honest verdict is the content |
| archW1z title evaluation | **open** | Evaluation shape of record (population-routed evidence only); no qualifying evidence yet — nothing decidable to discharge |
| CMP-1…CMP-6 (CMP register) | **open** | CMP-2 carries the epoch's fullest record (interim + full review at 3 routed: working default, NOT ESTABLISHED); review-point predicates formalizable per entry |
| chat-intent v1 → v2 | **open** (evidenced: tests 12/12) | Executable evidence of record; the version-succession + backfill-delta claims (exactly 3) are decidable arithmetic awaiting a packet |
| exchange-scoring v0 / validation-yield v0 | **open** | Candidate measurement methods; the ≥2-leg TRUE-validation rule is E001 §5's corroboration statement in other clothes — formalization rides E001's line |
| M5 cert set / nested-family join | **open** (evidenced: script verdicts PASS) | Workflow-class instance convention verified by its own machinery; Lean statement not authored |
| Dreambeans candidates ×4 (bisociation · dual-accumulator · interface-gates · strands-patterns) | **open** (candidates) | specified_not_run; dual-accumulator carries the epoch's richest pre-registered invariants (non-compensability: V ≥ τ_risk ⇒ avoidance regardless of A) — first in line when a candidate is briefed |

## Gap order (proofs authored down this list)

1. **E002 — EGM verdict arithmetic** (instances #2 then #1):
   fully decidable, verdicts of record deserve their proofs.
2. **E003 — Speculators acceptance predicate** + lossless
   gate: statements now, decidable discharge per run record
   as execution lands.
3. **E004 — Rule-7 protocol accounting**: set/cumulative-n
   arithmetic + the INCONCLUSIVE cap as predicates.
4. **E005 — Mirror scoring**: statements now; Brier/hit-rate
   discharged over L1–L5 at judging close (2026-11-18).
5. **E006 — Census count arithmetic**: ledger fold counts ==
   feed counts as decidable computations over the records.
6. **M001 (Mathlib leg) — Wilson/Dirichlet bounds** for
   pool-scope-methods/v1: E001 §5's named referent.
7. Campaign decision-rule predicates (live-1/2/3, fb-pages,
   util-1, CMP entries) as their windows produce the numbers
   the predicates read.

Each packet follows the E001 pattern and lands in
`research/nse-023/examples/`; each landing updates this map by
new entry (the map is append-only in revision, like the
registers it indexes). Until its row moves, every experiment
above reads **INCOMPLETE** in the register — including, until
run 41746401168 returns its verdict, the proved-fragment rows'
run leg.
