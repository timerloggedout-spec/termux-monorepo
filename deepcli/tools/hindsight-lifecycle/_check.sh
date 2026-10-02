#!/usr/bin/env bash
PGPASSWORD=hindsight /home/vscode/.pg0/installation/18.1.0/bin/psql -h /tmp -U hindsight -d hindsight -tAc "
SELECT to_char(created_at,'HH24:MI:SS') || '|' || metadata->>'origin' || '|' || metadata->>'event' || '|' || substring(text,1,70)
FROM memory_units
WHERE bank_id='termux-monorepo::primary'
ORDER BY created_at DESC LIMIT 5;
"
