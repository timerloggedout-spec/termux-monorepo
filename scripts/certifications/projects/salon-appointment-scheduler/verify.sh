#!/bin/bash
# Unit 040 verification: structure stories, then the course's own scripted
# flows (new customer, returning customer, unknown service re-list).
set -e
cd "$(dirname "$0")"

psql -d salon -v ON_ERROR_STOP=1 -f verify.sql

# Flow 1: new customer books service 1
OUT1=$(printf "1\n555-555-5555\nFabio\n10:30\n" | ./salon.sh)
echo "$OUT1"
echo "$OUT1" | grep -q "I have put you down for a cut at 10:30, Fabio." || { echo "FLOW1 FAIL: confirmation"; exit 1; }

# Flow 2: returning customer books service 2 (no name prompt)
OUT2=$(printf "2\n555-555-5555\n11am\n" | ./salon.sh)
echo "$OUT2"
echo "$OUT2" | grep -q "I have put you down for a color at 11am, Fabio." || { echo "FLOW2 FAIL: confirmation"; exit 1; }

# Flow 3: unknown service id re-lists, then books service 2
OUT3=$(printf "10\n2\n555-555-5555\n12:00\n" | ./salon.sh)
echo "$OUT3"
echo "$OUT3" | grep -q "I could not find that service. What would you like today?" || { echo "FLOW3 FAIL: re-list"; exit 1; }
echo "$OUT3" | grep -q "I have put you down for a color at 12:00, Fabio." || { echo "FLOW3 FAIL: confirmation"; exit 1; }

n=$(psql -d salon -t --no-align -c "SELECT count(*) FROM appointments a JOIN customers c ON c.customer_id=a.customer_id WHERE c.phone='555-555-5555'")
echo "appointments for Fabio: $n"
[ "$n" = "3" ] || { echo "APPOINTMENT COUNT FAIL"; exit 1; }

[ -x files/salon.sh ] || { echo "deliverable salon.sh not executable"; exit 1; }
echo "VERIFY DONE"
