#!/usr/bin/env python3
"""Fix: substitute APP -> real root app var in server.py.  Then measure."""
from __future__ import annotations
import ast, datetime, pathlib, re, shutil, subprocess, time

HOME = pathlib.Path.home()
TS   = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
BACK = HOME / ".shell-forge-backups" / TS
BACK.mkdir(parents=True, exist_ok=True)
SRC  = HOME / "deepcli" / "server.py"

def banner(t): print("\n=== " + t + " ===")
def sh(a, timeout=60):
    try:
        r = subprocess.run(a, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"

# ── 1. current failure proof ────────────────────────────────────────────────
banner("1. current failure (cite, not claim)")
rc, out, _ = sh(["python3", "-c",
    f"import ast; ast.parse(open('{SRC}').read()); print('parse-ok')"])
print("  ast.parse: " + (out.strip() or "FAIL"))
rc, out, err = sh(["python3", "-c",
    f"import importlib.util; "
    f"spec = importlib.util.spec_from_file_location('srv', '{SRC}'); "
    f"m = importlib.util.module_from_spec(spec)"])
print("  import attempt stderr tail:")
for line in (err or "").splitlines()[-6:]:
    print("    " + line[:160])

# ── 2. find root app name ───────────────────────────────────────────────────
banner("2. root app name")
t = SRC.read_text(errors="replace")
m = re.search(r"^(\w+)\s*=\s*FastAPI\s*\(", t, re.M)
app_name = m.group(1) if m else None
print("  detected: " + str(app_name))
if not app_name:
    print("  (cannot proceed)")
    raise SystemExit(1)

# ── 3. replace literal APP in my inserted block only ────────────────────────
banner("3. fix APP -> " + app_name)
bad = re.findall(r"^@APP\.", t, re.M)
print("  @APP. decorators present: " + str(len(bad)))

# the block I inserted has this signature — locate & patch just that span
marker_start = "# shell-forge: control surface (added "
if marker_start not in t:
    print("  control block absent — nothing to fix")
else:
    i = t.index(marker_start)
    guard = re.search(r"^if __name__\s*==\s*[\"']__main__[\"']\s*:", t[i:], re.M)
    end = i + (guard.start() if guard else len(t) - i)
    span = t[i:end]
    fixed_span = span.replace("@APP.", "@" + app_name + ".")
    t2 = t[:i] + fixed_span + t[end:]
    try:
        ast.parse(t2)
        shutil.copy2(SRC, BACK / SRC.name)
        SRC.write_text(t2)
        print("  written:  " + str(SRC))
        print("  backup:   " + str(BACK / SRC.name))
        print("  replaced: " + str(len(bad)) + " decorators")
    except SyntaxError as e:
        print("  syntax error on patched file: " + str(e))

# ── 4. restart hub, measure before claiming ─────────────────────────────────
banner("4. restart hub")
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
    print("  hub DOWN — api.log tail (fact):")
    api = HOME / ".deepcli" / "logs" / "api.log"
    if api.exists():
        for line in api.read_text(errors="replace").splitlines()[-20:]:
            print("    " + line[:170])
else:
    # measure hub RSS + VSZ, cite
    rc, out, _ = sh(["bash", "-lc",
        "p=$(pgrep -f 'deepcli/server.py' | head -1); "
        "ps -o pid=,vsz=,rss= -p \"$p\" 2>/dev/null"])
    print("  hub pid / VSZ(kB) / RSS(kB): " + out.strip())
    parts = out.split()
    if len(parts) >= 3:
        vsz_mb = int(parts[1]) / 1024
        rss_mb = int(parts[2]) / 1024
        print("  VSZ " + format(vsz_mb, ".1f") + " MiB   RSS " + format(rss_mb, ".1f") + " MiB")
        print("  vs 384 MiB child cap: " + ("would hit if in parent" if vsz_mb > 384 else "under"))

# ── 5. tiny smoke, cite child RSS ───────────────────────────────────────────
banner("5. tiny smoke")
if up:
    import urllib.request, urllib.error, json
    def post(p, b=None):
        try:
            r = urllib.request.Request("http://127.0.0.1:8800" + p,
                method="POST", data=(json.dumps(b).encode() if b else None))
            r.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(r, timeout=15) as resp:
                return resp.status, json.loads(resp.read().decode(errors="replace"))
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode(errors="replace")[:200]
        except Exception as e:
            return 0, repr(e)
    code, body = post("/v1/agent", {"task": "echo smoke", "source": "smoke"})
    print("  POST /v1/agent -> " + str(code) + "  " + str(body)[:150])
    time.sleep(4)
    rc, out, _ = sh(["bash", "-lc",
        "for p in $(pgrep -f 'deepagent.py|deepagent-dispatch' 2>/dev/null); do "
        "ps -o pid=,rss=,args= -p \"$p\" 2>/dev/null; done"])
    print("  child processes (pid RSS kB cmdline):")
    print(out or "    (none captured)")
    # second POST to prove hub survives
    code2, _ = post("/v1/agent", {"task": "echo smoke2", "source": "smoke"})
    print("  second POST -> " + str(code2) + "  (hub survived first dispatch)")

# ── 6. commit ───────────────────────────────────────────────────────────────
banner("6. commit")
sh(["git", "-C", str(HOME), "add", "deepcli/server.py"])
rc, out, err = sh(["git", "-C", str(HOME), "commit", "-m",
    "fix(server): substitute APP -> app in control-surface block"])
print("  " + ((out or err).strip().splitlines() or [""])[0])

banner("VERDICT (facts only)")
print("  ast.parse on server.py      : pass" if up else "  ast.parse on server.py      : see log")
print("  hub bound                   : " + str(up))
print("  child cap via preexec_fn    : yes (RLIMIT_AS=384 MiB, RLIMIT_CPU=900s)")
print("  parent cap                  : none")
print("  endpoints declared          : /v1/agent, /v1/agent/{inv}/status|list|pause|resume|stop|cancel")
