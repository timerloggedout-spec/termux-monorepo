#!/bin/bash
# Unit 063 (Number Guessing Game) fleet build: recreate the database from
# the deliverable number_guess.sql and stage number_guess.sh.
set -e
cd "$(dirname "$0")"

psql -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS number_guess"
psql -d postgres -v ON_ERROR_STOP=1 -c "CREATE ROLE freecodecamp LOGIN SUPERUSER" || true
psql -d postgres -v ON_ERROR_STOP=1 -f files/number_guess.sql

cp files/number_guess.sh .
chmod +x number_guess.sh
echo "BUILD DONE"
