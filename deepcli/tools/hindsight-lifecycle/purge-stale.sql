\set ON_ERROR_STOP on
\if :{?purge_apply}
\else
  \set purge_apply 0
\endif

-- Hindsight stale-bank reconciliation.
-- Default: read-only preflight.
-- Apply: psql -v purge_apply=1 -f purge-stale.sql
-- Safety: transaction, advisory lock, target existence, schema-driven
-- reconciliation, post-move residue check, and no FK dropping.

BEGIN;

SELECT pg_advisory_xact_lock(
  hashtextextended('hindsight:purge:deepagent::termux-monorepo', 0)
);

DO $$
DECLARE
  source_bank constant text := 'deepagent::termux-monorepo';
  target_bank constant text := 'termux-monorepo::primary';
  source_count bigint;
  target_exists boolean;
BEGIN
  SELECT EXISTS (SELECT 1 FROM banks WHERE bank_id = target_bank)
    INTO target_exists;

  IF NOT target_exists THEN
    RAISE EXCEPTION 'purge preflight failed: target bank % does not exist', target_bank;
  END IF;

  SELECT count(*) INTO source_count
  FROM memory_units
  WHERE bank_id = source_bank;

  IF source_count = 0 THEN
    RAISE NOTICE 'purge preflight: source bank % is already empty', source_bank;
  ELSE
    RAISE NOTICE 'purge preflight: % memory units in %', source_count, source_bank;
  END IF;
END $$;

\if :purge_apply

DO $$
DECLARE
  source_bank constant text := 'deepagent::termux-monorepo';
  target_bank constant text := 'termux-monorepo::primary';
  rec record;
  remaining bigint;
BEGIN
  -- Reconcile every writable public base/partitioned table carrying bank_id.
  -- Schema is the source of truth; no FK constraints are dropped.
  FOR rec IN
    SELECT n.nspname AS schema_name, c.relname AS table_name
    FROM pg_attribute a
    JOIN pg_class c ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE a.attname = 'bank_id'
      AND a.attnum > 0
      AND NOT a.attisdropped
      AND c.relkind IN ('r','p')
      AND n.nspname = 'public'
      AND c.relname <> 'banks'
    ORDER BY c.relname
  LOOP
    EXECUTE format(
      'UPDATE %I.%I SET bank_id = $1 WHERE bank_id = $2',
      rec.schema_name, rec.table_name
    ) USING target_bank, source_bank;

    GET DIAGNOSTICS remaining = ROW_COUNT;
    IF remaining > 0 THEN
      RAISE NOTICE 'reconciled %.%: % rows',
        rec.schema_name, rec.table_name, remaining;
    END IF;
  END LOOP;

  -- Never delete the source bank while any dependent bank_id row remains.
  FOR rec IN
    SELECT n.nspname AS schema_name, c.relname AS table_name
    FROM pg_attribute a
    JOIN pg_class c ON c.oid = a.attrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE a.attname = 'bank_id'
      AND a.attnum > 0
      AND NOT a.attisdropped
      AND c.relkind IN ('r','p')
      AND n.nspname = 'public'
      AND c.relname <> 'banks'
    ORDER BY c.relname
  LOOP
    EXECUTE format(
      'SELECT count(*) FROM %I.%I WHERE bank_id = $1',
      rec.schema_name, rec.table_name
    ) INTO remaining USING source_bank;

    IF remaining <> 0 THEN
      RAISE EXCEPTION
        'purge safety check failed: %.% still has % rows for %',
        rec.schema_name, rec.table_name, remaining, source_bank;
    END IF;
  END LOOP;

  DELETE FROM banks WHERE bank_id = source_bank;

  IF NOT FOUND THEN
    RAISE EXCEPTION
      'purge safety check failed: source bank was not present at delete step';
  END IF;

  RAISE NOTICE 'purge applied: % -> %', source_bank, target_bank;
END $$;

\else

DO $$
BEGIN
  RAISE NOTICE
    'purge dry-run only; no rows changed. Use -v purge_apply=1 to apply.';
END $$;

\endif

COMMIT;

SELECT
  'remaining_source_rows=' ||
    (SELECT count(*) FROM memory_units
     WHERE bank_id='deepagent::termux-monorepo') ||
  ', source_bank_exists=' ||
    CASE WHEN EXISTS (
      SELECT 1 FROM banks WHERE bank_id='deepagent::termux-monorepo'
    ) THEN 'true' ELSE 'false' END ||
  ', target_bank_exists=' ||
    CASE WHEN EXISTS (
      SELECT 1 FROM banks WHERE bank_id='termux-monorepo::primary'
    ) THEN 'true' ELSE 'false' END
  AS purge_receipt;
