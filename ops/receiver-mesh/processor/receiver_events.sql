-- Receiver Mesh — Neon ledger DDL. Design: docs/ops/RECEIVER-MESH.md
-- Target: lane-events project / a dedicated receiver-events database is a
-- provisioning decision for the DB lane; this DDL is not applied by the
-- prototype PR.
CREATE TABLE IF NOT EXISTS receiver_events (
  delivery_id TEXT PRIMARY KEY,
  source      TEXT NOT NULL,
  event       TEXT NOT NULL,
  received_at TIMESTAMPTZ NOT NULL,
  repo        TEXT,
  action      TEXT,
  actor       TEXT,
  object_id   TEXT,
  leg         TEXT NOT NULL DEFAULT 'cloudflare',
  processed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS receiver_events_source_event_idx
  ON receiver_events (source, event, received_at);
