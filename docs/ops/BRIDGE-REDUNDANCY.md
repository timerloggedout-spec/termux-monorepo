# Bridge redundancy (primary UI offline)

When the primary Termux unit has a **broken screen**, operators and agents must not block on interactive device UI.

## Execution hierarchy (use in order)

1. **GitHub Actions runners** (ubuntu-latest) — Cadence Lead/Lag, Tunnel Canary, telemetry, dual-gate, n8n emit.
2. **Secondary node** — set `TERMUX_DEVICE_ID` to a distinct opaque token; publish Pinggy from that unit.
3. **Cloudflare tunnel** (parallel to Pinggy per RESILIENCE.md) — when configured as alternate transport.
4. **Codespaces / Fly / Hindsight** — cloud execution surfaces already in workflows.
5. **Primary node headless** — ADB/SSH-only if reachable without the panel; publisher job 43109 does not need a working display.

## Opaque device IDs

Public manifest: `device_id` only (e.g. `tmx-node-primary`). No make/model. Map physical units off-repo.

## Lead/Lag applied to cadence

| Class | Meaning | Dual-gate? |
|-------|---------|------------|
| `lag_failure` | failure / timed_out / action_required | Blocks promote if named gate |
| `lag_operational` | skipped / cancelled / unset tunnel | Observation only |
| `lag_success_badge` | workflow success | Not task PASS alone |
| `lead_in_flight` | queued / in_progress | Adaptive WAIT |

Cadence workflow: `.github/workflows/cadence-lead-lag.yml`  
Classifier: `scripts/ops/lead_lag_cadence.py`  
Artifact: `docs/ops/generated/lead-lag-cadence.json`

**Correctness > green badges. Skipped route ≠ model failure.**
