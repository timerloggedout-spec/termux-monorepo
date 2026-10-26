# Consolidated Actions Workflows Matrix — 2026-10-26 Live Refresh (tip 7bdabc5a + current session)

**Branch:** `ops/actions-matrix-upgrade-2026-10-18` (continued BIUDL cycle)
**Authority:** Issue #631 13-phase + evidence-led-monorepo-ops + adaptive-wait + C.A.D.E.
**Goal:** Z3π0 Failures, 100% SUCCESS on required dual-gates. Attentive validation audits of Skipped/Cancelled/Stale/Timed-out/Action Required (never silenced). Reduce notification spam via modular consolidations + shared scheduled poller. Operational Pinggy or alternative on device #1 (`tmx-node-primary`, BLU B160V#1). Quota-aware caching, cadence, 3L0 moneyball adaptive telemetry.

## Current State Recon (2026-10-26 ~06:00Z / master tip `7bdabc5a00e15fc576c8de1fa232d8235133cc2b`)

- Master tip: `7bdabc5a00e15fc576c8de1fa232d8235133cc2b` (sweep accountability receipt). Dual-gate success-dominant. Recent completed runs show no new required-gate hard failures.
- **Residual high-volume skipped** (notification spam source): lane-events-recorder (dozens of runs per minute on workflow_run cascades from ecc-tools[bot] and others; job `if: conclusion == 'success'` skips the job but still creates the workflow run record that notifies). agent-throughput-evidence, delphi-signal-bridge, issue_comment bot cascades (Phantom secrets, DeepSeek CI, Action Effectiveness Ledger, etc. on #184 and similar). Concurrency cancels also contribute.
- Pure skips are audited as operational (filters working as designed); the volume of run records is the spam vector. Path: shared scheduled poller + modular router eliminate the per-event records.
- Tunnel / Agentic Auth Canary: lag treated as ::notice:: exit 0. Device #1 opaque public ID `tmx-node-primary`. **Pinggy or Tailscale MUST be operational** on BLU B160V#1 (broken screen; device-side publisher required). Device #2 is replica/observer only. September tests on original #1; continuity now dual-device.
- Credentials: names-only in issue #184 (extend connectors as needed; no values in docs).
- Quota / rate-limits: ~214 active workflows. Adaptive cache (versioned by SHA + day, never authoritative for live quota) + cadence + moneyball. Capacity/403 → ::warning:: + exit 0, never gate failure.
- Shared Observer Poller (`observer-poller-scheduled.yml` every 20m) and Issue Comment Router (`issue-comment-router.yml`) are the modular cuts. Expand poller targets; retire residual workflow_run triggers once dual-gate green on poller SHA.

## Repeated Issue Classes & Disposition

| Class | Examples | Root Cause | Fix / Disposition | Status |
|-------|----------|------------|-------------------|--------|
| Skip/Cancel/ActionRequired spam | lane-events-recorder (dozens/min), agent-throughput-evidence, delphi-*, issue_comment bots (ecc-tools[bot] etc.) | `workflow_run` on completed (incl. non-success) creates run record even if job-level `if` skips; broad `issue_comment` triggers | Shared success-only scheduled poller queries API and emits consolidated ledger (no per-event skip records). Modular issue-comment-router classifies early (bot/human/keywords/labels) and only proceeds on match. Concurrency groups. Retire workflow_run triggers post dual-gate proof. | Poller + router active; residual volume → expand + retire |
| Device tunnel / auth lag | Tunnel Canary, Agentic Auth Canary | Publisher lag / offline / OIDC / heartbeat missing | Opaque `device_id=tmx-node-primary`. Lag = ::notice:: exit 0. Pinggy fallback (`ssh -R0:localhost:port free.pinggy.io`) until Tailscale proven on device. Device #2 observer only. | Operational gap (device-side heartbeat required on #1) |
| Rate-limit / capacity | ECC Tools 403, historical observatory, Gemini, Vercel | High volume / free tier / hobby plan | Resilient ::warning:: + exit 0. Moneyball adaptive rotation. Never hard-fail required gates. Path filters. | Active / non-gate |
| Quota / caching | Free Actions minutes; 214 workflows | Provider limits | Dynamic adaptive cache, SHA+path filters, versioned namespaces (never treat cache as live quota). 3L0 telemetry for moneyball. Capacity ≠ failure. | Active |

## Cadence & Cache Improvements (3L0 Moneyball)

- **Shared Observer Poller**: every 20 min, batches recent successful runs into one receipt/ledger entry. Eliminates thousands of per-event skip-run records. Expand targets: lane-events, throughput, hark, context-relationship next.
- **Modular Issue Comment Router**: early classification prevents unmatched bot comments from spawning downstream jobs/spam.
- Adaptive WAIT: re-fetch only on material delta (new SHA or new failure class); concurrent progress on disjoint work.
- Cache: versioned by SHA + Pacific day; cache hit never skips current-SHA validation. Never authoritative for live quota/balance.
- Notification reduction: only actionable required-gate failures or incidents. Batched by SHA. Pure skip/cancel audited in matrix/ledger, not emailed. Poller + router is the cut for residual spam.
- Modular consolidations: group high-volume observers under one poller; deprecate individual `workflow_run` after dual-gate proof. Target <150 active trigger surfaces (from 214).

## Flowchart (Skip/Cancel Audit + Poller + Router Path)

```mermaid
flowchart TD
  Event[Event / schedule / issue_comment] --> Router{Filter / concurrency / poller / classify}
  Router -->|Pure skip/cancel or non-success or unmatched comment| Audit[Audit only — ledger + matrix, no notify]
  Router -->|Material success| Poller[Shared success-only poller every 20m]
  Router -->|Matched comment| Modular[Issue Comment Router routes only needed]
  Poller --> Classify{success / fail / lag / capacity}
  Classify -->|Required-gate fail| Alert[Notify + fix lane]
  Classify -->|Device lag / heartbeat missing| Notice[::notice:: exit 0; tmx-node-primary]
  Classify -->|Capacity / quota / 403| Defer[Moneyball ::warning:: exit 0]
  Classify -->|Success| Receipt[Evidence SHA-bound]
  Notice --> Matrix[Update matrix]
  Defer --> Wait[Adaptive WAIT]
  Receipt --> Promote[Dual-gate promote]
  Audit --> Matrix
  Modular --> Receipt
```

## Pinggy / Device #1

- **MUST** be operational on BLU B160V#1 (`tmx-node-primary`). Public obfuscation only (no raw IPs, serials, or hardware identifiers).
- Fallback: `ssh -R0:localhost:port free.pinggy.io` until Tailscale proven device-side.
- Probes treat missing heartbeat as notice, not failure. Device #2 is replication/observer only.
- September tests on original #1 (broken screen); continuity via #2 replica + #1 publisher.
- Supporting scripts: publish-pinggy-endpoint.sh, diagnose-pinggy-publisher.sh, install-pinggy-publisher-job.sh.

## Superceded Notes

- Per-event `workflow_run` observers partially superseded by shared poller (residual skip records remain until triggers retired post dual-gate).
- Individual `issue_comment` workflows partially superseded by modular router (starting point; full absorption next).
- Dual-gate (hygiene/portability + agentic termux smoke) remains sole promote authority. Vercel and capacity are non-gate.
- Skipped/Cancelled/Stale/Timed-out/Action Required require attentive validation audits — not erroneous rollbacks or silent failures. Residual run records from job-level `if` still notify; poller + router is the modular consolidation cut.
- Historical Phantom secrets / Auth Canary / observatory 403 classified as lag/capacity, not gate failures.

**What was refined this cycle (2026-10-26 session):**
- Live recon bound to tip `7bdabc5a` + current completed runs (no required-gate failures).
- Residual skip spam quantified from live workflow_run cascades (lane-events-recorder, throughput, delphi, bot issue_comment on multiple workflows).
- Poller + router path confirmed as the cut; expand targets and retire residual triggers next.
- Pinggy/Tailscale operational requirement on device #1 reaffirmed with public obfuscation (`tmx-node-primary`).
- Cadence/cache/3L0 moneyball tightened; notification reduction via poller + router + concurrency.
- Feature preservation: all historical classes audited; superseded workflows noted with upgrade path.

**Next:** Expand poller to throughput / hark / context; retire residual `workflow_run` triggers once dual-gate green on poller SHA. Complete absorption of issue_comment workflows into router. Device-side heartbeat publish on tmx-node-primary. Further consolidations to <150 active trigger surfaces. Zero residual required-gate failures. Promote on dual-gate.

Agent-Identity: Grok (Administrator)
**BIUDL** — Broad → Integrate → Validate → Develop → Learn.
C.A.D.E. Continuously Autonomous Development Environment.
