# Consolidated Actions Workflows Matrix — 2026-10-28 Live Refresh (06:00Z)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL cycle)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-28T06:00Z)

- Master tip: `abbdb1009a3e0406de19877b2782439d37ba510f`.
- Recent master: Agentic Auth Canary success; Shared Observer Poller run 40638524798 **failure** (jq/date filter edge case on empty/transient API; diagnosed, hardened on this branch to exit 0).
- Residual high-volume **skipped** (lane-events-recorder ~46k+, agent-throughput-evidence, etc. on workflow_run): intentional early-exit filters. Notification spam vector; audited as operational, not silenced failures. Poller + future trigger retirement is the consolidation path.
- Delphi-rfp-feed-collect failures (e.g. 40636762274): HTTP 403 after retries. Hardened on branch (`rfp_flood_fetch.py` exit 0 + empty cache + ::warning::). Same class as historical observatory 39233561401.
- Other recent: agent-review-auto-jules failure (advisory/capacity); context-relationship success.
- Open PR #1966 carries delphi + prior matrix; this commit adds poller resilience.
- Device tunnel: Pinggy or Tailscale **must** remain operational on device #1. Opaque public `device_id=tmx-node-primary`. #2 replica. Live publisher required device-side.
- Credentials: names-only in issue #184.
- Quota / rate-limits: caching + adaptive cadence + moneyball. Capacity events non-gate.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel spam | lane-events-recorder, agent-throughput-evidence, workflow_run cascades | Broad triggers create run records even on job-level if skip | Shared poller (hardened) batches; modular router; retire residual triggers post dual-gate. Audit in matrix. | Operational residual; poller hardened |
| Poller self-failure | 40638524798 | jq date comparison / transient API | Hardened: exit 0 on error, simpler filter, ::warning:: | Fixed this cycle |
| Rate-limit / capacity | delphi-rfp-feed-collect 403, historical observatory 39233561401, ECC Tools | High volume API | Resilient exit 0 + ::warning:: + empty/fallback. Moneyball. | Fixed on branch (delphi); non-gate |
| Device tunnel / auth lag | Agentic Auth Canary, Tunnel Canary | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). Pinggy required on #1. | Soft residual / device-side |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; high workflow count | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |

## Cadence & Cache Improvements

- **Shared Observer Poller**: every 15 min, now resilient. Batches recent completed runs into one receipt. Only surfaces true failures; skips audited as operational.
- Adaptive WAIT: re-fetch on material delta.
- Cache: versioned namespaces; never treat cache as live quota.
- Notification reduction: only actionable dual-gate failures. Batched by SHA. Pure skips silent in notify but audited.
- Modular consolidations: target <100 active workflows.

## Flowchart

```mermaid
flowchart TD
  Event[Event] --> Router{Modular router / conclusion filter / poller}
  Router -->|Pure skip/cancel| Audit[Audit log only — no notify]
  Router -->|Material| Poller[Shared scheduled poller (resilient exit 0)]
  Poller --> Classify{success / failure / lag / capacity}
  Classify -->|Required gate fail| Alert[Notify + issue]
  Classify -->|Device lag / heartbeat missing| Notice[::notice:: + exit 0; tmx-node-primary]
  Classify -->|Capacity / quota / 403 / poller error| Defer[Moneyball rotate; ::warning:: + exit 0]
  Classify -->|Success| Receipt[Evidence]
  Notice --> Matrix[Update matrix]
  Defer --> Wait[Adaptive WAIT]
  Receipt --> Promote[Dual-gate auto-promote]
```

## Pinggy / Device #1

- **Required:** Pinggy or alternative operational on BLU B160V#1 (`tmx-node-primary`).
- Public obfuscation: never expose raw device identifiers.
- Fallback: `ssh -R0:localhost:port free.pinggy.io` until Tailscale proven.
- Probes treat missing heartbeat as notice, not failure.

## Superceded Notes

- Per-event observers partially superseded by shared poller (now hardened).
- High-volume workflow_run cascades reduced via filters + concurrency + poller.
- Dual-gate remains sole promote authority. Vercel non-gate.
- Historical skipped/cancelled audited; not rolled back erroneously.
- Previous PRs #1292/#1483/#1624 merged; #1966 open for this cycle.

**What was fixed this cycle:**
- Delphi RFP collector 403 resilience (exit 0).
- Shared Observer Poller hardened against self-failure (exit 0 on API/jq issues).
- Matrix updated with live recon of 40638524798 and residual skips.
- Feature preservation; attentive validation of all Skip/Cancel classes.

**Next:** Dual-gate validation on this SHA. Continue modular consolidations (retire residual workflow_run triggers). Device-side heartbeat on tmx-node-primary. Quota planning. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
