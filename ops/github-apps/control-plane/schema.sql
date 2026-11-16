-- AppID control plane — read-model schema over the lane-events Neon store.
-- [MUSEai]@{role:{appid-migration-plan}} · schema appid-control-plane/read-model-1
-- Owns ONLY appid_cp_* objects. lane_events is read (VIEW) — never written,
-- never altered (it is append-only by trigger). Safe to re-run (idempotent).
CREATE TABLE IF NOT EXISTS appid_cp_apps (
  app_id               bigint PRIMARY KEY,
  slug                 text NOT NULL,
  role                 text NOT NULL,
  installation_id      bigint,
  account              text,
  repository_selection text,
  custody_ref          text,
  sec03_pair_present   text,
  observed_at          timestamptz NOT NULL
);
CREATE TABLE IF NOT EXISTS appid_cp_permission_snapshots (
  id          bigserial PRIMARY KEY,
  app_id      bigint NOT NULL,
  declared    jsonb NOT NULL,
  observed    jsonb NOT NULL,
  drift       jsonb,
  observed_at timestamptz NOT NULL,
  probe_ref   text
);
CREATE TABLE IF NOT EXISTS appid_cp_migration_waves (
  wave_id   text PRIMARY KEY,
  state     text NOT NULL,  -- migrated | skipped | blocked | failed (program terminal vocabulary)
  items_ref text,
  note      text
);
CREATE TABLE IF NOT EXISTS appid_cp_replay_runs (
  run_id         text PRIMARY KEY,
  wave_id        text,
  snapshot_ref   text,
  classification text NOT NULL,  -- MATCH | DRIFT | UNREPLAYABLE
  receipt        jsonb NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now()
);
-- Usage join, event-plane leg: per-lane/window event counts from lane_events.
-- QUE admission + telemetry-receipt legs join at read time (one telemetry of
-- record per plane; this view never becomes a second usage store).
CREATE OR REPLACE VIEW appid_cp_usage_events AS
  SELECT lane, workflow, event_type, repo, occurred_at, run_id
  FROM lane_events;
