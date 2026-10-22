# Consolidated Actions Workflows Matrix — 2026-10-22 Refresh

**Branch:** `ops/actions-matrix-upgrade-2026-10-22`
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait.
**Goal:** Z3π0 Failures, 100% SUCCESS on required gates. Attentive audit of Skipped/Cancelled. Reduce notification spam via modular consolidations. Operational Pinggy/Tailscale alternatives with public-obfuscated device identification. Quota-aware caching, cadence, 3L0 moneyball telemetry. C.A.D.E. Continuously Autonomous Development Environment.

## Current State Recon (2026-10-22 ~23:00 UTC)

- Master tip: `b488810e630b18bee1c2c7820aa1adcf3cf48e82` (sweep accountability receipt).
- Recent completed runs (latest 30+): success-dominant on core (Issue Observatory, context backfill, Merge Promotion Queue v3, ATES, etc.). Skipped/Cancelled are concurrency/workflow_run no-ops (lane-events-recorder, Agent Throughput Evidence, Fix-on-Failure, Context Relationship Audit). Not failures.
- Agent Runtime Stall Watch: failure on historical SHA `ff0c145e` (run 39836452223, open incident #1546) superseded by success on `2c58c8fc` (run 39863618840). Resilient capacity classification active.
- Dual-gate preserved. Vercel Hobby non-gate. Intentional concurrency cancels audited as non-failures.
- High-volume cascades remain (lane-events ~24k, throughput ~39k). Modular issue-comment-router live from #1483 reduces bot fan-out.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Vercel rate-limit / deploy cap | Historical #1419, #1314 | Hobby plan daily cap | Path filters, admission, non-gate. Adaptive defer. | Active / non-gate |
| Skipped/Cancelled spam | bot issue_comment, concurrency, workflow_run cascades | Broad triggers + high volume | Modular router + `if:` + concurrency groups + cadence ownership. Suppress pure skips in notifications. | Advancing (router live; expand extraction) |
| Zero-job / queued ghosts | Historical | Schedule/workflow id | v3 live; reaper active. | Historical |
| Device tunnel / auth (Pinggy / Tailscale) | Auth Canary, Tunnel Canary, BLU B160V#1/#2 | Publisher not live; stale heartbeat | Opaque `device_id: tmx-node-primary`. Lag as notice (exit 0). Tailscale preferred; Pinggy fallback. | Operational gap / device-side |
| API pressure / stall watch | Runtime Stall Watch run 39836452223 | High Actions volume / transient | Resilient collection: capacity lag → exit 0 + receipt. Latest run success. | Superseded / Fixed |
| Quota / capacity | Actions free; Vercel constrained | Provider limits | Adaptive telemetry, dynamic cache, 3L0 moneyball. No blind retries. | Active |
| Filename / YAML parse | Historical | Not current-tree | Closed. | Closed |

## Cadence & Cache Improvements (3L0 Moneyball)

- Adaptive WAIT: re-fetch on material delta; concurrent non-conflicting progress. Backoff only on QUIET.
- Cache: SHA + path filters; provider capacity snapshots; device health. Dynamic adaptive for quota headroom.
- Modular consolidations: issue-comment-router absorbs unmatched bot comments; fewer full orchestrators. Expand to full job extraction.
- Notification reduction: only actionable gates/failures/incidents. Suppress skipped/cancelled bot spam + pure lag notices. Audit trail in step summary / JSONL.
- Quota planning: soft classification; moneyball selection. Act before exhaustion.

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
- Stall-watch resilient to API capacity. Latest success.
- Dual-gate promote authority. Device probes non-gate when classified as lag.

**Next:** Expand router to full job extraction / deprecate redundant workflows. Live device publisher on #1 (tmx-node-primary) or proven Tailscale. Continue C.A.D.E. BIUDL. Close #1546 on superseded evidence.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
