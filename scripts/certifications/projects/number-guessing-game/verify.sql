-- Unit 063 -- structure assertions for the number_guess database.
DO $$
BEGIN
  IF (SELECT count(*) FROM information_schema.tables WHERE table_schema='public'
       AND table_name IN ('users','games')) <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: users/games tables'; END IF;
  -- usernames up to 22 characters, unique
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users'
                  AND column_name='username' AND data_type='character varying' AND character_maximum_length=22) THEN
    RAISE EXCEPTION 'STORY FAIL: users.username is not VARCHAR(22)'; END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints tc
                  JOIN information_schema.key_column_usage kcu ON kcu.constraint_name=tc.constraint_name
                 WHERE tc.constraint_type='UNIQUE' AND tc.table_name='users' AND kcu.column_name='username') THEN
    RAISE EXCEPTION 'STORY FAIL: users.username is not UNIQUE'; END IF;
  -- auto-incrementing primary keys
  IF (SELECT count(*) FROM information_schema.columns
       WHERE column_name IN ('user_id','game_id') AND column_default LIKE 'nextval%') <> 2 THEN
    RAISE EXCEPTION 'STORY FAIL: serial primary keys'; END IF;
  -- games.user_id FK -> users; games.guesses integer
  IF NOT EXISTS (SELECT 1 FROM pg_constraint c JOIN pg_class ct ON ct.oid=c.conrelid JOIN pg_class rt ON rt.oid=c.confrelid
                  JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
                 WHERE c.contype='f' AND ct.relname='games' AND rt.relname='users' AND a.attname='user_id') THEN
    RAISE EXCEPTION 'STORY FAIL: games.user_id FK'; END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='games' AND column_name='guesses' AND data_type='integer') THEN
    RAISE EXCEPTION 'STORY FAIL: games.guesses is not INT'; END IF;
  RAISE NOTICE 'ALL STORIES PASS';
END $$;
