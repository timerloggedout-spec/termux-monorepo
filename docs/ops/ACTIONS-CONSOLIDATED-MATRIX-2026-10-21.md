# Consolidated Actions Workflows Matrix — 2026-10-22 Upgrade (refreshed)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (PR #1483)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait.
**Goal:** Z3π0 Failures, 100% SUCCESS on required gates. Attentive audit of Skipped/Cancelled. Reduce notification spam via modular consolidations. Operational Pinggy/Tailscale alternatives with public-obfuscated device identification. Quota-aware caching, cadence, 3L0 moneyball telemetry. C.A.D.E. Continuously Autonomous Development Environment.

## Current State Recon (2026-10-22 ~05:25 UTC)

- Master tip recent: success-dominant (lane events recorder, help-wanted-dashboard-deploy, Merge Promotion Queue v3, etc.). Example runs: 39727825830 success, 39727702096 success.
- Residual non-gate / operational:
  - Device tunnel/auth (Pinggy / Tailscale on BLU B160V #1/#2): lag classified as notice (exit 0 preferred). Opaque `device_id=tmx-node-primary`. Live publisher pending.
  - High-volume issue_comment bots: modular `issue-comment-router.yml` classifies early (jules/ledger/gemini only on match; bots skipped) → reduces Skipped/Cancelled spam.
  - Historical capacity/rate-limit (e.g. observatory 39233561401 403): superseded; stall-watch resilient.
- Watcher: dispatch-only. Cadence Lead/Lag (`*/4`) owns incident emission for true lag_failure.
- Dual-gate on PR #1483 preserved. Vercel Hobby non-gate (#772).
- Intentional concurrency cancels / skips: audited as non-failures; suppress notify where pure operational.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Vercel rate-limit / deploy cap | #1419, #1314 | Hobby plan daily cap | Path filters, admission, non-gate. Adaptive defer. | Active / non-gate |
| Skipped/Cancelled spam | bot issue_comment, concurrency | Broad triggers | Modular router + `if:` + concurrency groups. Cadence owns incidents. Suppress pure skips. | Advancing (router live) |
| Zero-job / queued ghosts | Historical | Schedule/workflow id | v3 live; reaper active. | Historical |
| Device tunnel / auth (Pinggy / Tailscale) | Auth Canary, Tunnel Canary, #1440, BLU B160V#1/#2 | Publisher not live; stale heartbeat/endpoint | Opaque `device_id: tmx-node-primary`. Lag as notice (exit 0). Live proof required. Tailscale preferred. | Operational gap / device-side |
| API pressure / stall watch | Runtime Stall Watch | High Actions volume | Resilient collection: capacity lag → exit 0 + receipt. | Fixed on branch |
| Quota / capacity | Actions free; Vercel constrained | Provider limits | Adaptive telemetry, dynamic cache, 3L0 moneyball. No blind retries. | Active |
| Filename / YAML parse | Historical | Not current-tree | Closed. | Closed |

## Cadence & Cache Improvements (3L0 Moneyball)

- Adaptive WAIT: re-fetch on material delta; concurrent non-conflicting progress. Backoff only on QUIET.
- Cache: SHA + path filters; provider capacity snapshots; device health.
- Modular consolidations: issue-comment-router absorbs high-volume unmatched comments; fewer orchestrators. Stall-watch resilience reduces false fails.
- Notification reduction: only actionable gates/failures/incidents. Suppress skipped/cancelled bot spam + pure lag notices. Audit trail preserved in step summary / JSONL.
- Quota planning: soft classification; moneyball selection. Act before exhaustion. Dynamic adaptive cache for capacity.

## Flowchart: Consolidated Decision Path

```mermaid
flowchart TD
  Event[Workflow Event] --> Filter{Relevant event?<br/>not pure bot comment spam}
  Filter -->|No| Skip[Skip + no notify + audit log]
  Filter -->|Yes| Classify{State: success/fail/skip/cancel/queued}
  Classify -->|Required gate fail| Alert[Notify + issue]
  Classify -->|Capacity / rate-limit / API pressure| Quota[Record + defer / moneyball rotate; exit 0 if non-gate]
  Classify -->|Skip/Cancel| Audit[Validation audit; suppress notify]
  Classify -->|Success| Record[Evidence receipt]
  Classify -->|Probe / tunnel / auth lag| Device[Record notice + device reconnect #1; exit 0 if non-gate]
  Quota --> Wait[Adaptive WAIT concurrent]
  Audit --> Matrix[Update consolidated matrix]
  Record --> Promote[Dual-gate auto-promote]
  Device --> Matrix
```

## Pinggy / Device Identification (Public Obfuscation)

- Device #1 (original BLU B160V, broken screen): operational tunnel or alternative required. Opaque public ID `tmx-node-primary`.
- Device #2: replica/observer; do not overwrite origin manifest.
- September tests on #1; dual-device now. Manifests report device_id + TTL + role.
- Tailscale preferred; Pinggy emergency fallback (ssh -R0:localhost:port free.pinggy.io). Credentials names-only in #184.
- Branch tunnel-canary + intended probes treat lag as notice (exit 0) to reduce spam while preserving visibility via step summary / issues.

## Quota Limit Planning

- Vercel: non-gate, path-scoped ignore-build.
- Actions: free for public; track pressure (stall-watch resilience added).
- Cache dynamic adaptive; 3L0 moneyball.
- No blind retries.

## Superceded / Combined Workflows Notes

- Merge Promotion Queue v1/v2 → v3.
- High-volume issue_comment → modular router + filters (early classify, no fan-out on bot spam).
- Watcher dispatch-only; cadence owns incidents.
- Stall-watch resilient to API capacity.
- Dual-gate promote authority. Device probes non-gate when classified as lag.

**Next:** Promote PR #1483 (dual-gate green). Live device publisher on #1 (tmx-node-primary) or proven Tailscale. Expand router to full job extraction. Continue C.A.D.E. BIUDL.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
