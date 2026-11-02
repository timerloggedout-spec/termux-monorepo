#!/bin/bash
# Unit 039 (World Cup) fleet build: rebuild both databases from the
# deliverable worldcup.sql, then load data with the deliverable
# insert_data.sh exactly as the course tests do (test + production modes).
set -e
cd "$(dirname "$0")"

psql -d postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS worldcup" -c "DROP DATABASE IF EXISTS worldcuptest"
psql -d postgres -v ON_ERROR_STOP=1 -c "CREATE ROLE freecodecamp LOGIN SUPERUSER" || true
psql -d postgres -v ON_ERROR_STOP=1 -f files/worldcup.sql
psql -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE worldcuptest TEMPLATE worldcup"

cp files/games.csv files/insert_data.sh files/queries.sh .
chmod +x insert_data.sh queries.sh

./insert_data.sh test
./insert_data.sh
echo "BUILD DONE"
