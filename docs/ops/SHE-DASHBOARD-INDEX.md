# SHE Dashboard / Evidence Surface Index

SHE is a projection surface over GitHub-native evidence. This index is the collaboration map so future agents do not recreate the same specification in another location.

## Canonical product contract

- `docs/ops/SHE-DASHBOARD-PRD.md` — product requirements and free-scope boundary.
- `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md` — machine-facing snapshot contract.
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd` — canonical Mermaid architecture source.

## Evidence and provenance contracts

- `docs/ops/HISTORICAL-CORPUS-BACKFILL-STATUS.md` — live corpus coverage and continuation state.
- `docs/ops/CONTEXT-RELATIONSHIP-INDEX.md` — corpus/index operating model.
- `docs/ops/HEX-ARTIFACT-RECOVERY.md` — ZIP provenance/relevance register.
- `docs/ops/HEX-MONEYBALL-INTEGRATION.md` — Hex contract and five-dataset topology.
- `docs/ops/EVIDENCE-ENVELOPE.schema.json` — generic evidence envelope.
- `docs/ops/ACTION-EFFECT-EVENT.schema.json` — temporal Action→Effect evidence.

## Existing automation / visual lane

The repository already has an automated documentation catalog and diagram asset lane:

- `.github/workflows/automation-docs-continuous-refresh.yml`
- `scripts/ci/automation_docs.py`
- `docs/ops/diagrams/*.mmd`
- `docs/ops/generated/automation-diagram-assets.json`
- `docs/ops/generated/*.png` derived renders where present

`.mmd` is authoritative source. Rendered PNGs are derived review assets. A generated PNG must never become the source of truth.

## Performance / telemetry lane

- `docs/ops/ACTIONS-METRICS-INTEGRATION.md` — durable Actions timing methodology.
- `she/metrics/job_timestamps.py` — pure Actions duration reducer.
- `she/metrics/agent_throughput.py` — Phase A ATES/WTCV reducer.
- `tests/test_she_agent_throughput.py` — focused ATES fixtures and missing-evidence invariants.
- `.github/workflows/agent-quality-lane.yml` — visible documentation/policy/schema/test quality check.
- `scripts/ci/verify_agent_quality.py` — deterministic static quality verifier.
- `docs/ops/AGENT-THROUGHPUT-METRICS.md` — ATES/WTCV evaluation policy and phased review model.
- `docs/ops/AGENT-OBSERVABILITY-PRIORITY-DECISION.md` — P0/P1/P2 provider, Docker, and Codespaces decisions.
- `docs/ops/AGENTIC-INTEGRATION-PLAN-STATUS.md` — current implementation/evidence state and next transitions.

## Hex boundary

Hex is not the execution authority and is not the repository source of truth. Sanitized GitHub evidence can be consumed by Hex when the connected workspace supports it. A native Hex ZIP is **not established** unless exact bytes and provenance are recovered.

## Historical backfill rule

`workspace/llm_map/context_relationships/manifest.json` is authoritative for current corpus coverage. `history_window.next_start_page != null` means continuation is required. A larger stale staging corpus must never silently replace canonical master evidence.
