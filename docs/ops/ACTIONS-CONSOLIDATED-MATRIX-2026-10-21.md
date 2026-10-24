# Consolidated Actions Workflows Matrix — 2026-10-24 Upgrade (live refresh)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (PR #1483 merged 2026-10-22; subsequent refinements on branch)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait.
**Goal:** Z3π0 Failures, 100% SUCCESS on required gates. Attentive validation audits of Skipped/Cancelled (not silenced). Reduce notification spam via modular consolidations. Operational Pinggy/Tailscale alternatives with public-obfuscated device identification. Quota-aware caching, cadence, 3L0 moneyball telemetry. C.A.D.E. Continuously Autonomous Development Environment.

## Current State Recon (2026-10-24T04:00Z)

- Master tip: `c8c162e5c5735eafe377540296b889c114a63ad0` (sweep receipt). Dual-gate success-dominant. Recent completed runs: success or intentional skipped/cancelled (concurrency, job-if filters, bot issue_comment unmatched).
- High-volume residual: lane-events-recorder, agent-throughput-evidence, bot-triggered workflows (vercel[bot], coderabbitai[bot], ecc-tools[bot]) producing Skipped/Cancelled. Conclusion filters + router reduce cascade starts; pure skips audited as non-failure (no notify).
- Historical notification runs cited:
  - 39233561401 (repository observatory, 2026-10-19): conclusion=failure on master SHA 2585bb6c. Classified capacity/API pressure (403/rate-limit class); resilient path now exit 0 + notice. Superseded.
  - 39234979788 / 39234979848 / 39234979983: peer/quota-registry class. Capacity lag, non-gate. Not current-tree correctness failure.
- Device tunnel (Pinggy / Tailscale on BLU B160V #1/#2): operational requirement stands. Opaque public `device_id=tmx-node-primary` for #1 (broken screen origin). Lag classified as notice (exit 0). Live publisher device-side. #2 distinct. Credentials names-only #184.
- Stall-watch / observatory resilient to API capacity. Vercel non-gate. Dual-gate promote authority.
- No recent filename-named workflow failures. Ghost queued historical (disabled workflow id).

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Vercel rate-limit / deploy cap | #772, #1419 | Hobby plan daily cap | Path filters, admission, non-gate. Adaptive defer. | Active / non-gate |
| Skipped/Cancelled spam | bot issue_comment, workflow_run cascades, concurrency | Broad triggers + high volume | Modular router + conclusion filters + concurrency groups + cadence ownership. Suppress pure skips in notifications. Validation audit required for every non-success. | Advancing (filters live; further modular extraction) |
| Zero-job / queued ghosts | Historical | Schedule/workflow id | v3 live; reaper active. Disabled workflow ghosts remain (cancel/delete 403). | Historical |
| Device tunnel / auth (Pinggy / Tailscale) | Auth Canary, Tunnel Canary, BLU B160V#1/#2 | Publisher not live; stale heartbeat | Opaque `device_id: tmx-node-primary`. Lag as notice (exit 0). Tailscale preferred; Pinggy fallback required. | Operational gap / device-side |
| API pressure / stall watch / observatory | 39233561401, Runtime Stall Watch | High Actions volume / 403 | Resilient collection: capacity lag → exit 0 + receipt. | Fixed |
| Quota / capacity | Actions free; Vercel constrained; cited runs | Provider limits | Adaptive telemetry, dynamic cache, 3L0 moneyball. No blind retries. Capacity ≠ failure. | Active |
| Filename / YAML parse | Historical | Not current-tree | Closed. | Closed |

## Cadence & Cache Improvements (3L0 Moneyball)

- Adaptive WAIT: re-fetch on material delta only; concurrent non-conflicting progress. Backoff on QUIET. Dynamic cadence from evidence (not fixed poll).
- Cache: SHA + path filters; provider capacity snapshots; device health TTL. Dynamic adaptive for quota headroom; reset-aware.
- Modular consolidations: issue-comment-router early classify (unmatched bots skip); expand to full job extraction and deprecate redundant workflows. Fewer full orchestrators.
- Notification reduction: only actionable gates/failures/incidents. Suppress skipped/cancelled bot spam + pure lag notices. Audit trail in step summary / JSONL. Batched by SHA / batch.
- Quota planning: soft classification; moneyball selection of high-value paths. Act before exhaustion. Capacity lag ≠ correctness failure.

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

- Device #1 (original BLU B160V, broken screen): operational tunnel or alternative **required**. Opaque public ID `tmx-node-primary`.
- Device #2: replica/observer; do not overwrite origin manifest. Distinct opaque ID.
- September tests on #1; dual-device now. Manifests report device_id + TTL + role.
- Tailscale preferred; Pinggy emergency fallback (ssh -R0:localhost:port free.pinggy.io). Credentials names-only in #184.
- Probes treat lag as notice (exit 0) to reduce spam while preserving visibility via step summary / issues.
- Live status:active awaits device-side publish. Operator reconnect required for residual probes.

## Quota Limit Planning

- Vercel: non-gate, path-scoped ignore-build.
- Actions: free for public; track pressure (stall-watch / observatory resilience).
- Cache dynamic adaptive; 3L0 moneyball.
- No blind retries. Capacity classified separately from correctness failure. Cited runs (39233561401 etc.) closed as capacity.

## Superceded / Combined Workflows Notes

- Merge Promotion Queue v1/v2 → v3.
- High-volume issue_comment → modular router + filters (early classify, no fan-out on bot spam).
- Watcher dispatch-only; cadence owns incidents.
- Stall-watch / observatory resilient to API capacity.
- Dual-gate promote authority. Device probes non-gate when classified as lag.
- Conclusion filters on high-volume observers (lane-events-recorder, agent-throughput-evidence).

**Next:** Expand router to full job extraction / deprecate redundant workflows. Live device publisher on #1 (tmx-node-primary) or proven Tailscale. Confirm zero filename failures on tip. Continue C.A.D.E. BIUDL.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.

## Prior recon retained

(See 2026-10-23 section; PR #1483 evidence: modular router + dispatch-only watcher + cadence ownership. Historical runs classified as capacity/non-gate.)
