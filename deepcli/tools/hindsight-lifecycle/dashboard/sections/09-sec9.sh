#!/usr/bin/env bash
echo "[ RECENT ERRORS — llm_requests (1h) ]"
if [ -n "$PSQL" ]; then
  "$PSQL" -tA -c "SELECT '  ' || to_char(started_at,'HH24:MI:SS') || '  ' || provider || '  ' || model || '  ' || status || '  ' || coalesce(duration_ms::text,'?') || 'ms  ' || coalesce(substring(error,1,60),'-') FROM llm_requests WHERE started_at > now() - interval '1 hour' AND status != 'success' ORDER BY started_at DESC LIMIT 10;" 2>&1 || echo "  (none)"
fi

echo
