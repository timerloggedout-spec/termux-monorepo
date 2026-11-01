# Cadence amendment — doe-nc1-continuous-log (owner, 2026-11-01)

Owner: daily as-landed is insufficient. Cadence = statistically
significant intervals; BACKFILL chosen to raise baseline n; NO
step-down/step-back to daily (owner correction — backfill does not
license any frequency reduction; frequency changes only on
significance evidence, never calendar defaults).

## Backfill (baseline, one-time, idempotent on source hash)
Source: ops/telemetry/density-stats.json (telemetry ingest surface;
per-artifact density + stratum; evidence_hash-deduped).
- github +600 · records +28 (chat/docs not present in that surface)

## Cumulative per-stratum n after backfill + population snapshot
(population = layer-outputs 233u; snapshots never summed across runs)
- chat 32 · github 697 · docs 78 · records 54 — all >= 30 ✓
- Minority caveat (stated, not hidden): chat drift minority in the
  snapshot is 3/32 (<10) — verdict-share stats for chat remain
  NOT_ESTABLISHED until the minority clears; n-based density stats
  clear. Full rule: ESTABLISHED only n>=30 ∧ minority>=10 ∧ p<.05.

## Cadence
- Every 6h at :41 UTC (4x/day), single-flight, Swarm token, fail-soft.
- Each run logs window_new_units (population units new since the
  previous snapshot). Frequency is reviewed against that evidence
  only: a change requires recorded per-window significance numbers
  in a follow-up amendment — no silent or calendar-driven change.
- Scored gates unchanged (Linguist re-review); tau/floors frozen.

## Struck clauses (owner correction, 2026-11-01 00:25 PT)
The following clauses appeared in relayed versions of this amendment
(main submissions eb9ab979 / e77649df) and are STRUCK — they were
main's misread, rejected by the owner outright, and must not
propagate:
- STRUCK: "step-down to daily" (on evidence or otherwise).
- STRUCK: "daily may stand if backfill lands the baseline".
OF RECORD: cadence = statistically significant intervals, full stop.
Frequency is set by significance (per-stratum n clearing thresholds),
initially >1x/day (6h here), and changes only when the significance
evidence itself changes — never by reverting to a calendar default.
Backfill raises baseline n; it does not license any frequency
reduction by itself.
