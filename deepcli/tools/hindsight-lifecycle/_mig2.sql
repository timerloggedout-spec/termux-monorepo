
DO $$
DECLARE rec RECORD;
BEGIN
  FOR rec IN
    SELECT conname, conrelid::regclass::text AS tbl FROM pg_constraint
    WHERE contype='f' AND confrelid IN ('documents'::regclass, 'banks'::regclass)
  LOOP
    EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I', rec.tbl, rec.conname);
  END LOOP;
END $$;

-- entities: unique on (bank_id, lower(canonical_name)). Delete source dupes whose name already exists in target.
DELETE FROM entities e
WHERE e.bank_id = 'deepagent::termux-monorepo'
  AND EXISTS (
    SELECT 1 FROM entities t
    WHERE t.bank_id = 'termux-monorepo::primary'
      AND lower(t.canonical_name) = lower(e.canonical_name));

-- All other tables: simple reassign
DO $$
DECLARE rec RECORD;
BEGIN
  FOR rec IN
    SELECT table_name FROM information_schema.columns
    WHERE column_name='bank_id' AND table_schema='public'
      AND table_name NOT IN ('banks','entities')
  LOOP
    EXECUTE format($f$UPDATE %I SET bank_id='termux-monorepo::primary' WHERE bank_id='deepagent::termux-monorepo';$f$, rec.table_name);
  END LOOP;
END $$;

-- entities without conflict
UPDATE entities SET bank_id='termux-monorepo::primary' WHERE bank_id='deepagent::termux-monorepo';

-- drop old bank row
DELETE FROM banks WHERE bank_id='deepagent::termux-monorepo';

SELECT 'banks: ' || string_agg(bank_id, ' | ') FROM banks;
