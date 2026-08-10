# Delphi-style agent weighting (critical)

**Status:** active design — implement incrementally. **Critical component** of Decision Matrix evolution.

## Intent

Keep [`DECISION-MATRIX.md`](DECISION-MATRIX.md) as clean numeric data. Track **which agent / role / session** proposed each change in the signing ledger and debate log. Interpolate via Delphi-like consensus.

Roster taxonomy (incl. **l337**, **haxor**, script-kiddie, scout, MoneyBall): [`ROLES-ROSTER.md`](ROLES-ROSTER.md) · **#129**.

## Signals

| Signal | Source | Use |
|--------|--------|-----|
| Agent identity | `Signed-off-by` + ledger | Who voted |
| Role | See roster + challenge roles | Weight class |
| Session id | Provider session | Continuity / recency |
| Diff pointer | Commit / PR URL | Audit |
| Score delta | Before/after Impact×Importance | Magnitude |
| Matrix-queue proposal | `<!-- matrix-proposal -->` | Non-binding cue |
| Arena (3L0/ELO) | #131 betting agents | Soft performance prior |

## Seed weights

| Role | Weight |
|------|--------|
| operator | 1.0 |
| 11th-man | 0.9 (reject+evidence) / 0.5 (bare accept) |
| haxor | 0.85 |
| skeptic | 0.8 |
| l337 | 0.75 |
| critic | 0.7 |
| engineer | 0.65 |
| researcher | 0.6 |
| scout / orchestrator | 0.55 |
| script-kiddie | 0.25 |
| bettor / spectator | 0.1 |
| unrostered bot | 0.0 |

```text
effective_score = Σ (agent_weight_i × score_i) / Σ agent_weight_i
```

## Non-goals

- No silent auto-rewrite of DECISION-MATRIX.md from Delphi alone.
- No secret session material in weights.

## Related

- [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md)
- [`ROLES-ROSTER.md`](ROLES-ROSTER.md)
- [`MATRIX-QUEUE.md`](MATRIX-QUEUE.md)
- #129 · #131 · `docs/CONSENSUS.md`

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-delphi-l337
