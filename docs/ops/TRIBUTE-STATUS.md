# Tribute — Living Status & Human Review

**SSOT board (generated):** `docs/ops/generated/tribute-status.md`  
**Machine:** `docs/ops/generated/tribute-status.json`  
**Receipts:** `docs/ops/generated/tribute-evidence/*.jsonl`  
**Public dashboard:** `apps/tribute-dashboard/` → canonical Pages route `/tribute/`; Vercel **tribute-oversight** remains an implementation/deployment identifier.

Regenerate:

```bash
python3 scripts/ci/tribute_status.py
cp docs/ops/generated/tribute-status.json apps/tribute-dashboard/data/status.json
```

## Why this exists

Help-wanted is an **Oversight + evaluation** arm that also produces real external PRs.
This is **not** MoneyBall admission.

## Working well with others

| Rule | Behavior |
|------|----------|
| Claim idempotent | One claim marker; re-runs skip post |
| Closed issues | Default **skip** |
| Maintainer routing | Prefer upstream / feature fork when directed |
| Stake ≠ fix | Replace stake or close |

## Follow-up loop

1. Scout → claim once → upstream PR (or FALLBACK)
2. Evidence JSONL
3. `tribute_status.py` rebuilds board + dashboard snapshot
4. Vercel serves `apps/tribute-dashboard`

BIUDL. Agent-Identity: Grok (Administrator)
