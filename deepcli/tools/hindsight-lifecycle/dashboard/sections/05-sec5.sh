#!/usr/bin/env bash
echo "[ OPENROUTER QUOTA — live ]"
_or=$(tr '\0' '\n' < /proc/$(pgrep -f 'hindsight-api --port 8888' | head -1)/environ 2>/dev/null | grep '^OPENROUTER_API_KEY=' | cut -d= -f2-)
if [ -n "$_or" ]; then
  curl -sS --max-time 8 -H "Authorization: Bearer $_or" https://openrouter.ai/api/v1/auth/key 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin).get('data') or {}
    rl = d.get('rate_limit') or {}
    print('  label=' + str(d.get('label', '?')) + '  tier=' + str(d.get('tier', '?')))
    print('  limit=' + str(d.get('limit', 'unlimited')) + '  usage=' + str(d.get('usage', '0')) + '  remaining=' + str(d.get('limit_remaining', 'inf')))
    print('  rpm=' + str(rl.get('requests', '?')) + '  interval=' + str(rl.get('interval', '?')))
except Exception as e:
    print('  err:', e)
"
  curl -sS --max-time 8 -H "Authorization: Bearer $_or" https://openrouter.ai/api/v1/credits 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin).get('data') or {}
    print('  credits_total=' + str(d.get('total_credits', '?')) + '  credits_used=' + str(d.get('total_usage', '?')))
except Exception:
    pass
"
  echo "  --- OR models seen in llm_requests ---"
  if [ -n "$PSQL" ]; then
    "$PSQL" -tA -c "SELECT '    ' || coalesce(model,'?') || '  calls=' || count(*) FROM llm_requests WHERE model ILIKE '%llama%' OR model ILIKE '%qwen%' OR model ILIKE '%oss%' OR model ILIKE '%openrouter%' GROUP BY model ORDER BY count(*) DESC LIMIT 10;" 2>&1
  fi
else
  echo "  no OPENROUTER_API_KEY in :8888 env"
fi

echo
