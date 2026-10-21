#!/usr/bin/env bash
# @section TEMPLATE
# @owner yourhandle
# @depends db
# Copy this file to NN-yourname.sh and edit.
echo
echo "=== [ YOUR SECTION ] ==="
if [ -n "${PSQL:-}" ]; then
  "$PSQL" -tA -c "SELECT '  sample: ' || count(*) FROM memory_units;" 2>&1
fi
