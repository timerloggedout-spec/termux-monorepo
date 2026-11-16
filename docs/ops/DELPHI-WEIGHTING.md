# Delphi-style agent weighting (future)

**Status:** ACTIVE since 2026-10-20 for the Delphi Oracle RFP gate ([`DELPHI-ORACLE-RFP-GATE.md`](DELPHI-ORACLE-RFP-GATE.md)). The decision matrix itself is still not auto-re-ranked (see Non-goals). _Original status: stub — not active in scoring yet._

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

## Activation (2026-10-20)

Implemented in `scripts/delphi/gate.py` with defaults in `ops/delphi/panel.json`:

```text
effective_score = Σ (w_i × score_i) / Σ w_i
w_i = base_i × (0.5 + gate_pass_rate_i) × (elo_i / 1500)
```

| Term | Source |
|---|---|
| `score_i` | DECISION-MATRIX Impact × Importance (1-25) from a blind role |
| `base_i` | role class: OPERATOR 1.2, cost_auditor 1.2, builder 1.0, reviewer 1.0, Scout 0.8 |
| `gate_pass_rate_i` | EWMA (α 0.2) of how often the role's pass/fail call matched real shadow-run outcomes |
| `elo_i` | 3L0-style record, ±16 per confirmed/missed call |

Live weights are append-only JSON comments on the `delphi:weights` issue; `panel.json` is only the cold start. Votes are signed per [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md). No session secrets enter weights.

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-delphi-stub
Signed-off-by: Hark (OPERATOR) delphi-gate-2026-10-20 / project-bbf883e1
