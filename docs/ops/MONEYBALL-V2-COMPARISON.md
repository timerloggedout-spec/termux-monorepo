# MoneyBall v2 — competing schema + comparison vs v1

**Seat:** `[MUSEai]@{role:{moneyball-plane}}` · **Research cross-check:** issue #2206 (`[research:service] moneyball-decision-engine`, intake seed `research-seed:service:moneyball-decision-engine`) · **Status:** competing version, proposed alongside v1 — v1 records remain valid and untouched.

Owner order (2026-10-28): validate the existing schemas, build a competing version informed by the owner-supplied MoneyBall design export (decision-opportunity record; five separated quantities; point-in-time semantics; scouting evidence discipline), and execute the comparison tests on GitHub (`.github/workflows/moneyball-compare.yml`).

## Validation of the existing schemas (firsthand, 2026-10-28)

| existing artifact | what it guarantees | gap found |
|---|---|---|
| `ops/moneyball/plane.json` (`moneyball-plane/v1`) | plane config: axes, weight law, pass index, seams | no per-candidate score record schema at all; nothing validates a score |
| `oracle-method-pass/v1` (`docs/proposals/passes/*/pass.json`) | `moneyball_weighted` = candidate → number map | the record itself is a bare number — the charter's own rule ("a bare number is not a result") is unenforceable at record level; explanation lives only in RFP prose; no JSON Schema for the pass format exists in `docs/schemas/` |
| `ml/pipelines/moneyball/` (PR-triage) | deterministic `score()` (verified: green-PR fixture → 95.0); `explain()` returns score + global weights + why | no per-axis decomposition; weights are PR-domain constants, not per-pass intake fixes; separate domain (unchanged by v2) |
| `quota_weights.py` (`3l0.moneyball.v1`) | neutral 1.0 multiplier without live evidence | seam only; not a score record (unchanged by v2) |

## What v2 changes (`moneyball-plane/v2`)

Schema: `docs/schemas/moneyball-score.schema.json` · Validator: `scripts/moneyball/moneyball_v2.py` · Tests: `tests/test_moneyball_compare.py`.

1. **Opportunity, not entity.** A record scores `entity × action × context × decision_time`. The same entity can be attractive under one action/context and not another.
2. **Explanation is structural.** Every axis carries `value`, `evidence_refs`, `evidence_strength`, optional `uncertainty`. The validator recomputes the composite from weights × axes and rejects a mismatch — a bare number cannot validate.
3. **Weight law enforced.** `weights.fixed_at` must name the intake that fixed them; axes must sum to 1.
4. **Five quantities stay separate.** `capability / forecast / incremental_effect / value / surplus / portfolio_marginal_contribution` are distinct required keys. `incremental_effect: null` (unidentified) is valid and visible; an *absent* key is rejected.
5. **Baseline is required.** `baseline_id` names what the score is compared against.
6. **Ballot stays beside.** `ballot.relation` is the constant `beside_never_merged`.
7. **Point-in-time.** `event_time / published_at / ingested_at` are required; evidence published or ingested after `decision_time` is rejected (replay leakage).

What v2 deliberately does **not** do: change the axes or starting weights (per-pass law stands), touch the PR-triage scorer, touch 3L0 records, or migrate existing pass records. Temporal/Strands v1 records stay as history; v2 applies to new score records.

## Comparison tests (executed on GitHub)

`tests/test_moneyball_compare.py` — 16 tests:

- v1: Temporal record validates as v1; its explanation field set is exactly `{composite}` (the documented gap).
- v2: Temporal fixtures (synthetic uniform axes reproducing the recorded composites exactly) validate, recompute, and preserve the recorded ordering 8.9 > 8.5 > 6.5 > 4.8 > 3.6; identical Strands-style profiles stay tied; null `incremental_effect` validates.
- v2 rejections (all inexpressible in v1): bare-number record, weights ≠ 1, unfixed weights, merged ballot, missing baseline, absent quantity key, composite mismatch, axis without evidence, point-in-time leakage.
- Expressiveness: v2's field set strictly extends v1's.

Results are reported on the PR and on research issue #2206 with the Actions run id.
