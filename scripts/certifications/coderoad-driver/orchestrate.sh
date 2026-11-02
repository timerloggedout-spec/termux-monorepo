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

# Deterministic pre-setup (do not rely on extension setup hooks):
# start PostgreSQL and install the .freeCodeCamp test harness deps.
{
  echo "== pre-setup =="
  pg_lsclusters 2>&1 || true
  service postgresql start 2>&1 || pg_ctlcluster 12 main start 2>&1 || \
    su postgres -c '/usr/lib/postgresql/12/bin/pg_ctl -D /var/lib/postgresql/12/main -l /tmp/pg.log start' 2>&1 || true
  sleep 3
  pg_isready 2>&1 || true
  if [ -d /workspace/project/.freeCodeCamp ] && [ -f /workspace/project/.freeCodeCamp/package.json ]; then
    (cd /workspace/project/.freeCodeCamp && npm install --no-audit --no-fund 2>&1 | tail -3) || true
    ls /workspace/project/.freeCodeCamp/node_modules 2>/dev/null | head -3 || echo "node_modules absent"
  else
    echo "no .freeCodeCamp/package.json — harness is not npm-based for this course; skipping npm install"
  fi
} >> "$LOG" 2>&1

# Launch VS Code (CodeRoad activates on the .freeCodeCamp workspace and
# auto-loads the tutorial from CODEROAD_TUTORIAL_URL). Electron in a bare
# container needs a D-Bus session + XDG_RUNTIME_DIR; without them the main
# process spins and dies (pilot 8: all code processes defunct, no exthost).
export XDG_RUNTIME_DIR=/tmp/runtime-root
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
# GH-hosted runner kernels are Azure/Microsoft builds: /proc/version matches
# the bin/code script's WSL check, which prompts on stdin and exits on EOF.
export DONT_PROMPT_WSL_INSTALL=1
# Fresh user-data-dir per run: the image bakes build-time state into
# "$UD" (a CLI session's state.vscdb + logs); pilot 11's GUI
# session wrote main.log but never opened a window / started exthost —
# baked state is the prime suspect. UD is exported for the probes below.
export UD=/tmp/vscode-ud-run
mkdir -p "$UD"
(dbus-run-session -- xvfb-run -a code --no-sandbox --user-data-dir "$UD" --disable-gpu --disable-dev-shm-usage \
  --extensions-dir /opt/vscode-extensions \
  /workspace/project > "$EV/code.log" 2>&1 &)
echo "code launched" >> "$LOG"

# Wait for the environment: PostgreSQL accepting connections (pre-setup
# started it; CodeRoad setup hooks may add more, but pg is the hard gate).
ready=0
for i in $(seq 1 24); do
  if pg_isready -q 2>/dev/null; then
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
# proves the staged state independently of the CodeRoad run). Only for
# npm-harness courses; this course family drives tests from tutorial.json.
if [ -f /workspace/project/.freeCodeCamp/package.json ]; then
  (cd /workspace/project/.freeCodeCamp && npm run programmatic-test \
    > "$EV/tap-direct.txt" 2>&1; echo "direct mocha rc=$?" >> "$LOG") || true
else
  echo "direct mocha skipped (no package.json)" >> "$LOG"
fi

# Raise GO: the driver extension fires coderoad.run_test.
touch "$EV/GO"
echo "GO raised" >> "$LOG"

# Post-launch probes: prove VS Code + extensions actually came up and find
# CodeRoad's REAL session storage (the env-path guess is uncalibrated).
sleep 25
{
  echo "== probes =="
  cat /proc/version || true
  which dbus-run-session xvfb-run || true
  ls /opt/vscode-extensions 2>/dev/null || true
  ps aux | grep -iE "code|electron" | grep -v grep | head -8
  code --no-sandbox --user-data-dir "$UD" --extensions-dir /opt/vscode-extensions --list-extensions 2>&1 | head -10
  echo "-- globalStorage tree --"
  find "$UD"/User/globalStorage -maxdepth 2 2>/dev/null | head -30
  echo "-- coderoad-ish files --"
  find "$UD" /root/.config -iname "*coderoad*" 2>/dev/null | head -20
  echo "-- logs + User trees --"
  ls -R "$UD"/logs 2>/dev/null | head -30 || echo "(no logs dir)"
  find "$UD"/User -maxdepth 3 2>/dev/null | head -30
  echo "-- GUI session main.log tail --"
  for d in "$UD"/logs/*/; do
    [ -f "$d/main.log" ] && { echo "## $d"; tail -30 "$d/main.log"; }
  done
  echo "-- newest exthost log tail --"
  newest=$(ls -t "$UD"/logs/*/window*/exthost/exthost.log 2>/dev/null | head -1)
  [ -n "$newest" ] && tail -25 "$newest" || echo "(no exthost log found)"
} > "$EV/session-files.txt" 2>&1 || true

# If no live code process survived, capture a foreground launch's output
# verbatim (the backgrounded launch's code.log has been empty every pilot).
if ! pgrep -f "VSCode-linux-x64/code" > /dev/null 2>&1; then
  timeout 15 dbus-run-session -- xvfb-run -a code --no-sandbox --user-data-dir "$UD" \
    --disable-gpu --disable-dev-shm-usage --extensions-dir /opt/vscode-extensions \
    /workspace/project > "$EV/code-fg.txt" 2>&1 || true
fi

for i in $(seq 1 72); do
  [ -f "$EV/RESULT.json" ] && break
  sleep 5
done
if [ -f "$EV/RESULT.json" ]; then
  cat "$EV/RESULT.json"
else
  echo '{"ok":false,"detail":"driver RESULT timeout"}' | tee "$EV/RESULT.json"
fi
