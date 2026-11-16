# OpenRouter free-counter question — probe design of record

`[MUSEai]@{role:{quota-specialist}}` · Question (owner, 2026-10-31): do PAID OpenRouter requests count against the 50/day free-model allowance (`free_model_daily_requests` in `GET /api/v1/auth/key`)?

## Final design (owner, 2026-10-31 — supersedes amendments 1–3)

∅ synthetic calls of any size. Measurement wraps PRODUCTION: bracket reads (free counter + credits balance) around the fleet's next REAL production paid-model request — the production call is the instrument, its natural size produces the Δ. Zero extra spend, zero test traffic.

Instrument: `scripts/ops/openrouter_bracket_snapshot.py` + `.github/workflows/openrouter-bracket-snapshot.yml` — read-only snapshots every 15 min (run artifacts, 90-day retention). Verdict rule: for a production paid call at time T, `free_model_daily_requests.used` at the first snapshot ≥ T minus at the last snapshot ≤ T ∈ {0, +n} answers inclusion; the credits Δ across the same bracket is the call's actual cost. Both readings also land per-snapshot (`is_free_tier`, key usage fields).

## Established en route (firsthand, probe v1 run 41261080142, PR #2828)

- Fleet key: `is_free_tier = true`; free counter live: used 3 / limit 50 / remaining 47 at 2026-11-01T01:26Z (the 3 = production free-variant traffic — the counter demonstrably counts free calls).
- Credits: `total_credits = 0`, `total_usage = 0.206466965` ⇒ purchased balance $0.00; account has never purchased credits (settles lab-1 blocker B1). Key-level usage counters all 0; the $0.2065 sits at account level.
- A paid call attempted in v1 returned HTTP 402 (never purchased credits) — NOT evidence on the question: no admitted paid call has occurred yet on this account.

## Amendment chain (all superseded designs, never dispatched)

1. Real-task paid call (retained review output) — owner correction: framing misread.
2. Batch N=10 small paid calls, Δ arithmetic — superseded by 3.
3. One LARGE paid call (~100k input tokens) — superseded by FINAL: ∅ synthetic, production is the instrument.

The v1/v2/batch/large probe workflows remain on master as dispatch-only artifacts of the chain; none runs without a deliberate dispatch, and the FINAL design needs none of them.

## State

Bracket series LIVE from the snapshot workflow's first run. Verdict = PENDING the first admitted production paid-model request inside the bracket — which, at balance $0.00, postdates any credit purchase on the account.
