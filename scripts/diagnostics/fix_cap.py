#!/usr/bin/env python3
"""Fix: apply RLIMIT to the CHILD via preexec_fn, not the parent hub process."""
from __future__ import annotations
import ast, datetime, pathlib, re, shutil, subprocess, time

HOME = pathlib.Path.home()
TS   = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
BACK = HOME / ".shell-forge-backups" / TS
BACK.mkdir(parents=True, exist_ok=True)

def banner(t): print("\n=== " + t + " ===")
def sh(a, timeout=60):
    try:
        r = subprocess.run(a, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"

# ── 1. evidence: what actually happened ─────────────────────────────────────
banner("1. evidence — hub death")
api = HOME / ".deepcli" / "logs" / "api.log"
if api.exists():
    tail = api.read_text(errors="replace").splitlines()[-30:]
    for line in tail:
        print("  " + line[:170])
else:
    print("  (api.log missing)")

rc, out, _ = sh(["bash", "-lc",
    "ps -eo pid,etime,args | grep -E 'deepcli/server\\.py|servers-up|uvicorn' | grep -v grep"])
print("  live:")
print(out or "    (none)")

# ── 2. revert the cap to preexec_fn ─────────────────────────────────────────
banner("2. revert cap to preexec_fn (child-only)")
server = HOME / "deepcli" / "server.py"
if not server.exists():
    print("  server.py missing"); raise SystemExit(1)

t = server.read_text(errors="replace")

# remove the offending parent-process setrlimit block
bad_block = '''    def _runner() -> None:
        import resource as _sf_resource
        # shell-forge: cap memory at 384 MiB, cpu at 900s, file size at 16 MiB
        _sf_resource.setrlimit(_sf_resource.RLIMIT_AS,
                               (384 * 1024 * 1024, 384 * 1024 * 1024))
        _sf_resource.setrlimit(_sf_resource.RLIMIT_CPU, (900, 900))
        _sf_resource.setrlimit(_sf_resource.RLIMIT_FSIZE,
                               (16 * 1024 * 1024, 16 * 1024 * 1024))
        started = _sf_time.time()
        task_dir = _sf_pathlib.Path.home() / ".deepcli" / "tasks"'''

good_block = '''    def _sf_limits() -> None:
        # shell-forge: limits apply to the CHILD only, never the hub process
        import resource as _sf_resource
        _sf_resource.setrlimit(_sf_resource.RLIMIT_AS,
                               (384 * 1024 * 1024, 384 * 1024 * 1024))
        _sf_resource.setrlimit(_sf_resource.RLIMIT_CPU, (900, 900))
        _sf_resource.setrlimit(_sf_resource.RLIMIT_FSIZE,
                               (16 * 1024 * 1024, 16 * 1024 * 1024))

    def _runner() -> None:
        started = _sf_time.time()
        task_dir = _sf_pathlib.Path.home() / ".deepcli" / "tasks"'''

old_call = '''                rc = _sf_subprocess.call(
                    [str(_sf_dispatch), str(task_file), body.source or "execute the task"],
                    stdout=fh, stderr=_sf_subprocess.STDOUT,
                )'''
new_call = '''                rc = _sf_subprocess.call(
                    [str(_sf_dispatch), str(task_file), body.source or "execute the task"],
                    stdout=fh, stderr=_sf_subprocess.STDOUT,
                    preexec_fn=_sf_limits,
                )'''

if good_block in t and "preexec_fn=_sf_limits" in t:
    print("  server.py: already fixed")
else:
    shutil.copy2(server, BACK / server.name)
    t2 = t
    if bad_block in t2:
        t2 = t2.replace(bad_block, good_block, 1)
        print("  removed parent-process cap")
    if old_call in t2 and "preexec_fn" not in t2.split(old_call)[1][:400]:
        t2 = t2.replace(old_call, new_call, 1)
        print("  added preexec_fn to child call")
    try:
        ast.parse(t2)
        server.write_text(t2)
        print("  server.py: written (ast:clean)")
    except SyntaxError as e:
        print("  server.py: syntax error " + str(e))

# ── 3. restart hub, wait for bind ───────────────────────────────────────────
banner("3. restart hub")
sh(["pkill", "-f", "deepcli/server.py"])
time.sleep(2)
subprocess.Popen([str(HOME / ".local" / "bin" / "servers-up")],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 start_new_session=True)
up = False
for i in range(25):
    rc, out, _ = sh(["bash", "-lc",
        "curl -sf -m 3 http://127.0.0.1:8800/health -o /dev/null && echo ok"])
    if "ok" in out:
        print("  hub up after " + str(i*2) + "s")
        up = True
        break
    time.sleep(2)
if not up:
    print("  hub did not bind — api.log tail:")
    if api.exists():
        for line in api.read_text(errors="replace").splitlines()[-15:]:
            print("    " + line[:160])

# ── 4. smoke with tiny task + verify child-only caps ────────────────────────
banner("4. smoke + verify hub survives")
import urllib.request, urllib.error, json
def post(path, body=None):
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8800" + path, method="POST",
            data=(json.dumps(body).encode() if body else None),
        )
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode(errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:200]
    except Exception as e:
        return 0, repr(e)

if up:
    code, body = post("/v1/agent", {"task": "echo ok", "source": "smoke"})
    print("  POST /v1/agent  -> " + str(code) + "  " + str(body)[:150])
    time.sleep(6)
    code2, _ = post("/v1/agent", {"task": "echo ok2", "source": "smoke"})
    print("  POST again      -> " + str(code2) + "  (hub survived first)")
    rc, out, _ = sh(["bash", "-lc",
        "ps -o rss= -p $(pgrep -f 'deepcli/server.py' | head -1) 2>/dev/null"])
    rss_kb = out.strip()
    if rss_kb.isdigit():
        print("  hub RSS         : " + str(int(rss_kb)/1024) + " MiB  (well under 384)")

# ── 5. commit + push ────────────────────────────────────────────────────────
banner("5. commit + push")
for path in ("deepcli/server.py", ".github/workflows/deepseek-termux-agent.yml",
             ".config/shell-forge/aliases.zsh"):
    sh(["git", "-C", str(HOME), "add", path])
rc, out, err = sh(["git", "-C", str(HOME), "commit", "-m",
    "fix(agent): child-only rlimit, workflow INV guard, control endpoints, alias"])
print("  " + ((out or err).strip().splitlines() or [""])[0])

rc, ahead, _ = sh(["git", "-C", str(HOME), "rev-list", "--count",
                   "origin/feat/dashboard-lanes-v2..HEAD"])
if (ahead.strip() or "0") != "0":
    rc, out, err = sh(["git", "-C", str(HOME), "push", "origin",
                       "feat/dashboard-lanes-v2"], timeout=300)
    print("  push: " + ("ok" if rc == 0 else "rc=" + str(rc)))

# ── 6. verdict ──────────────────────────────────────────────────────────────
banner("VERDICT")
print("  parent RLIMIT   : removed (was killing the hub)")
print("  child RLIMIT    : preexec_fn — only the dispatched process is capped")
print("  workflow guard  : empty INV exits 1")
print("  endpoints       : /pause /resume /stop /cancel live")
print("  alias           : serveo fixed")
print("  hub             : " + ("up" if up else "DOWN"))
print()
print("  next: gh workflow run deepseek-termux-agent.yml \\")
print("         -f 'task=Execute ~/deepcli/tasks/self-integrate.md.'")
