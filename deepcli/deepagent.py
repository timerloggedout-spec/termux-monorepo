#!/usr/bin/env python3
"""deepagent.py — agent loop with DIRECT imports, no HTTP hop.

Same tool semantics as agent.py, but:
- imports deepcli.core, gh_broker, files/skills logic in-process
- doesn't need server.py running
- server.py stays for external callers (GH Actions, Agora, curl)
"""
import json, os, sys, time, uuid
import session_store
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / "deepcli"))
sys.path.insert(0, str(HOME))

from deepcli.core import get_token, create_session, chat_completion  # noqa
from src.gh_broker import GhBroker                                    # noqa

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

def _gh_edit_file(a):
    """Fetch a file, apply {old->new} replacements, push. Server-side RMW.

    Args:
      repo: owner/name
      path: path in repo
      edits: list of {"old": "...", "new": "..."} — each must match exactly once
      message: commit message
      branch: default master
      create_if_missing: if True and file absent, use edits[0].new as content
    """
    import subprocess as _sp, json as _json, base64 as _b64
    repo = a["repo"]; path = a["path"]; edits = a.get("edits") or []
    msg = a.get("message", f"edit {path}"); branch = a.get("branch", "master")
    create = bool(a.get("create_if_missing"))

    # fetch
    r = _sp.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}"],
                capture_output=True, text=True)
    cur_sha = ""
    if r.returncode == 0:
        try:
            d = _json.loads(r.stdout)
            cur_sha = d.get("sha", "")
            b64 = (d.get("content") or "").replace(chr(10), "").replace(" ", "")
            b64 += "=" * ((-len(b64)) % 4)
            text = _b64.b64decode(b64).decode("utf-8", "replace")
        except Exception as e:
            return {"error": f"decode: {e}"}
    elif create and edits and not edits[0].get("old"):
        text = edits[0].get("new", "")
    else:
        return {"error": f"file not found: {path}", "stderr": r.stderr[-300:]}

    # apply edits
    applied, errors = [], []
    for i, ed in enumerate(edits):
        old = ed.get("old", ""); new = ed.get("new", "")
        if not old and not create:
            errors.append(f"edit[{i}]: missing 'old' (use gh_put to create files)")
            continue
        n = text.count(old)
        if n == 0:
            errors.append(f"edit[{i}]: old text not found")
            continue
        if n > 1:
            errors.append(f"edit[{i}]: old text appears {n}x — must be unique")
            continue
        text = text.replace(old, new, 1)
        applied.append(i)

    if errors and not applied:
        return {"error": "no edits applied", "details": errors}
    if not applied:
        return {"error": "no edits specified"}

    # push
    body = {"message": msg,
            "content": _b64.b64encode(text.encode()).decode(),
            "branch": branch}
    if cur_sha:
        body["sha"] = cur_sha
    r = _sp.run(["gh", "api", f"repos/{repo}/contents/{path}", "-X", "PUT", "--input", "-"],
                input=_json.dumps(body), capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": f"PUT failed: {r.stderr[-400:]}", "applied": applied, "errors": errors}
    resp = _json.loads(r.stdout)
    c = resp.get("content", {})
    return {"path": c.get("path"), "sha": c.get("sha"),
            "html_url": c.get("html_url"),
            "commit": resp.get("commit", {}).get("sha"),
            "applied": applied, "errors": errors}


def _gh_put(a):
    """Commit content to repo via gh api PUT. Auto-detects existing sha."""
    import base64 as _b64, json as _json, subprocess as _sp
    repo = a["repo"]; path = a["path"]; content = a["content"]
    msg = a.get("message", f"update {path}"); branch = a.get("branch", "master")
    r = _sp.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}", "--jq", ".sha"],
                capture_output=True, text=True)
    sha = r.stdout.strip() if r.returncode == 0 else ""
    body = {"message": msg,
            "content": _b64.b64encode(content.encode()).decode(),
            "branch": branch}
    if sha and sha != "null" and sha:
        body["sha"] = sha
    r = _sp.run(["gh", "api", f"repos/{repo}/contents/{path}", "-X", "PUT", "--input", "-"],
                input=_json.dumps(body), capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": f"gh api PUT failed: {r.stderr[-500:]}"}
    try:
        resp = _json.loads(r.stdout)
        c = resp.get("content", {})
        return {"path": c.get("path"), "sha": c.get("sha"),
                "html_url": c.get("html_url"),
                "commit": resp.get("commit", {}).get("sha")}
    except Exception as e:
        return {"error": str(e), "raw": r.stdout[:300]}


def _b64_decode(a):
    import base64 as _b64
    s = "".join((a["data"] or "").split())
    s += "=" * ((-len(s)) % 4)
    try:
        return {"text": _b64.b64decode(s).decode("utf-8", "replace")}
    except Exception as e:
        return {"error": str(e), "input_len": len(s)}


def _gh_get_file(a):
    """Fetch a repo file, return decoded text + sha. One call."""
    import base64 as _b64, subprocess as _sp, json as _json
    repo = a["repo"]; path = a["path"]; ref = a.get("ref", "master")
    r = _sp.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}"],
                capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": r.stderr[-400:]}
    try:
        d = _json.loads(r.stdout)
    except Exception as e:
        return {"error": f"json: {e}", "raw": r.stdout[:200]}
    b64 = (d.get("content") or "").replace(chr(10), "").replace(" ", "")
    b64 += "=" * ((-len(b64)) % 4)
    try:
        text = _b64.b64decode(b64).decode("utf-8", "replace")
    except Exception as e:
        return {"error": f"b64: {e}"}
    return {"path": d.get("path"), "sha": d.get("sha"),
            "size": d.get("size"), "content": text}


