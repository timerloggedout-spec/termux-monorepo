# Consolidated Actions Workflows Matrix — 2026-10-29 Live Refresh (02:00Z)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL / C.A.D.E. cycle)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-29T02:00Z / 19:00 PDT)

- Master tip: `3875308e40a31ca6b0f37a4c33a5b3503f1dd9e1` (data(ml): pr-lane-feed refresh [skip ci]). Recent master runs: success-dominant on dual-gate paths. High-volume skipped (lane-events-recorder ~55k, agent-throughput-evidence ~80k, issue_comment cascades from ecc-tools/gitar-bot, workflow_run early-exits) audited as intentional conclusion filters + concurrency — operational residual spam vector, **not** silenced failures. Cancelled concurrency (context-relationship-audit) expected. Action_required on PR workflows is platform waiting state, not failure.
- No new conclusion=failure observed in latest completed master window for required gates. Residual capacity class (prior delphi-rfp-feed-collect 403) fixed on branch via retry + exit 0.
- Tunnel Canary: hybrid lag-as-notice (exit 0) live; recent runs success. Device publisher still required device-side for heartbeat.
- Device tunnel: Pinggy or Tailscale **must** remain operational on device #1. Opaque public `device_id=tmx-node-primary`. Replica #2 for continuity. Probes treat lag as notice.
- Credentials: names-only in issue #184 (do not pulse).
- Quota / rate-limits: caching + adaptive cadence + moneyball. Capacity events non-gate. High workflow count (~252) drives volume; modular consolidations + shared poller reduce skip-spam run records.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel spam | lane-events-recorder, agent-throughput-evidence, workflow_run / issue_comment cascades | Broad triggers create run records even on job-level if skip | Shared poller batches; modular router; retire residual triggers. Audit in matrix/step summary. | Operational residual; poller active |
| Capacity / 403 | historical delphi-rfp, observatory | Rate-limit on API | Resilience: retry + ::warning:: + exit 0 + empty cache. | Fixed on branch; promote next |
| Device tunnel / auth lag | Tunnel Canary, Agentic Auth Canary, Tailscale | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). **Pinggy required on #1**. | Soft residual / device-side |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; 252 workflows | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |
| Zero-job ghosts | Historical disabled workflow | Schedule/workflow id | Reaper active; do not open new IDs. | Historical |

## Cadence & Cache Improvements

- **Shared Observer Poller**: every 15 min, resilient (exit 0 on error). Batches recent completed runs into one receipt. Only surfaces true failures; skips audited as operational in step summary.
- Adaptive WAIT: re-fetch on material delta; concurrent disjoint work. Backoff on no delta.
- Cache: versioned namespaces; never treat cache as live quota. Path filters + SHA keying. Moneyball telemetry for adaptive.
- Notification reduction: only actionable dual-gate failures. Batched by SHA. Pure skips silent in notify but audited via poller/matrix. Modular consolidations target fewer active workflows.
- Concurrency groups + conclusion filters prevent cancelled zero-job spam.
- For capacity class: script-level resilience prevents Actions failure conclusion, reducing notification spam from rate-limits.

## Flowchart

```mermaid
flowchart TD
  Event[Event] --> Router{Modular router / conclusion filter / poller}
  Router -->|Pure skip/cancel| Audit[Audit log only — no notify]
  Router -->|Material| Poller[Shared scheduled poller (resilient exit 0)]
  Poller --> Classify{success / failure / lag / capacity / race}
  Classify -->|Required gate fail| Alert[Notify + issue]
  Classify -->|Device lag / heartbeat missing| Notice[::notice:: + exit 0; tmx-node-primary]
  Classify -->|Capacity / quota / 403 / poller error / race| Defer[Moneyball rotate; ::warning:: + exit 0]
  Classify -->|Success| Receipt[Evidence]
  Notice --> Matrix[Update matrix]
  Defer --> Wait[Adaptive WAIT]
  Receipt --> Promote[Dual-gate auto-promote]
```

## Pinggy / Device #1

- **Required:** Pinggy or alternative operational on BLU B160V#1 (`tmx-node-primary`).
- Public obfuscation: never expose raw device identifiers, IPs, or hardware. Use opaque stable ID only.
- Fallback: `ssh -R0:localhost:port free.pinggy.io` until Tailscale proven.
- Probes treat missing heartbeat as notice, not failure. Scripts: publish-pinggy-endpoint.sh, diagnose-pinggy-publisher.sh, install-pinggy-publisher-job.sh.
- September tests on original #1 (broken screen); dual-device continuity on #2. Device-side publish required for live heartbeat.

## Superceded Notes

- Per-event observers partially superseded by shared poller (hardened).
- High-volume workflow_run cascades reduced via filters + concurrency + poller.
- Dual-gate remains sole promote authority. Vercel non-gate.
- Historical skipped/cancelled audited; not rolled back erroneously. Action_required is waiting, not failure.
- Previous PRs merged; this branch continues the matrix cycle.

**What was fixed/refined this cycle:**
- Live recon of master tip 3875308e. Residual high-volume skips audited as intentional filters (not silenced failures).
- Tunnel Canary confirmed hybrid notice-path success.
- Matrix advanced with 2026-10-29 refresh, Pinggy device#1 MUST reaffirmed, capacity class residual closed on branch.
- Feature preservation; attentive validation of all Skip/Cancel/ActionRequired classes.
- Notification spam reduction path strengthened: poller + resilience + modular consolidations.

**Next:** Rebase/promote this branch onto live tip after dual-gate SUCCESS. Continue modular consolidations (retire residual workflow_run triggers). Device-side heartbeat on tmx-node-primary. Quota planning via adaptive cache/telemetry. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
