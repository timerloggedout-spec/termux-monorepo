#!/usr/bin/env bash
set -u
# Get HINDSIGHT env from the running API (local)
p=$(pgrep -f 'hindsight-api --port 8888' | head -1)
[ -z "$p" ] && { echo "no api"; exit 1; }
export HINDSIGHT_API_KEY=$(tr '\0' '\n' < /proc/$p/environ | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)
export HINDSIGHT_BASE_URL="http://localhost:8888"
export HINDSIGHT_BANK_ID="termux-monorepo::primary"
echo "env: base=$HINDSIGHT_BASE_URL bank=$HINDSIGHT_BANK_ID"
echo "--- count before ---"
psql() { /home/vscode/.pg0/installation/18.1.0/bin/psql -h /tmp -U hindsight -d hindsight -tAc "$1"; }
PGPASSWORD=hindsight psql "SELECT count(*) FROM memory_units WHERE bank_id='termux-monorepo::primary' AND metadata->>'origin'='deepagent'"

echo "--- invoke deepagent ---"
cd ~/deepcli
timeout 90 python3 agent_hindsight.py 2>/dev/null || true
python3 -c "
import sys, os
sys.path.insert(0, '/home/vscode/deepcli')
os.environ.setdefault('HINDSIGHT_BASE_URL', 'http://localhost:8888')
os.environ.setdefault('HINDSIGHT_BANK_ID', 'termux-monorepo::primary')
from agent_hindsight import retain
r = retain('DeepAgent e2e test: synthetic task completed, closing the loop',
           metadata={'origin':'deepagent','event':'finish','task':'e2e-test'})
print('retain:', r)
"
echo "--- count after ---"
PGPASSWORD=hindsight psql "SELECT count(*) FROM memory_units WHERE bank_id='termux-monorepo::primary' AND metadata->>'origin'='deepagent'"
