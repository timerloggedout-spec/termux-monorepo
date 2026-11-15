-- Unified Integration Intelligence ingestion tables.
-- This migration extends the existing Neon "lane-events" project/database.
-- It creates no new database, scheduler, source registry, or merge authority.
-- Apply with: psql "$LANE_EVENTS_MIGRATION_DATABASE_URL" -v ON_ERROR_STOP=1 -f integration-events.sql

CREATE TABLE IF NOT EXISTS integration_ingest_batches (
  batch_id             uuid PRIMARY KEY,
  integration_id       text NOT NULL,
  adapter_version      text NOT NULL,
  record_type          text NOT NULL,
  status               text NOT NULL,
  records_received     integer NOT NULL,
  records_inserted     integer NOT NULL,
  records_duplicates   integer NOT NULL,
  records_rejected     integer NOT NULL DEFAULT 0,
  payload_bytes        bigint NOT NULL,
  payload_sha256       text NOT NULL,
  cursor_before        text,
  cursor_after         text,
  started_at           timestamptz NOT NULL,
  completed_at         timestamptz NOT NULL,
  error_class          text,
  recorded_at          timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT integration_ingest_batches_integration_id_ck
    CHECK (integration_id ~ '^[a-z0-9][a-z0-9-]{1,63}$'),
  CONSTRAINT integration_ingest_batches_record_type_ck
    CHECK (record_type IN ('event','measurement')),
  CONSTRAINT integration_ingest_batches_status_ck
    CHECK (status IN ('emitted','partial','skipped','deferred','failed')),
  CONSTRAINT integration_ingest_batches_counts_ck
    CHECK (
      records_received >= 0 AND records_inserted >= 0 AND
      records_duplicates >= 0 AND records_rejected >= 0 AND
      records_inserted + records_duplicates + records_rejected <= records_received
    ),
  CONSTRAINT integration_ingest_batches_emitted_counts_ck
    CHECK (status <> 'emitted' OR
      records_received = records_inserted + records_duplicates + records_rejected),
  CONSTRAINT integration_ingest_batches_bytes_ck CHECK (payload_bytes >= 0),
  CONSTRAINT integration_ingest_batches_hash_ck
    CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
  CONSTRAINT integration_ingest_batches_cursor_before_ck
    CHECK (cursor_before IS NULL OR length(cursor_before) BETWEEN 1 AND 512),
  CONSTRAINT integration_ingest_batches_cursor_after_ck
    CHECK (cursor_after IS NULL OR length(cursor_after) BETWEEN 1 AND 512)
);

CREATE INDEX IF NOT EXISTS integration_ingest_batches_integration_time_ix
  ON integration_ingest_batches (integration_id, completed_at DESC);

CREATE INDEX IF NOT EXISTS integration_ingest_batches_cursor_latest_ix
  ON integration_ingest_batches (integration_id, record_type, completed_at DESC, recorded_at DESC)
  WHERE status = 'emitted' AND cursor_after IS NOT NULL;

CREATE OR REPLACE VIEW integration_latest_cursors AS
SELECT DISTINCT ON (integration_id, record_type)
  integration_id, record_type, cursor_before, cursor_after, batch_id, completed_at
FROM integration_ingest_batches
WHERE status = 'emitted' AND cursor_after IS NOT NULL
ORDER BY integration_id, record_type, completed_at DESC, recorded_at DESC, batch_id DESC;

