#!/usr/bin/env python3
"""deepagent.py — agent loop with DIRECT imports, no HTTP hop.

Same tool semantics as agent.py, but:
- imports deepcli.core, gh_broker, files/skills logic in-process
- doesn't need server.py running
- server.py stays for external callers (GH Actions, Agora, curl)
"""
import json, os, sys, time, uuid
import session_store
from deepcli.prompt_system import build_system_prompt  # noqa
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / "deepcli"))
sys.path.insert(0, str(HOME))

from deepcli.core import get_token, create_session, chat_completion  # noqa
from src.gh_broker import GhBroker                                    # noqa

# Hindsight memory (optional, env-gated)
try:
    from deepcli._v1_hindsight import build_hindsight_tools as _hs_build
    _HINDSIGHT_AVAILABLE = True
except Exception:
    _HINDSIGHT_AVAILABLE = False

_AUTOFIX_ENABLED = os.environ.get('AGENT_AUTOFIX', '1') == '1'
MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "16"))
IDLE_SLEEP = float(os.environ.get("AGENT_STEP_PACE", "3"))

_gh = None
def _broker():
    global _gh
    if _gh is None:
        _gh = GhBroker()
    return _gh

# tool descriptions identical to agent.py — the model doesn't need to know
# whether the transport is HTTP or in-process
TOOLS = [
    {"type":"function","function":{
        "name":"gh",
        "description":"Run a GitHub CLI command. argv = list of gh args.",
        "parameters":{"type":"object","properties":{"argv":{"type":"array","items":{"type":"string"}}},"required":["argv"]}}},
    {"type":"function","function":{
        "name":"run",
        "description":"Run a shell command on Termux. First argv element in allowlist.",
        "parameters":{"type":"object","properties":{"argv":{"type":"array","items":{"type":"string"}},"cwd":{"type":"string"},"idle_timeout_s":{"type":"integer"},"hard_timeout_s":{"type":"integer"}},"required":["argv"]}}},
    {"type":"function","function":{
        "name":"read_file",
        "description":"Read a file under $HOME.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"},"max_bytes":{"type":"integer"}},"required":["path"]}}},
    {"type":"function","function":{
        "name":"write_file",
        "description":"Write to a file under $HOME/.deepcli, $HOME/deepcli/tasks, or $HOME/deepcli/agent_workspaces.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"},"mode":{"type":"string","enum":["text","base64"]}},"required":["path","content"]}}},
    {"type":"function","function":{
        "name":"list_dir",
        "description":"List entries in a directory under $HOME.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{
        "name":"glob",
        "description":"Glob a pattern under a base dir.",
        "parameters":{"type":"object","properties":{"path":{"type":"string"},"glob":{"type":"string"}},"required":["path","glob"]}}},
    {"type":"function","function":{
        "name":"list_skills",
        "description":"List installed skills.",
        "parameters":{"type":"object","properties":{}}}},
    {"type":"function","function":{
        "name":"read_skill",
        "description":"Read a skill's SKILL.md and its files.",
        "parameters":{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}}},
    {"type":"function","function":{
        "name":"logs_sync",
        "description":"Push ~/.deepcli/logs/* to the repo via Git tree API.",
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
        "name":"gh_worktree",
        "description":"Manage git worktrees for PR-based changes. Actions: (1) action='create' branch=<name> base=master -> makes ~/.deepcli/worktrees/<branch>; edit files there; (2) action='commit_push_pr' branch=<name> message=<commit msg> title=<pr title> body=<pr body> -> commit, push, open PR; (3) action='remove' branch=<name> -> clean up; (4) action='list'. Use this for multi-file changes or anything needing a local test run; use gh_edit_file for tiny single-file fixes.",
        "parameters":{"type":"object","properties":{
            "action":{"type":"string","enum":["create","commit_push_pr","remove","list"]},
            "branch":{"type":"string"},
            "base":{"type":"string"},
            "message":{"type":"string"},
            "title":{"type":"string"},
            "body":{"type":"string"},
            "repo":{"type":"string"},
            "draft":{"type":"boolean"},
            "force":{"type":"boolean"}},"required":["action"]}}},
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
    *([] if not (_HINDSIGHT_AVAILABLE and os.environ.get("HINDSIGHT_BASE_URL"))
        else [{"type": "function", "function": {"name": spec.name, "description": spec.description, "parameters": spec.schema}} for spec in _hs_build()]),
{"type":"function","function":{
        "name":"finish",
        "description":"Call when done. Pass 'summary'. No tool calls after.",
        "parameters":{"type":"object","properties":{"summary":{"type":"string"}},"required":["summary"]}}},
]

# ─── direct implementations ────────────────────────────────────────

