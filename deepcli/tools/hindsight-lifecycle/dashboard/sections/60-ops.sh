#!/usr/bin/env bash
# @section OPS
# @owner collaborator
# @depends db|api
set -u
echo
echo "=== [ OPS - live product surface ] ==="
if [ -z "${PSQL:-}" ]; then exit 0; fi

echo "  --- observations formed (proof_count>=5) ---"
"$PSQL" -tAc "
SELECT '  proof=' || lpad(proof_count::text,3,' ') || '  ' || substring(text,1,100)
FROM memory_units
WHERE bank_id='termux-monorepo::primary' AND proof_count >= 5
ORDER BY proof_count DESC LIMIT 5;" 2>&1

echo "  --- observation_history: consolidation events ---"
"$PSQL" -tAc "
SELECT '  ' || to_char(changed_at,'HH24:MI:SS') || '  ' || substring(content::text,1,90)
FROM observation_history ORDER BY changed_at DESC LIMIT 5;" 2>&1

echo "  --- memory_links by link_type ---"
"$PSQL" -tAc "
SELECT '  ' || link_type || '  n=' || count(*) FROM memory_links GROUP BY link_type ORDER BY count(*) DESC LIMIT 8;" 2>&1

echo "  --- primary bank: last 3 by type ---"
"$PSQL" -tAc "
SELECT '  ' || to_char(created_at,'HH24:MI:SS') || '  ' || fact_type || '  ' || substring(text,1,80)
FROM memory_units WHERE bank_id='termux-monorepo::primary'
ORDER BY created_at DESC LIMIT 3;" 2>&1
