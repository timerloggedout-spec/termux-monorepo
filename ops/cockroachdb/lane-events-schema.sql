-- CockroachDB projection of the canonical lane_events evidence stream.
-- Keep event identity and row shape aligned with ops/lane-events/schema.sql.
-- Append-only access is enforced by the CockroachDB writer role grants.
CREATE TABLE IF NOT EXISTS lane_events (
  event_key    STRING PRIMARY KEY,
  lane         STRING NOT NULL,
  workflow     STRING NOT NULL,
  event_type   STRING NOT NULL,
  repo         STRING NOT NULL,
  run_id       INT8,
  run_attempt  INT4,
  subject_url  STRING,
  phase_id     STRING,
  conclusion   STRING,
  head_sha     STRING,
  payload      JSONB NOT NULL DEFAULT '{}'::JSONB,
  occurred_at  TIMESTAMPTZ NOT NULL,
  recorded_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT lane_events_has_subject CHECK (
    run_id IS NOT NULL OR subject_url IS NOT NULL OR phase_id IS NOT NULL
  )
);

CREATE UNIQUE INDEX IF NOT EXISTS lane_events_run_subject_uq
  ON lane_events (run_id, run_attempt, (coalesce(subject_url, phase_id, '')), event_type);
CREATE INDEX IF NOT EXISTS lane_events_lane_time_ix
  ON lane_events (lane, occurred_at DESC);
CREATE INDEX IF NOT EXISTS lane_events_subject_ix
  ON lane_events (subject_url) WHERE subject_url IS NOT NULL;
