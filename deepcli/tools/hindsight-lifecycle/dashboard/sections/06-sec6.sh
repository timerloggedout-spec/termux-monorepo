#!/usr/bin/env bash
echo "[ PROVENANCE — recent fact edits ]"
if [ -n "$PSQL" ]; then
  "$PSQL" -tA -c "SELECT '  ' || to_char(ts,'MM-DD HH24:MI') || '  ' || actor || '  ' || op || '  ' || left(unit_id,12) || '  ' || coalesce(reason,'') FROM hs_facts_journal ORDER BY ts DESC LIMIT 10;" 2>&1 || echo "  (no journal yet)"
fi

echo