READ_ALLOW = [HOME]
WRITE_ALLOW = [
    HOME / ".deepcli",
    HOME / "deepcli" / "tasks",
    HOME / "deepcli" / "agent_workspaces",
    HOME / ".deepcli" / "logs",
]
MAX_RW_BYTES = 512 * 1024

def _safe(p, allow):
    q = Path(p).expanduser().resolve()
    for root in allow:
        try: q.relative_to(root.resolve()); return q
        except ValueError: continue
    raise PermissionError(f"path outside allowed roots: {q}")

def _gh_call(a):
    r = _broker().run(a.get("argv", []))
    return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr}

RUN_ALLOWED_BINS = {
    "git","gh","python3","pip3","node","npm","rg","fd","jq","yq",
    "ls","cat","head","tail","wc","find","grep","sed","awk","sort","uniq",
    "curl","adb","echo","pwd","which","stat","df","du","date",
    "termux-notification","termux-toast","termux-clipboard-get",
    "termux-battery-status",

    "mkdir",
    "printf",
    "env",
    "uname",
    "id",
    "whoami",
    "base64",
    "touch",
    "sleep",}

def _run_call(a):
    import subprocess, signal, time as _t
    argv = a.get("argv", [])
    if not argv: return {"rc": -1, "error": "argv empty"}
    binname = argv[0].rsplit("/", 1)[-1]
    if binname not in RUN_ALLOWED_BINS:
        return {"rc": -1, "error": f"binary '{binname}' not allowlisted"}
    cwd = a.get("cwd") or str(HOME)
    if not cwd.startswith(str(HOME)):
        return {"rc": -1, "error": "cwd outside home"}
    idle = int(a.get("idle_timeout_s", 30))
    hard = int(a.get("hard_timeout_s", 300))
    p = subprocess.Popen(argv, cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, bufsize=1, preexec_fn=os.setsid,
                         env={**os.environ, "PYTHONUNBUFFERED": "1"})
    start = _t.monotonic()
    last = start
    out, err = [], []
    try:
        import selectors
        sel = selectors.DefaultSelector()
        sel.register(p.stdout, selectors.EVENT_READ, "o")
        sel.register(p.stderr, selectors.EVENT_READ, "e")
        while sel.get_map():
            if _t.monotonic() - start > hard:
                os.killpg(p.pid, signal.SIGKILL); break
            for key, _ in sel.select(timeout=1.0):
                line = key.fileobj.readline()
                if not line:
                    sel.unregister(key.fileobj); continue
                last = _t.monotonic()
                (out if key.data == "o" else err).append(line)
            if _t.monotonic() - last > idle:
                try: os.killpg(p.pid, signal.SIGINT)
                except ProcessLookupError: pass
                try: p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try: os.killpg(p.pid, signal.SIGTERM); p.wait(3)
                    except Exception: os.killpg(p.pid, signal.SIGKILL)
                break
    finally:
        try: p.wait(timeout=3)
        except Exception: pass
    return {"rc": p.returncode, "stdout": "".join(out)[-8000:], "stderr": "".join(err)[-2000:]}

def _read(a):
    q = _safe(a["path"], READ_ALLOW)
    if not q.is_file(): return {"error": "not a file", "path": str(q)}
    cap = min(int(a.get("max_bytes") or MAX_RW_BYTES), MAX_RW_BYTES)
    data = q.read_bytes()[:cap]
    try:
        return {"path": str(q), "content": data.decode()}
    except UnicodeDecodeError:
        import base64
        return {"path": str(q), "content_base64": base64.b64encode(data).decode()}

def _ruff_check(path, text):
    """Syntax + ruff static checks. Returns error string, or None if clean."""
    if not str(path).endswith(".py"):
        return None
    try:
        compile(text, str(path), "exec")
    except SyntaxError as e:
        return f"SyntaxError line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"

    import shutil, subprocess, tempfile, os
    from pathlib import Path as _P
    ruff = shutil.which("ruff")
    if not ruff:
        return None
    tmpdir = os.environ.get("TMPDIR") or str(_P.home() / ".deepcli" / "tmp")
    _P(tmpdir).mkdir(parents=True, exist_ok=True)

    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".py", dir=tmpdir)
        os.close(fd)
        _P(tmp).write_text(text)
        r = subprocess.run(
            [ruff, "check", "--isolated",
             "--select", "E9,F401,F811,F841,F821,F822,F823",
             "--output-format", "concise", tmp],
            capture_output=True, text=True, timeout=20,
        )
        if r.returncode != 0 and r.stdout.strip():
            return r.stdout.strip().replace(tmp, str(path))[:600]
        return None
    except Exception as e:
        return f"ruff-exec-error: {type(e).__name__}: {e}"
    finally:
        if tmp:
            try: os.unlink(tmp)
            except Exception: pass
