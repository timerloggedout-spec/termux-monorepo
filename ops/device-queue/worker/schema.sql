CREATE TABLE tasks (
  id            TEXT PRIMARY KEY,
  dedupe_key    TEXT UNIQUE,
  kind          TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'engineer',
  payload       TEXT NOT NULL DEFAULT '{}',
  state         TEXT NOT NULL DEFAULT 'queued'
                CHECK (state IN ('queued','claimed','done','failed','expired','dead')),
  producer      TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  expires_at    TEXT NOT NULL,
  claimed_by    TEXT,
  claimed_at    TEXT,
  lease_until   TEXT,
  attempts      INTEGER NOT NULL DEFAULT 0,
  max_attempts  INTEGER NOT NULL DEFAULT 3,
  receipt       TEXT,
  finished_at   TEXT
);
CREATE INDEX idx_tasks_claim ON tasks (state, expires_at, created_at);
CREATE TABLE events (
  task_id TEXT NOT NULL, at TEXT NOT NULL, actor TEXT NOT NULL,
  from_state TEXT, to_state TEXT NOT NULL, note TEXT
);
CREATE INDEX idx_events_task ON events (task_id, at);
