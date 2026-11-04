/- Packet E-001 — epoch-methods formalization, compiled against
   batteries_fork pin 36cc05ca2d0e469bfbeea9437f460e19238e885e
   (toolchain v4.34.0-rc1), batteries leg of the NSE-023 oracle.
   Source of record: docs/ops/DOE-METHODS-EPOCH-2026-11-03.md
   @ master 855a112f818b (PRs #4722/#4724/#4725/#4727).
   Claim: the epoch methods' invariants and verdict criteria,
   stated as Lean definitions over the records they govern;
   the decidable fragment is DISCHARGED on fixtures that mirror
   the replay audit's own acceptance fixtures (moneyball
   replay.py, DoE re-check 2026-11-03). Prefetch: these are
   domain predicates — no Batteries-native forms exist; the
   statements are this packet's own.
   Discipline: statements first; proofs where decidable;
   everything else is a Prop definition under OPEN STATEMENTS.
   No `sorry`, no axioms claimed anywhere in this file. -/
import Batteries

namespace EpochMethods

/-! ## 1. The Book fragment (replay-audit invariants, methods §1)

The audit's objects, abstracted to the fields its checks read.
Timestamps are abstract naturals (epoch seconds at the source);
probabilities are rationals, as in the audit's Brier control. -/

structure Subject where
  id : String
  expectationRecords : Nat
  recordOfRecord : String
  knowable : Option Nat
deriving DecidableEq, Repr

structure Position where
  id : String
  subjectId : String
  basis : Option String
  p : Option Rat
  ts : Option Nat
deriving DecidableEq

/-- B1 — one expectation record per subject. -/
def b1Ok (ss : List Subject) : Bool :=
  ss.all fun s => s.expectationRecords == 1

/-- B2 — basis cited per position (a basis ref is present). -/
def b2Ok (ps : List Position) : Bool :=
  ps.all fun p => p.basis.isSome

/-- B3, checkable part — a settlement cites exactly its
    subject's record of record, nothing else. (The authenticity
    of the cited record is OPEN, §5.) -/
structure Settlement where
  subjectId : String
  citedSource : String
deriving DecidableEq, Repr

def b3Ok (s : Settlement) (sub : Subject) : Bool :=
  s.subjectId == sub.id && s.citedSource == sub.recordOfRecord

/-- B4, checkable part — the public render derives from the
    append-only ledger of record and from nothing else. (The
    render-side criteria R1–R3 are served-surface checks;
    kernel-side this is the statement they answer to.) -/
def b4Ok (renderDerivedFrom : String) : Bool :=
  renderDerivedFrom == "ledger.jsonl"

/-- B5 — no numeric winprob / metrics_internal key anywhere in
    the inputs. Keys are (name, isNumeric) pairs, mirroring the
    audit's walk: a numeric value under either name is an
    import; a string mention (the boundary note) is not. -/
def b5Ok (keys : List (String × Bool)) : Bool :=
  keys.all fun kv =>
    !((kv.1 == "winprob" || kv.1 == "metrics_internal") && kv.2)

/-- F1 — §6.1 forecast timing. A position whose timestamp
    cannot be proven (none) fails closed; a position at or
    after its subject's knowable instant is a violation; a
    subject whose knowable is NOT_ESTABLISHED lists the
    position (f1ListedNE), it does not violate. -/
def f1Violation (p : Position) (knowable : Option Nat) : Bool :=
  match p.ts, knowable with
  | none, _ => true
  | _, none => false
  | some t, some k => k ≤ t

def f1ListedNE (knowable : Option Nat) : Bool :=
  knowable.isNone

/-- F3 — p = 1/2 exactly is an abstention, not a call. -/
def abstain (p : Position) : Bool :=
  match p.p with
  | some q => decide (q = (1 / 2 : Rat))
  | none => false

/-- The scoring kernel the audit controls against: Brier. -/
def brier (p outcome : Rat) : Rat := (p - outcome) ^ 2

/-! ### The audit's fixtures, discharged

Same objects as the DoE re-check fixtures: a subject knowable
at t=20; one valid position (t=10, p=4/5), one post-outcome
(t=30), one unprovable (no ts), one abstention (p=1/2). -/

def subj : Subject :=
  ⟨"D1-1", 1, "coordinator.json", some 20⟩

