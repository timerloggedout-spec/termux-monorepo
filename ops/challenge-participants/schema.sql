-- challenge participants mirror: append-only mirror of the participant
-- lists in ops/challenge/coordinator.json (the repo JSON is the source
-- of truth; design: docs/ops/CHALLENGE-PARTICIPANT-MIRROR.md).
-- Idempotent: event_key = sha256('challenge-participants'|<event>|<participant>).
-- Rows are never updated or deleted (trigger below). Safe to re-run.
-- Credentials (repo secrets, names only — same Neon route as
-- lane_events / delphi_ledger): LANE_EVENTS_DATABASE_URL or NEON_API_KEY.

-- One row per sync of the source file. sync_key keys the batch so the
-- current view can mirror the source exactly (incl. removals) while
-- history stays append-only.
CREATE TABLE IF NOT EXISTS participant_syncs (
  sync_key   text PRIMARY KEY,                 -- sha256(source_ref)
  source_ref text NOT NULL,                    -- git SHA of coordinator.json at sync
  counts     jsonb NOT NULL DEFAULT '{}'::jsonb, -- {event_id: participant count}
  synced_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS participant_events (
  event_key       text PRIMARY KEY,            -- sha256(challenge-participants|event_id|participant_key)
  sync_key        text NOT NULL,
  event_id        text NOT NULL,               -- coordinator event id (D0..D5)
  participant_key text NOT NULL,               -- first of id/handle/username/name/url, else sha256(record)
  payload         jsonb NOT NULL,              -- the participant record verbatim
  recorded_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (sync_key, event_id, participant_key)
);

CREATE INDEX IF NOT EXISTS participant_events_event_ix
  ON participant_events (event_id, participant_key);

CREATE OR REPLACE FUNCTION participant_mirror_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'participant mirror is append-only (% blocked)', TG_OP;
END $$;

DROP TRIGGER IF EXISTS participant_events_no_mutation ON participant_events;
CREATE TRIGGER participant_events_no_mutation
  BEFORE UPDATE OR DELETE ON participant_events
  FOR EACH ROW EXECUTE FUNCTION participant_mirror_append_only();

DROP TRIGGER IF EXISTS participant_syncs_no_mutation ON participant_syncs;
CREATE TRIGGER participant_syncs_no_mutation
  BEFORE UPDATE OR DELETE ON participant_syncs
  FOR EACH ROW EXECUTE FUNCTION participant_mirror_append_only();

-- Current participants = the newest sync batch, exactly mirroring the
-- source file at that sync (a participant removed from the source
-- leaves the current view; their history rows remain).
CREATE OR REPLACE VIEW participants_current AS
SELECT e.event_id, e.participant_key, e.payload, e.recorded_at
FROM participant_events e
JOIN (SELECT sync_key FROM participant_syncs ORDER BY synced_at DESC, sync_key DESC LIMIT 1) latest
  ON e.sync_key = latest.sync_key;

-- Engagement touchpoints are EXECUTED logs (owner correction,
-- 2026-10-28): engagement is autonomous — there is no draft/approval
-- state anywhere in this schema or its writer, by design. Each
-- participant record's engagement.touchpoints[] entries
-- ({surface, at, content_ref}) are first-class mirror data, exposed
-- here as rows over the current batch.
CREATE OR REPLACE VIEW participant_touchpoints AS
SELECT c.event_id, c.participant_key,
       t->>'surface' AS surface,
       t->>'at' AS at,
       t->>'content_ref' AS content_ref
FROM participants_current c,
     jsonb_array_elements(
       CASE WHEN jsonb_typeof(c.payload->'engagement'->'touchpoints') = 'array'
            THEN c.payload->'engagement'->'touchpoints' ELSE '[]'::jsonb END) AS t;
