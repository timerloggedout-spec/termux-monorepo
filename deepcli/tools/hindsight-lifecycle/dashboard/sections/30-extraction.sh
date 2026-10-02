#!/usr/bin/env bash
# @section EXTRACTION
# @owner collaborator
# @depends db
set -u
echo
echo "=== [ EXTRACTION ] ==="
[ -n "${PSQL:-}" ] || { echo "  database:  unavailable"; exit 0; }
"$PSQL" -tA <<'SQL' 2>/dev/null || echo "  query:     unavailable"
WITH d AS (SELECT bank_id,count(*) documents FROM documents GROUP BY bank_id),
m AS (SELECT bank_id,count(*) memories FROM memory_units GROUP BY bank_id)
SELECT rpad(coalesce(d.bank_id,m.bank_id),56,' ') ||
 ' docs='||coalesce(d.documents,0)||' memories='||coalesce(m.memories,0)||
 ' ratio='||CASE WHEN coalesce(d.documents,0)=0 THEN 'n/a'
 ELSE round(coalesce(m.memories,0)::numeric/d.documents,2)::text END
FROM d FULL OUTER JOIN m USING(bank_id)
ORDER BY coalesce(d.documents,0)+coalesce(m.memories,0) DESC;
SQL
