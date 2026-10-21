#!/usr/bin/env bash
# @section BANKS
# @owner collaborator
# @depends db
set -u
echo
echo "=== [ BANKS ] ==="
[ -n "${PSQL:-}" ] || { echo "  database:  unavailable"; exit 0; }
"$PSQL" -tA <<'SQL' 2>/dev/null || echo "  query:     unavailable"
SELECT rpad(bank_id,56,' ') || ' facts=' || count(*) ||
 ' age_min=' || coalesce(round(extract(epoch from (now()-max(created_at)))/60)::int::text,'?') ||
 CASE WHEN bank_id='termux-monorepo::primary' THEN ' [PRIMARY]'
      WHEN bank_id LIKE 'mvt::%' THEN ' [MVT]'
      WHEN bank_id LIKE 'deepagent::%' THEN ' [STALE-CANDIDATE]' ELSE '' END
FROM memory_units GROUP BY bank_id ORDER BY max(created_at) DESC NULLS LAST;
SQL
