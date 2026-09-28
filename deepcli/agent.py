#!/usr/bin/env python3
"""agent.py — YOLO loop with gh, run, file ops, and skill access."""
import json, os, sys, time, urllib.request

HUB = os.environ.get("DSH_HUB", "http://127.0.0.1:8800")
TOK = open(os.path.expanduser("~/.deepcli/hub.token")).read().strip()
import session_store

MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "16"))

TOOLS = [
    {"type":"function","function":{
        "name":"gh",
        "description":"Run a GitHub CLI command. argv = list of gh args (e.g. ['pr','list','--repo','o/r','--json','number,title']). Blocked: DELETE, /keys, /secrets, /collaborators, /hooks.",
        "parameters":{"type":"object","properties":{"argv":{"type":"array","items":{"type":"string"}}},"required":["argv"]}}},
    {"type":"function","function":{
        "name":"run",
        "description":"Run a shell command on Termux. First argv element must be in the allowlist (git, gh, python3, jq, rg, fd, ls, cat, etc.). cwd defaults to $HOME. Streams via SSE.",
        "parameters":{"type":"object","properties":{"argv":{"type":"array","items":{"type":"string"}},"cwd":{"type":"string"},"idle_timeout_s":{"type":"integer"},"hard_timeout_s":{"type":"integer"}},"required":["argv"]}}},
    {"type":"function","function":{
        "name":"read_file",
        "description":"Read a file under $HOME. Returns {content} or {content_base64} for binary.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"},"max_bytes":{"type":"integer"}},"required":["path"]}}},
    {"type":"function","function":{
        "name":"write_file",
        "description":"Write to a file. ONLY allowed under $HOME/.deepcli, $HOME/deepcli/tasks, $HOME/deepcli/agent_workspaces. Use gh api PUT to modify repo files.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"},"mode":{"type":"string","enum":["text","base64"]}},"required":["path","content"]}}},
    {"type":"function","function":{
        "name":"list_dir",
        "description":"List entries in a directory under $HOME.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{
        "name":"glob",
        "description":"Glob a pattern under a base dir (e.g. path='~/.agents/skills', glob='*​/SKILL.md').",
        "parameters":{"type":"object","properties":{"path":{"type":"string"},"glob":{"type":"string"}},"required":["path","glob"]}}},
    {"type":"function","function":{
        "name":"list_skills",
        "description":"List installed skills (name, description, path).",
        "parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{
        "name":"read_skill",
        "description":"Read a skill's SKILL.md body and its sibling files. Use this to load instructions when the skill's description matches the current task.",
        "parameters":{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}}},
    {"type":"function","function":{
        "name":"logs_sync",
        "description":"Push ~/.deepcli/logs/* to termux-monorepo/.deepseek-logs/<date>/ via Git tree API. Fire-and-forget.",
        "parameters":{"type":"object","properties":{}}}},
            {"type":"function","function":{
        "name":"gh_get_file",
        "description":"Fetch a file from a GitHub repo. Returns {path, sha, size, content} where content is the DECODED text. Use THIS instead of gh api ... --jq .content + b64_decode. Args: repo='owner/name', path='.github/workflows/x.yml', ref='master'.",
        "parameters":{"type":"object","properties":{
            "repo":{"type":"string"},
            "path":{"type":"string"},
            "ref":{"type":"string"}},"required":["repo","path"]}}},
    {"type":"function","function":{
        "name":"gh_edit_file",
        "description":"Surgical edit of a repo file. Fetches, applies each {old,new} replacement (each 'old' must appear exactly once), pushes. Use this INSTEAD of gh_get_file+gh_put when you only need to change a few lines. Args: repo, path, edits=[{old,new}], message, branch (default master).",
        "parameters":{"type":"object","properties":{
            "repo":{"type":"string"},
            "path":{"type":"string"},
            "edits":{"type":"array","items":{"type":"object","properties":{"old":{"type":"string"},"new":{"type":"string"}},"required":["old","new"]}},
            "message":{"type":"string"},
            "branch":{"type":"string"},
            "create_if_missing":{"type":"boolean"}},"required":["repo","path","edits"]}}},
{"type":"function","function":{
        "name":"gh_put",
        "description":"Commit a file to a GitHub repo via API. Handles base64 + existing sha detection automatically. Use THIS instead of shelling out to base64/curl. Args: repo='owner/name', path='.github/workflows/x.yml', content='<full file text>', message='<commit msg>', branch='master'.",
        "parameters":{"type":"object","properties":{
            "repo":{"type":"string"},
            "path":{"type":"string"},
            "content":{"type":"string"},
            "message":{"type":"string"},
            "branch":{"type":"string"}},"required":["repo","path","content"]}}},
    {"type":"function","function":{
        "name":"b64_decode",
        "description":"Decode a base64 string to UTF-8 text. Use after gh api ... --jq .content to get the file body. Args: data='<base64>'.",
        "parameters":{"type":"object","properties":{"data":{"type":"string"}},"required":["data"]}}},
{"type":"function","function":{
        "name":"finish",
        "description":"Call when the task is complete. Pass 'summary'. Do NOT call any other tool after this.",
        "parameters":{"type":"object","properties":{"summary":{"type":"string"}},"required":["summary"]}}},
]


