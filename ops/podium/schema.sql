-- Podium dataset store: crawled lablab venue evidence (editions, judges,
-- prize tiers, winning projects) with per-row receipts and preserved
-- conflicts. Design: docs/ops/PODIUM-DATASET.md.
-- Pattern follows ops/challenge-participants/schema.sql (append-only
-- batches + current views), but the source is the crawler, not
-- coordinator.json: this is the EXTERNAL evidence layer used to
-- triple-source podium claims.
-- Credentials (repo secrets, names only — same Neon lane-events route):
-- LANE_EVENTS_DATABASE_URL or NEON_API_KEY. Safe to re-run.

-- One row per crawl batch landed.
CREATE TABLE IF NOT EXISTS podium_crawls (
  crawl_key    text PRIMARY KEY,               -- sha256(dataset version)
  version      text NOT NULL,                  -- dataset version, e.g. 2026-11-03.v1
  captured_at  timestamptz NOT NULL,           -- snapshot capture time
  collector    text NOT NULL,                  -- collector id of record
  counts       jsonb NOT NULL DEFAULT '{}'::jsonb,
  landed_at    timestamptz NOT NULL DEFAULT now()
);

-- Append-only entity observations, verbatim dataset fields + receipts.
CREATE TABLE IF NOT EXISTS podium_observations (
  obs_key      text NOT NULL,                  -- sha256(crawl_key|entity_key|content_hash)
  crawl_key    text NOT NULL,
  entity_key   text NOT NULL,                  -- kind:edition[:team[:project]] etc.
  kind         text NOT NULL,                  -- edition|placement_tier|judge|project|comment
  fields       jsonb NOT NULL,                 -- normalized fields (verbatim values)
  content_hash text NOT NULL,
  receipts     jsonb NOT NULL DEFAULT '[]'::jsonb, -- [{source_url, captured_at, collector}]
  recorded_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (crawl_key, entity_key)
);
CREATE INDEX IF NOT EXISTS podium_obs_entity_ix ON podium_observations (entity_key);
CREATE INDEX IF NOT EXISTS podium_obs_kind_ix ON podium_observations (kind, entity_key);

-- Conflicts are data, never silently merged: one row per
-- (entity, field, crawl) where sources disagree.
CREATE TABLE IF NOT EXISTS podium_conflicts (
  conflict_key text PRIMARY KEY,               -- sha256(crawl_key|entity|field|values)
  crawl_key    text NOT NULL,
  entity_key   text NOT NULL,
  field        text NOT NULL,
  values       jsonb NOT NULL,                 -- all conflicting values
  receipts     jsonb NOT NULL DEFAULT '[]'::jsonb,
  note         text,
  recorded_at  timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION podium_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'podium store is append-only (% blocked)', TG_OP;
END $$;

DROP TRIGGER IF EXISTS podium_obs_no_mutation ON podium_observations;
CREATE TRIGGER podium_obs_no_mutation
  BEFORE UPDATE OR DELETE ON podium_observations
  FOR EACH ROW EXECUTE FUNCTION podium_append_only();

DROP TRIGGER IF EXISTS podium_conflicts_no_mutation ON podium_conflicts;
CREATE TRIGGER podium_conflicts_no_mutation
  BEFORE UPDATE OR DELETE ON podium_conflicts
  FOR EACH ROW EXECUTE FUNCTION podium_append_only();

-- Current = observations of the newest crawl batch.
CREATE OR REPLACE VIEW podium_current AS
SELECT o.entity_key, o.kind, o.fields, o.content_hash, o.receipts, o.recorded_at
FROM podium_observations o
JOIN (SELECT crawl_key FROM podium_crawls ORDER BY landed_at DESC, crawl_key DESC LIMIT 1) latest
  ON o.crawl_key = latest.crawl_key;

-- Podium join for consumers: per edition, its tiers, projects by
-- placement, and judges — all from the current crawl.
CREATE OR REPLACE VIEW podium_by_edition AS
SELECT
  e.fields->>'title' AS edition_title,
  (SELECT jsonb_agg(t.fields) FROM podium_current t
     WHERE t.kind = 'placement_tier'
       AND t.entity_key LIKE 'tier:' || split_part(e.entity_key, ':', 2) || ':%') AS tiers,
  (SELECT jsonb_agg(p.fields) FROM podium_current p
     WHERE p.kind = 'project' AND p.fields->>'edition' = split_part(e.entity_key, ':', 2)) AS projects,
  (SELECT jsonb_agg(j.fields) FROM podium_current j
     WHERE j.kind = 'judge' AND j.fields->>'edition' = split_part(e.entity_key, ':', 2)) AS judges
FROM podium_current e
WHERE e.kind = 'edition';
