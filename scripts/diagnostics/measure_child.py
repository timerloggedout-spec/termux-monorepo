#!/usr/bin/env python3
"""Measure real VSZ/RSS of the dispatched child.  No claims.  Cite only."""
from __future__ import annotations
import json, pathlib, subprocess, time, urllib.request, urllib.error

HOME = pathlib.Path.home()

def banner(t): print("\n=== " + t + " ===")
def sh(a, timeout=60):
    try:
        r = subprocess.run(a, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"

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

def sample_pids(pattern, samples=40, interval=0.5):
    """Return list of dicts: ts, pid, vsz_kb, rss_kb, cmd."""
    rows = []
    for _ in range(samples):
        rc, out, _ = sh(["bash", "-lc",
            f"for p in $(pgrep -f '{pattern}' 2>/dev/null); do "
            f"ps -o pid=,vsz=,rss=,args= -p $p 2>/dev/null | head -1; done"])
        for line in out.strip().splitlines():
            parts = line.split(None, 3)
            if len(parts) >= 3 and parts[0].isdigit():
                rows.append({
                    "t": round(time.time(), 2),
                    "pid": int(parts[0]),
                    "vsz_mb": round(int(parts[1]) / 1024, 1),
                    "rss_mb": round(int(parts[2]) / 1024, 1),
                    "cmd": (parts[3] if len(parts) > 3 else "")[:90],
                })
        time.sleep(interval)
    return rows

# ── 1. baseline VSZ/RSS of a bare python3 on this device ───────────────────
banner("1. baseline: bare python3 VSZ/RSS")
p = subprocess.Popen(["python3", "-c", "import time; time.sleep(3)"])
time.sleep(0.8)
rc, out, _ = sh(["bash", "-lc",
    f"ps -o pid=,vsz=,rss= -p {p.pid} 2>/dev/null"])
print("  bare python3: " + out.strip() + "  (kB)")
if out.strip():
    parts = out.split()
    print("  VSZ " + format(int(parts[1])/1024, ".1f") + " MiB   RSS "
          + format(int(parts[2])/1024, ".1f") + " MiB")
p.wait()

# ── 2. baseline: hub process (real, running) ────────────────────────────────
banner("2. hub process (real)")
rc, out, _ = sh(["bash", "-lc",
    "p=$(pgrep -f 'deepcli/server.py' | head -1); "
    "ps -o pid=,vsz=,rss= -p \"$p\" 2>/dev/null"])
print("  hub: " + out.strip() + "  (kB)")
if out.strip():
    parts = out.split()
    print("  VSZ " + format(int(parts[1])/1024, ".1f") + " MiB   RSS "
          + format(int(parts[2])/1024, ".1f") + " MiB")

# ── 3. fire a real dispatch, sample child ───────────────────────────────────
banner("3. fire dispatch, sample child for 20s")
code, body = post("/v1/agent", {"task": "echo measuring; sleep 5; echo done",
                                "source": "measure"})
print("  POST /v1/agent -> " + str(code) + "  " + str(body)[:150])
inv = (body or {}).get("invocation_id") if isinstance(body, dict) else None

print("  sampling children (deepagent* / dispatch*):")
rows = sample_pids("deepagent|dispatch", samples=40, interval=0.5)
if not rows:
    print("    (no child observed — the child either never forked or exited <500ms)")
else:
    print("    pid     vsz_mb  rss_mb  cmd")
    seen = set()
    for r in rows:
        key = (r["pid"], r["vsz_mb"], r["rss_mb"])
        if key in seen: continue
        seen.add(key)
        print("    " + str(r["pid"]).rjust(6) + "  "
              + format(r["vsz_mb"], "7.1f") + "  "
              + format(r["rss_mb"], "7.1f") + "  "
              + r["cmd"])
    vsz_max = max(r["vsz_mb"] for r in rows)
    rss_max = max(r["rss_mb"] for r in rows)
    print()
    print("  peak VSZ: " + format(vsz_max, ".1f") + " MiB")
    print("  peak RSS: " + format(rss_max, ".1f") + " MiB")
    print()
    if vsz_max > 384:
        print("  FACT: child VSZ exceeded 384 MiB — RLIMIT_AS=384 would kill it")
    else:
        print("  FACT: child VSZ stayed under 384 MiB in this sample")

# ── 4. agent log content ────────────────────────────────────────────────────
banner("4. agent log content")
if inv:
    log = HOME / ".deepcli" / "logs" / "agent" / (inv + ".log")
    if log.exists():
        print("  " + str(log))
        for line in log.read_text(errors="replace").splitlines()[-15:]:
            print("    " + line[:170])
    else:
        print("  (no log written for " + inv + ")")

# ── 5. dispatch PID file + child tree ───────────────────────────────────────
banner("5. dispatch pid file")
pidf = HOME / ".deepcli" / "watchdog" / "dispatch.pid"
if pidf.exists():
    print("  " + str(pidf) + " = " + pidf.read_text().strip())
else:
    print("  (no dispatch.pid)")

banner("VERDICT — numbers only")
print("  see VSZ/RSS tables above for the real values")
