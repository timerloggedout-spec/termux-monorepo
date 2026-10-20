---
id: temporal-langsmith-adapter
title: "Temporal self-host + LangSmith Trajectories adapter (P1 observational)"
author: grok
posted_at: 2026-09-24
source: operator directive — LangSmith Trajectories blog + Temporal FOSS Free Tier; self-host first
status: executing
priority: P1
reviewers:
  - id: grok
    role: author+executor
    status: executing
  - id: timerloggedout-spec
    role: operator-authorizer
    status: requested
related_prs: []
related_branches:
  - feat/temporal-langsmith-adapter
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — Temporal + LangSmith Trajectories Adapter

## Summary

Upgrade agent observability and durable-execution posture with:

1. **Temporal** (MIT OSS) — self-host first (`temporal server start-dev` → Docker Compose under `mcp-docker/temporal/`) using existing surfaces (Docker, Codespaces agent lane, local). Free Tier Cloud is optional later, not required.
2. **LangSmith Trajectories** — readable chronological path over multi-turn agent sessions (flat ordered messages). P1 observational adapter parallel to Langfuse/Phoenix. Never replaces OTEL + GitHub JSONL canonical evidence.

Official Temporal Python `LangSmithPlugin` connects Worker-boundary traces so trajectories remain coherent across durable Activities.

## Boundary

- Self-host path is primary. Cloud Free Tier only after operator confirms account.
- Capability-gated: no hard dependency for dual-gate paths.
- No secrets committed (`LANGSMITH_API_KEY`, Temporal Cloud keys stay external).
- OTEL + ATES remain P0 canonical; LangSmith/Temporal are adapters/substrate.
- Extract-only; no mega-PR fold into mcp-hub / Vercel.

## Surfaces used

| Surface | Role |
|---------|------|
| Local CLI | `temporal server start-dev` |
| Docker Compose | `mcp-docker/temporal/` (same separation pattern as github-mcp) |
| Codespaces agent lane | Interactive reproduction / Worker runs |
| GitHub Actions | Optional smoke later; not a merge gate dependency |

## Evidence

See `ITEMS.md`, `docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md`, matrix updates.
