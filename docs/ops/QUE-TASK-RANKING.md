# QUE task-plane prioritization (QUE #5283)

Origin: owner direct 2026-11-12 ("Get it done") after main's audit:
the QUE task/registry plane carried prioritization stamps but no
prioritization function — claim order was age alone, escalations rose
13 → 28 in a day while wall-bound filings sat unclaimed.

## Method of record: `que-task-rank/v1`

`scripts/que/task_ranking.py` — a pure function of feed-row content.
Pure means backfill-comparable (backfill doctrine): re-running the
module over archived rows reproduces a ranking exactly; a method
change bumps the method id and historical dispatches re-rank under
the new version alongside the old. DoE countersign of the method is
an external stamp, requested on #5283.

### Dispatch score (per row, published with its components)

- **tier** — priority_timebox tier index × 20 (BASE 0 … FINAL 4)
- **wall** — nearest wall/landing proximity from the entry's
  priority_timebox tier instants: inside 48h (or overdue) is the
  imminent class (≥1000) and outranks every non-imminent combination;
  beyond 48h the term decays to zero at 200h
- **age** — age_min capped at 30 days, scaled to 50
- **state** — escalated +40, queued +10, claimed 0 (neutral)

### Where rank publishes

- `dispatch-watchdog` feed rows (`ops/challenge/dispatch-state-feed.json`):
  every dispatch carries `score`, `rank`, `components`, `nearest_wall`;
  the feed carries a `ranking` block {method, claim_order, age_order,
  delta_vs_age_order}. Counts and measurement are unchanged — ranking
  is additive, never a recount.
- `que-feed-collect` folds score + rank into `dispatch_claims` and
  passes the ranking block through (re-deriving it under the same
  method for a pre-#5283 source feed, so no cycle publishes unranked).
- `opportunity_cycle` feed (`ops/que/feeds/opportunity-priority.json`):
  terminal/closed opportunities leave the active ranking (published
  under `terminal_opportunities` with state, never on top); every
  parseable coordinator date becomes a ranked sub-opportunity gate
  row (`gate_rows`) and contributes its nearest wall to the parent —
  AMD Academy's C3 course wall ranks even though the parent row's
  next gate is the Dec-1 league wall; a wall inside 48h outranks any
  past-gate score. The per-opportunity score of record is unchanged.

### Claim order: advisory until stamped

Claim/escalation consumers keep their current order until a
QDesk/Desk decision stamp on #5283 binds rank order (filing point 4).
Until then the feed publishes rank as advisory and reports the delta
vs age-order every cycle. A rank never auto-merges, auto-claims
value-class work, or overrides a QDesk/Desk stamp, and nothing here
touches admission thresholds or governor deferral rules (Cadence
custody).
