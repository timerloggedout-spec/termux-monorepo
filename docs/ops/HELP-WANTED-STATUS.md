# Help-Wanted — Living Status & Human Review

**SSOT board (generated):** `docs/ops/generated/help-wanted-status.md`  
**Machine:** `docs/ops/generated/help-wanted-status.json`  
**Receipts:** `docs/ops/generated/help-wanted-evidence/*.jsonl`

Regenerate:

```bash
python3 scripts/ci/help_wanted_status.py
```

## Why this exists

Help-wanted is an **Oversight + evaluation** arm that also produces real external PRs.
Humans need a single place to see:

- what was claimed
- which upstream PRs opened (or fallback notices)
- failures and why
- whether we are being good neighbors (no claim spam, respect closed + maintainer routing)

This is **not** MoneyBall admission. It is the human-review surface; a public Vercel dashboard can later read the JSON.

## Working well with others (non-negotiable)

| Rule | Behavior |
|------|----------|
| Claim idempotent | One claim marker per issue; re-runs skip post |
| Closed issues | Default **skip** (no claim, no stake PR) |
| Maintainer routing | If maintainers direct “fix upstream / use feature fork”, do not keep staking the parity fork |
| Stake ≠ fix | Stake PRs document intent; replace with real patch or close |
| Budget | Soft daily ceiling; prefer quality over volume |

### Example — DioNanos/codex-termux#14

Maintainer policy ([comment](https://github.com/DioNanos/codex-termux/issues/14#issuecomment-5231401407)):

- **codex-termux** = Android/Termux **parity** with upstream; platform packaging/runtime only.
- Upstream *logic* defects → report/fix **upstream** (benefits all platforms; sync picks up).
- **[codex-vl](https://github.com/DioNanos/codex-vl)** = deliberate feature-delta fork (not for parity patches).

`/init` AGENTS.md cache behavior was classified as upstream logic. Our help-wanted path must **not** keep re-claiming or staking that closed issue on the parity fork. Follow-up belongs upstream (or verification on current releases), not repeated stake noise.

## Follow-up loop

1. Scout ranks candidates (CPPH).
2. Execute claims once → contributes PRIMARY upstream PR (or FALLBACK notice).
3. Evidence receipt append-only JSONL.
4. `help_wanted_status.py` rebuilds the living board.
5. Humans (or agents) review board before re-dispatching the same issue.
6. Schedule stays adaptive (scout ~2h / execute ~4h) with budget gate.

## Dashboard (next)

- Public Vercel page: counts, last-N issues, PR links, fail reasons.
- Source of truth remains git JSON/JSONL under `docs/ops/generated/`.

BIUDL. Agent-Identity: Grok (Administrator)
