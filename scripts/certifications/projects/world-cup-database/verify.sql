-- Unit 039 -- structure assertions replicating the World Cup story set.
DO $$
DECLARE
  n int;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='teams')
     OR NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='games') THEN
    RAISE EXCEPTION 'STORY FAIL: teams/games tables missing'; END IF;
  -- serial primary keys named team_id / game_id, auto-incrementing
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='teams' AND column_name='team_id'
                  AND data_type='integer' AND column_default LIKE 'nextval%') THEN
    RAISE EXCEPTION 'STORY FAIL: teams.team_id is not SERIAL'; END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='games' AND column_name='game_id'
                  AND data_type='integer' AND column_default LIKE 'nextval%') THEN
    RAISE EXCEPTION 'STORY FAIL: games.game_id is not SERIAL'; END IF;
  -- teams.name UNIQUE
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE table_name='teams' AND constraint_type='UNIQUE') THEN
    RAISE EXCEPTION 'STORY FAIL: teams.name is not UNIQUE'; END IF;
  -- column types
  IF (SELECT data_type FROM information_schema.columns WHERE table_name='games' AND column_name='year') <> 'integer'
     OR (SELECT data_type FROM information_schema.columns WHERE table_name='games' AND column_name='round') <> 'character varying'
     OR (SELECT data_type FROM information_schema.columns WHERE table_name='games' AND column_name='winner_goals') <> 'integer'
     OR (SELECT data_type FROM information_schema.columns WHERE table_name='games' AND column_name='opponent_goals') <> 'integer' THEN
    RAISE EXCEPTION 'STORY FAIL: games column types'; END IF;
  -- every column NOT NULL in both tables
  SELECT count(*) INTO n FROM information_schema.columns
   WHERE table_name IN ('teams','games') AND is_nullable='YES';
  IF n > 0 THEN RAISE EXCEPTION 'STORY FAIL: % nullable columns', n; END IF;
  -- foreign keys winner_id / opponent_id -> teams.team_id
  IF (SELECT count(*) FROM pg_constraint c
       JOIN pg_class ct ON ct.oid=c.conrelid JOIN pg_class rt ON rt.oid=c.confrelid
       JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
      WHERE c.contype='f' AND ct.relname='games' AND rt.relname='teams'
        AND a.attname IN ('winner_id','opponent_id')) <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: games foreign keys'; END IF;
  RAISE NOTICE 'ALL STORIES PASS';
END $$;
