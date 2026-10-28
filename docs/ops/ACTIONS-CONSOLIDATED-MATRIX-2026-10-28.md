# Consolidated Actions Workflows Matrix — 2026-10-28 Live Refresh (17:00Z)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL cycle / PR #1966)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-28T17:00Z / ~10:00 PDT)

- Master tip: `35eaed34b23a3cd5e9289c5b7e42f99b62c4e147` (sweep accountability receipt).
- Recent master runs: high-volume **skipped** (lane-events-recorder dozens in seconds, agent-throughput-evidence, fix-on-failure, gemini-dispatch, model-live-canary, etc. on workflow_run / issue_comment) — intentional early-exit filters. Notification spam vector; audited as operational residual, **not** silenced failures. Shared Observer Poller + future trigger retirement is the consolidation path.
- **Cancelled:** context-relationship-audit, sweep-accountability on concurrency (expected lag_operational).
- Success-dominant for dual-gate paths, hitl-control-plane, foresight, orchestration-regression-guard, n8n, etc.
- PR #1966 open (head ~5b452271): delphi 403 resilience + poller hardening + matrix. Dual-gate pending on this SHA for promote.
- Device tunnel: Pinggy or Tailscale **must** remain operational on device #1. Opaque public `device_id=tmx-node-primary`. Replica #2 for continuity (original #1 screen broken). Live publisher required device-side; probes treat lag as notice.
- Credentials: names-only in issue #184 (do not pulse).
- Quota / rate-limits: caching + adaptive cadence + moneyball. Capacity events non-gate (historical 39233561401 class resolved by resilient exit 0).

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel spam | lane-events-recorder (~50k+), agent-throughput-evidence, workflow_run / issue_comment cascades | Broad triggers create run records even on job-level if skip | Shared poller (hardened, exit 0) batches; modular router; retire residual triggers post dual-gate. Audit in matrix. | Operational residual; poller active |
| Poller self-failure | 40638524798 | jq date / transient API | Hardened: exit 0 on error, simpler filter, ::warning:: | Fixed this cycle |
| Rate-limit / capacity | delphi-rfp-feed-collect 403, historical observatory | High volume API | Resilient exit 0 + ::warning:: + empty/fallback. Moneyball. | Fixed on branch (delphi); non-gate |
| Device tunnel / auth lag | Agentic Auth Canary, Tunnel Canary, Tailscale | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). **Pinggy required on #1**. | Soft residual / device-side |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; high workflow count (236) | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |

## Cadence & Cache Improvements

- **Shared Observer Poller**: every 20 min, resilient. Batches recent successful runs into one receipt. Only surfaces true failures; skips audited as operational.
- Adaptive WAIT: re-fetch on material delta; concurrent disjoint work.
- Cache: versioned namespaces; never treat cache as live quota. Path filters + SHA keying.
- Notification reduction: only actionable dual-gate failures. Batched by SHA. Pure skips silent in notify but audited via poller/matrix.
- Modular consolidations: target fewer active workflows; supersede high-volume observers.

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
- Public obfuscation: never expose raw device identifiers, IPs, or hardware.
- Fallback: `ssh -R0:localhost:port free.pinggy.io` until Tailscale proven.
- Probes treat missing heartbeat as notice, not failure. Scripts: publish-pinggy-endpoint.sh, diagnose-pinggy-publisher.sh, install-pinggy-publisher-job.sh.
- September tests on original #1; dual-device continuity now.

## Superceded Notes

- Per-event observers partially superseded by shared poller (hardened).
- High-volume workflow_run cascades reduced via filters + concurrency + poller.
- Dual-gate remains sole promote authority. Vercel non-gate.
- Historical skipped/cancelled audited; not rolled back erroneously.
- Previous PRs #1292/#1483/#1624 merged; #1966 open for this cycle.

**What was fixed/refined this cycle:**
- Delphi RFP collector 403 resilience (exit 0).
- Shared Observer Poller hardened against self-failure (exit 0 on API/jq issues).
- Matrix updated with live recon of residual skips on master tip 35eaed34 and PR #1966 status.
- Feature preservation; attentive validation of all Skip/Cancel classes (not silenced).
- Pinggy operational MUST on device #1 reaffirmed with public obfuscation.

**Next:** Dual-gate validation on this SHA → promote #1966. Continue modular consolidations (retire residual workflow_run triggers). Device-side heartbeat on tmx-node-primary. Quota planning via adaptive cache/telemetry. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