def _ruff_autofix(text: str) -> tuple[str, list[str]]:
    """Run `ruff check --fix` and `ruff format` on Python text.
    Returns (fixed_text, list_of_changes). Empty list = no changes needed."""
    import shutil, subprocess, tempfile, os
    from pathlib import Path as _P
    ruff = shutil.which("ruff")
    if not ruff:
        return text, []
    tmpdir = os.environ.get("TMPDIR") or str(_P.home() / ".deepcli" / "tmp")
    _P(tmpdir).mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix=".py", dir=tmpdir)
    os.close(fd)
    try:
        _P(tmp).write_text(text)
        changes = []
        # pass 1: safe autofixes
        r1 = subprocess.run([ruff, "check", "--isolated", "--fix", "--exit-zero",
                             "--select", "E9,F401,F811,F841,F821,F822,F823",
                             "--output-format", "concise", tmp],
                            capture_output=True, text=True, timeout=20)
        if r1.stdout.strip():
            changes.extend(l for l in r1.stdout.splitlines() if l.strip())
        # pass 2: formatter
        r2 = subprocess.run([ruff, "format", "--isolated", tmp],
                            capture_output=True, text=True, timeout=20)
        if r2.returncode == 0 and r2.stdout.strip():
            changes.append("formatted (ruff format)")
        return _P(tmp).read_text(), changes
    finally:
        try: os.unlink(tmp)
        except Exception: pass


def _log_autofix(provider: str, model: str, path: str, changes: list[str]):
    """Append one row to the autofix metrics log. Provider/model keyed."""
    import json as _j, datetime as _dt, os as _os
    from pathlib import Path as _P
    log = _P.home() / ".deepcli" / "logs" / "autofix_metrics.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": _dt.datetime.utcnow().isoformat(),
        "provider": provider,          # e.g. "deepseek-web"
        "model": model,                # e.g. "deepseek-chat"
        "path": str(path),
        "n_changes": len(changes),
        "changes": changes[:20],
    }
    with log.open("a") as f:
        f.write(_j.dumps(row) + "\n")


# ─── gh_worktree: structured git worktree + PR flow ─────────────────

WORKTREE_ROOT = HOME / ".deepcli" / "worktrees"


