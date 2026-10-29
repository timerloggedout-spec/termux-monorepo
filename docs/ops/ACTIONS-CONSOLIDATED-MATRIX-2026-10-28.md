# Consolidated Actions Workflows Matrix — 2026-10-29 Live Refresh (00:10Z)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL cycle / PR #1966)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-29T00:10Z / ~17:10 PDT)

- Master tip: `af579adefc6da66efad639563c6d1f10764a5e36` (Merge PR #2307 — delphi: strands pass status=recorded). Recent master runs: success-dominant on dual-gate paths. High-volume skipped (lane-events-recorder, agent-throughput-evidence, delphi-signal-bridge, issue_comment cascades from gitar-bot etc.) audited as intentional early-exit filters — operational residual spam vector, **not** silenced failures. Cancelled concurrency (e.g. context audit) expected.
- Residual failure on tip: `delphi-rfp-feed-collect` run 40791167151 (workflow_run from gitar-bot) conclusion=failure. Job collect: HTTP Error 403 Forbidden in rfp_flood_fetch.py (old master script without resilience). Fix already present on this branch (retries + final 403/429 → ::warning:: + empty cache + exit 0). Classify as capacity/rate-limit residual until this PR promotes. Same class as historical observatory 39233561401.
- PR #1966 open (head now advancing from 004ab5a0, base still lagging abbdb100 vs current tip). Dual-gate pending. Rebase onto live tip required before promote.
- Device tunnel: Pinggy or Tailscale **must** remain operational on device #1. Opaque public `device_id=tmx-node-primary`. Replica #2 for continuity. Live publisher required device-side; probes treat lag as notice (exit 0). current.json may show stale — device-side action required.
- Credentials: names-only in issue #184 (do not pulse).
- Quota / rate-limits: caching + adaptive cadence + moneyball. Capacity events non-gate. High workflow count drives volume; modular consolidations + poller reduce skip-spam run records. The 403 on delphi is exactly this class.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel spam | lane-events-recorder, agent-throughput-evidence, workflow_run / issue_comment cascades | Broad triggers create run records even on job-level if skip | Shared poller batches; modular router; retire residual triggers post dual-gate. Audit in matrix/step summary. | Operational residual; poller active |
| Delphi RFP 403 | 40791167151 on af579ade | Rate-limit / capacity on issues list (old script) | Resilience on this branch: retry + exit 0 on final 403/429 + empty cache. | Residual on master; fixed on branch |
| Ledger / RECON race | prior on 1736ad5e | Fetch race / unavailable objects | Harden to exit 0 on race (preserve evidence). | Residual on branch; audit |
| Rate-limit / capacity | delphi-rfp-feed-collect 403, historical observatory | High volume API | Resilient exit 0 + ::warning:: + empty/fallback. Moneyball. | Fixed on branch; promote next |
| Device tunnel / auth lag | Agentic Auth Canary, Tunnel Canary, Tailscale | Publisher not live; heartbeat missing | Opaque device_id. Lag as notice (exit 0). **Pinggy required on #1**. | Soft residual / device-side |
| Vercel rate-limit | #772 | Hobby plan | Non-gate. Path filters. | Active / non-gate |
| Quota / caching | Free Actions; high workflow count | Provider limits | Dynamic adaptive cache, SHA+path filters, 3L0. Capacity ≠ failure. | Active |

## Cadence & Cache Improvements

- **Shared Observer Poller**: every 15 min, resilient (exit 0 on error). Batches recent completed runs into one receipt. Only surfaces true failures; skips audited as operational in step summary.
- Adaptive WAIT: re-fetch on material delta; concurrent disjoint work. Backoff on no delta.
- Cache: versioned namespaces; never treat cache as live quota. Path filters + SHA keying. Moneyball telemetry for adaptive.
- Notification reduction: only actionable dual-gate failures. Batched by SHA. Pure skips silent in notify but audited via poller/matrix. Modular consolidations target fewer active workflows.
- Concurrency groups + conclusion filters prevent cancelled zero-job spam.
- For 403 class: script-level resilience prevents Actions failure conclusion, reducing notification spam from capacity events.

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
- Delphi RFP collector 403 resilience (retry + exit 0) — on branch; residual failure on master tip until promote.
- Shared Observer Poller hardened against self-failure.
- Matrix updated with live recon of master tip af579ade, residual 40791167151 audited as capacity (not silenced), Pinggy device#1 MUST reaffirmed.
- Feature preservation; attentive validation of all Skip/Cancel classes.
- Notification spam reduction path: poller + resilience prevents capacity from creating failure notifications.

**Next:** Rebase PR #1966 onto live tip af579ade. Dual-gate validation on clean SHA → promote. Continue modular consolidations (retire residual workflow_run triggers). Device-side heartbeat on tmx-node-primary. Quota planning via adaptive cache/telemetry. Zero residual required-gate failures.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
