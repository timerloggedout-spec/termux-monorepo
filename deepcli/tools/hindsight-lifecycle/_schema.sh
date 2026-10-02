#!/usr/bin/env bash
P=/home/vscode/.pg0/installation/18.1.0/bin/psql
export PGPASSWORD=hindsight
echo "--- observation_history columns ---"
$P -h /tmp -U hindsight -d hindsight -tAc "SELECT column_name || ':' || data_type FROM information_schema.columns WHERE table_name='observation_history' ORDER BY ordinal_position;"
echo
echo "--- memory_links columns ---"
$P -h /tmp -U hindsight -d hindsight -tAc "SELECT column_name || ':' || data_type FROM information_schema.columns WHERE table_name='memory_links' ORDER BY ordinal_position;"
