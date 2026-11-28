-- ops_queue: shared planning/ops task queue (Neon Postgres).
-- Idempotent; safe to run repeatedly. The collector also runs this at start-up.
CREATE TABLE IF NOT EXISTS ops_queue (
  id          TEXT PRIMARY KEY,
  source      TEXT NOT NULL,                 -- who enqueued it: hark, gh-actions, device, ...
  repo        TEXT,                          -- owner/name, optional
  kind        TEXT NOT NULL,                 -- task type: plan, deploy, triage, extract, ...
  payload     JSONB NOT NULL DEFAULT '{}'::jsonb,
  status      TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','claimed','done','failed','stale')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  claimed_by  TEXT,
  claimed_at  TIMESTAMPTZ,
  done_at     TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ops_queue_status_created_idx ON ops_queue (status, created_at);
CREATE INDEX IF NOT EXISTS ops_queue_repo_idx ON ops_queue (repo);

-- Optional, for the Neon Data API (PostgREST-style HTTPS access, JWT roles).
-- Run once after enabling the Data API on the branch. Neon's Data API maps JWTs to the
-- `authenticated` role; grant it queue access. Tighten with RLS if multi-tenant.
-- GRANT SELECT, INSERT, UPDATE ON ops_queue TO authenticated;
