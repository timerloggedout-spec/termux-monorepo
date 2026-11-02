#!/usr/bin/env bash
# Host-side orchestration for the CodeRoad completion run (route B).
# VS Code runs on the Actions runner host (modern userland); PostgreSQL
# runs in the prebuilt coderoad image as a container named pg with 5432
# published and the workspace mounted at /workspace/project (path parity
# with the course env). Env in: STAGE_CMD (executed INSIDE the pg
# container), CODEROAD_* contract set, GITHUB_WORKSPACE.
set -u
EV="$GITHUB_WORKSPACE/evidence"
mkdir -p "$EV"
LOG="$EV/orchestrate.log"
: > "$LOG"
WS="$GITHUB_WORKSPACE/project"

# --- PostgreSQL container: course pg_hba in place, service up ----------
docker rm -f pg > /dev/null 2>&1 || true
docker run -d --name pg \
  -p 5432:5432 \
  -v "$WS:/workspace/project" \
  -v "$GITHUB_WORKSPACE/solution:/solution:ro" \
  coderoad:local sleep infinity >> "$LOG" 2>&1
docker exec pg bash -c '
  sed -i -E "s/^(host[[:space:]]+all[[:space:]]+all[[:space:]]+(127.0.0.1\/32|::1\/128)[[:space:]]+).*/\1trust/" /etc/postgresql/12/main/pg_hba.conf
  grep -E "^host" /etc/postgresql/12/main/pg_hba.conf
  service postgresql start || pg_ctlcluster 12 main start
' >> "$LOG" 2>&1
for i in $(seq 1 24); do
  if docker exec pg pg_isready -q 2>/dev/null; then
    echo "pg ready after ~$((i*5))s" >> "$LOG"; break
  fi
  sleep 5
done
docker exec pg pg_isready >> "$LOG" 2>&1 || true

# --- Harness deps on host (CodeRoad setup would run this too) -----------
if [ -f "$WS/.freeCodeCamp/package.json" ]; then
  (cd "$WS/.freeCodeCamp" && npm install --no-audit --no-fund 2>&1 | tail -3) >> "$LOG" 2>&1 || true
fi

# --- sudo shim: setup.sh's host-mutating lines no-op (logged) -----------
SHIM="$HOME/shim"
mkdir -p "$SHIM"
cat > "$SHIM/sudo" <<'SHIMEOF'
#!/usr/bin/env bash
echo "sudo-shim: $*" >> "$HOME/shim.log"
case "$*" in
  *service*postgresql*|*pg_hba.conf*|*postgresql/12/main*|*"/workspace/.bash_history"*)
    exit 0 ;;
  *)
    exec /usr/bin/sudo "$@" ;;
esac
SHIMEOF
chmod 755 "$SHIM/sudo"

# --- VS Code launch (host) ----------------------------------------------
UD="$HOME/vsud"
mkdir -p "$UD/User"
cat > "$UD/User/settings.json" <<'JSON'
{"workbench.startupEditor": "none", "window.restoreWindows": "none",
 "update.mode": "none", "telemetry.telemetryLevel": "off",
 "extensions.autoUpdate": false, "extensions.autoCheckUpdates": false,
 "workbench.enableExperiments": false, "git.enabled": false}
JSON
export XDG_RUNTIME_DIR="$HOME/runtime-dir"
mkdir -p "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
export DONT_PROMPT_WSL_INSTALL=1
CODE="$HOME/vscode/VSCode-linux-x64/bin/code"
LAUNCH=(xvfb-run -a -s "-screen 0 1024x768x24" "$CODE" --no-sandbox
  --user-data-dir "$UD" --disable-gpu --disable-dev-shm-usage
  --disable-workspace-trust --enable-logging=stderr --v=1
  --extensions-dir "$HOME/vscode-extensions" "$WS")
(PATH="$SHIM:$PATH" "${LAUNCH[@]}" > "$EV/code.log" 2>&1 &)
echo "code launched (host)" >> "$LOG"

# --- Stage the verified solution inside the pg container -----------------
docker exec pg bash -c "$STAGE_CMD" > "$EV/stage.log" 2>&1
echo "stage rc=$?" >> "$LOG"

# Direct mocha run as a diagnostic (host, against container postgres).
if [ -f "$WS/.freeCodeCamp/package.json" ]; then
  (cd "$WS/.freeCodeCamp" && npm run programmatic-test \
    > "$EV/tap-direct.txt" 2>&1; echo "direct mocha rc=$?" >> "$LOG") || true
fi

# --- GO + RESULT wait with relaunch watchdog -----------------------------
touch "$EV/GO"
echo "GO raised" >> "$LOG"
sleep 25
{ ps aux | grep -iE "xvfb|code|electron" | grep -v grep | head -8; free -m | head -2; } \
  > "$EV/session-early.txt" 2>&1 || true
relaunches=0
for i in $(seq 1 72); do
  [ -f "$EV/RESULT.json" ] && break
  if ! pgrep -f "VSCode-linux-x64/code" > /dev/null 2>&1 && [ $relaunches -lt 4 ]; then
    relaunches=$((relaunches+1))
    echo "watchdog: code tree dead; relaunch #$relaunches" >> "$LOG"
    (PATH="$SHIM:$PATH" "${LAUNCH[@]}" >> "$EV/code.log" 2>&1 &)
    sleep 20
  fi
  sleep 5
done
echo "watchdog relaunches=$relaunches" >> "$LOG"

# --- End-of-run probes -----------------------------------------------------
{
  echo "== probes (end of run, host) =="
  cat /proc/version || true
  ls "$HOME/vscode-extensions" 2>/dev/null || true
  ps aux | grep -iE "xvfb|code|electron" | grep -v grep | head -10
  "$CODE" --no-sandbox --user-data-dir "$UD" --extensions-dir "$HOME/vscode-extensions" --list-extensions 2>&1 | head -10
  echo "-- globalStorage tree --"
  find "$UD/User/globalStorage" -maxdepth 2 2>/dev/null | head -30
  echo "-- coderoad-ish files --"
  find "$UD" "$HOME/.config" -iname "*coderoad*" 2>/dev/null | head -20
  echo "-- logs + User trees --"
  ls -R "$UD/logs" 2>/dev/null | head -40 || echo "(no logs dir)"
  find "$UD/User" -maxdepth 3 2>/dev/null | head -30
  echo "-- GUI session main.log tails --"
  for d in "$UD"/logs/*/; do
    [ -f "$d/main.log" ] && { echo "## $d"; tail -15 "$d/main.log"; }
  done
  echo "-- newest exthost log tail --"
  newest=$(ls -t "$UD"/logs/*/window*/exthost/exthost.log 2>/dev/null | head -1)
  [ -n "$newest" ] && tail -25 "$newest" || echo "(no exthost log found)"
} > "$EV/session-files.txt" 2>&1 || true

if [ -f "$EV/RESULT.json" ]; then
  cat "$EV/RESULT.json"
else
  echo '{"ok":false,"detail":"driver RESULT timeout"}' | tee "$EV/RESULT.json"
fi
