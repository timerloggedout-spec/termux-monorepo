# Role register of the epoch — who does what (2026-11-03)

Owner commission (2026-11-03): for the work actually done this
epoch, name the appropriate roles and their expected duties —
as a layer beside `docs/ops/DOE-METHODS-EPOCH-2026-11-03.md`.

**Names discipline:** role names are the Registry SSOT's
canonical set only (AGENT-MONIKERS registry, naming-collapse
conformity PR #3828): **builder · operator · steward ·
observer · reviewer · scout · gambler · participant**.
`forecast` is an OUTPUT class, not a role. **bookmaker** and
**11th man** are RESERVED-ABSENT: no work-stream this epoch
required them, and they are listed absent wherever roles are
listed (the naming-collapse watch-item). One practice word is
mapped, not adopted: the epoch's seats said "custodian" for
ledger-keeping work; in SSOT names those duties are the
**steward**'s, and this register says steward throughout —
the mapping is stated here for the Registry's concurrence or
correction.

Duties are one line each, as practiced, with the receipt where
the duty was exercised.

## Pool program (693 pools · wallet ledger · settlement machinery)

- **builder** — builds the provisioning and fold/verify
  machinery and the settlement artifacts the program runs on.
  (Speculators-build: pool provisioning program PR #4688;
  replay.py PRs #5/#7; wallet_ledger fold.)
- **steward** — keeps the ledger of record: append-only,
  corrections as new entries, fold == claims at every check.
  (Wallet ledger 28 → 717 events under one custody; schema
  conformed to the landed ledger, never the reverse — PR #11.)
- **gambler** — takes positions on subjects, basis cited per
  position; is scored on asserted forecasts only, never on
  prices or pool shares. (POS-001 on D2-5: open, NOT_SCORED;
  D1-1 settled with no positions — G0, §4 of the methods doc.)
- **participant** — every provisioned pool and wallet is a
  participant of record: existence is registered, standing is
  earned only through records. (693 pools, 705 wallets-feeds
  rows, all balances fold-proven 0 at census.)

## Census / validation

- **observer** — produces the count: censuses, attestations,
  and state reports that move nothing. (Custodian attestation
  on the 708-event ledger: every pool traced to an enumerated
  entity; NOT_ESTABLISHED cells named.)
- **reviewer** — issues the verdict on another seat's work:
  PASS / findings with severity, from firsthand reads, never
  from the report alone. (DoE census verdicts: landed-scope
  PASS corroborated two-leg; target table PASS at r2; the
  attestation-wording correction on arm split stamps.)
- **steward** — carries the checked artifacts forward as the
  record (feed regens, table revisions) without editing
  landed rows. (Pools feed regens 1→5; target table r1→r2 by
  append and revision note.)

## Methods + Lean formalization

- **builder** — authors the definitions and the formalization.
  (DOE-METHODS-EPOCH-2026-11-03, PRs #4722–#4727; E001.lean,
  PR #4729.)
- **reviewer** — concurs or corrects a definition against the
  record before it stands as co-sourced. (MVT seat on methods
  §6: firsthand read, concurrence, ∅ correction.)
- **steward** — keeps the method register: versions entered,
  backfill doctrine applied, nothing silently revised.
  (DOE-FAMILY §Method versions: the epoch entries and their
  register lines.)
- The Lean kernel is not a role-holder: the oracle's verdict
  is an artifact the **reviewer** reads (PASS from the verdict
  artifact, never the job color — run 41746401168 in flight at
  this register's writing).

## QUE / dispatch

- **operator** — runs the plane: admission, ordering, and
  timebox pressure applied to live work. (Desk QUE operates
  dispatch under priority_timebox; allocations claims assign
  slices — claim #1884.)
- **builder** — builds the dispatch automation and the feed
  machinery the plane reads. (Swarm: dispatch-tree feed,
  stamp fan-out.)
- **observer** — maintains the plane's state of record that
  operators act on. (Dispatch-tree feed as the lane population
  of record, 32 QUE lanes at census.)
- **participant** — the lanes themselves: dispatched units
  whose admission and ordering are the treatments of record
  (methods §8).

## Tribute diagnostics

- **observer** — builds and reads the diagnostic surfaces:
  state rendered faithfully, gaps shown as gaps. (Viz/Web
  Design: dashboard + pools census matrix, PR #4714 — NE
  cells rendered NE, counts computed at render.)
- **steward** — owns the receipt discipline behind the
  surfaces: coverage measured over a versioned selected set,
  parity accounted. (ATES improvement frame, Stewardship
  step 6: IMP-001…004.)
- **reviewer** — cold-reads landed surfaces and files only
  what verification sustains. (EGM instance #1: 26 claims →
  25 verified / 1 partial / 0 refuted; goldfish reviewers =
  the reviewer role in its cold form.)

## D1 slate / freeze assembly

- **operator** — the submission hand: publishes, cuts
  releases of record, assembles the freeze. (Desk, owner
  ruling 2026-11-03: "You submit; you && the event manager are
  responsible" — project published 10:01 PT; v1.0.0 cut owed
  on submission day.)
- **builder** — builds the slate iterations and surfaces.
  (Swarm seat-build: parity slate 0.2.0→0.5.0; TUI/webApp/APK
  surface family.)
- **reviewer** — verifies independently of the producer:
  PASS verdicts, device-smoke adjudication, the re-read that
  catches what the producing session missed. (D1 seat: the
  post-publish divergence caught by independent re-read and
  corrected verbatim, 2026-11-03.)
- **observer** — keeps the forecast record honest against the
  freeze: layers filed pre-outcome, scored at close.
  (Panel Judge Mirror custody: baseline → L4 filed; L5 on the
  v1.0.0 cut; scoring 2026-11-18.)
- **scout** — selects what enters the next round from the
  live feed state, under the health gates — never by static
  reputation. (Scout frame of record: selections stamped as
  selection experiments; the Desk's trigger lines to the
  mirror are scout-shaped acts under this duty.)

## The new wiring: DoE pool × Desk QUE dispatch (2026-11-03)

The pool program's DoE-class pools are consumed by Desk QUE
on task dispatch. Three sides, three duties, no overlap:

- **operator (Desk, dispatch consumer)** — reads the pool of
  record at dispatch time and dispatches against it; consumes
  existence and state, asserts nothing about standing.
- **steward (ledger ops)** — keeps the pool ledger the
  dispatch reads: provisioning, fold, and corrections current
  before any dispatch cycle depends on them.
- **reviewer (DoE, integrity)** — verifies the pool the
  dispatch consumed is the pool of record (feed == ledger,
  deltas named), and that nothing downstream renders
  existence as standing; issues findings to either side when
  the wiring drifts.

## Roles not assigned this epoch

- **bookmaker** — RESERVED-ABSENT (no book is made by a
  bookmaker in this family; the Book is a record, priced
  parimutuel by stake distribution).
- **11th man** — RESERVED-ABSENT (audience/reserve class; no
  audience participation surface existed this epoch).
- No stream required a role the SSOT does not carry; where
  practice used a non-SSOT word (custodian), the mapping to
  **steward** is stated above rather than a new name coined.

## Plane-layer note (2026-11-04)

Registry ruling (owner-endorsed, this gate): **Custodian**
is ISSUED as the custody-plane name. Layer separation, not
amendment: the custodian -> steward mapping above stands
untouched at the role layer (steward stays the role-class
word); this register coined no plane name - the plane was
the open gap, now filled by the issued plane name.
Scope narrowing (owner line, PR #4908): **Custodian**
names the custody plane on the Web3 MoneyBall plane;
in termux-monorepo, plane references read **steward**
(except when naming the MoneyBall plane's Custodian
explicitly). References to the role read **steward**
everywhere.
