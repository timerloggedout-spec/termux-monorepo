#!/usr/bin/env bash
echo "[ MVT QUALITY - per bank ]"
if [ -n "$PSQL" ]; then
  "$PSQL" -tA -c "SELECT bank_id || '  n=' || count(*) || '  len=' || coalesce(avg(length(coalesce(nullif(text,''),context,''))))::int || '  proof=' || round(avg(proof_count)::numeric,2) || '  tags=' || round(avg(coalesce(array_length(tags,1),0))::numeric,2) FROM memory_units WHERE bank_id LIKE '%::mvt::%' GROUP BY bank_id ORDER BY count(*) DESC;" 2>&1 | sed 's/^/  /'
  echo "  --- cross-bank divergence (same origin) ---"
  "$PSQL" -tA -c "SELECT '    ' || substring(coalesce(metadata->>'origin','unknown'),1,40) || '  banks=' || count(DISTINCT bank_id) || '  facts=' || count(*) FROM memory_units WHERE bank_id LIKE '%::mvt::%' GROUP BY substring(coalesce(metadata->>'origin','unknown'),1,40) HAVING count(DISTINCT bank_id) > 1 ORDER BY count(*) DESC LIMIT 8;" 2>&1 || echo "    (no cross-bank origin yet)"
fi

echo