def posValid : Position := ⟨"POS-V", "D1-1", some "cited basis", some (4 / 5 : Rat), some 10⟩
def posLate : Position := ⟨"POS-L", "D1-1", some "cited basis", some (4 / 5 : Rat), some 30⟩
def posNoTs : Position := ⟨"POS-N", "D1-1", some "cited basis", some (4 / 5 : Rat), none⟩
def posAbstain : Position := ⟨"POS-A", "D1-1", some "cited basis", some (1 / 2 : Rat), some 10⟩

theorem b1_fixture : b1Ok [subj] = true := by decide
theorem b2_fixture : b2Ok [posValid, posLate] = true := by decide
theorem b3_fixture : b3Ok ⟨"D1-1", "coordinator.json"⟩ subj = true := by decide
theorem b4_fixture : b4Ok "ledger.jsonl" = true := by decide
theorem b5_clean : b5Ok [("posterior", true), ("metrics_internal", false)] = true := by decide
theorem b5_import : b5Ok [("winprob", true)] = false := by decide
theorem f1_valid : f1Violation posValid subj.knowable = false := by decide
theorem f1_late : f1Violation posLate subj.knowable = true := by decide
theorem f1_unprovable : f1Violation posNoTs subj.knowable = true := by decide
theorem f1_ne_listed : f1ListedNE none = true ∧ f1Violation posValid none = false := by decide
theorem f3_abstain : abstain posAbstain = true ∧ abstain posValid = false := by decide

/-- The audit's Brier control, exact: p = 4/5 on outcome Y
    scores (1/5)^2 = 1/25 — the 0.04 the live re-check
    reproduced against the real ledger. -/
theorem brier_control : brier (4 / 5 : Rat) 1 = 1 / 25 := by decide

#print axioms brier_control
#print axioms f1_late

/-! ## 2. The snapshot method (Amendment-6, methods §7)

A % exists only as a stamped snapshot. The stamp's shape is
the type; validity is the recorded rule: method of record,
declared window, and a point % only at or above the evidence
floor (N ≥ 30 — below it, bounds-only or absent). -/

structure Snapshot where
  at : Nat
  windowStart : Nat
  windowEnd : Nat
  method : String
  n : Nat
  hasPoint : Bool
  boundsLo : Rat
  boundsHi : Rat
  clamped : List String
deriving DecidableEq

def SnapshotValid (s : Snapshot) : Bool :=
  s.method == "pool-scope-methods/v1" &&
  s.windowStart ≤ s.windowEnd &&
  (!s.hasPoint || s.n ≥ 30) &&
  s.boundsLo ≤ s.boundsHi

def snapPoint : Snapshot := ⟨100, 0, 90, "pool-scope-methods/v1", 30, true, 0, 1, []⟩
def snapThin : Snapshot := ⟨100, 0, 90, "pool-scope-methods/v1", 29, true, 0, 1, []⟩
def snapBoundsOnly : Snapshot := ⟨100, 0, 90, "pool-scope-methods/v1", 5, false, 0, 1, []⟩

theorem snapshot_point_at_floor : SnapshotValid snapPoint = true := by decide
theorem snapshot_point_below_floor : SnapshotValid snapThin = false := by decide
theorem snapshot_bounds_only_lawful : SnapshotValid snapBoundsOnly = true := by decide

#print axioms snapshot_point_below_floor

/-! ## 3. The cycle as a state structure (methods: the cycle)

Stages in practiced order. `layer` re-enters `verify` (a new
layer is verified, never asserted), and `close` is terminal:
no transition leaves it. A trace is valid iff every step is
an allowed transition. -/

inductive Stage
  | preregister | build | verify | corroborate
  | verdict | register | layer | close
deriving DecidableEq, Repr

def stageNext : Stage → Stage → Bool
  | .preregister, .build => true
  | .build, .verify => true
  | .verify, .corroborate => true
  | .corroborate, .verdict => true
  | .verdict, .register => true
  | .register, .layer => true
  | .register, .close => true
  | .layer, .verify => true
  | .layer, .close => true
  | _, _ => false

def validTrace : List Stage → Bool
  | [] => true
  | [_] => true
  | a :: b :: rest => stageNext a b && validTrace (b :: rest)

/-- The G0 cycle as it ran: straight through, no layering. -/
def g0Trace : List Stage :=
  [.preregister, .build, .verify, .corroborate, .verdict, .register, .close]

/-- A layered cycle: register → layer → verify again → close. -/
def layeredTrace : List Stage :=
  [.preregister, .build, .verify, .corroborate, .verdict, .register, .layer, .verify, .corroborate, .verdict, .register, .close]

