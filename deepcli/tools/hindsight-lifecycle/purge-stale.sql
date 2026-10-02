
DO $$
DECLARE rec RECORD; n int;
BEGIN
  SELECT count(*) INTO n FROM memory_units WHERE bank_id='termux-monorepo::primary';
  IF n = 0 THEN RAISE NOTICE 'clean'; RETURN; END IF;

  FOR rec IN SELECT conname, conrelid::regclass::text AS tbl FROM pg_constraint
    WHERE contype='f' AND confrelid IN ('documents'::regclass, 'banks'::regclass)
  LOOP EXECUTE format('ALTER TABLE %s DROP CONSTRAINT %I', rec.tbl, rec.conname); END LOOP;

  DELETE FROM entities e WHERE e.bank_id='termux-monorepo::primary'
    AND EXISTS (SELECT 1 FROM entities t WHERE t.bank_id='termux-monorepo::primary'
                AND lower(t.canonical_name)=lower(e.canonical_name));

  FOR rec IN SELECT table_name FROM information_schema.columns
    WHERE column_name='bank_id' AND table_schema='public' AND table_name NOT IN ('banks','entities')
  LOOP EXECUTE format($f$UPDATE %I SET bank_id='termux-monorepo::primary' WHERE bank_id='termux-monorepo::primary';$f$, rec.table_name); END LOOP;

  UPDATE entities SET bank_id='termux-monorepo::primary' WHERE bank_id='termux-monorepo::primary';
  DELETE FROM banks WHERE bank_id='termux-monorepo::primary';
END $$;
SELECT 'moved=' || count(*) FROM memory_units WHERE bank_id='termux-monorepo::primary';
