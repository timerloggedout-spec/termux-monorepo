# Help-Wanted — Living Status & Human Review

**SSOT board (generated):** `docs/ops/generated/help-wanted-status.md`
**Machine:** `docs/ops/generated/help-wanted-status.json`
**Receipts:** `docs/ops/generated/help-wanted-evidence/*.jsonl`
**Public dashboard:** `apps/help-wanted-dashboard/` → Vercel **help-wanted-oversight**

Regenerate:

```bash
python3 scripts/ci/help_wanted_status.py
cp docs/ops/generated/help-wanted-status.json apps/help-wanted-dashboard/data/status.json
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
3. `help_wanted_status.py` rebuilds board + dashboard snapshot
4. Vercel serves `apps/help-wanted-dashboard`

BIUDL. Agent-Identity: Grok (Administrator)
