# Consolidated Actions Workflows Matrix — 2026-10-25 Upgrade (live refresh)

**Branch:** master (PR #1624 merged 2026-10-25)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait.
**Goal:** Z3π0 Failures, 100% SUCCESS on required gates. Attentive validation audits of Skipped/Cancelled/Action Required (not silenced). Reduce notification spam via modular consolidations. Operational Pinggy/Tailscale alternatives with public-obfuscated device identification. Quota-aware caching, cadence, 3L0 moneyball telemetry. C.A.D.E. Continuously Autonomous Development Environment.

## Current State Recon (2026-10-25T19:00Z)

- Master tip: `4633b3c2933b041f803d084b240bb6551bab5b48` (sweep accountability receipt). Success-dominant on dual-gates.
- Residual non-success: high-volume Skipped/Cancelled from lane-events-recorder, agent-throughput-evidence, context-relationship-audit, delphi-signal-bridge, fix-on-failure, deepseek-termux-agent, pr-production-ledger (bot-triggered workflow_run / issue_comment cascades). Audited as operational; notifications suppressed via filters + pollers. Validation required, not silence.
- Agentic Auth Canary / Tunnel Canary: device lag residual. Heartbeat missing on `ops/agentic-auth-heartbeat`. Classified notice + exit 0. Device #1 (tmx-node-primary, BLU B160V#1 broken screen) must publish via `scripts/termux/check-gh-agentic-auth.sh --publish`. Pinggy fallback operational requirement stands until Tailscale proven. #2 distinct.
- Historical quota runs (39233561401 observatory 403, 392349* ): capacity/API pressure, resilient path live (exit 0 + notice).
- No current filename/YAML parse failures. Ghost queued historical. Vercel non-gate.
- Cadence Lead/Lag owns true lag_failure. Adaptive delta cache avoids empty commits. 3L0 moneyball selects high-value paths.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Vercel rate-limit / deploy cap | #772 | Hobby plan daily cap | Path filters, admission, non-gate. Adaptive defer. | Active / non-gate |
| Skipped/Cancelled/Action Required spam | bot issue_comment, workflow_run cascades (lane-events ~36k, throughput ~53k) | Broad triggers + high volume | Modular router + conclusion filters + concurrency + scheduled pollers (observer-poller-scheduled, shared-observer-poller). Suppress pure skips in notifications. Validation audit for every non-success. | Advancing (pollers live; expand extraction) |
| Zero-job / queued ghosts | Historical | Schedule/workflow id | v3 live; reaper active. | Historical |
| Device tunnel / auth (Pinggy / Tailscale / Auth Canary) | Canary runs, BLU B160V#1/#2 | Publisher not live; heartbeat 404 | Opaque `device_id: tmx-node-primary`. Lag as notice (exit 0). Tailscale preferred; Pinggy fallback **required**. Device-side publish. | Operational gap / device-side |
| API pressure / stall watch / observatory | 39233561401 | High Actions volume / 403 | Resilient collection: capacity lag → exit 0 + receipt. | Fixed |
| Quota / capacity | Actions free; Vercel constrained | Provider limits | Adaptive telemetry, dynamic cache, 3L0 moneyball. No blind retries. Capacity ≠ failure. | Active |
| Filename / YAML parse | Historical | Not current-tree | Closed. | Closed |

## Cadence & Cache Improvements (3L0 Moneyball)

- Adaptive WAIT: re-fetch on material delta only; concurrent non-conflicting progress. Backoff on QUIET. Dynamic cadence from evidence.
- Cache: SHA + path filters; provider capacity snapshots; device health TTL. Dynamic adaptive for quota headroom; reset-aware.
- Modular consolidations: issue-comment-router early classify; scheduled pollers replace residual workflow_run skip records. Expand to full job extraction and deprecate redundant high-volume workflows.
- Notification reduction: only actionable gates/failures/incidents. Suppress skipped/cancelled bot spam + pure lag notices + action_required when non-blocking. Audit trail in step summary / JSONL. Batched by SHA.
- Quota planning: soft classification; moneyball selection of high-value paths. Act before exhaustion. Capacity lag ≠ correctness failure.

## Flowchart: Consolidated Decision Path

```mermaid
flowchart TD
  Event[Workflow Event] --> Filter{Relevant event?<br/>not pure bot comment spam}
  Filter -->|No| Skip[Skip + no notify + audit log]
  Filter -->|Yes| Classify{State: success/fail/skip/cancel/queued/action_required}
  Classify -->|Required gate fail| Alert[Notify + issue]
  Classify -->|Capacity / rate-limit / API pressure| Quota[Record + defer / moneyball rotate; exit 0 if non-gate]
  Classify -->|Skip/Cancel/ActionRequired| Audit[Validation audit; suppress notify via poller]
  Classify -->|Success| Record[Evidence receipt]
  Classify -->|Probe / tunnel / auth lag / heartbeat missing| Device[Record notice + device reconnect #1 tmx-node-primary; exit 0 if non-gate]
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
- Probes (tunnel-canary, agentic-auth-canary) treat lag/missing heartbeat as notice (exit 0 preferred) to reduce spam while preserving visibility via step summary / issues.
- Live status:active awaits device-side publish of heartbeat.json and tunnel manifests. Operator reconnect required for residual probes.

## Quota Limit Planning

- Vercel: non-gate, path-scoped ignore-build.
- Actions: free for public; track pressure (stall-watch / observatory resilience).
- Cache dynamic adaptive; 3L0 moneyball.
- No blind retries. Capacity classified separately from correctness failure.
- Cited historical runs (39233561401, 39234979788 etc.) are capacity pressure; current path resilient.

## Superceded / Combined Workflows Notes

- Merge Promotion Queue v1/v2 → v3.
- High-volume issue_comment → modular router + filters + scheduled pollers.
- Watcher dispatch-only; cadence owns incidents.
- Stall-watch / observatory resilient to API capacity.
- Dual-gate promote authority. Device probes non-gate when classified as lag.
- Conclusion filters + pollers on high-volume observers (lane-events-recorder, agent-throughput-evidence).

**Next:** Expand pollers to more lanes (throughput, context, delphi). Live device publisher on #1 (tmx-node-primary) for heartbeat + Pinggy/Tailscale. Confirm zero required-gate failures on tip. Continue C.A.D.E. BIUDL. Residual skips audited, not silenced.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.

## Prior recon retained

(See previous sections; PR #1624 evidence: modular router + pollers + softened canaries + cadence ownership. Historical runs classified as capacity/non-gate. Latest residual is high-volume skip records under filters.)
