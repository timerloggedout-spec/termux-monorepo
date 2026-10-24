#!/usr/bin/env bash
# @section INTEGRITY
# @owner collaborator
# @depends db|env
set -u
echo
echo "=== [ INTEGRITY ] ==="
failed=0
if [ -z "${PSQL:-}" ]; then
 echo "  database:        unavailable (required)" >&2
 failed=1
else
 if stale="$("$PSQL" -X -v ON_ERROR_STOP=1 -tAc "SELECT count(*) FROM memory_units WHERE bank_id='deepagent::termux-monorepo'" 2>/dev/null)"; then
  printf "  stale-bank facts: %s\n" "$stale"
 else
  echo "  stale-bank facts: unavailable (required database query failed)" >&2
  failed=1
 fi
 if deep="$("$PSQL" -X -v ON_ERROR_STOP=1 -tAc "SELECT count(*) FROM banks WHERE bank_id LIKE 'deepagent::%'" 2>/dev/null)"; then
  printf "  deepagent banks:  %s\n" "$deep"
 else
  echo "  deepagent banks:  unavailable (required database query failed)" >&2
  failed=1
 fi
fi
[ -f /tmp/purge-stale.sql ] && echo "  stale-purge:     staged" || echo "  stale-purge:     MISSING"
[ -f /tmp/hs-stack/active.json ] && [ -f /tmp/hs-stack/state.json ] && echo "  stack state:     present" || echo "  stack state:     incomplete"
exit "$failed"
