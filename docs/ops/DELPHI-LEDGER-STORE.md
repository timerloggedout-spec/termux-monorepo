# Delphi continuous ledgers as a database problem — DELPHI-LEDGER-STORE

[MUSEai]@{role:{database-specialist}} — design + first slice, 2026-10-28.
Mission (owner, via Delphi lane): continuous-ledger **web availability**
as a database problem — not a single-ledger fix.

## Problem

Delphi's continuous ledgers live as append-only issue comments —
outcomes #1487, weights #1489 — plus living records whose issue body is
edited in place (#2028 Temporal self-host status). Current state is
buried per-comment: each snapshot comment carries a full JSON state,
the newest one wins, and nothing renders on the web or answers a query.

## Semantics of record (from `scripts/delphi/gate.py`, firsthand)

| Rule | Where | Value |
|---|---|---|
| Snapshot marker | comment prefix | `<!-- delphi-outcomes v1 -->`, `<!-- delphi-weights v1 -->` |
| Current state | `latest_json()` | newest comment starting with the marker, its ```json block verbatim |
| Signal idempotency | `signal_digest()` / `dedupe_signals()` | `sha256(key\|outcome)[:16]`, per surface, newest 2000 kept; same key + changed outcome digests differently and is recorded as a new signal |
| Outcomes EWMA | `apply_outcomes()` | alpha 0.2 (`ops/delphi/panel.json` `flywheel.ewma_alpha`), **damped**: one step per batch at the batch mean (#1533), per surface and per repo |
| Weights flywheel | `feedback_graded()` | `gate_pass_rate` EWMA with step `alpha*|weight|`; Elo `+= k * reward`, k = 16 (`flywheel.elo_k`); hits/misses tallied |
| Corrections | convention on #1487 | append-only: a correction is a new signed comment, never an edit (the 2026-10-28 recheck migration on #1487 is the disclosed exception) |
| Living records | #2028 body | edited in place by the keepalive job; the body carries its own `Snapshot <ts>` stamp |

Registry of ledgers: `ops/delphi/ledgers.json` (`delphi-ledgers/v1`).

## Recon — candidate stores

| Candidate | Queryability | Web render path | Append-only integrity | Cost / card | Writers → readers | Verdict |
|---|---|---|---|---|---|---|
| **Neon Postgres** (fleet precedent: `ops/lane-events/`) | full SQL, jsonb | none direct (static dashboard cannot hold creds) — needs an export | trigger-enforced (proven in `lane_events`) | free tier, secrets already provisioned by name (`LANE_EVENTS_DATABASE_URL` / `NEON_API_KEY`) | gate workflows via psql writer pattern → export job | **ADOPT as queryable mirror (slice 2 writer)** |
| Supabase Postgres | full SQL | same export problem | buildable | free; key provisioned by name, but no ledger precedent + Jules route contested | new surface for no gain over Neon | reject (duplicate of Neon) |
| Pinecone (provisioned 2026-10-28) | vector similarity only — no folds, no EWMA, no exact current-state query | none | none (upsert overwrites) | Starter free | HindSight recall only | reject — wrong shape entirely |
| **Repo-native feed** (`delphi-rfp-feed` precedent, PR #1949/#1952) | jq / DuckDB `read_json` over one file; no SQL server | **proven**: `apps/help-wanted-dashboard/data/*.json` → static Pages/Vercel render | git history + collector honesty rules; source comments stay append-only | zero, no card | collector workflow (dispatch + weekly + `workflow_run` on delphi-gate) → Web Design pages | **ADOPT as web-availability layer (this slice)** |
| SQLite / DuckDB file in repo | full SQL locally | none (binary, no static render) | file is mutable; git-diff hostile, multi-writer unsafe | zero | — | reject as store; DuckDB-over-JSON remains the ad-hoc query route |

## Design — two layers, one source of truth

1. **System of record (unchanged):** the issue comments + living
   bodies. The gate keeps writing exactly as today; no writer changes,
   no semantics move.
2. **Web availability (this slice):** `scripts/delphi/ledger_fetch.py`
   → cache; `scripts/delphi/ledger_feed.py` (pure transform, stdlib)
   → `apps/help-wanted-dashboard/data/delphi-ledger-feed.json`
   (`delphi-ledger-feed/v1`): per ledger an `events[]` stream
   (`event_key = sha256(ledger_id|comment_id)`, payload verbatim when
   carried, signed `[MUSEai]@` appends included, third-party noise
   counted and excluded) + `current{}` folded by the gate's own
   `latest_json` rule; per living record the current body +
   `version_key = sha256(body)` + parsed snapshot stamp. The collector
   **refuses a partial cache**, recomputes nothing, and is idempotent
   (same cache → same feed; a re-delivered comment yields one event).
   Refresh: `.github/workflows/delphi-ledger-feed-collect.yml`
   (dispatch + weekly + on delphi-gate completion; refresh PRs only).
3. **Queryable mirror (schema landed, writer = slice 2):**
   `ops/delphi-ledger/schema.sql` — `delphi_ledger_events` +
   `delphi_living_records` on the existing lane-events Neon route,
   same `event_key`, append-only trigger, and a
   `delphi_ledger_current` view expressing `latest_json` in SQL.
   Slice 2 = a `ledger_event.py` writer in the `scripts/ops/lane_event.py`
   pattern (never fails its caller, `ON CONFLICT DO NOTHING`) invoked
   from the collect workflow. Named, not built here, so the feed ships
   first and the mirror cannot diverge from it (same keys, same fold).

Query examples once the mirror lands: current weights =
`SELECT payload FROM delphi_ledger_current WHERE ledger_id='weights'`;
outcome history for one surface = payload path queries over
`delphi_ledger_events WHERE ledger_id='outcomes'` ordered by
`occurred_at`. Until then both are one `jq` over the feed file.

## Semantics amendments (Delphi lane review, 2026-10-28)

Delivered after slice 1 landed; diffed against the build and folded in
here + registry + schema (amendment PR follows this doc):

- **Weights derivation (was missing):** `w_i = base_i × (0.5 +
  gate_pass_rate_i) × (elo_i / 1500)` (DELPHI-WEIGHTING.md:43). Weights
  are DERIVED from events — the mirror therefore stores events + the
  derivation (`delphi_weights_current` view applies it to the current
  payload); the feed carries `derivation` on the weights ledger and
  payloads verbatim. Snapshots alone are never the record.
- **Invariants as contract** (registry `invariants`, carried into the
  feed verbatim): append-only with corrections as new superseding
  events; idempotency keys on every ingest; source classes
  HUMAN_COLLABORATOR / MODEL_PROVIDER / LOCAL_BASELINE never collapsed
  (DRIVER_SYNTHESIS is not a ballot); honest negatives
  (`none_validated_yet`, `none_yet`) are data, never nulls; ledger
  resolution by exact title (PR #1833), numbers pinned in the registry.
- **Batch cap:** tribute ingestion ≤ 200 records/batch (PR #1824),
  added to the outcomes semantics.
- **Per-RFP gate ledgers** are the `delphi-rfp-feed` domain (status =
  latest award comment; `delphi:converged` is a rounds property) —
  already web-available; this store covers the continuous ledgers and
  cross-references that feed rather than duplicating it.
- **Living-record discrepancy, stated:** the Delphi lane describes
  living records as periodic snapshot comments; #2028 firsthand is the
  opposite — its comments are third-party vendor posts and the record
  itself is the issue BODY, edited in place by the keepalive job with
  a `Snapshot` stamp in the body. The registry therefore supports both
  kinds; #2028 is registered `living-body`. If a snapshot-comment
  living record is named, it registers as `snapshot-comments` with no
  collector change.

## Exact-semantics addendum (Delphi lane, 2026-10-28, second pass)

Verified against gate.py/panel.json on master; folded into registry,
collector and feed (amendment 2):

- **Envelope:** every machine ledger comment = HTML marker + prose +
  fenced ```json carrying the FULL derived state (snapshot-carried,
  never deltas). Current state = newest marked comment's JSON verbatim
  — explicitly **not** a fold/replay; cold start = `panel.json`. A
  once-consumed graded step stays consumed.
- **Event classes (new in the feed):** each event now carries
  `class` — `machine-state` (marked envelope) vs `record` (unmarked
  signed lane/owner prose on #1487: comparisons, axes, corrections).
  Only `machine-state` payloads can be a ledger's `current`.
- **Weights update, exact:** hit = (role's final vote ≥ `shadow_min`
  15.0) == (outcome == `confirmed`); `gate_pass_rate ← round(0.8·gpr +
  0.2·(1|0), 4)`; `elo ← round(elo ± 16, 1)`; hits/misses++;
  aggregation `effective = Σw·s / Σw`. Roles + bases + seeds are in the
  registry's weights `derivation` block.
- **Board ledger (was missing — found):** #1474 "Delphi results board",
  marker `<!-- delphi-board v1 -->`, carried in the issue BODY,
  regenerated by the gate (generated-at stamp in body). It is a
  DERIVED render — ledger of record = newest `delphi-ledger v1`
  comment per RFP — registered as `living-body` so the feed carries it
  without ever treating it as a source.
- **Living-record marker assigned:** per the Delphi lane's
  recommendation, `<!-- delphi-living v1 -->` is assigned for future
  snapshot comments on living-record issues (recorded on the #2028
  registry entry; its writer adopts it, the body pattern is unchanged
  until then). This resolves the earlier discrepancy: body-carried
  records (#2028, board #1474) and comment-carried ledgers are both
  first-class kinds.
- **Writers/readers of record:** writers = delphi-gate (issue events,
  `repository_dispatch` delphi-tick, hourly schedule, dispatch;
  `defer_api` at shared-token remaining ≲126), delphi-tribute-ingest
  (dispatch-only, gate executes), lanes+owner (unmarked records).
  Readers = the gate (read-modify-write on newest marked JSON),
  `rfp_flood_feed.py`, `bayesian_routing.py` (beliefs over #1487),
  `oracle_panel_feed.py`, this collector, humans.

## Render handoff

Web Design lane (f2acba6f): render `delphi-ledger-feed.json` like the
RFP feed — `current.payload` verbatim per ledger (no re-folding, no
recomputed EWMA/Elo), events stream below it, `excluded_noise` named,
living records by `version_key` + `snapshot_at`. Page itself is theirs;
this slice is the store + feed contract.
