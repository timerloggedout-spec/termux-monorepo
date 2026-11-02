-- Unit 025 -- story assertions replicating the CodeRoad test set for
-- "Build a Celestial Bodies Database". Run with ON_ERROR_STOP against the
-- built (or dump-rebuilt) `universe` database; any failed story raises.
DO $$
DECLARE
  t text;
  n int;
  tables text[] := ARRAY['galaxy','star','planet','moon','asteroid'];
  big_tables text[] := ARRAY['galaxy','star','planet','moon'];
  min_rows int;
BEGIN
  -- at least five tables
  SELECT count(*) INTO n FROM information_schema.tables
   WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
  IF n < 5 THEN RAISE EXCEPTION 'STORY FAIL: at least five tables (found %)', n; END IF;

  FOREACH t IN ARRAY tables LOOP
    -- table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables
                    WHERE table_schema='public' AND table_name=t) THEN
      RAISE EXCEPTION 'STORY FAIL: table % missing', t; END IF;
    -- primary key named <table>_id
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage k
                      ON tc.constraint_name = k.constraint_name
                     AND tc.table_schema = k.table_schema
                   WHERE tc.table_schema='public' AND tc.table_name=t
                     AND tc.constraint_type='PRIMARY KEY'
                     AND k.column_name = t || '_id') THEN
      RAISE EXCEPTION 'STORY FAIL: % primary key column %_id', t, t; END IF;
    -- primary key auto-increments
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema='public' AND table_name=t
                      AND column_name = t || '_id'
                      AND (column_default LIKE 'nextval%' OR is_identity = 'YES')) THEN
      RAISE EXCEPTION 'STORY FAIL: % primary key does not auto-increment', t; END IF;
    -- name column of type VARCHAR
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                    WHERE table_schema='public' AND table_name=t
                      AND column_name='name' AND data_type='character varying') THEN
      RAISE EXCEPTION 'STORY FAIL: % name column is not VARCHAR', t; END IF;
    -- at least three columns
    SELECT count(*) INTO n FROM information_schema.columns
     WHERE table_schema='public' AND table_name=t;
    IF n < 3 THEN RAISE EXCEPTION 'STORY FAIL: % has fewer than three columns', t; END IF;
    -- at least two NOT NULL columns
    SELECT count(*) INTO n FROM information_schema.columns
     WHERE table_schema='public' AND table_name=t AND is_nullable='NO';
    IF n < 2 THEN RAISE EXCEPTION 'STORY FAIL: % has fewer than two NOT NULL columns', t; END IF;
    -- at least one UNIQUE column
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                    WHERE table_schema='public' AND table_name=t
                      AND constraint_type='UNIQUE') THEN
      RAISE EXCEPTION 'STORY FAIL: % has no UNIQUE column', t; END IF;
    -- at least three rows
    EXECUTE format('SELECT count(*) FROM %I', t) INTO n;
    IF n < 3 THEN RAISE EXCEPTION 'STORY FAIL: % has fewer than three rows', t; END IF;
  END LOOP;

  FOREACH t IN ARRAY big_tables LOOP
    -- at least five columns
    SELECT count(*) INTO n FROM information_schema.columns
     WHERE table_schema='public' AND table_name=t;
    IF n < 5 THEN RAISE EXCEPTION 'STORY FAIL: % has fewer than five columns', t; END IF;
  END LOOP;

  -- row minimums per table
  SELECT count(*) INTO n FROM galaxy;  IF n < 6  THEN RAISE EXCEPTION 'STORY FAIL: galaxy < 6 rows'; END IF;
  SELECT count(*) INTO n FROM star;    IF n < 6  THEN RAISE EXCEPTION 'STORY FAIL: star < 6 rows'; END IF;
  SELECT count(*) INTO n FROM planet;  IF n < 12 THEN RAISE EXCEPTION 'STORY FAIL: planet < 12 rows'; END IF;
  SELECT count(*) INTO n FROM moon;    IF n < 20 THEN RAISE EXCEPTION 'STORY FAIL: moon < 20 rows'; END IF;

  -- INT on at least two columns that are not a primary or foreign key
  -- (in this schema every key column is named <something>_id)
  SELECT count(*) INTO n FROM information_schema.columns
   WHERE table_schema='public' AND data_type='integer' AND column_name NOT LIKE '%\_id';
  IF n < 2 THEN RAISE EXCEPTION 'STORY FAIL: INT used on fewer than two non-key columns'; END IF;
  -- NUMERIC at least once
  SELECT count(*) INTO n FROM information_schema.columns
   WHERE table_schema='public' AND data_type='numeric';
  IF n < 1 THEN RAISE EXCEPTION 'STORY FAIL: NUMERIC never used'; END IF;
  -- TEXT at least once
  SELECT count(*) INTO n FROM information_schema.columns
   WHERE table_schema='public' AND data_type='text';
  IF n < 1 THEN RAISE EXCEPTION 'STORY FAIL: TEXT never used'; END IF;
  -- BOOLEAN on at least two columns
  SELECT count(*) INTO n FROM information_schema.columns
   WHERE table_schema='public' AND data_type='boolean';
  IF n < 2 THEN RAISE EXCEPTION 'STORY FAIL: BOOLEAN used on fewer than two columns'; END IF;

  -- foreign keys with matching names
  IF NOT EXISTS (SELECT 1 FROM pg_constraint c
                  JOIN pg_class ct ON ct.oid = c.conrelid
                  JOIN pg_class rt ON rt.oid = c.confrelid
                  JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
                  JOIN pg_attribute ra ON ra.attrelid = c.confrelid AND ra.attnum = c.confkey[1]
                 WHERE c.contype='f' AND ct.relname='star' AND rt.relname='galaxy'
                   AND a.attname='galaxy_id' AND ra.attname='galaxy_id') THEN
    RAISE EXCEPTION 'STORY FAIL: star.galaxy_id foreign key missing'; END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint c
                  JOIN pg_class ct ON ct.oid = c.conrelid
                  JOIN pg_class rt ON rt.oid = c.confrelid
                  JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
                  JOIN pg_attribute ra ON ra.attrelid = c.confrelid AND ra.attnum = c.confkey[1]
                 WHERE c.contype='f' AND ct.relname='planet' AND rt.relname='star'
                   AND a.attname='star_id' AND ra.attname='star_id') THEN
    RAISE EXCEPTION 'STORY FAIL: planet.star_id foreign key missing'; END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint c
                  JOIN pg_class ct ON ct.oid = c.conrelid
                  JOIN pg_class rt ON rt.oid = c.confrelid
                  JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
                  JOIN pg_attribute ra ON ra.attrelid = c.confrelid AND ra.attnum = c.confkey[1]
                 WHERE c.contype='f' AND ct.relname='moon' AND rt.relname='planet'
                   AND a.attname='planet_id' AND ra.attname='planet_id') THEN
    RAISE EXCEPTION 'STORY FAIL: moon.planet_id foreign key missing'; END IF;

  RAISE NOTICE 'ALL STORIES PASS';
END $$;
