#!/bin/bash
# Unit 039 verification: structure stories, row counts in both databases,
# and queries.sh output diffed exactly against expected_output.txt.
set -e
cd "$(dirname "$0")"

psql -d worldcup -v ON_ERROR_STOP=1 -f verify.sql

for db in worldcup worldcuptest; do
  t=$(psql -d "$db" -t --no-align -c "SELECT count(*) FROM teams")
  g=$(psql -d "$db" -t --no-align -c "SELECT count(*) FROM games")
  echo "$db: teams=$t games=$g"
  [ "$t" = "24" ] && [ "$g" = "32" ] || { echo "COUNT FAIL for $db"; exit 1; }
done

./queries.sh > /tmp/queries-out.txt 2>&1
diff -u files/expected_output.txt /tmp/queries-out.txt
echo "QUERIES OUTPUT MATCHES expected_output.txt"

[ -x files/insert_data.sh ] && [ -x files/queries.sh ] || { echo "deliverable scripts not executable"; exit 1; }
echo "VERIFY DONE"
