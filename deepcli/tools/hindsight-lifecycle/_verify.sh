#!/usr/bin/env bash
PGPASSWORD=hindsight /home/vscode/.pg0/installation/18.1.0/bin/psql -h /tmp -U hindsight -d hindsight -tAc "
SELECT to_char(created_at,'HH24:MI:SS') || '|' || bank_id || '|' || coalesce(metadata::jsonb->>'origin','?') || '|' || coalesce(metadata::jsonb->>'event','?') || '|' || substring(text,1,60)
FROM memory_units
WHERE bank_id='termux-monorepo::primary'
  AND metadata::jsonb->>'origin'='deepagent'
ORDER BY created_at DESC LIMIT 5;
"
