# Help-Wanted Oversight Dashboard

Public Vercel surface for the help-wanted lane (evaluation / Oversight — **not** MoneyBall admission).

## Source of truth

| Layer | Path |
|-------|------|
| Evidence receipts | `docs/ops/generated/help-wanted-evidence/*.jsonl` |
| Status board (docs) | `docs/ops/HELP-WANTED-STATUS.md` |
| Machine status | `docs/ops/generated/help-wanted-status.json` |
| Dashboard snapshot | `apps/help-wanted-dashboard/data/status.json` |

```bash
python3 scripts/ci/help_wanted_status.py
cp docs/ops/generated/help-wanted-status.json apps/help-wanted-dashboard/data/status.json
```

Vercel root directory: `apps/help-wanted-dashboard`.
