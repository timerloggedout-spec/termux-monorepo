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

## Mechanism correction (2026-11-02 — supersedes v0 text)

Stewardship firsthand (artifacts read in full), verified by
doe-expert against `scripts/ci/emit_ates_run_receipt.py`
@master: **there is NO conclusion filter** in the receipt
workflow. The emitter maps the source conclusion onto the
receipt `status` field — success -> "success", failure /
timed_out / action_required / startup_failure -> "failed",
cancelled / neutral / skipped -> "skipped", anything else ->
"error" — while `event` stays "task_completed" for ALL
receipts. Truth rides the status field; a consumer counting
by event type misreads failures and cancellations as
completions. Issue #3812's "success-only emitter" mechanism
claim is SUPERSEDED (Stewardship is correcting it as a step-6
item); the parity problem is a MEASUREMENT problem
(status-blind counting), not an emission problem. The
quantity definitions and IMP-002 below are restated on the
status field accordingly.

Established denominator facts (Stewardship census): the
emitting surface is ONE workflow_run path over ONE selected
source workflow ("Continuous agent ops") of 271 repo
workflows; the receipt workflow has 9 runs ever and is
DORMANT since 2026-10-23; output is artifact-only (30-day
retention, no in-repo persistence); payloads missing run
id / attempt / timestamp produce NO receipt (the emitter
refuses a synthetic receipt) — an exclusion class invisible
in the store, countable only from the census leg.

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
- **Run-level receipt rate**, per STATUS class c in
  {success, failed, skipped, error} (the emitter's
  conclusion -> status map, cited above): receipts with
  status c / total source runs mapping to c in S (census leg:
  Actions API).
- **Parity gap (measurement)** = success rate as counted by
  event type − TRUE success rate counted by status. Emission
  parity exists by construction (no filter); the gap this
  frame tracks is the inflation status-blind consumers
  introduce, driven to zero when every coverage consumer of
  record reads the status field (IMP-002, clause K8).
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
- **ATES-IMP-002 — Status-true parity accounting.**
  Statement: every coverage/parity quantity and every
  coverage consumer of record computes on the receipt
  `status` field; event-type counting is retired. Basis: the
  mechanism correction above (v0's emission-parity statement
  rested on #3812's superseded mechanism claim and is
  withdrawn). Evidence requirement: a status-based census
  (IMP-001 recomputed on status) + a consumer audit listing
  every coverage consumer of record and its counting field.
  State: PROPOSED. (The v0 owner-ruling flag on a parity
  TARGET is dissolved by the correction: no emission filter
  exists, so there is no full-vs-bounded emission decision
  to take; a future proposal to ADD a filter re-opens it.)
- **ATES-IMP-003 — Receipt validation suite.** Statement:
  standing checks over the receipt store {deduplication ·
  schema conformance · source run/attempt/SHA provenance},
  results published per window. Basis: #3812 work item
  ("validate ATES receipt coverage, deduplication, schema,
  and source run/attempt/SHA provenance"). Evidence
  requirement: the checks exist, run, and their first results
  are on record. State: PROPOSED.
- **ATES-IMP-004 — Receipt persistence.** Statement: receipts
  land in a durable in-repo store; today output is
  artifact-only with 30-day retention, so the receipt record
  evaporates and long-window coverage is unverifiable.
  Evidence requirement: the store exists, emitter output
  lands there, and a window older than 30 days is read back
  from it. State: PROPOSED.

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
  (K5 applies equally to emitter-refused payloads — missing
  run id / attempt / timestamp — which are counted as
  exclusions from the census leg, since the store cannot see
  them.)
- **K8 — Status-field accounting.** Coverage and parity
  quantities are computed on the receipt `status` field.
  Counting by event type ("task_completed") is non-conformant
  per se: it misreads failed/skipped receipts as completions.
- **K6 — Claims follow entry states.** "Improvement landed"
  is stated only when the entry's evidence requirement is met
  and cited; otherwise HELD/PROPOSED language.
- **K7 — Regressions are findings.** A window-over-window
  coverage drop or parity-gap widening is reported as a
  finding, not smoothed into an average.

## Open owner rulings (flagged, not assumed)

1. **Parity target** — DISSOLVED by the mechanism correction
   (no emission filter exists; see IMP-002). Re-opens only if
   a filter is ever proposed.
2. **S governance** — v0 takes S descriptively from the
   receipt workflow's trigger list. Whether S should be a
   DoE-designated set (potentially wider: every workflow whose
   runs should receipt) is an owner call.
3. **Stewardship seat of record** for step 6 — this frame
   supplies the clauses; the validating seat's identity is
   confirmed by main, not invented here.
