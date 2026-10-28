# scripts/temporal

Minimal Temporal smoke for the self-host lane.

## Prerequisites

1. Temporal frontend up:
   - `temporal server start-dev`, or
   - `docker compose -f mcp-docker/temporal/docker-compose.yml up -d`
2. Python package: `pip install temporalio`  
   Optional trajectories bridge: `pip install 'temporalio[langsmith]'`

## Run

```bash
export TEMPORAL_ADDRESS=localhost:7233
python3 scripts/temporal/hello_workflow.py
# → hello, termux-monorepo
```

With LangSmith Trajectories (external secret only):

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_...
export LANGSMITH_PROJECT=termux-monorepo-agents
python3 scripts/temporal/hello_workflow.py
```

See `docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md`.

## §6 kill-and-resume harness + pass assets

Built for the Temporal durable-execution RFP (Oracle Method pass,
`docs/proposals/passes/temporal-durable-execution/`):

- `kill_resume_harness.py prove --address localhost:7233 --workdir <dir>` —
  the RFP §6 bounded build: kills a worker mid-activity, resumes on a
  second worker, asserts exactly one receipt + unknown-outcome
  reconciliation + history digest in an evidence envelope.
- `hitl_approval.py prove` — HITL approval: pause on signal, resume, complete.
- `envelope_schema.json` + `validate_envelope.py` / `validate_envelope.js` +
  `run_contract_fixture.py` — one schema, validators in 2 languages,
  aggregated violations (contract-first fixture).
- `skill_dry_walk.py` — serverless-skill dry-walk; cloud steps
  `specified_not_run` (card rule), local steps executed.
- `versioning_model.py` — Worker Versioning + autoscale model self-check.
- `doe_slice.py` — DoE 2⁴ factorial slice publishing canonical rows.

All assets: self-host dev server only, `pip install temporalio`, no
credentials.