def _post(path, body, timeout=180):
    """POST with retry on 5xx / timeout. DeepSeek web session is flaky."""
    import time as _t, urllib.error
    last_err = None
    delays = [30] * 10  # fixed 30s
    for i, d in enumerate([0] + delays):
        if d: _t.sleep(d)
        req = urllib.request.Request(HUB+path, data=json.dumps(body).encode(),
            headers={"Content-Type":"application/json","Authorization":"Bearer "+TOK})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode()
            return json.loads(raw) if raw.lstrip().startswith(("{","[")) else raw
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < len(delays):
                last_err = f"{e.code} {e.reason}"
                print(f"    [retry {i+1}/{len(delays)}] {path} -> {e.code}, sleeping {delays[i] if i < len(delays) else 0}s")
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if i < len(delays):
                last_err = str(e)
                print(f"    [retry {i+1}/{len(delays)}] {path} -> {type(e).__name__}, sleeping")
                continue
            raise
    raise RuntimeError(f"gave up after retries: {last_err}")
def _post_sse(path, body, timeout=600):
    """Stream POST with retry on connect failures."""
    import time as _t, urllib.error
    for attempt in range(4):
        if attempt: _t.sleep([0, 3, 8, 15][attempt])
        req = urllib.request.Request(HUB+path, data=json.dumps(body).encode(),
            headers={"Content-Type":"application/json","Authorization":"Bearer "+TOK})
        try:
            events = []
            with urllib.request.urlopen(req, timeout=timeout) as r:
                buf = b""
                for chunk in iter(lambda: r.read(1024), b""):
                    buf += chunk
                    while b"\n\n" in buf:
                        frame, buf = buf.split(b"\n\n", 1)
                        ev, data = "message", ""
                        for line in frame.split(b"\n"):
                            if line.startswith(b"event: "): ev = line[7:].decode()
                            elif line.startswith(b"data: "): data = line[6:].decode()
                        events.append((ev, data))
            return events
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 504) and attempt < 3:
                print(f"    [sse retry {attempt+1}/3] {path} -> {e.code}")
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 3:
                print(f"    [sse retry {attempt+1}/3] {path} -> {type(e).__name__}")
                continue
            raise
def call_gh(a): return _post("/gh", {"argv": a.get("argv", [])})

def call_run(a):
    ev = _post_sse("/run", {
        "argv": a["argv"], "cwd": a.get("cwd"),
        "idle_timeout_s": a.get("idle_timeout_s", 30),
        "hard_timeout_s": a.get("hard_timeout_s", 300)})
    out, err, rc = [], [], None
    for e, d in ev:
        if e == "stdout":
            try: out.append(json.loads(d))
            except Exception: out.append(d)
        elif e == "stderr":
            try: err.append(json.loads(d))
            except Exception: err.append(d)
        elif e == "status":
            try: rc = json.loads(d).get("rc")
            except Exception: pass
    return {"rc": rc, "stdout": "".join(out), "stderr": "".join(err)}

