#!/bin/bash
# Unit 040 (Salon) fleet build: recreate the salon database from the
# deliverable salon.sql and stage the deliverable salon.sh.
set -e
cd "$(dirname "$0")"

psql -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS salon"
psql -d postgres -v ON_ERROR_STOP=1 -c "CREATE ROLE freecodecamp LOGIN SUPERUSER" || true
psql -d postgres -v ON_ERROR_STOP=1 -f files/salon.sql

cp files/salon.sh .
chmod +x salon.sh
echo "BUILD DONE"
