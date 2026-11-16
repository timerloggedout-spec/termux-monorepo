-- Unit 040 -- structure assertions replicating the Salon story set.
DO $$
DECLARE
  n int;
BEGIN
  IF (SELECT count(*) FROM information_schema.tables WHERE table_schema='public'
       AND table_name IN ('customers','appointments','services')) <> 3 THEN
    RAISE EXCEPTION 'STORY FAIL: customers/appointments/services tables'; END IF;
  -- primary keys named <singular>_id and auto-incrementing, one per table
  IF (SELECT count(*) FROM information_schema.columns
       WHERE column_name IN ('customer_id','service_id','appointment_id')
         AND column_default LIKE 'nextval%') <> 3 THEN
    RAISE EXCEPTION 'STORY FAIL: serial primary keys'; END IF;
  IF (SELECT count(*) FROM information_schema.table_constraints
       WHERE constraint_type='PRIMARY KEY' AND table_name IN ('customers','appointments','services')) <> 3 THEN
    RAISE EXCEPTION 'STORY FAIL: primary key constraints'; END IF;
  -- foreign keys appointments.customer_id -> customers, appointments.service_id -> services
  IF (SELECT count(*) FROM pg_constraint c
       JOIN pg_class ct ON ct.oid=c.conrelid
       JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
      WHERE c.contype='f' AND ct.relname='appointments'
        AND a.attname IN ('customer_id','service_id')) <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: appointments foreign keys'; END IF;
  -- customers.phone VARCHAR + UNIQUE
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customers'
                  AND column_name='phone' AND data_type='character varying') THEN
    RAISE EXCEPTION 'STORY FAIL: customers.phone is not VARCHAR'; END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints tc
                  JOIN information_schema.key_column_usage kcu ON kcu.constraint_name=tc.constraint_name
                 WHERE tc.constraint_type='UNIQUE' AND tc.table_name='customers' AND kcu.column_name='phone') THEN
    RAISE EXCEPTION 'STORY FAIL: customers.phone is not UNIQUE'; END IF;
  -- name columns on customers + services; appointments.time VARCHAR
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='customers' AND column_name='name')
     OR NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='services' AND column_name='name') THEN
    RAISE EXCEPTION 'STORY FAIL: name columns'; END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='appointments'
                  AND column_name='time' AND data_type='character varying') THEN
    RAISE EXCEPTION 'STORY FAIL: appointments.time is not VARCHAR'; END IF;
  -- at least three services, one with service_id = 1
  SELECT count(*) INTO n FROM services;
  IF n < 3 OR NOT EXISTS (SELECT 1 FROM services WHERE service_id=1) THEN
    RAISE EXCEPTION 'STORY FAIL: services seed rows (%)', n; END IF;
  RAISE NOTICE 'ALL STORIES PASS';
END $$;
