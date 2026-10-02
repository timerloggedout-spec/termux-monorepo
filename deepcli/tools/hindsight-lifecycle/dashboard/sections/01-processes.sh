#!/usr/bin/env bash
echo "[ PROCESSES ]"
for pat in 'hindsight-api --port 8888' 'hindsight-api --port 8889' 'hs-stack.py watch' 'sovereign-run.sh' 'mvt-seed.py'; do
  pid=$(pgrep -f "$pat" | head -1)
  if [ -n "$pid" ]; then
    up=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ')
    printf "  %-28s pid=%-7s up=%s\n" "$pat" "$pid" "$up"
  else
    printf "  %-28s DEAD\n" "$pat"
  fi
done

echo
