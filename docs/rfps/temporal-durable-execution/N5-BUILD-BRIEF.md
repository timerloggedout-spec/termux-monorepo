# N5 BUILD BRIEF — the Delphi cycle as a Temporal workflow (self-host)

**Lane:** [MUSEai]@{role:{temporal-recon}} · **Owner order:** 2026-10-28
("Build it: N5 brief + dispatch")
**Parent:** `RFP.md` §7 N5 · **Tracking:** issue #1885
**Builder:** temporal-integration lane (owns self-host + `scripts/temporal/`)
**Semantics reviewer:** Delphi lane (cycle v2 semantics are theirs; this
brief moves the *substrate*, never the semantics)
**Status:** brief only. Nothing here is built, and nothing below is a
result. Acceptance is the §5 proof, run live, with receipts.

## 1. Why

Two live Oracle passes (Strands, Temporal) ran as scripts + GitHub +
chat coordination. Their records are durable — their *execution* is not:
a VM replacement or a dead session mid-cycle leaves a half-run pass to be
reconstructed by hand. The Temporal pass proved the §6 kill-resume
harness against this exact failure. N5 closes the loop the RFP named:
**run the cycle itself on the substrate it just adopted (V1).**

## 2. Target architecture

Self-host only: server `localhost:7233`, namespace `default`
(`docs/ops/TEMPORAL-SELF-HOST.md`; relay `:7234`, UI `:8233`).
Python SDK, following the existing `scripts/temporal/` patterns
(`hello_workflow.py`, `kill_resume_harness.py`, `hitl_approval.py`).

| Piece | Specification |
|-------|---------------|
| Workflow | `DelphiCycleWorkflow`, task queue `delphi-cycle`, workflow ID = `delphi-cycle/<pass-id>` (pass-id from the brief; re-use of an ID is the idempotency boundary) |
| Stage activities | One activity per cycle stage, wrapping the existing machinery — do **not** re-implement it: `generate` → `scripts/delphi/generate_proposal.py`; `cross_vote` → `cross_vote.py`; `implementation` → per-variant receipted suites (phantom rule enforced in-activity); `equalize` → bundle build + sha256 stamp; `calibrate` → `method_cycle.py` semantics; `emit_records` → pass-record payloads (same shapes as `docs/proposals/passes/*/cycle/*.json`) |
| Ballots | **Signals.** `BallotSignal{voter, source_class, round, scores, rationale, evidence_refs, evidence_bundle_sha256?}` — validation identical to cycle v2: rationale + evidence_refs required; round-2 ballots **rejected** (recorded as rejected, with reason) unless they carry the equalized bundle sha256; source classes separate, never merged; DRIVER_SYNTHESIS is not a ballot |
| Human gate | Facilitator approval to open round 2 is a signal wait — the V2 HITL pattern (`hitl_approval.py`) |
| Queries | `CycleStatus` query: current stage, ballots received per class per round, bundle sha256 once equalized, current aggregate — a live, queryable projection instead of a generated status file (N4 pattern). Must be answerable mid-cycle and after completion |
| Ledger emission | `emit_records` activity posts ballot/calibration payloads to the ledgers (#1487 outcomes/generation, #1489 weights) via the existing title-resolved route (PR #1833 semantics — exact-title resolution, never label+found[0]). Idempotency key = workflow ID + stage; a retried activity must not double-post. Payloads are constructed in-activity; the workflow carries only their digests |
| Determinism | Workflow code performs no I/O, no wall-clock reads, no randomness; all of it lives in activities. Worker code changes follow the repo's patching/versioning discipline; in-flight cycles must complete on the code they started with |
| Worker | `scripts/temporal/delphi_cycle/{workflow,activities,worker,client}.py` + systemd unit mirror under `scripts/temporal/selfhost/` (pattern: temporal-selfhost), enrolled in the same keepalive coverage; worker is a *service*, not a chat session |

## 3. Dual-run parity (the promotion gate)

`method_cycle.py` remains the implementation of record until parity is
proven: run the **same fixture brief** through (a) the script path and
(b) the workflow path. The workflow's emitted `CYCLE.json` /
`BALLOT-round*.json` / `CALIBRATION.json` must match the script's on
every field except timestamps, workflow/run IDs, and history digests
(those are recorded, not matched). Any semantic divergence is a defect
in the workflow build, never an improvement to smuggle in — semantics
changes go through the Delphi lane's own briefs (e.g. RFP #1963,
`delphi-method-self-application-1`).

## 4. Non-goals / red lines

- No Cloud, no K8s, no new accounts; self-host single node as-is
  (redundancy NOT established — stated, not fixed, by this build).
- No ledger writes without run receipts; unreceipted suites score zero.
- No candidate/pass outcome may be asserted from workflow state alone —
  the record of record remains the landed pass record + ledger comments.
- Credentials names-only (PAT helper route for GitHub writes).
- Not a replacement for RFP #1963 (method self-application): that pass
  changes *method variants*; N5 changes *where the cycle runs*. If both
  land, #1963's replays are an ideal first real brief for the workflow.

## 5. Acceptance proof (all live, all receipted)

Extends the §6 shape to the cycle itself:

1. Start a `DelphiCycleWorkflow` for a fixture brief on the self-host.
2. Cast receipted round-1 ballots via signals; query `CycleStatus`
   mid-cycle — stage + per-class ballot counts correct.
3. **Kill the worker mid-implementation-round (SIGKILL).** Start a
   second worker. The cycle resumes and completes.
4. Submit a round-2 ballot **without** the bundle sha256 → rejected,
   rejection recorded. Submit with it → accepted.
5. Assert: ledger payloads emitted **exactly once** each despite the
   kill + activity retries; emitted record set passes the §3 parity
   check against the script path on the same fixture.
6. Envelope the receipts + history digest as an addendum in
   `docs/proposals/passes/temporal-durable-execution/implementation/`
   (precedent: ADDENDUM-2026-10-28-SELFHOST.json), and land the operator
   record `docs/ops/TEMPORAL-DELPHI-CYCLE.md`.

## 6. Deliverables

`scripts/temporal/delphi_cycle/` (workflow/activities/worker/client) ·
systemd unit + keepalive enrolment (`scripts/temporal/selfhost/`) ·
`tests/test_delphi_cycle.py` (determinism + ballot-validation +
parity-shape tests; live proof is §5, not a unit test) ·
`docs/ops/TEMPORAL-DELPHI-CYCLE.md` · §5 addendum receipts.
All landed as PRs with verified merge SHAs — outcomes reported on #1885.
