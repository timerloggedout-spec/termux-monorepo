-- delphi_ledger: append-only mirror of the Delphi continuous ledgers
-- (design: docs/ops/DELPHI-LEDGER-STORE.md). The issue comments stay the
-- system of record; this store is the queryable mirror. Idempotent:
-- one row per source comment, keyed sha256(ledger_id|comment_id).
-- Rows are never updated or deleted (trigger below). Safe to re-run.
-- Credentials (repo secrets, names only — same Neon project route as
-- lane_events): LANE_EVENTS_DATABASE_URL or NEON_API_KEY.
CREATE TABLE IF NOT EXISTS delphi_ledger_events (
  event_key   text PRIMARY KEY,                -- sha256(ledger_id|comment_id)
  ledger_id   text NOT NULL,                   -- outcomes | weights | generation | ...
  issue_number integer NOT NULL,
  comment_id  bigint NOT NULL,
  marker      text,                            -- '<!-- delphi-outcomes v1 -->' etc; null = signed [MUSEai]@ append
  payload     jsonb,                           -- snapshot json verbatim when the comment carries one
  body        text NOT NULL,
  occurred_at timestamptz NOT NULL,            -- comment created_at
  recorded_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (ledger_id, comment_id)
);

CREATE INDEX IF NOT EXISTS delphi_ledger_events_ledger_time_ix
  ON delphi_ledger_events (ledger_id, occurred_at DESC);

-- Living records (e.g. #2028) are edited in place at the source, so the
-- mirror versions them: one row per distinct body hash.
CREATE TABLE IF NOT EXISTS delphi_living_records (
  version_key  text PRIMARY KEY,               -- sha256(issue_number|body_sha256)
  record_id    text NOT NULL,
  issue_number integer NOT NULL,
  body_sha256  text NOT NULL,
  snapshot_at  timestamptz,                    -- parsed from the body when present
  body         text NOT NULL,
  recorded_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (issue_number, body_sha256)
);

CREATE OR REPLACE FUNCTION delphi_ledger_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'delphi ledger mirror is append-only (% blocked)', TG_OP;
END $$;

DROP TRIGGER IF EXISTS delphi_ledger_events_no_mutation ON delphi_ledger_events;
CREATE TRIGGER delphi_ledger_events_no_mutation
  BEFORE UPDATE OR DELETE ON delphi_ledger_events
  FOR EACH ROW EXECUTE FUNCTION delphi_ledger_append_only();

DROP TRIGGER IF EXISTS delphi_living_records_no_mutation ON delphi_living_records;
CREATE TRIGGER delphi_living_records_no_mutation
  BEFORE UPDATE OR DELETE ON delphi_living_records
  FOR EACH ROW EXECUTE FUNCTION delphi_ledger_append_only();

-- Current state per snapshot ledger: the newest payload-bearing event —
-- the same rule as gate.py latest_json, expressed as a view.
CREATE OR REPLACE VIEW delphi_ledger_current AS
SELECT DISTINCT ON (ledger_id)
  ledger_id, issue_number, comment_id, occurred_at, payload
FROM delphi_ledger_events
WHERE payload IS NOT NULL
ORDER BY ledger_id, occurred_at DESC, comment_id DESC;
