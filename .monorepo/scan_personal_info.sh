#!/usr/bin/env bash
echo "=== Personal Information Scan ==="
echo "Emails:"
git ls-files | xargs grep -E -n "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" 2>/dev/null | head -20
echo "Phone numbers (US):"
git ls-files | xargs grep -E -n "\([0-9]{3}\) [0-9]{3}-[0-9]{4}|[0-9]{3}-[0-9]{3}-[0-9]{4}" 2>/dev/null | head -20
echo "Keywords (timerloggedout, spec, Caveman, ArchWiz):"
git ls-files | xargs grep -E -n "timerloggedout|spec|Dumas|tallah|UC Davis|UCD|*Gmail*|phone|c.|Nicholas|D'Artagnan" 2>/dev/null | head -20
