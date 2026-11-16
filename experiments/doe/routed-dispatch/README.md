# routed-dispatch — the routing layer's intake campaign

`[MUSEai]@{role:{optimizations-assurance}}` · Owner routing update, 2026-11-01.

Every routed+assigned dispatch completed by the fleet routing layer emits its full stamp here (one EXPERIMENT record per dispatch) via `scripts/dispatch/stamp_fanout.py` / `.github/workflows/dispatch-stamp-fanout.yml`, alongside the sibling plane intakes (`ops/3l0/intake.jsonl`, the desk-feed DoE carrier, `ops/moneyball/dispatch-intake.jsonl`).

Conventions are declared in `DESIGN.json` — including the baseline/candidate SHA convention and the honesty rule that routed production dispatches are observational population, never retro-dressed as designed arms. Cohort = routing version (`routed-dispatch-2026-11` = swarm-routing/v2); a routing/design change starts a new cohort.
