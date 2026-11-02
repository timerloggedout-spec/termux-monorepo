# ATES Improvement Frame

**`ates-improvement-frame` v0** — registered 2026-11-02 under DoE
governance (see `docs/ops/DOE-FAMILY.md`, Method versions).
ATES is nested under DoE (leveling of record); this frame is
its improvement surface.

## Why this exists

Until this registration, ATES improvements lived ONLY as work
items in issue #3812 and in the continuous audit
(`docs/ops/CONTINUOUS-REPOSITORY-AUDIT-2026-11-02.md`, PR
#3815) — unversioned, unregistered, outside DoE governance:
proposals with no evidence discipline and no measured
quantity. This frame closes that gap. It does not replace
#3812's work items; it versions them as entries (below) whose
claims are governed by rule 9 (attribution corroboration) and
the significance standard.

## The measured quantity — receipt coverage

ATES receipts are emitted by
`.github/workflows/ates-phase-b-run-receipt.yml`
(`scripts/ci/emit_ates_run_receipt.py`; metadata-only rows
against `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`).

- **Selected set S** = the workflows the receipt machinery
  selects (v0: the `workflow_run` trigger list of record in
  the receipt workflow). S is versioned with this frame; a
  coverage figure without its S version is NOT_ESTABLISHED.
- **Workflow coverage** (per window) = workflows in S emitting
  at least one receipt / |S|.
- **Run-level receipt rate**, per conclusion class c in
  {success, failure, cancelled, other}: receipts emitted for
  runs of class c / total runs of class c in S (census leg:
  Actions API).
- **Parity gap** = rate(success) − rate(failure ∪ cancelled).
  At frame open the gap is structural: the emitter runs only
  on success conclusions (#3812), so failure/cancelled rates
  sit at ~0 BY CONSTRUCTION. The gap is the headline quantity
  this frame exists to close or consciously bound.
- Readings are expectation records: a coverage claim cites
  {S version · window · n runs censused · census source}.
  Emitter self-count alone is a single leg — HELD under
  rule 9; the Actions-API census is the corroborating leg.

## Improvement entries

Entries are versioned (rule 8: version changes get comparison,
never silent edits). Entry shape: {id · statement · basis ·
evidence_requirement · state}. States: HELD (evidence
requirement unmet — the entry may be discussed, never stated
as an improvement) · PROPOSED · EVIDENCED · ADOPTED ·
REJECTED. An entry's claim may not exceed its state.

- **ATES-IMP-001 — Coverage census.** Statement: receipt
  coverage is measured and published per window (quantity
  above). Basis: #3812 ("an explicit coverage limitation to
  quantify"). Evidence requirement: first census landed —
  S enumerated, rates by conclusion class, parity gap stated.
  State at registration: PROPOSED.
- **ATES-IMP-002 — Failure/cancelled parity.** Statement:
  failed and cancelled source runs receive main-path receipts
  equivalent to success runs, OR parity is consciously bounded
  at a stated rate. Basis: #3812 emitter condition. Evidence
  requirement: post-change census showing failure/cancelled
  receipt_rate at the adopted target, with dedup, schema and
  provenance validation passing (IMP-003). State: HELD —
  **the parity target (full vs bounded/sampled) is an owner
  decision, not assumed here** (#3812 itself notes full-cost
  emission of every failure is not necessarily warranted).
- **ATES-IMP-003 — Receipt validation suite.** Statement:
  standing checks over the receipt store {deduplication ·
  schema conformance · source run/attempt/SHA provenance},
  results published per window. Basis: #3812 work item
  ("validate ATES receipt coverage, deduplication, schema,
  and source run/attempt/SHA provenance"). Evidence
  requirement: the checks exist, run, and their first results
  are on record. State: PROPOSED.

New entries append with the next id; entry amendments are new
versions of the entry, with the superseded text retained.

## Conformity clauses — Stewardship step 6

Receipt-coverage validation (Stewardship step 6) is judged
against these clauses. A validation that violates a clause is
non-conformant regardless of its conclusion.

- **K1 — Versioned denominator.** Every coverage claim cites
  {S version · window · census source}. No S version, no
  claim.
- **K2 — Parity by stratum.** Receipt rates are stated per
  conclusion class. A pooled coverage figure that hides the
  failure/cancelled gap is non-conformant (wrong-stratum
  evidence counts as zero for the parity claim).
- **K3 — Corroborated counts.** Counted receipts are
  corroborated by an independent leg (Actions-API census vs
  receipt-store count). Emitter self-report alone = HELD.
- **K4 — Dedup.** Receipts count once, keyed {workflow ·
  run_id · attempt}. Re-emission updates the record; it never
  double-counts.
- **K5 — Schema + provenance.** A counted receipt validates
  against the AGENT-THROUGHPUT-EVENT schema and carries
  {run_id · attempt · source SHA} provenance. Failures are
  excluded AND reported as exclusions — never silently
  dropped.
- **K6 — Claims follow entry states.** "Improvement landed"
  is stated only when the entry's evidence requirement is met
  and cited; otherwise HELD/PROPOSED language.
- **K7 — Regressions are findings.** A window-over-window
  coverage drop or parity-gap widening is reported as a
  finding, not smoothed into an average.

## Open owner rulings (flagged, not assumed)

1. **Parity target** for IMP-002 (full parity vs a bounded
   rate) — a cost decision #3812 leaves open.
2. **S governance** — v0 takes S descriptively from the
   receipt workflow's trigger list. Whether S should be a
   DoE-designated set (potentially wider: every workflow whose
   runs should receipt) is an owner call.
3. **Stewardship seat of record** for step 6 — this frame
   supplies the clauses; the validating seat's identity is
   confirmed by main, not invented here.
