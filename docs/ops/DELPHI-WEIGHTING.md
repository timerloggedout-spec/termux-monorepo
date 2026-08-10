# Delphi-style agent weighting (critical)

**Status:** active design — implement incrementally. **Critical component** of Decision Matrix evolution.

## Intent

Keep [`DECISION-MATRIX.md`](DECISION-MATRIX.md) as clean numeric data. Track **which agent / role / session** proposed each change in the signing ledger and debate log. Interpolate those traces as weights in a Delphi-like consensus layer.

## Signals

| Signal | Source | Use |
|--------|--------|-----|
| Agent identity | `Signed-off-by` + ledger | Who voted |
| Role | OPERATOR · skeptic · critic · **11th-man** · builder · reviewer | Weight class |
| Session id | Provider session | Continuity / recency |
| Diff pointer | Commit / PR URL | Audit |
| Score delta | Before/after Impact×Importance | Magnitude |
| Matrix-queue proposal | `<!-- matrix-proposal -->` | Non-binding cue |

## Illustrative formula (not yet enforced in CI)

```text
effective_score = Σ (agent_weight_i × score_i) / Σ agent_weight_i
```

Suggested initial weights (OPERATOR-tunable):

| Role | Weight |
|------|--------|
| OPERATOR | 1.0 |
| 11th-man (red-team) | 0.9 on reject evidence; 0.5 on bare accept |
| Skeptic | 0.8 |
| Critic | 0.7 |
| Builder/driver | 0.6 |
| Unrostered bot evidence | 0.0 (evidence only) |

## Non-goals

- No silent auto-rewrite of DECISION-MATRIX.md from Delphi alone without log commit.
- No secret session material in weights.

## Related

- [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md)
- [`ROLES-SKEPTIC-CRITIC-11TH.md`](ROLES-SKEPTIC-CRITIC-11TH.md)
- [`MATRIX-QUEUE.md`](MATRIX-QUEUE.md)
- `docs/CONSENSUS.md`

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-delphi-critical
