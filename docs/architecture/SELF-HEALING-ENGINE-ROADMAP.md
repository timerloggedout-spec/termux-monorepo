# Self-Healing Engine — P0 Delivery Roadmap

## P0.1 Incident primitive

**Status:** implemented (code) — `she/incident.py`  
**PR slice:** `feat/she-p01-incident-primitive` / #294

Define stable incident identity, lifecycle state, provenance, evidence references, authority scope, transition history, and terminal/escalation states.

- Module: `she.incident` (`Incident`, `IncidentState`, `Transition`)
- Tests: `tests/test_she_incident.py`
- Durable JSON via `to_mapping` / `from_mapping`

## P0.2 Event ingestion

**Status:** implemented (observer complete) — `she/ingest/`  
**PR slices:** #345 Actions · #346 repo-gate · stacked Dependabot + termux-smoke

Normalize GitHub Actions failures, repo-gate, termux-smoke, Dependabot signals into the incident fabric.

| Module | Entry points |
|--------|----------------|
| `she.ingest.actions` | workflow_run / job → Incident |
| `she.ingest.repo_gate` | gate/check failure → Incident |
| `she.ingest.termux_smoke` | smoke result → Incident |
| `she.ingest.dependabot` | alert/advisory → Incident |

Observer only: pure construction; no network, no persistence. Stable fingerprints for dedupe / known-fix.

**Vendor framing:** prefer no vendoring; note upstreams when useful (e.g. MSFT SWE-bench-Live for eval research). Not a promotion gate.

## P0.3 L0 recovery

**Status:** implemented (planner + executor intents + Actions bridge dry-run) — `she/recovery/`

Deterministic recovery **without source mutation**: retry, restart, reconnect, refresh, regenerate transient state, reacquire locks, safe rollback of ephemeral state.

- `L0Plan` + `plan_l0_recovery(incident)` → ordered actions + authority scope
- `L0ExecutionPlan` + `plan_l0_execution(plan)` → Actions / Termux intent shapes
- Security/Dependabot signals → `observe_only` (no auto-retry)
- Canary helper: `intents_for_workflow_failure` (agentic-report / CE class)
- Actions bridge: `plan_actions_commands` / `execute_actions_bridge` (live behind `SHE_L0_LIVE=1`)

## P0.4 Dynamic dispatcher

**Status:** implemented (code) — `she/recovery/dispatcher.py` · #375  
**Package:** SHE `0.4.0` on master (dispatcher); SHE `0.5.0` after P0.4.1 wire

Select temporary worker roles from capability, authority, availability, workload, historical performance, environment compatibility, cost/quota, and MoneyBall/3L0 scoring signals.

MoneyBall/3L0 are decision-support inputs only; hard authority and policy constraints always dominate ranking. Capability checks use **subset** (`needed.issubset(have)`), never intersection.

### P0.4.1 Dispatch → Actions bridge (dry-run wire)

**Status:** implemented — #378 merged `eac116b` (`dispatch_then_bridge`)  
**Note:** branch/title historically said “P0.5”; roadmap reserves **P0.5** for repair sandbox. This slice is the thin ranking→command-plan wire.

- `dispatch_then_bridge(plan, …)` ranks via `dispatch_l0_plan`, then plans Actions commands
- Default remains dry-run; network still requires `SHE_L0_LIVE=1`
- Unfiltered `bridge_workflow_failure` kept for P0.3 regression

## P0.5 Repair sandbox

**Status:** implemented (planner) — `she/sandbox.py` · package `0.6.0` · #380 `13c02d4`

Isolated workspace contract for later L1 repair. Observer-only in this slice: no git mutation, no network.

- `SandboxPlan` + `plan_repair_sandbox(incident)` → branch, worktree path, credential profile, env profile, evidence dir
- Branch namespace: `she/repair/<incident>-<fingerprint>`
- Dependabot / security signals → `credential_profile=none`
- Live materialization gated by `SHE_SANDBOX_LIVE=1` and **not implemented** here
- Tests: `tests/test_she_sandbox.py`

## P0.6 Verification

**Status:** implemented (planner) — `she/verify.py` · package `0.7.0` · #381

Convert repo-gate, termux-smoke, domain tests, security checks, regression checks, and invariants into explicit healing evidence.

- `VerificationPlan` + `plan_verification(incident, sandbox=?)` → required check set
- Dual gates (`repo-gate` + `termux-smoke`) are **always required** (subset check)
- Dependabot/security fingerprints require `security-checks`
- `apply_check_results` records outcomes; HTTP 200 / `inconclusive` cannot promote
- No live workflow dispatch in this slice
- Tests: `tests/test_she_verify.py`

## P0.7 Autonomous repair PRs

**Status:** implemented (planner + P0.7.1 bindings) — `she/repair_pr.py` · package `0.8.0` · #383

Planner produces **metadata for inspectable repair PRs**. It does not create branches, commits, or pull requests.

- `RepairPRPlan` + `plan_repair_pr(incident, sandbox=?, verification=?)`
- Dual gates always required tests (subset)
- Security/Dependabot → observe-only (no repair PR)
- Branch stays in `she/repair/` namespace; `rollback_sha` must equal source `sha`
- Supplied sandbox/verification plans must match incident id + SHA
- `from_mapping` forces `promotion_ready=False` / `live=False` / `mutates_source=False`
- Live PR creation gated by `SHE_REPAIR_PR_LIVE=1` and **not implemented** here
- Tests: `tests/test_she_repair_pr.py`

## P0.8 Learning

**Status:** open / held — #384 (`feat/she-p08-learning-planner`)  
`mergeable_state=unstable` (cancelled non-gate checks). Dual gates on that SHA are green. No force-merge.

Persist successful and failed remediation patterns with provenance and verification history.

- Planned module: `she/learn.py` (`LearningRecord`, `plan_learning`)
- Live persistence gated by `SHE_LEARN_LIVE=1` and not implemented in the held slice

## P0.9 Evolutionary repair

**Status:** implemented (planner) — `she/evolve.py` · package `0.10.0`

L2: novel failures produce competing hypotheses, isolated experiments, benchmarks, candidate repairs, and gated promotion.

- `EvolutionPlan` + `plan_evolution(incident, sandbox=?, verification=?)`
- Five isolated hypotheses; one experiment each under `she/evolve/<id>/<kind>`
- Dual gates always required (subset) on plan, hypotheses, and experiments
- Security/Dependabot → observe-only
- `from_mapping` fail-closed (`live=False`, `mutates_source=False`, `promotion_ready=False`)
- Live evolution gated by `SHE_EVOLVE_LIVE=1` and **not implemented** here
- Tests: `tests/test_she_evolve.py`

## Priority boundary

ArchW1z and deepcli-TUI remain existing parallel Termux interfaces. They should consume and project the shared protocols; they are not the P0 target. UI consolidation is deferred until the underlying self-healing, task, handoff, evidence, state, and dispatch primitives are stable.
