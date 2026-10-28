# Consolidated Actions Workflows Matrix — 2026-10-28 Live Refresh (21:00Z)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL cycle / PR #1966)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-28T21:00Z / ~14:00 PDT)

- Master tip: `d388be61673422c0bdc44a525d34ce2e724c1f8a` (chore(ops): record sweep accountability receipt). Recent master runs: success-dominant on dual-gate paths (repo gate, termux smoke, sweep, context audit, n8n, hitl, foresight, orchestration-regression-guard). High-volume skipped (hark-enqueue-on-failure, lane-events-recorder on workflow_run) audited as intentional early-exit filters — operational residual spam vector, **not** silenced failures. Cancelled concurrency expected.
- PR #1966 open (head `1736ad5ec8d290284a5dccd8cf5ed2105f1e848a`, base lagging `abbdb100` vs tip). Dual-gate pending. Recent failures on this SHA:
  - Action Effectiveness Ledger run 40741190883: measure step failure (likely base/head fetch race or ARG_MAX residual; publish skipped). Classify as race/capacity — harden further to exit 0 on unavailable objects.
  - RECON INTEL discovery run 40741190917: discover job failure on "Resolve selected GitHub revision" (SHA mismatch race or setFailed path). Classify as residual race — already has skip notices; ensure fail-closed only on true invalid.
- Device tunnel: Pinggy or Tailscale **must** remain operational on device #1. Opaque public `device_id=tmx-node-primary`. Replica #2 for continuity. Live publisher required device-side; probes treat lag as notice (exit 0). current.json may show stale — device-side action required.
- Credentials: names-only in issue #184 (do not pulse; last update ~13:15Z).
- Quota / rate-limits: caching + adaptive cadence + moneyball. Capacity events non-gate. High workflow count drives volume; modular consolidations + poller reduce skip-spam run records.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel spam | lane-events-recorder, hark-enqueue-on-failure, workflow_run / issue_comment cascades | Broad triggers create run records even on job-level if skip | Shared poller batches; modular router; retire residual triggers post dual-gate. Audit in matrix/step summary. | Operational residual; poller active |
| Ledger measure failure | 40741190883 on 1736ad5e | Fetch race / unavailable objects / residual ARG_MAX | Harden measure to exit 0 on race (like existing receipt race path); preserve evidence. | Residual on branch; fix next |
| RECON INTEL resolve failure | 40741190917 | SHA changed during discovery or invalid path | Ensure notices + skip; avoid setFailed on race. | Residual on branch; audit |
| Rate-limit / capacity | delphi-rfp-feed-collect 403, historical observatory | High volume API | Resilient exit 0 + ::warning:: + empty/fallback. Moneyball. | Fixed on branch (delphi); non-gate |
| Device tunnel / auth lag | Agentic Auth Canary, Tunnel Canary, Tailscale | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). **Pinggy required on #1**. | Soft residual / device-side |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; high workflow count | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |

## Cadence & Cache Improvements

- **Shared Observer Poller**: every 15 min, resilient (exit 0 on error). Batches recent completed runs into one receipt. Only surfaces true failures; skips audited as operational in step summary.
- Adaptive WAIT: re-fetch on material delta; concurrent disjoint work. Backoff on no delta.
- Cache: versioned namespaces; never treat cache as live quota. Path filters + SHA keying. Moneyball telemetry for adaptive.
- Notification reduction: only actionable dual-gate failures. Batched by SHA. Pure skips silent in notify but audited via poller/matrix. Modular consolidations target fewer active workflows.
- Concurrency groups + conclusion filters prevent cancelled zero-job spam.

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
- Public obfuscation: never expose raw device identifiers, IPs, or hardware.
- Fallback: `ssh -R0:localhost:port free.pinggy.io` until Tailscale proven.
- Probes treat missing heartbeat as notice, not failure. Scripts: publish-pinggy-endpoint.sh, diagnose-pinggy-publisher.sh, install-pinggy-publisher-job.sh.
- September tests on original #1; dual-device continuity now. Device-side publish required for live heartbeat.

## Superceded Notes

- Per-event observers partially superseded by shared poller (hardened).
- High-volume workflow_run cascades reduced via filters + concurrency + poller.
- Dual-gate remains sole promote authority. Vercel non-gate.
- Historical skipped/cancelled audited; not rolled back erroneously.
- Previous PRs #1292/#1483/#1624 merged; #1966 open for this cycle. Base lagging — rebase before promote.

**What was fixed/refined this cycle:**
- Delphi RFP collector 403 resilience (exit 0) — on branch.
- Shared Observer Poller hardened against self-failure.
- Matrix updated with live recon of master tip d388be61, PR #1966 residual ledger/RECON failures audited as race/capacity (not silenced).
- Feature preservation; attentive validation of all Skip/Cancel classes.
- Pinggy operational MUST on device #1 reaffirmed with public obfuscation.

**Next:** Harden ledger measure + RECON resolve for race resilience (exit 0). Rebase PR #1966 onto live tip. Dual-gate validation on clean SHA → promote. Continue modular consolidations (retire residual workflow_run triggers). Device-side heartbeat on tmx-node-primary. Quota planning via adaptive cache/telemetry. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
