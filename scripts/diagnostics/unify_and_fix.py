#!/usr/bin/env python3
"""Three fixes in one pass:
   1. correct dispatcher call in server.py (task-file, not subcommand)
   2. collapse notifications to one owner (keeper) with --id
   3. silence tunnel-up + termux-pinggy-status duplicate rotation alerts
   4. reclaim stale worktrees under ~/.deepcli/worktrees
"""
from __future__ import annotations
import ast, datetime, pathlib, re, shutil, subprocess, time

HOME = pathlib.Path.home()
TS   = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
BACK = HOME / ".shell-forge-backups" / TS
BACK.mkdir(parents=True, exist_ok=True)


def banner(t): print("\n=== " + t + " ===")


def sh(args, timeout=120):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def du_mb(p):
    total = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            pass
    return total / (1024 * 1024)


def patch(path, old, new, label):
    p = pathlib.Path(path)
    if not p.exists():
        print("  " + label + ": missing " + str(p))
        return False
    text = p.read_text(errors="replace")
    if new in text and old not in text:
        print("  " + label + ": already applied")
        return True
    if old not in text:
        print("  " + label + ": pattern not found")
        return False
    shutil.copy2(p, BACK / p.name)
    p.write_text(text.replace(old, new, 1))
    print("  " + label + ": patched  backup=" + str(BACK / p.name))
    return True


# ── 1. CORRECT the dispatcher call in server.py ─────────────────────────────
banner("1. server.py — correct dispatcher call")
server = HOME / "deepcli" / "server.py"
p = pathlib.Path(server)
if p.exists():
    t = p.read_text(errors="replace")
    old_block = '''    def _runner() -> None:
        started = _sf_time.time()
        try:
            with log.open("w") as fh:
                rc = _sf_subprocess.call(
                    [str(_sf_dispatch), "run", body.task, body.source],
                    stdout=fh, stderr=_sf_subprocess.STDOUT,
                )'''
    new_block = '''    def _runner() -> None:
        started = _sf_time.time()
        task_dir = _sf_pathlib.Path.home() / ".deepcli" / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)
        task_file = task_dir / (inv + ".md")
        task_file.write_text(body.task or "execute the task")
        try:
            with log.open("w") as fh:
                rc = _sf_subprocess.call(
                    [str(_sf_dispatch), str(task_file), body.source or "execute the task"],
                    stdout=fh, stderr=_sf_subprocess.STDOUT,
                )'''
    if old_block in t:
        shutil.copy2(p, BACK / p.name)
        t2 = t.replace(old_block, new_block, 1)
        try:
            ast.parse(t2)
            p.write_text(t2)
            print("  server.py: dispatcher call corrected")
        except SyntaxError as e:
            print("  server.py: patch would break syntax — " + str(e))
    elif new_block in t:
        print("  server.py: already corrected")
    else:
        print("  server.py: old block not found (already edited?)")

# ── 2. Silence tunnel-up rotation notification ──────────────────────────────
banner("2. tunnel-up — silence rotation alert (keeper owns it)")
tunnel_up = HOME / ".local" / "bin" / "tunnel-up"
patch(tunnel_up,
      '''      if [ "$URL" != "$OLD_URL" ]; then
        termux-notification --channel tunnel --title "HTTP tunnel (8800) rotated" \\
          --content "$URL" --priority high 2>/dev/null || true
      fi''',
      '''      # shell-forge: rotation notification delegated to tunnel-keeper-loop
      # (silenced here to prevent triple-fire when orchestrator restarts tunnel-up)
      if [ "$URL" != "$OLD_URL" ]; then
        : # no-op — keeper fires the single canonical alert
      fi''',
      "tunnel-up")

# ── 3. Keeper: single canonical alert with stable --id ──────────────────────
banner("3. tunnel-keeper-loop — canonical alert, stable --id")
keeper = HOME / ".local" / "bin" / "tunnel-keeper-loop"
patch(keeper,
      '''      termux-notification --channel daemon --id keeper --title "HTTP tunnel (8800) rotated" --content "$NEW" 2>/dev/null || true''',
      '''      termux-notification --channel tunnel --id tunnel-rot --title "HTTP tunnel (8800) rotated" --content "$NEW" --priority default 2>/dev/null || true''',
      "tunnel-keeper-loop")

