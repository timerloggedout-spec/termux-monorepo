# skyhook

Termux **ground station** that hooks the **Jules cloud fleet**.

Multi-agent branch: `feature/skyhook` · Integration: `master-staging`

## Device first

Optimized for **BLU B160V** (Helio A22, ~3 GB RAM, 64 GB). See `research/DEVICE_B160V.md`.

- On-device: stdlib Python, existing HOME CLIs, offline doctor
- Off-device / CI: GH Actions (`jules-action`), full MCP, optional Bun dispatch
- Templates: **use or rewrite** — never bulk-install gold forks into Termux

## Doctor

```bash
python3 skyhook/scripts/doctor.py
```

## Layout

| Path | Role |
|------|------|
| `bridge/` | Config, plan_task, thin HTTP helpers |
| `mcp/` | Jules MCP wiring notes |
| `research/` | 🥇 RECON, B160V profile, deferred Antigravity |
| `scavenge/templates/` | SOURCE.txt only |
| `tasks/` | Claim queue + example Jules plans |
| `tests/` | Offline unit tests |

## Strategy

1. Jules protocol into skyhook (done: plans, tests, tier-1 RECON)
2. Production PRs via Jules sessions (Sentinel #18, Termux MCP #7)
3. Later: Antigravity via Jules + optional Colab credits
