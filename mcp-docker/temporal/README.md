# Temporal self-host (Docker)

Separated lane — **not** part of Vercel mcp-hub.

## Quick start

```bash
docker compose up -d
# gRPC frontend: localhost:7233
# UI:            http://localhost:8088
```

Prefer single-binary for pure local smoke:

```bash
temporal server start-dev --ui-port 8080
```

## Smoke worker

```bash
export TEMPORAL_ADDRESS=localhost:7233
python3 ../../scripts/temporal/hello_workflow.py
```

Optional LangSmith (external secret):

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=lsv2_...
export LANGSMITH_PROJECT=termux-monorepo-agents
```

## Boundary

- Dev/lab only until dual-gate path is proven.
- No secrets in this directory.
- Canonical telemetry remains OTEL + ATES/JSONL.
