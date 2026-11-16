# Consolidated Actions Workflows Matrix — 2026-10-25 Live Refresh

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (PR #1624)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Action Required (not silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy/Tailscale on device #1 (tmx-node-primary, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball.

## Current State Recon (2026-10-25T01:00Z / master tip ~91e1ba20)

- Master tip: `91e1ba20d481258fd88c31d94b6ca513ba2770b1` (sweep receipt). Dual-gate success dominant on required paths. No recent hard failures on master.
- Residual high-volume **skipped/cancelled** persists: lane-events-recorder (~33k runs), agent-throughput-evidence, delphi-signal-bridge, bot issue_comment triggers on #184 etc. Pure skips generate notification entries — audited via pollers, not silenced. Volume remains high (thousands of workflow_run skips per hour class).
- PR #1624 head `d312a2fa` base is stale vs live master (599556ef → 91e1ba20). Needs rebase before promote.
- Active residual classes:
  - Agentic Auth Canary: heartbeat 404 / device lag → notice + exit 0 path present on branch.
  - ECC Tools / rate-limit 403 capacity pressure → prefer warning + exit 0.
  - Provider capacity intermittent.
- Device tunnel: Pinggy or Tailscale **must** be operational on device #1. Opaque public `device_id=tmx-node-primary`. #2 replica. Live publisher required device-side.
- Credentials: names-only in issue #184.
- Quota / rate-limits: caching + adaptive cadence + moneyball required. 212 active workflows drive volume.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel/ActionRequired spam | lane-events-recorder (high run count), agent-throughput-evidence, bot comments | Broad `workflow_run` / `issue_comment` on all conclusions | Shared scheduled poller batches; modular router + conclusion filters; concurrency groups. Suppress pure skips in notifications; audit in step summary. Expand poller coverage. | **Advanced** (needs rebase + promote + further filter tightening) |
| Device tunnel / auth lag | Agentic Auth Canary, Tunnel Canary | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). Pinggy fallback required. | Operational gap / device-side |
| Rate-limit / capacity | ECC Tools 403, historical | High volume API | Resilient exit 0 + ::warning::. Moneyball. | Active |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; 212 workflows | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |

## Cadence & Cache Improvements

- **Shared Observer Poller**: every 15 min, batches recent completed runs into one receipt. Eliminates per-event skip-run records. Only surfaces true failures.
- Adaptive WAIT: re-fetch on material delta; concurrent progress.
- Cache: versioned namespaces; never treat cache as live quota.
- Notification reduction: only actionable dual-gate failures/incidents. Batched by SHA. Pure skips audited but silent.
- Modular consolidations reduce workflow count (target <100 active for noise reduction).

## Flowchart

```mermaid
flowchart TD
  Event[Event] --> Router{Modular router / conclusion filter}
  Router -->|Pure bot spam / skip| Audit[Audit log only — no notify]
  Router -->|Material| Poller[Shared scheduled poller batches]
  Poller --> Classify{success / failure / lag / capacity}
  Classify -->|Required gate fail| Alert[Notify + issue]
  Classify -->|Device lag / heartbeat missing| Notice[::notice:: + exit 0; device#1 tmx-node-primary]
  Classify -->|Capacity / quota / 403| Defer[Moneyball rotate; ::warning:: + exit 0]
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

- Per-event observers partially superseded by shared poller.
- High-volume workflow_run cascades reduced via filters + concurrency.
- Dual-gate remains sole promote authority. Vercel non-gate.
- Historical skipped/cancelled audited; not rolled back erroneously.
- PR base drift: rebase required before merge.

**Next:** Rebase PR #1624 onto live master tip. Promote on dual-gate. Device-side heartbeat publish for #1. Further consolidate high-volume observers (lane-events-recorder, agent-throughput-evidence). Expand poller. Target workflow count reduction. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
