#!/usr/bin/env bash
# @section TEMPLATE
# @owner yourhandle
# @depends db
# Copy this file to NN-yourname.sh and edit.
echo
echo "=== [ YOUR SECTION ] ==="
[ -n "${PSQL:-}" ] || { echo "  database:  unavailable (required)" >&2; exit 1; }
"$PSQL" -X -v ON_ERROR_STOP=1 -tA -c "SELECT '  sample: ' || count(*) FROM memory_units;" 2>/dev/null || {
 echo "  query:     unavailable (required database query failed)" >&2
 exit 1
}
