# Self-Healing Engine — P0 Delivery Roadmap

## P0.1 Incident primitive

**Status:** implemented (code) — `she/incident.py`  
**PR slice:** `feat/she-p01-incident-primitive` / #294

Define stable incident identity, lifecycle state, provenance, evidence references, authority scope, transition history, and terminal/escalation states.

- Module: `she.incident` (`Incident`, `IncidentState`, `Transition`)
- Tests: `tests/test_she_incident.py`
- Durable JSON via `to_mapping` / `from_mapping`

## P0.2 Event ingestion

**Status:** implemented (observer) — `she/ingest/actions.py`  
**PR slice:** `feat/she-p02-actions-ingest`

Normalize GitHub Actions failures, repo-gate, termux-smoke, Dependabot signals, tests, runtime health events, and agent failures into the incident fabric.

- Module: `she.ingest.actions` (`normalize_workflow_run_payload`, `incident_from_workflow_run`, `fingerprint_workflow_run`)
- Tests: `tests/test_she_ingest_actions.py`
- Observer only: pure construction of `Incident` from payload; no network, no persistence, no side effects.
- Stable fingerprint for optional later dedupe / known-fix lookup.
- Next increments: repo-gate / Dependabot normalizers, evidence store, optional webhook receiver.

## P0.3 L0 recovery

Implement deterministic recovery without source mutation: retry, restart, reconnect, refresh, regenerate transient state, reacquire locks, and safe rollback.

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