def call_read_file(a):    return _post("/v1/files/read",    {"path": a["path"], "max_bytes": a.get("max_bytes")})
def call_write_file(a):   return _post("/v1/files/write",   {"path": a["path"], "content": a["content"], "mode": a.get("mode","text")})
def call_list_dir(a):     return _post("/v1/files/list",    {"path": a["path"]})
def call_glob(a):         return _post("/v1/files/glob",    {"path": a["path"], "glob": a["glob"]})
def call_list_skills(_args=None): return _post("/v1/skills/list",   {})
def call_read_skill(a):   return _post("/v1/skills/read/"+a["name"], {})
def call_logs_sync(_args=None):
    import subprocess
    r = subprocess.run([sys.executable, os.path.expanduser("~/deepcli/logs_sync.py")],
                       capture_output=True, text=True, timeout=120)
    return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr[-500:]}


DISPATCH = {
    "gh": call_gh, "run": call_run,
    "read_file": call_read_file, "write_file": call_write_file,
    "list_dir": call_list_dir, "glob": call_glob,
    "list_skills": call_list_skills, "read_skill": call_read_skill,
    "logs_sync": call_logs_sync,
}


def _log_tool_error(fn, args, exc):
    """Append tool-implementation errors (not policy blocks) to a jsonl for post-mortem.
    Policy blocks (PermissionError, FileNotFoundError, HTTPException 4xx) do NOT go here."""
    import traceback as _tb, datetime as _dt, json as _j, os as _os
    from pathlib import Path as _P
    log = _P.home() / ".deepcli" / "logs" / "tool_errors.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        args_head = _j.dumps(args)[:300] if not isinstance(args, str) else str(args)[:300]
    except Exception:
        args_head = str(args)[:300]
    row = {
        "ts": _dt.datetime.utcnow().isoformat(),
        "pid": _os.getpid(),
        "tool": fn,
        "args_head": args_head,
        "exc": type(exc).__name__,
        "msg": str(exc)[:500],
        "tb": _tb.format_exc()[-2000:],
    }
    with log.open("a") as f:
        f.write(_j.dumps(row) + "\n")
    try: log.chmod(0o600)
    except Exception: pass


# ─── retry policy: burst → ±30s rest → repeat ────────────────────────
# Phase A: burst, escalating short waits (sub-second → 5s)
# Phase B: rest ~30s ± noise ± learned offset from prior successes
# Learns from history: ~/.deepcli/logs/retry_learning.jsonl
_BURST_WAITS = [0.3, 0.7, 1.5, 3.0, 5.0]
_REST_BASE = 30.0
_REST_JITTER = 15.0


def _learned_offset() -> float:
    """Median of successful rest durations from last 20 samples."""
    import json as _j, statistics as _st
    p = HOME / ".deepcli" / "logs" / "retry_learning.jsonl"
    if not p.exists():
        return 0.0
    samples = []
    try:
        for line in p.read_text().splitlines()[-200:]:
            try:
                r = _j.loads(line)
                if r.get("outcome") == "success" and "rest_s" in r:
                    samples.append(float(r["rest_s"]))
            except Exception:
                continue
    except Exception:
        return 0.0
    if len(samples) < 5:
        return 0.0
    med = _st.median(samples[-20:])
    return max(-15.0, min(15.0, med - _REST_BASE))


def _record_retry(outcome: str, rest_s: float, attempt: int, kind: str):
    import json as _j, datetime as _dt
    p = HOME / ".deepcli" / "logs" / "retry_learning.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        with p.open("a") as f:
            f.write(_j.dumps({
                "ts": _dt.datetime.utcnow().isoformat(),
                "outcome": outcome,
                "rest_s": round(rest_s, 2),
                "attempt": attempt,
                "kind": kind,
            }) + "\n")
    except Exception:
        pass


def _retry_plan(max_bursts: int = 4):
    """Yield (phase, wait_s) sequences. burst of 5, rest, repeat."""
    import random as _r
    offset = _learned_offset()
    for burst_i in range(max_bursts):
        for w in _BURST_WAITS:
            yield ("burst", w, burst_i)
        if burst_i < max_bursts - 1:
            rest = _REST_BASE + _r.uniform(-_REST_JITTER, _REST_JITTER) + offset
            yield ("rest", max(5.0, rest), burst_i)


