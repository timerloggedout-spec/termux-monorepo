#!/usr/bin/env bash
echo "[ QUOTA — token usage per model (from llm_requests) ]"
if [ -n "$PSQL" ]; then
  "$PSQL" -tA -c "SELECT '  ' || coalesce(model,'?') || '  calls=' || count(*) || '  in=' || coalesce(sum(input_tokens),0) || '  out=' || coalesce(sum(output_tokens),0) FROM llm_requests WHERE started_at > now() - interval '24 hours' GROUP BY model ORDER BY count(*) DESC;" 2>&1
  echo "  (today UTC)"
  "$PSQL" -tA -c "SELECT '  ' || coalesce(model,'?') || '  calls=' || count(*) || '  in=' || coalesce(sum(input_tokens),0) || '  out=' || coalesce(sum(output_tokens),0) FROM llm_requests WHERE started_at > date_trunc('day', now()) GROUP BY model ORDER BY count(*) DESC;" 2>&1
fi

echo
