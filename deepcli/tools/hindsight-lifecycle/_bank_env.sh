#!/usr/bin/env bash
for p in 8888 8889; do
  pid=$(pgrep -f "hindsight-api --port $p" | head -1)
  [ -z "$pid" ] && { echo ":$p DEAD"; continue; }
  v=$(tr '\0' '\n' < /proc/$pid/environ | grep '^HINDSIGHT_BANK_ID=' | cut -d= -f2-)
  echo ":$p pid=$pid bank_id=${v:-<unset>}"
done
