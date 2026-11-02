#!/usr/bin/env bash
# In-container orchestration for the CodeRoad completion run.
# Runs inside the rdb-alpha + VS Code image (container user: root; the
# course setup script uses sudo throughout, which is a no-op there).
# Env in: STAGE_CMD (solution staging command), plus the CODEROAD_* set.
set -u
EV=/evidence
mkdir -p "$EV"
LOG="$EV/orchestrate.log"
: > "$LOG"

git config --global user.email "camper@example.com" 2>/dev/null
git config --global user.name "camper" 2>/dev/null
git config --global --add safe.directory /workspace/project 2>/dev/null

# Launch VS Code (CodeRoad activates on the .freeCodeCamp workspace and
# auto-loads the tutorial from CODEROAD_TUTORIAL_URL).
(xvfb-run -a code --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --extensions-dir /opt/vscode-extensions \
  /workspace/project > "$EV/code.log" 2>&1 &)
echo "code launched" >> "$LOG"

# Wait for CodeRoad's setup hooks: PostgreSQL accepting connections and the
# .freeCodeCamp dependencies installed.
ready=0
for i in $(seq 1 120); do
  if pg_isready -q 2>/dev/null && [ -d /workspace/project/.freeCodeCamp/node_modules ]; then
    ready=1; echo "setup ready after ~$((i*5))s" >> "$LOG"; break
  fi
  sleep 5
done
echo "setup_ready=$ready" >> "$LOG"
pg_isready >> "$LOG" 2>&1 || true
ls /workspace/project/.freeCodeCamp >> "$LOG" 2>&1 || true

# Stage the verified solution (e.g. load the project dump).
if [ -n "${STAGE_CMD:-}" ]; then
  eval "$STAGE_CMD" > "$EV/stage.log" 2>&1
  echo "stage rc=$?" >> "$LOG"
fi

# Direct mocha run as a diagnostic TAP artifact (not the credited path;
# proves the staged state independently of the CodeRoad run).
(cd /workspace/project/.freeCodeCamp && npm run programmatic-test \
  > "$EV/tap-direct.txt" 2>&1; echo "direct mocha rc=$?" >> "$LOG") || true

# Raise GO: the driver extension fires coderoad.run_test.
touch "$EV/GO"
echo "GO raised" >> "$LOG"

for i in $(seq 1 72); do
  [ -f "$EV/RESULT.json" ] && break
  sleep 5
done
if [ -f "$EV/RESULT.json" ]; then
  cat "$EV/RESULT.json"
else
  echo '{"ok":false,"detail":"driver RESULT timeout"}'
fi