def execute(call):
    REQUIRED_ARGS = {
        "gh":         ["argv"],
        "run":        ["argv"],
        "read_file":  ["path"],
        "write_file": ["path", "content"],
        "list_dir":   ["path"],
        "glob":       ["path", "glob"],
        "read_skill": ["name"],
    }
    fn = call["function"]["name"]
    try:
        args = json.loads(call["function"]["arguments"] or "{}")
    except Exception as e:
        return f"ERROR parsing args: {e}"
    if fn == "finish":
        return {"finished": True, "summary": args.get("summary", "")}
    missing = [k for k in REQUIRED_ARGS.get(fn, []) if k not in args or args[k] in (None, "", [])]
    if missing:
        return (f"ERROR {fn}: missing required arg(s) {missing}. "
                f"Emit the call again with {REQUIRED_ARGS[fn]} populated.")
    h = DISPATCH.get(fn)
    if not h:
        return f"ERROR unknown tool: {fn}"
    try:
        return h(args)
    except Exception as e:
        return f"ERROR {type(e).__name__}: {e}"

_RATELIMIT_MARKERS = (
    "Messages too frequent",
    "too frequent",
    "rate limit",
    "please wait",
    "Please wait a moment",
    "sending messages too quickly",
)


def _looks_ratelimited(text) -> bool:
    if not text:
        return False
    t = text.lower()
    return any(m.lower() in t for m in _RATELIMIT_MARKERS)


def _completion_with_backoff(body, timeout=300, max_attempts=6):
    """POST /v1/chat/completions, retry on rate-limit signal in the reply."""
    import time as _t
    delays = [30] * 10  # fixed 30s
    last = None
    for i in range(max_attempts):
        if i: _t.sleep(delays[i-1])
        r = _post("/v1/chat/completions", body, timeout=timeout)
        try:
            content = r["choices"][0]["message"].get("content") or ""
            calls   = r["choices"][0]["message"].get("tool_calls") or []
        except Exception:
            content, calls = "", []
        if calls:
            return r
        if _looks_ratelimited(content):
            print(f"    [ratelimit {i+1}/{max_attempts}] sleeping {delays[i] if i < len(delays) else 'max'}s")
            last = content
            continue
        return r
    # fall through — return last even if rate-limited so caller can decide
    print("    [ratelimit] giving up after retries")
    return r


def _agent_notify(kind: str, title: str, content: str, priority: str = "default"):
    import subprocess as _sp, shutil as _sh
    if not _sh.which("termux-notification"):
        return
    try:
        _sp.Popen(["termux-notification",
                   "--id", f"agent-{kind}",
                   "--channel", "agent",
                   "--title", title,
                   "--content", content[:400],
                   "--priority", priority],
                  stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
    except Exception:
        pass


def loop(task, dry_run=False, model="deepseek-chat", task_path=None, fresh=False):
    print(f"\n▶ task: {task}\n")
    msgs = [{"role":"user","content":task}]
    for step in range(MAX_STEPS):
        print(f"── step {step+1}/{MAX_STEPS} ──")
        if step > 0:
            import time as _t2; _t2.sleep(3)   # pace against web-session rate limit
        r = _completion_with_backoff({
            "model": model, "messages": msgs, "tools": TOOLS, "stream": False},
            timeout=300)
        msg = r["choices"][0]["message"]
        calls = msg.get("tool_calls") or []
        if msg.get("content"):
            print(f"  (assistant): {msg['content'][:200]}")
        if not calls:
            print(f"\n✔ done (no tool calls)\n{msg.get('content','')}\n")
            return msg.get("content","")
        msgs.append(msg)
        for c in calls:
            fn = c["function"]["name"]
            raw_args = c["function"]["arguments"]
            print(f"  ▶ {fn}({raw_args[:120]})")
            if dry_run: continue
            result = execute(c)
            if fn == "finish":
                print(f"\n✔ FINISH\n{result.get('summary','')}\n")
                return result.get("summary","")
            printable = json.dumps(result) if not isinstance(result, str) else result
            pass  # no cap — DeepSeek web session is ~1M tokens; tool results fit
            print(f"    ← {printable[:300]}")
            msgs.append({"role":"tool","tool_call_id":c["id"],"content":printable})
    print(f"\n✗ hit MAX_STEPS={MAX_STEPS}\n")
    return ""


if __name__ == "__main__":
    argv = sys.argv[1:]
    dry = False
    if argv and argv[0] == "--dry-run":
        dry = True; argv = argv[1:]
    if not argv:
        print("usage: agent.py [--dry-run] \"<task>\""); sys.exit(2)
    loop(" ".join(argv), dry_run=dry)
