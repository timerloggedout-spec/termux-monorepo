-- Cloudflare D1 schema for the Admin Interaction Graph live projection.
-- Event IDs are deterministic and PRIMARY KEY provides delivery deduplication.
CREATE TABLE IF NOT EXISTS runtime_events (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  event TEXT NOT NULL,
  status TEXT NOT NULL,
  workflow TEXT NOT NULL,
  job TEXT,
  step TEXT,
  repo TEXT NOT NULL,
  run_id INTEGER NOT NULL,
  run_attempt INTEGER NOT NULL,
  job_id INTEGER,
  head_sha TEXT,
  url TEXT,
  occurred_at TEXT NOT NULL,
  received_at TEXT NOT NULL,
  payload TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS runtime_events_time_idx
  ON runtime_events(occurred_at);
CREATE INDEX IF NOT EXISTS runtime_events_run_idx
  ON runtime_events(run_id, run_attempt);
CREATE INDEX IF NOT EXISTS runtime_events_job_idx
  ON runtime_events(job_id) WHERE job_id IS NOT NULL;
