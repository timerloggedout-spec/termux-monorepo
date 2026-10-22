# Actions Workflows Consolidated Matrix & Cadence Upgrade (2026-10)

## Goals
- Zero dual-gate failures.
- Reduce notification spam from Skipped / Cancelled / Stale / Timed-out / Neutral / Queued by treating operational lag as notices, consolidating concurrency groups, and modularizing schedules.
- Device identification with public obfuscation (tmx-node-primary for BLU B160V#1).
- Pinggy / Tailscale / alternatives operational on device #1; replica #2 for continuity.
- Caching & quota planning: prefer artifact retention, sparse checkout, concurrency cancel-in-progress where safe.
- C.A.D.E. continuous autonomous development environment.

## Repeated Issue Classes (historical + current)

| Class | Examples | Fix Applied / Planned | Status |
|-------|----------|-----------------------|--------|
| Tunnel / Bridge lag | Tunnel Canary failures on stale Pinggy endpoint | Hybrid lag-as-notice (exit 0), device_id public obfuscation | FIXED on this branch |
| Tailscale OIDC 403 | tailscale-bridge-probe token exchange unauthorized | Trust credentials refresh required outside workflow; probe remains honest RED | OPEN (auth) |
| Broken action pin | ATES Phase B upload-artifact SHA not resolvable | Updated to known-good v4.6.2 pin | FIXED |
| Concurrency spam | Multiple Context Relationship / n8n SHE / ledger cancelled on overlapping workflow_run | Existing cancel-in-progress; further modular consolidation recommended | PARTIAL |
| Schedule ghost / zero-job | Historical Merge Promotion Queue ghosts | Reaper + v3 migration already on master | CLOSED |
| Quota / rate limit | GitHub API 403/429, Vercel non-gate | Adaptive backoff already present; expand to more probes | ONGOING |

## Superseded / Consolidated Notes
- Older strict Tunnel Canary (exit 1 on any lag) superseded by hybrid notice path.
- Multiple device probes should share device_id contract and lag classification.
- Cadence: hourly canaries + adaptive reapers; avoid overlapping schedule windows that trigger cancel cascades.

## Flowchart (textual)
```
Device publish (Pinggy/Tailscale) -> ops/termux-bridge/current.json
       |
       v
Tunnel Canary (hourly)
  - read manifest + TCP
  - if lag/stale/unreachable -> ::notice:: + exit 0 (non-gate)
  - if healthy -> ::notice::bridge_up
       |
       v
Dual-gate (hygiene + termux smoke) remains separate authority
```

## Next
- Promote this branch after dual-gate green.
- Extend lag-as-notice pattern to other non-critical probes.
- Device #1 publisher diagnostics (scripts/termux/diagnose-pinggy-publisher.sh) must stay green for true operational status.