CREATE TABLE IF NOT EXISTS integration_events (
  event_id              text PRIMARY KEY,
  integration_id        text NOT NULL,
  event_type            text NOT NULL,
  repository            text,
  commit_sha            text,
  pull_request          bigint,
  workflow_run_id       bigint,
  provider_request_id   text,
  execution_status      text NOT NULL,
  started_at            timestamptz,
  completed_at          timestamptz,
  duration_ms           bigint,
  outcome_state         text NOT NULL,
  outcome_summary       text NOT NULL DEFAULT '',
  confidence            text,
  evidence              jsonb NOT NULL,
  provenance            jsonb NOT NULL,
  privacy               jsonb NOT NULL DEFAULT '{}'::jsonb,
  idempotency_key       text NOT NULL,
  event_at              timestamptz,
  observed_at           timestamptz NOT NULL,
  recorded_at           timestamptz NOT NULL DEFAULT now(),
  batch_id              uuid REFERENCES integration_ingest_batches(batch_id)
                        ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  envelope              jsonb NOT NULL,
  CONSTRAINT integration_events_integration_id_ck
    CHECK (integration_id ~ '^[a-z0-9][a-z0-9-]{1,63}$'),
  CONSTRAINT integration_events_event_integration_uk UNIQUE (event_id, integration_id),
  CONSTRAINT integration_events_event_type_ck CHECK (length(event_type) > 0),
  CONSTRAINT integration_events_status_ck
    CHECK (execution_status IN ('queued','running','succeeded','failed','cancelled','blocked','unknown')),
  CONSTRAINT integration_events_outcome_ck
    CHECK (outcome_state IN ('observed','executed','validated','promoted','failed','unknown')),
  CONSTRAINT integration_events_duration_ck
    CHECK (duration_ms IS NULL OR duration_ms >= 0),
  CONSTRAINT integration_events_commit_ck
    CHECK (commit_sha IS NULL OR commit_sha ~ '^[0-9a-f]{7,64}$')
);

-- Provider idempotency keys are scoped to their integration namespace.
-- Drop the original single-column constraints when upgrading an already-created table.
ALTER TABLE integration_events
  DROP CONSTRAINT IF EXISTS integration_events_idempotency_key_key;
ALTER TABLE integration_events
  DROP CONSTRAINT IF EXISTS integration_events_integration_idempotency_uk;
ALTER TABLE integration_events
  ADD CONSTRAINT integration_events_integration_idempotency_uk
  UNIQUE (integration_id, idempotency_key);

