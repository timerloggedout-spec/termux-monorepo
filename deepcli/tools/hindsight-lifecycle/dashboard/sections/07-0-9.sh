#!/usr/bin/env bash
echo "[ MVT SEED — last 8 batch outcomes ]"
grep -oE 'batch #[0-9]+ -> HTTP [0-9]+' /tmp/mvt-seed.log 2>/dev/null | tail -8 | sed 's/^/  /'
grep -c 'local timeout' /tmp/mvt-seed.log 2>/dev/null | sed 's/^/  timeouts: /'

echo
