-- ops_queue: shared planning/work queue for Hark projects, GitHub Actions and devices.
-- Idempotent: safe to run on every start (queue-collector runs it automatically).
CREATE TABLE IF NOT EXISTS ops_queue (
  id          TEXT PRIMARY KEY,                 -- client- or server-generated UUID (idempotency key)
  source      TEXT NOT NULL,                    -- who enqueued it: hark:<project>, gha:<workflow>, device:<name>
  repo        TEXT,                             -- owner/repo the task concerns, if any
  kind        TEXT NOT NULL,                    -- task type: deploy, triage, review, sync, note ...
  payload     JSONB NOT NULL DEFAULT '{}'::jsonb,
  status      TEXT NOT NULL DEFAULT 'queued'
              CHECK (status IN ('queued','claimed','done','failed','stale')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  claimed_by  TEXT,
  claimed_at  TIMESTAMPTZ,
  done_at     TIMESTAMPTZ
);
ALTER TABLE ops_queue ADD COLUMN IF NOT EXISTS claimed_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS ops_queue_status_created_idx ON ops_queue (status, created_at);
CREATE INDEX IF NOT EXISTS ops_queue_created_idx ON ops_queue (created_at DESC);

-- Neon Data API (PostgREST-compatible) access. Run once after enabling the Data API.
-- Requests carry a JWT; the `authenticated` role is what Neon maps signed-in callers to.
-- GRANT USAGE ON SCHEMA public TO authenticated;
-- GRANT SELECT, INSERT, UPDATE ON ops_queue TO authenticated;
-- ALTER TABLE ops_queue ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY ops_queue_rw ON ops_queue FOR ALL TO authenticated USING (true) WITH CHECK (true);
