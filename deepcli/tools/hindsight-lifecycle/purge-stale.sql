\set ON_ERROR_STOP on
\if :{?purge_apply}
\else
  \set purge_apply 0
\endif

-- Hindsight stale-bank reconciliation. The only supported dependents are the
-- observed Hindsight tables memory_units and documents, each with a direct
-- bank_id -> public.banks(bank_id) FK. Refuse unknown FK dependents rather
-- than inferring ownership from a column name.
-- Default is read-only; apply with: psql -v purge_apply=1 -f purge-stale.sql

BEGIN;
SELECT pg_advisory_xact_lock(
  hashtextextended('hindsight:purge:deepagent::termux-monorepo', 0)
);

\if :purge_apply
-- Hold the validated table definitions and bank rows stable through apply.
-- ONLY avoids locking unverified descendants before the shape check rejects them.
LOCK TABLE ONLY public.banks, ONLY public.memory_units, ONLY public.documents
  IN SHARE ROW EXCLUSIVE MODE;
\endif

DO $$
DECLARE
  source_bank constant text := 'deepagent::termux-monorepo';
  target_bank constant text := 'termux-monorepo::primary';
  allowed constant text[] := ARRAY['memory_units','documents'];
  table_name text;
  source_count bigint;
  relation_oid oid;
BEGIN
  IF to_regclass('public.banks') IS NULL
     OR to_regclass('public.memory_units') IS NULL
     OR to_regclass('public.documents') IS NULL THEN
    RAISE EXCEPTION 'purge preflight failed: required public Hindsight tables are missing';
  END IF;

  -- Explicit UPDATE/DELETE on an inherited or partitioned parent may affect
  -- descendants without the verified direct FK. Require standalone tables.
  FOREACH table_name IN ARRAY ARRAY['banks','memory_units','documents'] LOOP
    relation_oid := to_regclass(format('public.%I', table_name));
    IF NOT EXISTS (
      SELECT 1 FROM pg_class c
      JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE c.oid = relation_oid AND n.nspname = 'public'
        AND c.relkind = 'r' AND NOT c.relispartition
        AND NOT EXISTS (SELECT 1 FROM pg_inherits i WHERE i.inhrelid = c.oid OR i.inhparent = c.oid)
    ) THEN
      RAISE EXCEPTION 'purge preflight failed: public.% must be a standalone, non-partitioned ordinary table', table_name;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_class WHERE oid = relation_oid AND relrowsecurity)
       OR EXISTS (SELECT 1 FROM pg_trigger WHERE tgrelid = relation_oid
         AND NOT tgisinternal AND tgenabled <> 'D')
       OR EXISTS (SELECT 1 FROM pg_rewrite WHERE ev_class = relation_oid
         AND ev_enabled <> 'D') THEN
      RAISE EXCEPTION 'purge preflight failed: public.% has unsupported row security, triggers, or rules', table_name;
    END IF;
  END LOOP;
  IF NOT EXISTS (SELECT 1 FROM public.banks WHERE bank_id = target_bank) THEN
    RAISE EXCEPTION 'purge preflight failed: target bank % does not exist', target_bank;
  END IF;

  -- Verify direct, single-column FK semantics for each allowlisted table.
  FOREACH table_name IN ARRAY allowed LOOP
    IF NOT EXISTS (
      SELECT 1 FROM pg_constraint con
      WHERE con.contype = 'f'
        AND con.conrelid = to_regclass(format('public.%I', table_name))
        AND con.confrelid = 'public.banks'::regclass
        AND con.convalidated
        AND con.conkey = ARRAY[(SELECT attnum FROM pg_attribute
          WHERE attrelid = con.conrelid AND attname = 'bank_id' AND NOT attisdropped)]::smallint[]
        AND con.confkey = ARRAY[(SELECT attnum FROM pg_attribute
          WHERE attrelid = con.confrelid AND attname = 'bank_id' AND NOT attisdropped)]::smallint[]
    ) THEN
      RAISE EXCEPTION 'purge preflight failed: public.% lacks the verified bank_id FK to public.banks(bank_id)', table_name;
    END IF;
  END LOOP;

  -- Reject indirect cascades too: an FK into memory_units/documents could
  -- otherwise update unrelated tables even without its own FK into banks.
  IF EXISTS (
    SELECT 1 FROM pg_constraint con
    JOIN pg_class child ON child.oid = con.conrelid
    JOIN pg_namespace ns ON ns.oid = child.relnamespace
    WHERE con.contype = 'f' AND con.confrelid IN
      ('public.banks'::regclass, 'public.memory_units'::regclass, 'public.documents'::regclass)
      AND NOT (con.confrelid = 'public.banks'::regclass
        AND ns.nspname = 'public' AND child.relname = ANY(allowed)
        AND con.conkey = ARRAY[(SELECT attnum FROM pg_attribute WHERE attrelid=con.conrelid AND attname='bank_id' AND NOT attisdropped)]::smallint[]
        AND con.confkey = ARRAY[(SELECT attnum FROM pg_attribute WHERE attrelid=con.confrelid AND attname='bank_id' AND NOT attisdropped)]::smallint[])
  ) THEN
    RAISE EXCEPTION 'purge preflight failed: unknown foreign-key dependency references purge tables';
  END IF;

  SELECT count(*) INTO source_count FROM public.memory_units WHERE bank_id = source_bank;
  RAISE NOTICE 'purge preflight: % memory units in %', source_count, source_bank;
END $$;

\if :purge_apply
DO $$
DECLARE
  source_bank constant text := 'deepagent::termux-monorepo';
  target_bank constant text := 'termux-monorepo::primary';
  remaining bigint;
BEGIN
  -- Explicit, qualified table list only; all writes remain transactional.
  UPDATE public.memory_units SET bank_id = target_bank WHERE bank_id = source_bank;
  UPDATE public.documents SET bank_id = target_bank WHERE bank_id = source_bank;

  SELECT count(*) INTO remaining FROM public.memory_units WHERE bank_id = source_bank;
  IF remaining <> 0 THEN
    RAISE EXCEPTION 'purge safety check failed: public.memory_units retains % source rows', remaining;
  END IF;
  SELECT count(*) INTO remaining FROM public.documents WHERE bank_id = source_bank;
  IF remaining <> 0 THEN
    RAISE EXCEPTION 'purge safety check failed: public.documents retains % source rows', remaining;
  END IF;
  DELETE FROM public.banks WHERE bank_id = source_bank;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'purge safety check failed: source bank was not present at delete step';
  END IF;
  RAISE NOTICE 'purge applied: % -> %', source_bank, target_bank;
END $$;
\else
DO $$ BEGIN RAISE NOTICE 'purge dry-run only; no rows changed. Use -v purge_apply=1 to apply.'; END $$;
\endif

COMMIT;

SELECT
  'remaining_source_rows=' || (SELECT count(*) FROM public.memory_units WHERE bank_id='deepagent::termux-monorepo') ||
  ', source_bank_exists=' || CASE WHEN EXISTS (SELECT 1 FROM public.banks WHERE bank_id='deepagent::termux-monorepo') THEN 'true' ELSE 'false' END ||
  ', target_bank_exists=' || CASE WHEN EXISTS (SELECT 1 FROM public.banks WHERE bank_id='termux-monorepo::primary') THEN 'true' ELSE 'false' END
  AS purge_receipt;
