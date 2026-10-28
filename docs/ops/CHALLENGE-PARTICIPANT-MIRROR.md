# Challenge participant mirror — CHALLENGE-PARTICIPANT-MIRROR

[MUSEai]@{role:{database-specialist}} — 2026-10-28, coordination ask
from the challenge-entries lane (owner order via ChallengeLane
Manager). Same pattern as the Delphi ledger mirror (PR #2035/#2048).

- **Source of truth:** `ops/challenge/coordinator.json` —
  `events[].participants[]`. The mirror tolerates the field being
  absent (the challenge lane's schema extension lands separately);
  absent = empty list, never an error.
- **Store:** Neon, lane-events route (secrets by name only:
  `LANE_EVENTS_DATABASE_URL` / `NEON_API_KEY`). Schema:
  `ops/challenge-participants/schema.sql` —
  `participant_syncs` (one row per sync, `sync_key =
  sha256(source_ref)`, source_ref = git SHA of the source file;
  `counts` = per-event participant counts incl. zeros),
  `participant_events` (append-only trigger;
  `event_key = sha256('challenge-participants'|event_id|participant_key)`;
  participant_key = first of id/handle/username/name/url in the
  record, else sha256 of its canonical JSON; payload verbatim),
  `participants_current` view = rows of the newest sync batch, so the
  current view mirrors the source exactly (removals included) while
  history stays append-only.
- **Writer:** `scripts/challenge/participant_event.py` (lane_event
  pattern: never fails its caller, no-op without creds, guest in the
  lane-events project; commands sync/schema/count; --dry-run prints
  the batch). Inserts are psql-variable `ON CONFLICT DO NOTHING`
  (`insert-sync.sql` / `insert-participant.sql`) — re-syncing the same
  source SHA inserts zero new rows.
- **Trigger:** `.github/workflows/challenge-participant-mirror.yml` —
  push on `ops/challenge/coordinator.json` + `workflow_dispatch`.
  No VM execution (owner VM rule): all continuous work is this
  workflow.
- **Expected state at landing:** galleries open D4 Oct 30 / D2 Nov 5 /
  D5 Nov 17; D1/D3 checked, no public gallery yet — first-mirror
  counts are 0 for every event until then, and that zero is the
  verified reading, not a gap.
- Out of scope this round: events/projects core fields (same mirror
  later, per the ask).

## Amendment — engagement is autonomous (owner correction, 2026-10-28)

Engagement has NO draft/approval gate anywhere in this design.
`engagement.touchpoints[]` on a participant record are **executed**
touchpoint logs — `{surface, at, content_ref}` entries for
touchpoints that happened — and are first-class mirror data: they
ride the payload verbatim, the writer extracts them
(`touchpoints_of`, counted in --dry-run), and the schema exposes them
as the `participant_touchpoints` view over the current batch. No
HITL/approval/draft state exists in the schema or the writer, and
none may be added without a new owner order.
- **Provisioning status (verified firsthand 2026-10-28):** the repo
  Actions secrets list (53 names, checked by name) contains NEITHER
  `LANE_EVENTS_DATABASE_URL` NOR `NEON_API_KEY` — the workflows
  reference the names, but the secrets are not provisioned, so every
  lane-events-route writer (lane_events, delphi_ledger, this mirror)
  currently no-ops in Actions. First dispatch run 40760335059 =
  success via the no-op path. DB-side counts are NOT ESTABLISHED until
  the owner provisions one of the two names (owner item of record;
  secret values are provisioning facts, never invented). Source-side
  first counts (dry-run vs master): D0–D5 = 0 each.
