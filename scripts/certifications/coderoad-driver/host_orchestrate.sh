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
  printf "\nhost all all 0.0.0.0/0 trust\n" >> /etc/postgresql/12/main/pg_hba.conf
  sed -i -E "s/^#?listen_addresses.*/listen_addresses = '\''*'\''/" /etc/postgresql/12/main/postgresql.conf
  grep -E "^host|^listen" /etc/postgresql/12/main/pg_hba.conf /etc/postgresql/12/main/postgresql.conf | tail -6
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
CODE="$HOME/vscode/VSCode-linux-x64/code"
LAUNCH=(xvfb-run -a -s "-screen 0 1024x768x24" "$CODE" --no-sandbox
  --user-data-dir "$UD" --disable-gpu --disable-dev-shm-usage
  --disable-workspace-trust
  --extensions-dir "$HOME/vscode-extensions" "$WS")
(PATH="$SHIM:$PATH" NODE_OPTIONS=--dns-result-order=ipv4first "${LAUNCH[@]}" > "$EV/code.log" 2>&1 &)
echo "code launched (host)" >> "$LOG"

# --- Stage the verified solution inside the pg container -----------------
docker exec pg bash -c "$STAGE_CMD" > "$EV/stage.log" 2>&1
echo "stage rc=$?" >> "$LOG"

# TCP probe from the host (the tests connect via localhost:5432 — B2's
# direct mocha died with ECONNRESET despite a healthy socket-side stage).
if [ -f "$WS/.freeCodeCamp/package.json" ]; then
  (cd "$WS/.freeCodeCamp" && node -e '
    const { Client } = require("pg");
    (async () => {
      for (const host of ["127.0.0.1", "::1", "localhost"]) {
        const c = new Client({ host, port: 5432, user: "postgres", database: "universe" });
        try { await c.connect(); const r = await c.query("select 1 as ok");
          console.log(host, "CONNECT OK", JSON.stringify(r.rows)); await c.end(); }
        catch (e) { console.log(host, "CONNECT FAIL", e.message); try { await c.end(); } catch (_) {} }
      }
    })();
  ' > "$EV/pg-probe.txt" 2>&1) || true
fi
docker exec pg bash -c 'tail -30 /var/log/postgresql/*.log' > "$EV/pg-container.log" 2>&1 || true
{ echo "== listeners on 5432 =="; ss -ltnp 2>/dev/null | grep 5432 || ss -ltn | grep 5432 || true
  echo "== docker port pg =="; docker port pg || true
  echo "== container IP connect =="
  CIP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pg 2>/dev/null)
  echo "container ip: $CIP"
  if [ -n "$CIP" ] && [ -f "$WS/.freeCodeCamp/package.json" ]; then
    (cd "$WS/.freeCodeCamp" && CIP="$CIP" node -e '
      const { Client } = require("pg");
      (async () => {
        const c = new Client({ host: process.env.CIP, port: 5432, user: "postgres", database: "universe" });
        try { await c.connect(); const r = await c.query("select 1 as ok");
          console.log("container-ip CONNECT OK", JSON.stringify(r.rows)); await c.end(); }
        catch (e) { console.log("container-ip CONNECT FAIL", e.message); }
      })();
    ') || true
  fi
} >> "$EV/pg-probe.txt" 2>&1 || true

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
    (PATH="$SHIM:$PATH" NODE_OPTIONS=--dns-result-order=ipv4first "${LAUNCH[@]}" >> "$EV/code.log" 2>&1 &)
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
  echo "-- exthost coderoad lines --"
  grep -i "coderoad" "$UD"/logs/*/window1/exthost/exthost.log 2>/dev/null | head -20 || echo "(none)"
  echo "-- extensions dir package names --"
  for d in "$HOME"/vscode-extensions/*/; do
    [ -f "$d/package.json" ] && echo "$d -> $(grep -o '"name": *"[^"]*"' "$d/package.json" | head -1)"
  done
  echo "-- newest exthost log tail --"
  newest=$(ls -t "$UD"/logs/*/window*/exthost/exthost.log 2>/dev/null | head -1)
  [ -n "$newest" ] && tail -25 "$newest" || echo "(no exthost log found)"
} > "$EV/session-files.txt" 2>&1 || true

# CodeRoad's own record: its output channel + the memento state DBs as text.
{
  echo "== output-channel files =="
  find "$UD/logs" -type f \( -iname "*coderoad*" -o -path "*output*" \) 2>/dev/null | head -10
  find "$UD/logs" -type f -iname "*coderoad*" -print0 2>/dev/null | while IFS= read -r -d '' f; do
    echo "== $f =="; tail -60 "$f"
  done
  for db in "$UD"/User/workspaceStorage/*/state.vscdb "$UD"/User/globalStorage/state.vscdb; do
    [ -f "$db" ] || continue
    echo "== strings $db (coderoad keys) =="
    strings "$db" 2>/dev/null | grep -o "coderoad:[a-zA-Z]*" | sort -u | head -20
    echo "== strings $db (complete/position context) =="
    strings "$db" 2>/dev/null | grep -i "\"complete\"\|currentPosition\|step_complete\|tutorial_complete" | head -15
  done
} > "$EV/coderoad-state.txt" 2>&1 || true

if [ -f "$EV/RESULT.json" ]; then
  cat "$EV/RESULT.json"
else
  echo '{"ok":false,"detail":"driver RESULT timeout"}' | tee "$EV/RESULT.json"
fi
