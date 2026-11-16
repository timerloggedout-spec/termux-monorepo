#!/bin/bash
# Unit 062 verification: structure stories + element.sh exact-output flows.
set -e
cd "$(dirname "$0")"

psql -d periodic_table -v ON_ERROR_STOP=1 -f verify.sql

check() {
  desc="$1"; expected="$2"; shift 2
  out=$("$@")
  if [ "$out" = "$expected" ]; then echo "OK: $desc"; else echo "FAIL: $desc"; echo "  expected: $expected"; echo "  actual:   $out"; exit 1; fi
}

H_LINE="The element with atomic number 1 is Hydrogen (H). It's a nonmetal, with a mass of 1.008 amu. Hydrogen has a melting point of -259.1 celsius and a boiling point of -252.9 celsius."
check "no argument" "Please provide an element as an argument." ./element.sh
check "by number" "$H_LINE" ./element.sh 1
check "by symbol" "$H_LINE" ./element.sh H
check "by name" "$H_LINE" ./element.sh Hydrogen
check "fluorine" "The element with atomic number 9 is Fluorine (F). It's a nonmetal, with a mass of 18.998 amu. Fluorine has a melting point of -220 celsius and a boiling point of -188.1 celsius." ./element.sh 9
check "neon by symbol" "The element with atomic number 10 is Neon (Ne). It's a nonmetal, with a mass of 20.18 amu. Neon has a melting point of -248.6 celsius and a boiling point of -246.1 celsius." ./element.sh Ne
check "bogus element deleted" "I could not find that element in the database." ./element.sh 1000
check "unknown symbol" "I could not find that element in the database." ./element.sh Xx

[ -x files/element.sh ] || { echo "deliverable element.sh not executable"; exit 1; }
echo "VERIFY DONE"
