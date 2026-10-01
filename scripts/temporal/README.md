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
