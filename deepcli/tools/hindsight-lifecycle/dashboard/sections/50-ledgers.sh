#!/usr/bin/env bash
# @section LEDGERS
# @owner collaborator
# @depends db
set -u
echo
echo "=== [ LEDGERS ] ==="
if [ -z "${PSQL:-}" ]; then echo "  (no psql)"; exit 0; fi
"$PSQL" -tAc "
SELECT '  llm_requests          rows=' || count(*) FROM llm_requests
UNION ALL
SELECT '  documents             rows=' || count(*) FROM documents
UNION ALL
SELECT '  memory_units          rows=' || count(*) FROM memory_units
UNION ALL
SELECT '  observation_history   rows=' || count(*) FROM observation_history
UNION ALL
SELECT '  async_operations      rows=' || count(*) FROM async_operations
UNION ALL
SELECT '  audit_log             rows=' || count(*) FROM audit_log
;" 2>&1
echo "  --- last 3 llm_requests ---"
"$PSQL" -tAc "
SELECT '  ' || to_char(started_at,'HH24:MI:SS') || '  ' || provider || '  ' || status
FROM llm_requests ORDER BY started_at DESC LIMIT 3;" 2>&1
