# Delphi-style agent weighting (future)

**Status:** stub — not active in scoring yet.

## Intent

Keep [`DECISION-MATRIX.md`](DECISION-MATRIX.md) as clean numeric data. Track **which OPERATOR agent / role / session** made each matrix edit in the signing ledger. Later, interpolate those traces as weights in a Delphi-like consensus layer.

## Sketch

| Signal | Source | Use |
|--------|--------|-----|
| Agent identity | `Signed-off-by` + ledger | Who voted |
| Role config | OPERATOR vs builder vs reviewer | Weight class |
| Session id | Provider session / Grok conversation | Continuity / recency |
| Diff pointer | Commit / PR URL | Audit |
| Score delta | Before/after Impact×Importance | Magnitude of shift |

Possible later formula (illustrative only):

```text
effective_score = Σ (agent_weight_i × score_i) / Σ agent_weight_i
```

where `agent_weight` derives from role reliability, historical gate-pass rate, or explicit OPERATOR roster config — not implemented yet.

## Non-goals (now)

- No automatic re-ranking of the matrix from this file.
- No secret session material in weights.

## Related

- [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md)
- `#145` / `#146` / `#118`

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-delphi-stub
