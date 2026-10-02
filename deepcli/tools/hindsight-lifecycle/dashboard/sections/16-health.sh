#!/usr/bin/env bash
echo "[ HEALTH ]"
for p in 8888 8889; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 4 http://localhost:$p/health 2>/dev/null || echo 000)
  echo "  :$p /health = $code"
done
echo "$BAR"