CREATE INDEX IF NOT EXISTS integration_events_integration_event_time_ix
  ON integration_events (integration_id, event_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS integration_events_integration_observed_ix
  ON integration_events (integration_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS integration_events_workflow_run_ix
  ON integration_events (repository, workflow_run_id) WHERE workflow_run_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS integration_events_provider_request_ix
  ON integration_events (provider_request_id) WHERE provider_request_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS integration_events_event_time_brin
  ON integration_events USING brin (event_at);

CREATE TABLE IF NOT EXISTS integration_measurements (
  measurement_id       text PRIMARY KEY,
  event_id             text NOT NULL,
  integration_id       text NOT NULL,
  metric_name          text NOT NULL,
  metric_type          text NOT NULL,
  value                double precision,
  unit                 text,
  temporality          text NOT NULL,
  measurement_status   text NOT NULL,
  event_at             timestamptz,
  observed_at          timestamptz NOT NULL,
  dimensions           jsonb NOT NULL DEFAULT '{}'::jsonb,
  provenance           jsonb NOT NULL,
  evidence_ref         text,
  confidence           text,
  idempotency_key      text NOT NULL,
  supersedes           text,
  recorded_at          timestamptz NOT NULL DEFAULT now(),
  batch_id             uuid REFERENCES integration_ingest_batches(batch_id)
                       ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  record               jsonb NOT NULL,
  CONSTRAINT integration_measurements_integration_id_ck
    CHECK (integration_id ~ '^[a-z0-9][a-z0-9-]{1,63}$'),
  CONSTRAINT integration_measurements_metric_name_ck
    CHECK (metric_name ~ '^[a-z][a-z0-9_.-]{0,127}$'),
  CONSTRAINT integration_measurements_event_integration_fk
    FOREIGN KEY (event_id, integration_id)
    REFERENCES integration_events(event_id, integration_id) ON DELETE RESTRICT,
  CONSTRAINT integration_measurements_metric_type_ck
    CHECK (metric_type IN ('counter','gauge','rate','duration','percentage')),
  CONSTRAINT integration_measurements_temporality_ck
    CHECK (temporality IN ('instant','delta','cumulative')),
  CONSTRAINT integration_measurements_status_ck
    CHECK (measurement_status IN ('measured','estimated','activity_only','not_established')),
  CONSTRAINT integration_measurements_value_status_ck
    CHECK (
      (measurement_status IN ('measured','estimated') AND value IS NOT NULL) OR
      (measurement_status IN ('activity_only','not_established') AND value IS NULL)
    ),
  CONSTRAINT integration_measurements_finite_value_ck
    CHECK (value IS NULL OR value NOT IN
      ('NaN'::double precision, 'Infinity'::double precision, '-Infinity'::double precision)),
  CONSTRAINT integration_measurements_dimensions_ck
    CHECK (jsonb_typeof(dimensions) = 'object')
);

ALTER TABLE integration_measurements
  DROP CONSTRAINT IF EXISTS integration_measurements_idempotency_key_key;
ALTER TABLE integration_measurements
  DROP CONSTRAINT IF EXISTS integration_measurements_integration_idempotency_uk;
ALTER TABLE integration_measurements
  ADD CONSTRAINT integration_measurements_integration_idempotency_uk
  UNIQUE (integration_id, idempotency_key);

CREATE INDEX IF NOT EXISTS integration_measurements_series_ix
  ON integration_measurements (integration_id, metric_name, observed_at DESC);
CREATE INDEX IF NOT EXISTS integration_measurements_event_ix
  ON integration_measurements (event_id);
CREATE INDEX IF NOT EXISTS integration_measurements_dimensions_gin
  ON integration_measurements USING gin (dimensions jsonb_path_ops);
CREATE INDEX IF NOT EXISTS integration_measurements_observed_brin
  ON integration_measurements USING brin (observed_at);
CREATE INDEX IF NOT EXISTS integration_measurements_event_time_brin
  ON integration_measurements USING brin (event_at);

CREATE OR REPLACE FUNCTION integration_records_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION '% is append-only (% blocked)', TG_TABLE_NAME, TG_OP;
END $$;

DROP TRIGGER IF EXISTS integration_events_no_mutation ON integration_events;
CREATE TRIGGER integration_events_no_mutation
  BEFORE UPDATE OR DELETE ON integration_events
  FOR EACH ROW EXECUTE FUNCTION integration_records_append_only();
DROP TRIGGER IF EXISTS integration_measurements_no_mutation ON integration_measurements;
CREATE TRIGGER integration_measurements_no_mutation
  BEFORE UPDATE OR DELETE ON integration_measurements
  FOR EACH ROW EXECUTE FUNCTION integration_records_append_only();
DROP TRIGGER IF EXISTS integration_ingest_batches_no_mutation ON integration_ingest_batches;
CREATE TRIGGER integration_ingest_batches_no_mutation
  BEFORE UPDATE OR DELETE ON integration_ingest_batches
  FOR EACH ROW EXECUTE FUNCTION integration_records_append_only();

DROP TRIGGER IF EXISTS integration_events_no_truncate ON integration_events;
CREATE TRIGGER integration_events_no_truncate
  BEFORE TRUNCATE ON integration_events
  FOR EACH STATEMENT EXECUTE FUNCTION integration_records_append_only();
DROP TRIGGER IF EXISTS integration_measurements_no_truncate ON integration_measurements;
CREATE TRIGGER integration_measurements_no_truncate
  BEFORE TRUNCATE ON integration_measurements
  FOR EACH STATEMENT EXECUTE FUNCTION integration_records_append_only();
DROP TRIGGER IF EXISTS integration_ingest_batches_no_truncate ON integration_ingest_batches;
CREATE TRIGGER integration_ingest_batches_no_truncate
  BEFORE TRUNCATE ON integration_ingest_batches
  FOR EACH STATEMENT EXECUTE FUNCTION integration_records_append_only();
