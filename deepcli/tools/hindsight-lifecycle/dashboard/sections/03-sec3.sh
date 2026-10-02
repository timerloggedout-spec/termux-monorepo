#!/usr/bin/env bash
echo "[ BANKS — memory_units count per bank ]"
if [ -n "$PSQL" ]; then
  "$PSQL" -tA -c "SELECT bank_id || '  facts=' || count(*) FROM memory_units GROUP BY bank_id ORDER BY count(*) DESC LIMIT 15;" 2>&1 | sed 's/^/  /'
  echo "  --- 5 most recent ---"
  "$PSQL" -tA -c "SELECT to_char(created_at,'HH24:MI:SS') || '  ' || bank_id || '  ' || left(context,60) FROM memory_units ORDER BY created_at DESC LIMIT 5;" 2>&1 | sed 's/^/  /'
fi

echo
