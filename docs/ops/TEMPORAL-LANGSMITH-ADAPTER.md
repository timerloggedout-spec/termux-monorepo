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

## Self-host first (automated surfaces)

### 1. GitHub Actions smoke (primary)

Workflow: `.github/workflows/temporal-self-host-smoke.yml`

Path-filtered + `workflow_dispatch`. Runner installs Temporal CLI, starts headless dev server, runs hello Workflow. Evidence = Actions run artifact/logs. **No operator CLI required.**

### 2. Docker Compose (repo surface)

```bash
cd mcp-docker/temporal && docker compose up -d
```

Separated from Vercel mcp-hub (same rule as `mcp-docker/github-mcp/`).

### 3. Codespaces agent lane

Existing Codespace agent lane hosts Worker reproduction when needed.

### 4. Temporal Cloud Free Tier (optional later)

Only after operator secrets exist. Not required for dual-gate or CI smoke.

## LangSmith Trajectories

| Concept | Shape | Use when |
|---------|-------|----------|
| Run | Single unit of work | Debug one step |
| Trace | Tree of runs | Full execution detail |
| Thread | Sequence of traces | Session linkage |
| **Trajectory** | Flat ordered messages | Read the path the agent took |

Capability-gated env (secrets external):

- `LANGSMITH_TRACING=true`
- `LANGSMITH_API_KEY` (Actions secret / Codespace secret)
- optional `LANGSMITH_PROJECT`

## Temporal ↔ LangSmith plugin

```python
from temporalio.client import Client
from temporalio.contrib.langsmith import LangSmithPlugin

client = await Client.connect(
    "localhost:7233",
    plugins=[LangSmithPlugin(project_name="termux-monorepo-agents")],
)
```

## Non-goals

- No hard dual-gate dependency on Temporal or LangSmith.
- No secrets in git.
- No replacement of OTEL/ATES as source of truth.
- FA-ADE: automation surfaces run the smoke; agents auto-promote on dual-gate + verified outcome.

## References

- https://www.langchain.com/blog/langsmith-trajectories-tracing
- https://docs.langchain.com/langsmith/observability-concepts
- https://docs.temporal.io/self-hosted-guide
- https://github.com/temporalio/sdk-python/tree/main/temporalio/contrib/langsmith
