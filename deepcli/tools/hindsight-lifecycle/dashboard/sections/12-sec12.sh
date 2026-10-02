#!/usr/bin/env bash
echo "[ BATCH PLAN — dynamic ]"
python3 /tmp/hs-batch-plan.py --verbose 2>/dev/null | sed 's/^/  /'

echo