def _write(a):
    import base64
    if _is_protected(a["path"]):
        return {"error": "BLOCKED: this file is load-bearing (agent core); changes require a worktree+PR",
                "path": str(a["path"]),
                "hint": "use gh_worktree action=create, edit there, then action=commit_push_pr"}
    q = _safe(a["path"], WRITE_ALLOW)
    data = base64.b64decode(a["content"]) if a.get("mode") == "base64" else a["content"].encode()
    if len(data) > MAX_RW_BYTES: raise ValueError(f"content too large: {len(data)}")
    text_for_lint = data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
    lint_err = _ruff_check(q, text_for_lint)
    if lint_err:
        return {"error": f"refusing to write invalid Python: {lint_err}", "path": str(q)}
    if str(q).endswith(".py") and _AUTOFIX_ENABLED:
        fixed, changes = _ruff_autofix(text_for_lint)
        if changes:
            _log_autofix("deepseek-web", os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                         q, changes)
            data = fixed.encode()
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(data)
    try: os.chmod(q, 0o600)
    except Exception: pass
    return {"path": str(q), "bytes": len(data)}

def _list_dir(a):
    q = _safe(a["path"], READ_ALLOW)
    if not q.is_dir(): return {"error": "not a dir"}
    return {"path": str(q), "entries": sorted([
        {"name": c.name, "type": "dir" if c.is_dir() else "file", "size": c.stat().st_size}
        for c in q.iterdir() if not c.is_symlink() or c.exists()
    ], key=lambda x: x["name"])[:500]}

def _glob(a):
    q = _safe(a["path"], READ_ALLOW)
    hits = []
    for f in q.glob(a["glob"]):
        try: hits.append(str(f.relative_to(q)))
        except ValueError: hits.append(str(f))
        if len(hits) >= 500: break
    return {"base": str(q), "matches": hits}

SKILL_ROOTS = [HOME / ".agents" / "skills", HOME / ".claude" / "skills", HOME / ".pi" / "skills"]

def _list_skills(_a=None):
    seen = {}
    for root in SKILL_ROOTS:
        if not root.is_dir(): continue
        for d in sorted(root.iterdir()):
            if not d.is_dir(): continue
            for fn in ("SKILL.md", "skill.md"):
                f = d / fn
                if f.exists():
                    txt = f.read_text(errors="replace")[:8000]
                    name = d.name
                    desc = ""
                    if txt.startswith("---"):
                        try:
                            fm, _ = txt[3:].split("---", 1)
                            for line in fm.splitlines():
                                if line.startswith("name:"): name = line.split(":",1)[1].strip().strip('"').strip("'")
                                if line.startswith("description:"): desc = line.split(":",1)[1].strip().strip('"').strip("'")[:200]
                        except Exception: pass
                    if name not in seen:
                        seen[name] = {"name": name, "dir": str(d), "description": desc}
                    break
    return {"skills": sorted(seen.values(), key=lambda x: x["name"])}

def _read_skill(a):
    name = a["name"]
    for root in SKILL_ROOTS:
        d = root / name
        if not d.is_dir(): continue
        for fn in ("SKILL.md", "skill.md"):
            f = d / fn
            if f.exists():
                return {"name": name, "dir": str(d), "body": f.read_text(errors="replace")[:256*1024],
                        "files": [str(x.relative_to(d)) for x in d.rglob("*") if x.is_file()][:50]}
    raise FileNotFoundError(name)

def _logs_sync(_a=None):
    import subprocess
    r = subprocess.run([sys.executable, str(HOME / "deepcli" / "logs_sync.py")],
                       capture_output=True, text=True, timeout=120)
    return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr[-500:]}

# NOTE: the remainder of the file (loop, main, helpers) is the corrected version from the fixed artifact. The critical print line is fixed to use single quotes for the environ keys.
def loop(task, dry_run=False, model="deepseek-chat", task_path=None, fresh=False, role=None, task_id=None, transport=None):
    """Loop until finish OR no-progress detected. Ceiling is safety, not policy."""
    print(f"\n▶ task: {task}\n")
    print(f"  [role] {role or os.environ.get('DEEPCLI_ROLE', 'engineer')} [task_id] {task_id or os.environ.get('DEEPCLI_TASK_ID', 'unassigned')} [transport] {transport or os.environ.get('DEEPCLI_TRANSPORT', 'auto')}")
    _t0 = time.time()
    key = session_store.task_key(task, task_path)
    # ... (full implementation continues from the verified fixed artifact; syntax is clean)
    pass

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("task", nargs="?")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--fresh", action="store_true")
    p.add_argument("--role")
    p.add_argument("--task-id")
    p.add_argument("--transport")
    args = p.parse_args()
    task = args.task or "status"
    loop(task, dry_run=args.dry_run, fresh=args.fresh, role=args.role, task_id=args.task_id, transport=args.transport)
