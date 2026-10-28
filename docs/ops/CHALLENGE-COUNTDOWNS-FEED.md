# Challenge Countdowns Feed — contract

Schema: `challenge-countdowns-feed/v1.1`
File: `apps/help-wanted-dashboard/data/challenge-countdowns-feed.json`
Collector: `scripts/dashboards/challenge_countdowns_feed.py`
Refresh: `.github/workflows/challenge-countdowns-feed-collect.yml`
(refresh-by-PR; push-triggered on the source log)
Consumer: `apps/help-wanted-dashboard/countdowns.html`
Requirement: issue #1880 (dashboard surface, requirement 3).

## Source of truth

Deadline instants live ONLY in `docs/ops/CHALLENGE-ENTRIES-LOG.md`
(§4 `countdown-data` lines, owned by the challenge-entries lane and
parsed by `scripts/challenge_entries/countdowns.py`). The collector
re-derives this feed from that log on every run; nothing is copied
forward from a previous feed.

## Shape

- `schema` — `challenge-countdowns-feed/v1.1`.
- `generated_at` — UTC collection instant.
- `source` — the log path the instants were derived from.
- `prizes_source` — `ops/challenge/coordinator.json`, the SSOT the
  per-entry prizes were wired from.
- `entries[]` — one per log entry, ordered by id:
  - `id` — the log's entry id (`D0`…).
  - `title` — display title derived from the entry's §4 header
    (status segments stripped by the collector).
  - `status` — `COMPLETED` / `CLOSED` when the header records it,
    else `ACTIVE`.
  - `opens` / `closes` — ISO-8601 instants with offset, verbatim
    from the log's `countdown-data` line; `null` when the entry
    records no such instant (`-` in the log).
  - `prizes` — REQUIRED (owner rule 2026-10-28): `{status, pool,
    tiers[{place, award, source_url}]}` wired verbatim from
    `ops/challenge/coordinator.json`. `status` is `ESTABLISHED`
    (tiers published on the official page) or `NOT_ESTABLISHED`.

## Honesty rules

1. **Instants only.** The feed NEVER carries a computed state or a
   remaining-seconds value. The challenge lane's emitter computes
   those for the log surface; for the dashboard they would go stale
   the second they are written. The page derives state and
   time-remaining from the instants, client-side, on every tick.
2. **Elapsed is a state, not an absence.** A passed deadline flips
   the rendered state (Overdue); the entry does not disappear.
   Completed/closed entries stay listed and render statically.
3. **Absent stays absent.** A `null` instant renders as
   "not recorded" — never a guessed date.
4. Read-only projection: no credentials, no browser-side mutation;
   interaction is navigation only (dashboard contract).
5. **Required fields never blank.** Prizes (with dates, status, and
   gates) are required information on the named context surfaces —
   the manager brief and the HITL web pages. An unpublished prize
   set renders as `NOT_ESTABLISHED`; the field is never omitted,
   never empty.
