
DO $$
DECLARE rec RECORD;
BEGIN
  FOR rec IN
    SELECT conname, conrelid::regclass::text AS tbl FROM pg_constraint
    WHERE contype='f' AND confrelid IN ('documents'::regclass, 'banks'::regclass)
  LOOP
    EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I', rec.tbl, rec.conname);
  END LOOP;

  FOR rec IN
    SELECT table_name FROM information_schema.columns
    WHERE column_name='bank_id' AND table_schema='public' AND table_name != 'banks'
  LOOP
    EXECUTE format($f$UPDATE %I SET bank_id='termux-monorepo::primary' WHERE bank_id='deepagent::termux-monorepo';$f$, rec.table_name);
  END LOOP;

  DELETE FROM banks WHERE bank_id='deepagent::termux-monorepo';
END $$;
SELECT 'banks: ' || string_agg(bank_id, ' | ') FROM banks;