def _wt_safe(branch: str) -> str:
    return branch.replace("/", "-").replace(":", "-").replace(" ", "-")[:60]


def _wt_git(args, cwd, timeout=60):
    import subprocess as _sp
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    return _sp.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                   timeout=timeout, env=env)


def _wt_default_repo() -> str | None:
    """Parse origin URL in $HOME to get owner/name."""
    r = _wt_git(["config", "--get", "remote.origin.url"], str(HOME))
    if r.returncode != 0:
        return None
    url = r.stdout.strip()
    # git@github.com:owner/name.git  or  https://github.com/owner/name.git
    import re as _re
    m = _re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def _gh_worktree(a):
    action = a.get("action", "")
    WORKTREE_ROOT.mkdir(parents=True, exist_ok=True)

    if action == "list":
        r = _wt_git(["worktree", "list", "--porcelain"], str(HOME))
        if r.returncode != 0:
            return {"error": r.stderr[-400:]}
        entries = []
        cur = {}
        for line in r.stdout.splitlines():
            if line.startswith("worktree "):
                if cur: entries.append(cur)
                cur = {"path": line[9:]}
            elif line.startswith("branch "):
                cur["branch"] = line[7:]
        if cur: entries.append(cur)
        return {"worktrees": entries}

    if action == "create":
        branch = a.get("branch") or ""
        base = a.get("base") or "master"
        if not branch:
            return {"error": "branch required"}
        safe = _wt_safe(branch)
        path = WORKTREE_ROOT / safe
        if path.exists():
            return {"error": f"worktree already exists: {path}", "path": str(path)}

        # fetch base
        r = _wt_git(["fetch", "origin", base], str(HOME), timeout=120)
        if r.returncode != 0:
            return {"error": f"fetch failed: {r.stderr[-300:]}"}

        # create worktree with new branch off origin/<base>
        r = _wt_git(["worktree", "add", "-b", branch, str(path), f"origin/{base}"],
                    str(HOME), timeout=120)
        if r.returncode != 0:
            return {"error": f"worktree add failed: {r.stderr[-300:]}"}
        return {"path": str(path), "branch": branch, "base": base,
                "created": True}

    if action == "commit_push_pr":
        branch = a.get("branch") or ""
        message = a.get("message") or "update via agent"
        title = a.get("title") or message.split("\n")[0][:200]
        body = a.get("body") or message
        repo = a.get("repo") or _wt_default_repo()
        draft = bool(a.get("draft"))
        if not branch or not repo:
            return {"error": "branch and repo required"}
        safe = _wt_safe(branch)
        path = WORKTREE_ROOT / safe
        if not path.exists():
            return {"error": f"worktree not found: {path}"}

        # stage and commit
        r = _wt_git(["add", "-A"], str(path))
        if r.returncode != 0:
            return {"error": f"git add: {r.stderr[-300:]}"}
        r = _wt_git(["status", "--porcelain"], str(path))
        if not r.stdout.strip():
            return {"error": "no changes to commit"}
        r = _wt_git(["commit", "-m", message], str(path), timeout=120)
        if r.returncode != 0:
            return {"error": f"git commit: {r.stderr[-300:]}"}

        # push branch
        r = _wt_git(["push", "-u", "origin", branch], str(path), timeout=180)
        if r.returncode != 0:
            return {"error": f"git push: {r.stderr[-400:]}"}

        # create PR via gh
        import subprocess as _sp
        pr_cmd = ["gh", "pr", "create", "--repo", repo,
                  "--base", a.get("base") or "master",
                  "--head", branch,
                  "--title", title, "--body", body]
        if draft: pr_cmd.append("--draft")
        r = _sp.run(pr_cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return {"error": f"gh pr create: {r.stderr[-400:]}",
                    "commit_pushed": True}
        return {"pr_url": r.stdout.strip(), "branch": branch,
                "commit_pushed": True, "repo": repo}

    if action == "remove":
        branch = a.get("branch") or ""
        force = bool(a.get("force", True))
        if not branch:
            return {"error": "branch required"}
        safe = _wt_safe(branch)
        path = WORKTREE_ROOT / safe
        args = ["worktree", "remove", str(path)]
        if force: args.append("--force")
        r = _wt_git(args, str(HOME), timeout=60)
        if r.returncode != 0:
            return {"error": f"worktree remove: {r.stderr[-300:]}"}
        # also delete the local branch reference if it was merged
        return {"removed": True, "branch": branch}

    return {"error": f"unknown action: {action}. Use create|commit_push_pr|remove|list"}


# ─── load-bearing file protection ────────────────────────────────────
# These files are the agent's own implementation. They are NOT writable
# by the agent's own write_file tool. Changes go through a worktree+PR.
PROTECTED_PATHS = (
    HOME / "deepcli" / "deepagent.py",
    HOME / "deepcli" / "agent.py",
    HOME / "deepcli" / "_v1_tools.py",
    HOME / "deepcli" / "_v1_agent.py",
    HOME / "deepcli" / "_v1_files.py",
    HOME / "deepcli" / "_v1_skills.py",
    HOME / "deepcli" / "server.py",
    HOME / "deepcli" / "deepcli" / "core.py",
    HOME / "deepcli" / "session_store.py",
    HOME / "deepcli" / "logs_sync.py",
)


def _is_protected(path) -> bool:
    try:
        q = Path(path).expanduser().resolve()
        for pp in PROTECTED_PATHS:
            if q == pp.resolve():
                return True
    except Exception:
        pass
    return False

DISPATCH = {
    "gh": _gh_call, "run": _run_call,
    "read_file": _read, "write_file": _write,
    "list_dir": _list_dir, "glob": _glob,
    "list_skills": _list_skills, "read_skill": _read_skill,
    "gh_put": _gh_put, "gh_worktree": _gh_worktree, "gh_edit_file": _gh_edit_file, "gh_get_file": _gh_get_file, "b64_decode": _b64_decode,
    "logs_sync": _logs_sync,
}
REQUIRED = {
    "gh":["argv"], "run":["argv"], "read_file":["path"], "write_file":["path","content"],
    "list_dir":["path"], "glob":["path","glob"], "read_skill":["name"],
    "gh_put":["repo","path","content"], "gh_worktree":["action"], "gh_edit_file":["repo","path","edits"], "gh_get_file":["repo","path"], "b64_decode":["data"],
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
    fn = call["function"]["name"]
    try:
        args = json.loads(call["function"]["arguments"] or "{}")
    except Exception as e:
        return f"ERROR parsing args: {e}"
    if fn == "finish":
        return {"finished": True, "summary": args.get("summary", "")}
    missing = [k for k in REQUIRED.get(fn, []) if k not in args or args[k] in (None, "", [])]
    if missing:
        return f"ERROR {fn}: missing required {missing}"
    h = DISPATCH.get(fn)
    if not h: return f"ERROR unknown tool: {fn}"
    try:
        return h(args)
    except (PermissionError, FileNotFoundError) as e:
        return f"BLOCKED: {type(e).__name__}: {e}"
    except Exception as e:
        _log_tool_error(fn, args, e)
        return f"ERROR {type(e).__name__}: {e}"

# ─── DeepSeek call — DIRECT, no server ─────────────────────────────

_RATE_MARKERS = ("Messages too frequent","too frequent","rate limit","please wait")

def _chat_once(messages, tools, model="deepseek-chat", session_id=None,
               parent_message_id=None, system=None, max_continues=3):
    tok = get_token()
    sid = session_id or create_session(tok)

    # flatten OpenAI messages + tools into a single prompt (same as _v1_tools)
    from _v1_tools import _flatten as _fl, _extract_calls as _ex, _strip as _st
    class _M:  # minimal shim to reuse _flatten
        def __init__(self, d): self.role = d["role"]; self.content = d.get("content"); self.tool_calls = d.get("tool_calls"); self.tool_call_id = d.get("tool_call_id"); self.name = d.get("name")
    class _T:
        def __init__(self, d): self.type = "function"
        # delegate
        # we need .function.name / .description / .parameters
    from _v1_tools import _Tool
    class _TM:
        def __init__(self, d): self.function = type("F",(),{"name":d["function"]["name"],"description":d["function"].get("description",""),"parameters":d["function"].get("parameters") or {"type":"object","properties":{}}})()
    msgs = [_M(m) for m in messages]
    tls  = [_TM(t) for t in tools] if tools else None
    prompt = _fl(msgs, tls)

    # rate-limit aware retry
    delays = [30] * 10  # fixed 30s, up to 10 attempts (reinstatement model)
    reply = ""
    parent_id = parent_message_id
    last_rest = 0.0
    last_kind = "start"
    for phase, wait, burst_i in _retry_plan(max_bursts=6):
        if wait:
            time.sleep(wait)
        try:
            reply = chat_completion(tok, prompt, sid,
                                    parent_message_id=parent_id,
                                    thinking=("reasoner" in model),
                                    search=False, auto_continue=True, max_continues=max_continues)
        except (ConnectionError, ConnectionResetError, TimeoutError, OSError) as e:
            last_kind = "transport"
            last_rest = wait
            print(f"    [retry {phase} #{burst_i} wait={wait:.1f}s] {type(e).__name__}")
            continue

        if any(m.lower() in (reply or "").lower() for m in _RATE_MARKERS):
            last_kind = "ratelimit"
            last_rest = wait
            print(f"    [retry {phase} #{burst_i} wait={wait:.1f}s] rate-limit text")
            continue

        # success
        if last_kind != "start":
            _record_retry("success", last_rest, burst_i, last_kind)
        break
    else:
        _record_retry("failure", last_rest, -1, last_kind)
        raise RuntimeError(f"gave up after retries: {last_kind}")

    calls = _ex(reply) if tools else []
    content = _st(reply)

    # capture assistant message_id for the next turn's parent
    try:
        from deepcli.core import get_history as _hist
        h = _hist(tok, sid, force_refresh=True)
        for m in reversed(h):
            if m.get("role", "").upper() == "ASSISTANT":
                parent_id = m.get("message_id")
                break
    except Exception:
        parent_id = None

    return sid, content, calls, parent_id


def _notify(kind: str, title: str, content: str, *, priority: str = "default"):
    """Best-effort Termux:API notification. Uses fixed id so start→finish replaces."""
    import subprocess as _sp, shutil as _sh
    if not _sh.which("termux-notification"):
        return
    try:
        _sp.Popen([
            "termux-notification",
            "--id", f"deepagent-{kind}",
            "--channel", "deepagent",
            "--title", title,
            "--content", content[:400],
            "--priority", priority,
        ], stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
    except Exception:
        pass


def _autosnapshot(reason: str = "auto"):
    """Spawn agent-snapshot in background; snapshot tool itself handles diff-gating."""
    import subprocess as _sp, shutil as _sh
    exe = _sh.which("agent-snapshot")
    if not exe:
        return
    try:
        _sp.Popen([exe, "--reason", reason], stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
    except Exception:
        pass


def loop(task, dry_run=False, model="deepseek-chat", task_path=None, fresh=False):
    """Loop until finish OR no-progress detected. Ceiling is safety, not policy."""
    print(f"\n▶ task: {task}\n")
    _t0 = time.time()
    key = session_store.task_key(task, task_path)
    _notify("run", "🤖 Agent starting",
            f"task: {task[:120]}\nsrc: {os.environ.get('AGENT_SOURCE','manual')}")

    if fresh:
        session_store.forget(key)
        print(f"  [session] fresh (forced, key={key})")
    else:
        _rec = session_store.load(key)
        if _rec and _rec.get("session_id"):
            sid = _rec["session_id"]
            print(f"  [session] resuming {sid[:12]}…  runs={_rec.get('runs',0)}")
        else:
            sid = None
            print(f"  [session] fresh (key={key})")
    SAFETY_CEILING = int(os.environ.get("AGENT_SAFETY_CEILING", "60"))
    NO_PROGRESS_LIMIT = int(os.environ.get("AGENT_NO_PROGRESS_LIMIT", "5"))
    msgs = [{"role":"user","content":task}]
    sid = None
    parent_id = None
    seen_sigs = []          # signatures of (tool, args) to detect repeats
    no_progress = 0
    for step in range(SAFETY_CEILING):
        print(f"── step {step+1}/<dynamic> ──")
        if step > 0 and IDLE_SLEEP: time.sleep(IDLE_SLEEP)
        sid, content, calls, next_parent = _chat_once(
            msgs, TOOLS, model=model, session_id=sid,
            parent_message_id=parent_id)
        parent_id = next_parent
        if content:
            print(f"  (assistant): {content[:200]}")
        if not calls:
            print(f"\n✔ done (no tool calls)\n{content}\n")
            return content
        am = {"role":"assistant","content":content or None,
              "tool_calls":[{"id":c["id"],"type":"function",
                             "function":{"name":c["function"]["name"],
                                         "arguments":c["function"]["arguments"]}} for c in calls]}
        msgs.append(am)
        step_had_progress = False
        for c in calls:
            fn = c["function"]["name"]
            raw = c["function"]["arguments"]
            sig = f"{fn}::{raw[:200]}"
            print(f"  ▶ {fn}({raw[:120]})")
            if sig in seen_sigs[-12:]:
                print(f"    [repeat blocked — skipping duplicate call]")
                msgs.append({"role":"tool","tool_call_id":c["id"],
                             "content": "SKIPPED: this exact call was already made; result is in prior tool message. Do not repeat."})
                continue
            seen_sigs.append(sig)
            step_had_progress = True
            if dry_run: continue
            result = execute(c)
            if fn == "finish":
                print(f"\n✔ FINISH\n{result.get('summary','')}\n")
                if sid and not dry_run:
                    session_store.save(key, sid, meta={"last_task": task[:200]})
                    print(f"  [session] saved {sid[:12]}\u2026 for key={key}")
                try:
                    _elapsed = round(time.time() - _t0, 1)
                except Exception:
                    _elapsed = 0.0
                _autosnapshot("finish")
                _notify("run", "✅ Agent done",
                        f"sid={sid[:12] if sid else '?'}  elapsed={_elapsed}s\n{result.get('summary','')[:200]}",
                        priority="high")
                return result.get("summary","")
            printable = json.dumps(result) if not isinstance(result, str) else result
            # non-error results count as progress
            if not printable.lstrip().startswith(("ERROR", "BLOCKED", "{\"error\"")):
                step_had_progress = True
            # no cap — see context size of the underlying model
            print(f"    ← {printable[:300]}")
            msgs.append({"role":"tool","tool_call_id":c["id"],"content":printable})
        if step_had_progress:
            no_progress = 0
        else:
            no_progress += 1
            print(f"    [no-progress {no_progress}/{NO_PROGRESS_LIMIT}]")
            if no_progress >= NO_PROGRESS_LIMIT:
                print(f"\n✗ stalled after {step+1} steps (no progress)")
                return content or ""
    print(f"\n✗ hit SAFETY_CEILING={SAFETY_CEILING}\n")
    return ""




if __name__ == "__main__":
    argv = sys.argv[1:]
    dry = False
    fresh = False
    task_path = None
    if "--dry-run" in argv:
        dry = True; argv.remove("--dry-run")
    if "--fresh" in argv:
        fresh = True; argv.remove("--fresh")
    if "--task-file" in argv:
        i = argv.index("--task-file")
        if i + 1 < len(argv):
            task_path = argv[i+1]
            del argv[i:i+2]
    if not argv:
        print("usage: deepagent.py [--dry-run] [--fresh] [--task-file P] \"<task>\"")
        sys.exit(2)
    loop(" ".join(argv), dry_run=dry, task_path=task_path, fresh=fresh)
