# Temporal (self-host) + LangSmith Trajectories Adapter

**Status:** P1 observational · **Self-host first** · **Date:** 2026-09-24  
**Proposal:** `docs/proposals/active/temporal-langsmith-adapter/`  
**Canonical evidence remains:** OpenTelemetry + GitHub JSONL / ATES. This adapter never replaces them.

## Why

Long-running agents produce nested traces that are hard to read. LangSmith **Trajectories** project a thread into a flat chronological path (human / AI / tool messages once each). Temporal provides durable Workflows/Activities so those sessions survive process death, retries, and Worker boundaries. The official Python `LangSmithPlugin` keeps a single connected trajectory across those boundaries.

## Priority placement

| Layer | Priority | Role |
|-------|----------|------|
| OpenTelemetry | P0 | Neutral transport |
| ATES / JSONL | P0 | Canonical corpus |
| Temporal self-host | P1 | Durable execution substrate (optional) |
| LangSmith Trajectories | P1 | Readable path + online evals + dataset export (adapter) |
| Langfuse / Phoenix | P1 | Parallel eval adapters (unchanged) |

## Self-host first (available surfaces)

### 1. Local single-binary (fastest)

```bash
# Install Temporal CLI (operator machine / Codespace)
# https://docs.temporal.io/cli
temporal server start-dev --ui-port 8080
# UI: http://localhost:8080
# Frontend: localhost:7233
```

### 2. Docker Compose (repo surface)

```bash
cd mcp-docker/temporal
docker compose up -d
# UI: http://localhost:8088
# Frontend gRPC: localhost:7233
```

Same separation rule as `mcp-docker/github-mcp/`: **not** folded into Vercel mcp-hub.

### 3. Codespaces agent lane

Use existing Codespace agent lane (`docs/ops/CODESPACE-AGENT-LANE.md`) to run:

- Temporal dev server or Compose stack
- Worker process from `scripts/temporal/`
- Optional LangSmith tracing when `LANGSMITH_API_KEY` is present in the Codespace secret store

### 4. Temporal Cloud Free Tier (optional later)

Only after operator confirms signup and injects secrets. Not required for dual-gate or local smoke.

## LangSmith Trajectories (concepts)

| Concept | Shape | Use when |
|---------|-------|----------|
| Run | Single unit of work (span-like) | Debug one step |
| Trace | Tree of runs for one operation | Full execution detail |
| Thread | Sequence of traces (multi-turn) | Session linkage |
| **Trajectory** | Flat ordered messages across the thread | Read the path the agent took |

Enable tracing (capability-gated):

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_...   # external secret only
# optional: LANGSMITH_PROJECT=termux-monorepo-agents
```

Works with LangChain / LangGraph / Deep Agents and with SDK-style agents. Trajectories support online evaluators, annotation queues, and export to SFT datasets.

## Temporal ↔ LangSmith plugin (Python)

Experimental official plugin propagates context across Workers and avoids duplicate traces on replay.

```bash
pip install 'temporalio[langsmith]'   # or uv add temporalio[langsmith]
```

```python
from temporalio.client import Client
from temporalio.contrib.langsmith import LangSmithPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[LangSmithPlugin(project_name="termux-monorepo-agents")],
)
```

Optional: `add_temporal_runs=True` to also surface Temporal operations in LangSmith. Default keeps application logic only.

## Repo smoke

```bash
# Terminal A: temporal server start-dev   OR  docker compose -f mcp-docker/temporal/docker-compose.yml up
# Terminal B:
python3 scripts/temporal/hello_workflow.py
```

Env (all optional for structural smoke):

| Variable | Purpose |
|----------|---------|
| `TEMPORAL_ADDRESS` | default `localhost:7233` |
| `TEMPORAL_NAMESPACE` | default `default` |
| `TEMPORAL_TASK_QUEUE` | default `termux-agent` |
| `LANGSMITH_TRACING` | `true` to enable |
| `LANGSMITH_API_KEY` | external only |
| `LANGSMITH_PROJECT` | project name |

## Non-goals

- No hard CI dependency on Temporal or LangSmith for `repo_gate` / `termux_smoke`.
- No secrets or Class 3/4 artifacts in git.
- No replacement of OTEL/ATES as source of truth.
- Dual-gate green + verified outcome before promote.

## References

- LangSmith Trajectories: https://www.langchain.com/blog/langsmith-trajectories-tracing
- Observability concepts: https://docs.langchain.com/langsmith/observability-concepts
- Temporal self-host: https://docs.temporal.io/self-hosted-guide
- Temporal Python + LangSmith plugin: https://github.com/temporalio/sdk-python/tree/main/temporalio/contrib/langsmith
- Local CLI: https://docs.temporal.io/cli
