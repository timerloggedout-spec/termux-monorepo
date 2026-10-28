# Temporal — the Delphi cycle as a workflow (N5)

**Built:** 2026-10-28, temporal-integration lane. **Brief:**
`docs/rfps/temporal-durable-execution/N5-BUILD-BRIEF.md` (PR #2163).
**Acceptance record:**
`docs/proposals/passes/temporal-durable-execution/implementation/ADDENDUM-2026-10-28-N5.json`.
The cycle v2 semantics belong to the Delphi lane; this build moved
the *substrate* only — `method_cycle.py` remains the implementation
of record for semantics, and the workflow's finalize stage calls it.

## What runs

| Piece | Value |
|---|---|
| Workflow | `DelphiCycleWorkflow`, task queue `delphi-cycle`, ID = `delphi-cycle/<pass-id>` (ID reuse is the idempotency boundary) |
| Server | Fleet self-host, `localhost:7233`, namespace `default` (`docs/ops/TEMPORAL-SELF-HOST.md`) |
| Code | `scripts/temporal/delphi_cycle/{workflow,activities,worker,client}.py` |
| Worker | NOT a VM service (owner order 2026-10-28: VM = sandbox only; the Temporal self-host server is the sole exception). Workers run **bounded, per engagement**: `client.py prove` spawns them for the proof, and a live cycle runs `worker.py` in the foreground for the cycle's duration. The repeatable proof's always-on home is GitHub Actions (`.github/workflows/delphi-cycle.yml`: ephemeral in-job dev server, tests + §5 prove in record_only mode + parity, receipts as artifacts). A `temporal-delphi-worker.service` unit shipped in the first landing and was removed the same day under this order — the acceptance addendum records the state as it was when the proof ran |
| Tests | `tests/test_delphi_cycle.py` (validation, phantom parity, staged parity, emission shape, payload-conversion regression) |

## How a cycle flows

1. **generate** activity → `generate_proposal.generate_pass`
   (n candidates + profiles, artifacts written to the workdir).
2. **Round 1 opens.** Ballots arrive as `BallotSignal` signals and
   are validated at the door (cycle v2 intake rules): voter,
   rationale, evidence_refs required; classes separate;
   DRIVER_SYNTHESIS refused; MODEL_PROVIDER needs its run record;
   dedupe per round. Rejections are **recorded with reasons** in the
   workflow state, never silent.
3. Facilitator signal `close_round_1` → **cross_vote_round_1**
   activity (`cross_vote.cross_vote` verbatim) →
   **expectations + synthesis** activity (method_cycle's own
   `derive_expectations` / `build_synthesis`; expectations are on
   record before implementation exists).
4. **implementation** activity: per-candidate receipted suites
   (argv + JSON summary contract; receipt = command, exit code,
   output sha256, code paths; heartbeats through long suites).
5. **equalize** activity: phantom rule applied (unreceipted suite =
   zero passes, flagged) and the round-2 evidence bundle sha256
   stamped. Round 2 cannot open without it.
6. Facilitator signal `open_round_2` (the HITL gate) → **round 2
   opens.** A round-2 ballot without the bundle sha256, or with a
   different one, is rejected and recorded; with it, accepted.
7. Facilitator `close_round_2` → **finalize** activity:
   `method_cycle.run_cycle` itself produces the canonical artifacts;
   before they are written, the activity asserts its expectations /
   implementation / bundle-hash artifacts equal the staged
   activities' outputs — divergence fails the cycle loudly (parity
   is enforced on every run, not just in tests).
8. **emit_records** activity: ballot + calibration payloads built
   in-activity and posted to the Delphi ledgers by exact-title
   resolution (PAT helper route), each carrying the registry kind
   marker + `<!-- n5-emit:<workflow_id>:<stage> -->`. A retried
   emission finds its marker and reports `already_posted` — exactly
   once per workflow + stage. `ledger_mode=record_only` writes the
   payloads to the workdir and posts nothing (tests).

`CycleStatus` query answers at any point (including after
completion): stage, per-class ballot counts per round, rejections,
bundle sha256, facilitator actions, ranked outcome.

## Operate

- Query a cycle (any worker on the queue serves it; for a completed
  cycle within retention, the self-host exception server holds the
  history): `client.py status --workflow-id delphi-cycle/<pass-id>`.
- Run a live cycle: start `worker.py --address localhost:7233` in
  the foreground on the VM (bounded to the engagement — kill it
  when the cycle completes), then drive it with `client.py`.
- Start a cycle / cast ballots / facilitator actions: `client.py`
  subcommands (`start`, `ballot`, `facilitator`, `result`); the
  fixture mode is the rehearsal brief — real passes supply their
  brief the same way.
- Acceptance re-run: `client.py prove` (§5: SIGKILL mid-round,
  resume, hash gate, exactly-once, parity) — see the addendum for
  the 2026-10-28 receipts and the three defects attempts 1–3 found
  and fixed (payload conversion typing, heartbeat-bound recovery,
  cross-round dedupe scope).

## Known limits

- Single node, as with the self-host itself: mesh redundancy NOT
  established; durability = server sqlite persistence + worker
  supervision + keepalive reinstall.
- Kill-recovery latency for the implementation stage is bounded by
  its 60s heartbeat timeout, by design.
- The debate/revision round is not wired as signals in v1
  (run_cycle records it `specified_not_run`); the facilitator
  synthesis is still issued. Wiring it is a Delphi-lane semantics
  decision, not a substrate gap.
- Namespace retention is 24h: pass records live in the repo
  (workdir artifacts + landed addenda + ledger comments), not in
  the server.
