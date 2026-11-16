# Search-Window Scheduling (Event Audit F4)

Owner standard via Event Audit audit-001 finding F4
(search-surface burst): the GitHub Search API is a narrow window
(30 requests/min, plus secondary limits) — search-heavy work is
**scheduled like a bucket, not discovered like a wall**.

## The three rules

1. **Batch.** A census never fans out one query per actor when a
   window pull answers it: one query over the window (repo +
   updated range), paginated, attribution joined locally.
   Per-key queries are the fallback — still paced, still
   checkpointed.
2. **Pace.** Token-bucket pacing under the cap (default 24/min —
   headroom is deliberate). On a 403/429 secondary response, back
   off to the reset the API names (`Retry-After` /
   `X-RateLimit-Reset`); never retry inside a closed window, and
   stop the census cleanly rather than burning the queue.
3. **Checkpoint.** Every completed unit (page or key) is
   watermarked to a JSON checkpoint as it lands. A limit cut
   resumes from the watermark — the 2026-11-02 census lost its
   tail (RepoStory + signature counts uncounted) because the
   queue lived only in the running process.

## Machinery

`scripts/quota_search_pacer.py` — `Pacer` (pacing + backoff),
`Checkpoint` (watermarks), `plan_window_pull` / `plan_per_key`
(batch planners), plus a `plan` CLI that prints the batched plan
and the paced schedule estimate before a single call is made.

## Adoption

- Registry lane censuses (the F4 event's owner lane) run on the
  pacer: plan first (window-pull preferred), checkpoint file per
  census, watermark committed with the census output so a resumed
  run is auditable.
- Any lane's enumeration work (GraphQL exempt — different bucket)
  follows the same three rules on the Search surface.

Evidence: event `census-2026-11-02T06:25:00Z-search-pat` in
`ops/quota/rate-limit-events.json`; audits in
`ops/quota/rate-limit-event-audits.json`.
