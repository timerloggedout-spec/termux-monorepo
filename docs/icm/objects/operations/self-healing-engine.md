---
type: object
cluster: operations
universe: live
status: initiated
entity: she/
verified_at: 2026-11-01
---

# Self-Healing Engine (SHE)

**SHE** is the repository's self-healing control plane: a Python package (`she/`) of control-plane primitives that turn repository failure signals into incidents, recovery plans, repair pull requests, and attested evidence. Its own package header (`she/__init__.py`) is the source of record for its pipeline; this card routes to the package and does not restate module internals.

## Shape (P0 pipeline, per `she/__init__.py`)

- **Incident + ingest (P0.1–P0.2):** observer-only normalizers convert Actions workflow runs, Dependabot, and the dual gates (`repo_gate`, `termux_smoke`) into `Incident` objects — no network, no side effects beyond constructing incidents.
- **Recovery (P0.3–P0.5):** L0 recovery planner + executor, an Actions re-run bridge (dry-run default), a dispatcher, and a repair sandbox planner.
- **Repair + decision (P0.6–P0.10):** verification planner, repair-PR planner, learning planner, evolutionary-repair planner, promotion-decision planner.
- **Evidence (P0.11–P0.14):** append-only evidence ledger, attestation digest, attestation replay verifier, publication planner.
- Supporting modules: `metrics/` (job timestamps, TDQS, ATES, agent throughput), `telemetry/` (canonical agent evidence projections), `provenance/` (runtime provenance, AIBOM-compatible builders), `edge/` (edge-inference conformance), `evaluation/` (manager-tournament primitives), `orchestration/` (DAG).

## Operating boundary

- Planners are **plan-first**: live execution is flag-gated per module (`live_*_enabled`), and the Actions bridge defaults to dry-run. A plan produced by SHE is not evidence that a repair ran.
- The lane-events source label `she` refers to this engine.
- Engine behavior changes belong to the package and its tests, never to this card.

## Read when

- Tracing how a CI/gate failure becomes an incident, a recovery action, or a repair PR.
- Checking what SHE may do autonomously versus what stays plan-only or flag-gated.
- Locating the evidence ledger / attestation surface for a self-repair claim.

## See

- Package: [`she/`](../../../../she/)
- Entry point: [`she/__init__.py`](../../../../she/__init__.py)
- Related workflows: [`.github/workflows/she-skill-clobber-heal.yml`](../../../../.github/workflows/she-skill-clobber-heal.yml)
