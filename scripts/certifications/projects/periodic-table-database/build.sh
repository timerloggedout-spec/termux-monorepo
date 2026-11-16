#!/bin/bash
# Unit 062 (Periodic Table) fleet build: recreate the database from the
# deliverable periodic_table.sql and stage element.sh.
set -e
cd "$(dirname "$0")"

psql -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS periodic_table"
psql -d postgres -v ON_ERROR_STOP=1 -c "CREATE ROLE freecodecamp LOGIN SUPERUSER" || true
psql -d postgres -v ON_ERROR_STOP=1 -f files/periodic_table.sql

cp files/element.sh .
chmod +x element.sh
echo "BUILD DONE"
