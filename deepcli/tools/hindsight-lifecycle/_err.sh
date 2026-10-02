#!/usr/bin/env bash
P=/home/vscode/.pg0/installation/18.1.0/bin/psql
export PGPASSWORD=hindsight
$P -h /tmp -U hindsight -d hindsight -tAc "
SELECT to_char(started_at,'HH24:MI:SS') || '  ' || model || E'\\n  ' || substring(coalesce(error,'(no err)'),1,300) || E'\\n'
FROM llm_requests WHERE status='error' ORDER BY started_at DESC LIMIT 5;
"
