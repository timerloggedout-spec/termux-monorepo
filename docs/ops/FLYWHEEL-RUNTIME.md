# Flywheel: executable repository adapter

This lane now has an executable **repository-native validation loop**, not just the source inventory added by [PR #1460](https://github.com/Timerloggedout-spec/termux-monorepo/pull/1460). It evaluates dependencies, prioritizes ready work, prepares a canonical coordination handoff, runs the repository's actual dual gates, and emits a versioned outcome receipt. It does **not** install or deploy the upstream ACFS stack.

## Run the loop

Read-only evaluation of the canonical graph against an explicit local evidence snapshot:

```sh
python3 scripts/agentic/flywheel.py \
  --plan docs/agentic/dependency-phases.json \
  --snapshot tests/fixtures/dependency_phases/ready.json
```

Run the real local gates for one eligible phase:

```sh
python3 scripts/agentic/flywheel.py \
  --plan docs/agentic/dependency-phases.json \
  --snapshot tests/fixtures/dependency_phases/ready.json \
  --phase DPH-100 --execute
```

The example snapshot is **synthetic test evidence**, not a live approval or a real claim. For useful repository work, supply a current normalized snapshot from the existing dependency-phase evidence adapter. Offline evaluation cannot prove that remote evidence is still current and never authorizes remote dispatch or deployment. No GitHub credentials are needed for this adapter.

Execution is deliberately bounded to `scripts/ci/repo_gate.py` and `scripts/ci/termux_smoke.py`, launched without a shell. The graph cannot inject commands. A process lock prevents concurrent local validation in the same repository. A blocked, already claimed, or non-ready phase cannot be executed. Exiting or failing releases the lock; there is no mailbox, persistent claim store, background scheduler, or new task ledger.

## What is reused, and what is deferred

| Capability | Authoritative surface | Adapter behavior |
|---|---|---|
| Task graph and dependencies | `docs/agentic/dependency-phases.json`, `dependency_phase_engine.evaluate_plan` | Reuses validation, approval checks, claim checks, readiness, plan digest, and admission waves. No Beads database is introduced. |
| Read-only triage | Existing deterministic admission waves | Sorts ready work by wave, then phase identifier; it does not rewrite priority or graph state. |
| Coordination | Existing phase claim idempotency key and dispatcher | Emits a handoff only. Live claims remain the responsibility of the existing dispatcher after its canonical-issue and routing checks. |
| Local concurrency | Process-scoped repository lock | Prevents overlapping validation, not a distributed file lease or Agent Mail substitute. |
| Validation | Repository gate and Termux smoke | Runs the same commands used by repository policy and records actual exit outcomes. |
| Decision-quality feedback | `scripts/delphi/gate.py`, existing append-only Delphi weights issue | Never changes weights or fabricates votes. A local validation receipt is not a confirmed/missed Delphi forecast. |
| Cadence and dispatch | Existing Cadence/Gantt/GitHub controls | No schedule, service, agent fleet, provider call, or live dispatch is added. |
| Upstream ACFS components | Source profile and adoption contract from #1460 | Agent Mail, br, bv, NTM, CASS, DCG, SLB and the installer remain uninstalled here. Their existing immutable-pin, fork, security and platform gates still apply. |

The overlap audit found no established runnable local Agent Mail API to reuse. The tracked Agent Mail integration proposal/PR is not evidence of an available service. This adapter therefore does not pretend that a coordination message was sent or that a distributed lease was acquired.

## Read a receipt correctly

Receipts bind the canonical plan and input snapshot to source provenance and the selected phase. They distinguish **local validation** from **task completion**: passing gates yields a validation PASS while `task_outcome` stays `UNKNOWN` and `deployed` stays `false`. Failed checks and lock/readiness failures return nonzero exit codes. Command output must not be used as a place to store credentials; the adapter retains safe result metadata rather than raw gate logs.

The handoff carries the existing phase idempotency key. It is not an actual claim, and a successful invocation does not mark a phase complete. Completion still needs the canonical merged PR, required checks and project evidence. Real Delphi feedback must refer to an attributable RFP and observed outcome through its existing feedback path; there is no second feedback ledger.

## Verification and rollback

`python3 -m unittest discover -s tests -p 'test_flywheel.py' -v` exercises the adapter. The dedicated `Flywheel adapter validation` workflow runs dependency-phase regressions and an executable loop, then retains the receipt as a CI artifact. The fixture-driven CI run proves adapter behavior only, not a production phase outcome or native Android compatibility. The portable smoke gate is not a substitute for a real Termux device test.

Rollback is a normal revert of the adapter, its test, and this scoped CI workflow. No installed upstream packages, running services, remote claims, weights, or task databases need cleanup. A production/live rollout remains a separate action requiring confirmation of its exact target and scope.

Implements: THUB-010.
