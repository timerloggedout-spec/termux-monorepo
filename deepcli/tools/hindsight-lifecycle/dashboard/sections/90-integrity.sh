#!/usr/bin/env bash
# @section INTEGRITY
# @owner collaborator
# @depends db|env
set -u
echo
echo "=== [ INTEGRITY ] ==="
if [ -n "${PSQL:-}" ]; then
 stale="$("$PSQL" -tAc "SELECT count(*) FROM memory_units WHERE bank_id='deepagent::termux-monorepo'" 2>/dev/null || echo '?')"
 printf "  stale-bank facts: %s\n" "$stale"
 deep="$("$PSQL" -tAc "SELECT count(*) FROM banks WHERE bank_id LIKE 'deepagent::%'" 2>/dev/null || echo '?')"
 printf "  deepagent banks:  %s\n" "$deep"
fi
[ -f /tmp/purge-stale.sql ] && echo "  stale-purge:     staged" || echo "  stale-purge:     MISSING"
[ -f /tmp/hs-stack/active.json ] && [ -f /tmp/hs-stack/state.json ] && echo "  stack state:     present" || echo "  stack state:     incomplete"