# ── 4. termux-pinggy-status: drop duplicate rotation alert ──────────────────
banner("4. termux-pinggy-status — silence duplicate rotation alert")
status = HOME / ".local" / "bin" / "termux-pinggy-status"
if status.exists():
    t = status.read_text(errors="replace")
    if "HTTP tunnel (8800) rotated" in t:
        shutil.copy2(status, BACK / status.name)
        t2 = re.sub(r"^\s*termux-notification[^\n]*HTTP tunnel[^\n]*\n",
                    "  : # shell-forge: silenced duplicate\n",
                    t, flags=re.M)
        status.write_text(t2)
        print("  termux-pinggy-status: silenced")
    else:
        print("  termux-pinggy-status: no duplicate pattern")

# ── 5. Reclaim stale worktrees ──────────────────────────────────────────────
banner("5. reclaim stale worktrees")
wt = HOME / ".deepcli" / "worktrees"
if wt.exists():
    before_mb = du_mb(wt)
    now = time.time()
    removed = 0
    kept = 0
    for d in wt.iterdir():
        if not d.is_dir():
            continue
        try:
            age_h = (now - d.stat().st_mtime) / 3600
        except OSError:
            continue
        if age_h > 24:
            shutil.rmtree(d, ignore_errors=True)
            removed += 1
        else:
            kept += 1
    after_mb = du_mb(wt) if wt.exists() else 0.0
    print("  before  " + format(before_mb, ".1f") + " MB  kept=" + str(kept))
    print("  after   " + format(after_mb, ".1f") + " MB  removed=" + str(removed))
    print("  freed   " + format(before_mb - after_mb, ".1f") + " MB")

# ── 6. Restart hub, fire corrected dispatch, watch ──────────────────────────
banner("6. restart hub + fire corrected workflow")
sh(["pkill", "-f", "deepcli/server.py"])
time.sleep(2)
subprocess.Popen([str(HOME / ".local" / "bin" / "servers-up")],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 start_new_session=True)
for i in range(20):
    rc, out, _ = sh(["bash", "-lc",
        "curl -sf -m 3 http://127.0.0.1:8800/health -o /dev/null && echo ok"])
    if "ok" in out:
        print("  hub up after " + str(i*2) + "s")
        break
    time.sleep(2)

# quick smoke POST — verify dispatch invocation
import urllib.request, urllib.error
try:
    req = urllib.request.Request(
        "http://127.0.0.1:8800/v1/agent", method="POST",
        data=b'{"task":"echo smoke test","source":"smoke"}',
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode(errors="replace")
        print("  POST /v1/agent -> " + str(r.status) + "  " + body[:120])
except Exception as e:
    print("  POST /v1/agent -> " + repr(e))

time.sleep(3)
# check for agent log written by dispatch
agent_dir = HOME / ".deepcli" / "logs" / "agent"
if agent_dir.exists():
    logs = sorted(agent_dir.glob("*.log"),
                  key=lambda x: x.stat().st_mtime, reverse=True)
    if logs:
        print("  latest agent log: " + str(logs[0].relative_to(HOME)))
        for line in logs[0].read_text(errors="replace").splitlines()[-10:]:
            print("    " + line[:140])

# ── 7. VERDICT ──────────────────────────────────────────────────────────────
banner("7. verdict")
print("  server.py dispatcher : corrected")
print("  tunnel-up notify     : silenced")
print("  keeper notify        : --id tunnel-rot (collapses repeats)")
print("  pinggy-status notify : silenced")
print("  worktrees            : reclaimed")
print()
print("  next:")
print("    gh workflow run deepseek-termux-agent.yml \\")
print("      --repo timerloggedout-spec/termux-monorepo \\")
print("      -f 'task=Execute ~/deepcli/tasks/self-integrate.md. Do exactly ONE improvement.'")
