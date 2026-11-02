-- Unit 062 -- assertions replicating the Periodic Table story set.
DO $$
DECLARE
  n int;
  expected_types jsonb := '{"1":"nonmetal","2":"nonmetal","3":"metal","4":"metal","5":"metalloid","6":"nonmetal","7":"nonmetal","8":"nonmetal","9":"nonmetal","10":"nonmetal"}';
  rec record;
BEGIN
  -- renames: weight gone + atomic_mass present; melting/boiling renamed + NOT NULL; old names gone
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='properties' AND column_name IN ('weight','melting_point','boiling_point','type')) THEN
    RAISE EXCEPTION 'STORY FAIL: legacy properties columns remain'; END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='properties' AND column_name='atomic_mass') THEN
    RAISE EXCEPTION 'STORY FAIL: atomic_mass missing'; END IF;
  IF (SELECT count(*) FROM information_schema.columns WHERE table_name='properties'
       AND column_name IN ('melting_point_celsius','boiling_point_celsius') AND is_nullable='NO') <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: melting/boiling celsius NOT NULL'; END IF;
  -- elements.symbol + name UNIQUE and NOT NULL
  IF (SELECT count(DISTINCT kcu.column_name) FROM information_schema.table_constraints tc
       JOIN information_schema.key_column_usage kcu ON kcu.constraint_name=tc.constraint_name
      WHERE tc.constraint_type='UNIQUE' AND tc.table_name='elements' AND kcu.column_name IN ('symbol','name')) <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: elements symbol/name UNIQUE'; END IF;
  IF (SELECT count(*) FROM information_schema.columns WHERE table_name='elements'
       AND column_name IN ('symbol','name') AND is_nullable='NO') <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: elements symbol/name NOT NULL'; END IF;
  -- properties.atomic_number is an FK to elements
  IF NOT EXISTS (SELECT 1 FROM pg_constraint c JOIN pg_class ct ON ct.oid=c.conrelid JOIN pg_class rt ON rt.oid=c.confrelid
                  WHERE c.contype='f' AND ct.relname='properties' AND rt.relname='elements') THEN
    RAISE EXCEPTION 'STORY FAIL: properties FK to elements'; END IF;
  -- types table: type_id integer PK, type VARCHAR NOT NULL, exactly the three types
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='types' AND column_name='type_id' AND data_type='integer')
     OR NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='types' AND column_name='type' AND data_type='character varying' AND is_nullable='NO') THEN
    RAISE EXCEPTION 'STORY FAIL: types columns'; END IF;
  IF (SELECT count(*) FROM types) <> 3
     OR (SELECT count(*) FROM types WHERE type IN ('metal','metalloid','nonmetal')) <> 3 THEN
    RAISE EXCEPTION 'STORY FAIL: types rows'; END IF;
  -- properties.type_id INT NOT NULL FK -> types, and every element maps to its original type
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='properties' AND column_name='type_id'
                  AND data_type='integer' AND is_nullable='NO') THEN
    RAISE EXCEPTION 'STORY FAIL: properties.type_id'; END IF;
  FOR rec IN SELECT p.atomic_number AS an, t.type AS ty FROM properties p JOIN types t ON t.type_id=p.type_id LOOP
    IF expected_types ->> rec.an::text IS DISTINCT FROM rec.ty THEN
      RAISE EXCEPTION 'STORY FAIL: element % type % incorrect', rec.an, rec.ty; END IF;
  END LOOP;
  -- symbols capitalized (first letter upper, rest lower)
  IF EXISTS (SELECT 1 FROM elements WHERE symbol !~ '^[A-Z][a-z]?$') THEN
    RAISE EXCEPTION 'STORY FAIL: symbol capitalization'; END IF;
  -- atomic masses exactly the trimmed set
  IF (SELECT count(*) FROM properties) <> 10
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=1 AND atomic_mass=1.008)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=2 AND atomic_mass=4.0026)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=3 AND atomic_mass=6.94)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=4 AND atomic_mass=9.0122)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=5 AND atomic_mass=10.81)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=6 AND atomic_mass=12.011)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=7 AND atomic_mass=14.007)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=8 AND atomic_mass=15.999)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=9 AND atomic_mass=18.998 AND melting_point_celsius=-220 AND boiling_point_celsius=-188.1)
     OR NOT EXISTS (SELECT 1 FROM properties WHERE atomic_number=10 AND atomic_mass=20.18 AND melting_point_celsius=-248.6 AND boiling_point_celsius=-246.1) THEN
    RAISE EXCEPTION 'STORY FAIL: atomic masses / F / Ne rows'; END IF;
  -- no bogus element 1000 anywhere; exactly 10 elements
  IF EXISTS (SELECT 1 FROM elements WHERE atomic_number=1000) OR EXISTS (SELECT 1 FROM properties WHERE atomic_number=1000)
     OR (SELECT count(*) FROM elements) <> 10 THEN
    RAISE EXCEPTION 'STORY FAIL: element 1000 / element count'; END IF;
  RAISE NOTICE 'ALL STORIES PASS';
END $$;