theorem g0_trace_valid : validTrace g0Trace = true := by decide
theorem layered_trace_valid : validTrace layeredTrace = true := by decide
theorem skipped_stage_invalid : validTrace [.preregister, .verdict] = false := by decide
theorem close_is_terminal : stageNext .close .build = false := by decide

#print axioms g0_trace_valid

/-! ## 4. Iteration, generation, epoch (composition of record)

The opening rule for an iteration, the cull record's required
shape, and the epoch's freeze bound — the decidable shapes of
the three definitions. -/

structure IterationRec where
  trigger : String
  seat : String
  doneCondition : String
deriving DecidableEq, Repr

/-- An iteration opens iff trigger, seat, and a stated
    done-condition are all present. -/
def OpensIteration (i : IterationRec) : Bool :=
  i.trigger != "" && i.seat != "" && i.doneCondition != ""

theorem iteration_opens : OpensIteration ⟨"landing", "doe-expert", "gate green"⟩ = true := by decide
theorem motion_is_not_iteration : OpensIteration ⟨"landing", "doe-expert", ""⟩ = false := by decide

/-- The cull record (rule of PR #3748): the act and its
    wallet routing are one record; an unrouted cull is not a
    cull of record. -/
structure CullRecord where
  culled : String
  balanceAtCull : Nat
  poolDestination : String
deriving DecidableEq, Repr

def CullRecorded (c : CullRecord) : Bool :=
  c.culled != "" && c.poolDestination != ""

structure EpochPass where
  datasetId : String
  freeze : Nat
deriving DecidableEq, Repr

/-- The ML epoch bound: a record at or before the freeze is
    this epoch's data; after it, next epoch's. -/
def InEpoch (e : EpochPass) (ts : Nat) : Bool := ts ≤ e.freeze

theorem epoch_bound : InEpoch ⟨"epoch-2026-11-03", 100⟩ 100 = true ∧ InEpoch ⟨"epoch-2026-11-03", 100⟩ 101 = false := by decide

#print axioms epoch_bound

/-! ## 5. OPEN STATEMENTS — stated, not proven

Each entry below is a definition of a proposition. No proof is
claimed; each names what its proof would require that the
kernel cannot supply from the records alone. This section is
the file's honesty boundary, and it is part of the structure,
not an apology appended to it. -/

/-- B3, full form: the cited record of record is AUTHENTIC —
    it is the record its receipts claim. Authenticity is a
    property of the receipt chain (signatures, platform state),
    which lives outside these records; the kernel can check
    the citation (b3Ok), not the world it cites. -/
def B3_Authentic (s : Settlement) (authentic : Settlement → Prop) : Prop :=
  authentic s

/-- Two-leg corroboration, full form: two legs AGREE (decidable
    — it is equality of outputs) and are INDEPENDENT.
    Independence — no shared input, author, or failure mode —
    is a property of the legs' provenance, not of their
    outputs; identical outputs from one leg run twice satisfy
    agreement and refute nothing. Stated so the distinction
    survives formalization. -/
def LegsCorroborate (agree independent : Prop) : Prop :=
  agree ∧ independent

/-- EKMAN citation adequacy: every preference claim cites a
    signal whose reference RESOLVES to a receipted artifact.
    Resolvability is checked against the world (the artifact
    exists at the ref), not inside the record that cites it. -/
def EkmanAdequate (claimCitesResolvableRef : Prop) : Prop :=
  claimCitesResolvableRef

/-- The mirror's dispersion discipline, full form: a run's
    seat-spread is wide enough that its forecast is a
    measurement rather than a constant. "Wide enough" is a
    statistical judgment over venues not yet observed; the
    decidable shadow (spread computed from stated scores) is
    arithmetic, but the adequacy threshold is OPEN. -/
def DispersionAdequate (spread : Rat) (threshold : Rat) : Prop :=
  spread ≥ threshold

/-- Wilson-95 / Dirichlet bound correctness for
    pool-scope-methods/v1. A Mathlib-leg statement (pin
    cc8b65263ab8): the bounds are what the method names. Not
    attempted on the batteries leg; carried here so the
    snapshot predicate's method string has its open referent
    named in the same file that uses it. -/
def BoundsAreAsNamed (methodId : String) : Prop :=
  methodId = "pool-scope-methods/v1"

end EpochMethods
