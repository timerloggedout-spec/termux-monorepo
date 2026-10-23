# Actions Workflows Consolidated Matrix & Cadence Upgrade (2026-10)

## Goals
- Zero dual-gate failures.
- Reduce notification spam from Skipped / Cancelled / Stale / Timed-out / Neutral / Queued by treating operational lag as notices, consolidating concurrency groups, and modularizing schedules.
- Device identification with public obfuscation (tmx-node-primary for BLU B160V#1; replica #2).
- Pinggy / Tailscale / alternatives operational on device #1; replica #2 for continuity when #1 screen broken.
- Caching & quota planning: prefer artifact retention, sparse checkout, concurrency cancel-in-progress where safe. Adaptive telemetry / moneyball for cadence.
- C.A.D.E. Continuously Autonomous Development Environment.

## Repeated Issue Classes (historical + current)

| Class | Examples | Fix Applied / Planned | Status |
|-------|----------|-----------------------|--------|
| Tunnel / Bridge lag | Tunnel Canary on stale Pinggy | Hybrid lag-as-notice (exit 0), device_id=tmx-node-primary | FIXED (master) |
| Tailscale unreachable | tailscale-bridge-probe exit 1 on offline | Hybrid lag-as-notice + device_id contract | FIXED on this branch |
| Tailscale OIDC 403 | token exchange unauthorized | Credentials refresh outside workflow (issue #184 names) | OPEN (auth) |
| Broken action pin | ATES Phase B upload-artifact | Updated to known-good v4.6.2 pin | FIXED |
| Concurrency spam | Context Relationship / n8n SHE / ledger cancelled on overlapping | cancel-in-progress; modular schedules; lag classification | PARTIAL → improved |
| Schedule ghost / zero-job | Historical Merge Promotion Queue | Reaper + v3 already on master | CLOSED |
| Quota / rate limit | GitHub API 403/429, Vercel non-gate | Adaptive backoff; expand probes | ONGOING |
| Skipped/Cancelled notifications | Watcher / status-refresh cascades | Concurrency groups + hybrid notices reduce surface | IMPROVED |

## Superseded / Consolidated Notes
- Older strict Tunnel Canary (exit 1 on any lag) superseded by hybrid notice path (PR #1496).
- Tailscale probe now shares the same lag classification contract as Tunnel Canary.
- Multiple device probes share public-obfuscated device_id=tmx-node-primary.
- Cadence: hourly canaries + adaptive reapers; avoid overlapping schedule windows that trigger cancel cascades.
- Skipped/Cancelled still generate notifications; further reduction via dedicated aggregator workflow recommended for future.

## Flowchart (textual)
```
Device publish (Pinggy preferred / Tailscale alt) -> ops/termux-bridge/current.json + tailscale.json
       |
       v
Tunnel Canary (hourly) + Tailscale Probe (every 30m)
  - read manifests + TCP/ping
  - if lag/stale/unreachable -> ::notice::lead_lag=lag_operational + exit 0 (non-gate)
  - if healthy -> ::notice::bridge_up
       |
       v
Dual-gate (hygiene + termux smoke) remains separate authority
       |
       v
Concurrency groups + cancel-in-progress limit cascade spam
```

## Next
- Dual-gate green on this SHA → promote.
- Extend lag-as-notice to remaining non-critical probes (vercel-quota, etc.).
- Device #1 publisher diagnostics (scripts/termux/diagnose-pinggy-publisher.sh) for true operational status.
- Consider consolidated notification router for residual Skipped/Cancelled.

Agent-Identity: Grok (Administrator)
