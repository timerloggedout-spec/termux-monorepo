-- lane_events: append-only ledger for the agentic planning lanes
-- (help-wanted / Tribute, SHE, and later cadence, MoneyBall, lane matrix).
-- Idempotent: one row per (run_id, run_attempt, subject, event_type).
-- Rows are never updated or deleted (trigger below). Safe to re-run.
CREATE TABLE IF NOT EXISTS lane_events (
  event_key    text PRIMARY KEY,               -- sha256(lane|workflow|run_id|run_attempt|subject|event_type)
  lane         text NOT NULL,                  -- help-wanted | she | ...
  workflow     text NOT NULL,                  -- workflow name that produced the event
  event_type   text NOT NULL,                  -- run_completed | pr_state:open | ...
  repo         text NOT NULL,                  -- OWNER/REPO the run belongs to
  run_id       bigint,
  run_attempt  integer,
  subject_url  text,                           -- issue / PR URL when the event is about one
  phase_id     text,                           -- dependency phase id (DPH-*) when relevant
  conclusion   text,
  head_sha     text,
  payload      jsonb NOT NULL DEFAULT '{}'::jsonb,
  occurred_at  timestamptz NOT NULL,
  recorded_at  timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT lane_events_has_subject CHECK (run_id IS NOT NULL OR subject_url IS NOT NULL OR phase_id IS NOT NULL)
);

CREATE UNIQUE INDEX IF NOT EXISTS lane_events_run_subject_uq
  ON lane_events (run_id, run_attempt, (coalesce(subject_url, phase_id, '')), event_type);
CREATE INDEX IF NOT EXISTS lane_events_lane_time_ix ON lane_events (lane, occurred_at DESC);
CREATE INDEX IF NOT EXISTS lane_events_subject_ix ON lane_events (subject_url) WHERE subject_url IS NOT NULL;

CREATE OR REPLACE FUNCTION lane_events_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'lane_events is append-only (% blocked)', TG_OP;
END $$;

DROP TRIGGER IF EXISTS lane_events_no_mutation ON lane_events;
CREATE TRIGGER lane_events_no_mutation
  BEFORE UPDATE OR DELETE ON lane_events
  FOR EACH ROW EXECUTE FUNCTION lane_events_append_only();
