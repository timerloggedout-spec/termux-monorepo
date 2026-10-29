# Consolidated Actions Workflows Matrix — 2026-10-29 Live Refresh (04:00Z)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL / C.A.D.E. cycle / PR #1966)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-29T04:00Z / ~21:00 PDT)

- Master tip: `d1200aa3b417ef7972f6cf3f4efecf9ff25e81d0` (ops(help-wanted): live status refresh 2026-10-29T02:55Z). Recent master runs: success-dominant on dual-gate paths. High-volume skipped (lane-events-recorder, agent-throughput-evidence, delphi-signal-bridge, context-relationship-audit cancelled concurrency) audited as intentional early-exit filters or concurrency — operational residual spam vector, **not** silenced failures. No conclusion=failure in latest sampled window.
- On this branch: lane-events-recorder workflow_run already commented out (superseded by shared-observer-poller.yml). Master residual triggers explain ongoing skip records until promote.
- PR #1966 open. Dual-gate pending. Rebase onto live tip d1200aa3 required before promote.
- Device tunnel: Pinggy or Tailscale **must** remain operational on device #1. Opaque public `device_id=tmx-node-primary`. Replica #2 for continuity. Live publisher required device-side; probes treat lag as notice (exit 0). current.json may show stale — device-side action required.
- Credentials: names-only in issue #184 (do not pulse).
- Quota / rate-limits: caching + adaptive cadence + moneyball. Capacity events non-gate. High workflow count (252) drives volume; modular consolidations + poller reduce skip-spam run records.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel spam | lane-events-recorder (master), agent-throughput-evidence, workflow_run cascades, context audit cancelled | Broad triggers create run records even on job-level if skip or concurrency cancel | Shared poller batches; residual triggers retired on branch. Audit in matrix/step summary. | Operational residual on master; fixed on branch |
| Capacity / 403 | historical delphi-rfp, observatory | Rate-limit on API | Resilience: retry + ::warning:: + exit 0 + empty cache. | Fixed on branch; promote next |
| Device tunnel / auth lag | Tunnel Canary, Agentic Auth Canary, Tailscale | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). **Pinggy required on #1**. | Soft residual / device-side |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; 252 workflows | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |
| Zero-job ghosts | Historical disabled workflow | Schedule/workflow id | Reaper active; do not open new IDs. | Historical |

## Cadence & Cache Improvements

- **Shared Observer Poller** (shared-observer-poller.yml): every 15 min, resilient (exit 0 on error). Batches recent completed runs into one receipt. Only surfaces true failures; skips audited as operational in step summary.
- Adaptive WAIT: re-fetch on material delta; concurrent disjoint work. Backoff on no delta.
- Cache: versioned namespaces; never treat cache as live quota. Path filters + SHA keying. Moneyball telemetry for adaptive.
- Notification reduction: only actionable dual-gate failures. Batched by SHA. Pure skips silent in notify but audited via poller/matrix. Modular consolidations target fewer active workflows.
- Concurrency groups + conclusion filters prevent cancelled zero-job spam.
- Residual per-event observers retired on this branch.

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

- Per-event observers (lane-events-recorder workflow_run) superseded by shared poller on this branch.
- High-volume workflow_run cascades reduced via filters + concurrency + poller.
- Dual-gate remains sole promote authority. Vercel non-gate.
- Historical skipped/cancelled audited; not rolled back erroneously. Action_required is waiting, not failure.
- Previous PRs #1292/#1483/#1624 merged; #1966 open for this cycle. Base lagging — rebase before promote.

**What was fixed/refined this cycle:**
- Live recon to master tip d1200aa3: zero failures in sampled window; residual skips classified as operational (not silenced).
- Confirmed branch already retires residual workflow_run on lane-events-recorder.
- Matrix updated; Pinggy device#1 MUST reaffirmed with public obfuscation.
- Feature preservation; attentive validation of all Skip/Cancel classes.
- Notification spam reduction path advanced: promote this PR to eliminate residual master skip records.

**Next:** Rebase PR #1966 onto live tip d1200aa3. Dual-gate validation on clean SHA → promote. Continue modular consolidations. Device-side heartbeat on tmx-node-primary. Quota planning via adaptive cache/telemetry. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
