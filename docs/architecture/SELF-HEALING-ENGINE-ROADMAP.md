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

**Status:** implemented (planner + executor intents) — `she/recovery/l0.py` · `she/recovery/executor.py`

Deterministic recovery **without source mutation**: retry, restart, reconnect, refresh, regenerate transient state, reacquire locks, safe rollback of ephemeral state.

- `L0Plan` + `plan_l0_recovery(incident)` → ordered actions + authority scope
- `L0ExecutionPlan` + `plan_l0_execution(plan)` → Actions / Termux intent shapes
- Security/Dependabot signals → `observe_only` (no auto-retry)
- Canary helper: `intents_for_workflow_failure` (agentic-report / CE class)
- Live Actions re-run bridge (token-bearing job) is the next thin wire

## P0.4 Dynamic dispatcher

Select temporary worker roles from capability, authority, availability, workload, historical performance, environment compatibility, cost/quota, and MoneyBall/3L0 scoring signals.

MoneyBall/3L0 are decision-support inputs only; hard authority and policy constraints always dominate ranking.

## P0.5 Repair sandbox

Provide isolated branches/worktrees, bounded execution, scoped credentials, reproducible environments, and evidence capture.

## P0.6 Verification

Convert repo-gate, termux-smoke, domain tests, security checks, regression checks, and invariants into explicit healing evidence.

## P0.7 Autonomous repair PRs

L1 repairs produce inspectable commits/PRs with incident linkage, evidence, tests, and rollback context.

## P0.8 Learning

Persist successful and failed remediation patterns with provenance and verification history.

## P0.9 Evolutionary repair

L2: novel failures produce competing hypotheses, isolated experiments, benchmarks, candidate repairs, and gated promotion.

## Priority boundary

ArchW1z and deepcli-TUI remain existing parallel Termux interfaces. They should consume and project the shared protocols; they are not the P0 target. UI consolidation is deferred until the underlying self-healing, task, handoff, evidence, state, and dispatch primitives are stable.
