# Lane Consolidation SSOT

This document is the **Single Source of Truth** for coordination, timing quotas, GHA debounces, and cooldown configurations across the monorepo's agentic pipelines.

## Active Quotas & Cooldown Configurations

| Layer / Component | Configuration Parameter | Value / Throttle | Purpose / Detail |
|---|---|---|---|
| **`model_router.py`** | Daily Soft Budget | Saved in `/tmp/model-router` | Elevated limits, OpenRouter free polling, ELO rankings |
| **`peer-review-orchestrator.yml`** | Auto-Fix Throttle | **45 minutes** | Cooldown between `@coderabbitai autofix` requests |
| **`peer-review-orchestrator.yml`** | Settle Delay | **90 seconds** | Settle time after autofix request before posting ready marker |
| **`agent-review-auto-jules.yml`** | Idempotent Window | **20 minutes** | Debounce window on bot feedback to avoid redundant Jules summons |
| **`agent-continuous-ops.yml`** | Sweep Debounce | **90 minutes** (Dynamic) | Time to wait after continuous ops comment before re-pinging |
| **`agent-continuous-ops.yml`** | Stale Agent Activity | **3 hours** (Dynamic) | Max idle time since last agent activity before nudging |
| **`agent-continuous-ops.yml`** | Schedule Interval | **Every 1 hour** (`17 * * * *`) | Backup cron job frequency to jump start stuck PRs |
| **`agent-continuous-ops.yml`** | Sweep Capacity | **8 to 20 PRs** | Max PRs evaluated per sweep |

## Current Work & Dynamic Response Lags

*Running locally/offline. Fallback defaults applied.*

| PR/Issue | Message Response Lag | Programmatic Response Lag | Status |
|---|---|---|---|
| Default Fallback | 1.5 hours | 3.0 hours | Active |
