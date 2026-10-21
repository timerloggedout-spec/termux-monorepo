"""/v1/files — read/write/list under allowlisted $HOME subtrees."""
import base64, os, sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

HOME = Path.home()
TOKEN_FILE = HOME / ".deepcli" / "hub.token"

# directories the agent may write to without escalation
WRITE_ALLOW = [
    HOME / ".deepcli",
    HOME / "deepcli" / "tasks",
    HOME / "deepcli" / "agent_workspaces",
    HOME / ".deepcli" / "logs",
]
# directories the agent may read from (broad but not /etc or /data/data/other-apps)
READ_ALLOW = [HOME]  # whole home, but no symlink escape
MAX_READ_BYTES  = 512 * 1024       # 512 KB
MAX_WRITE_BYTES = 512 * 1024

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


router = APIRouter(prefix="/v1/files", tags=["files"])
_bearer = HTTPBearer(auto_error=False)


def _auth(creds: HTTPAuthorizationCredentials = Depends(_bearer)):
    expected = os.environ.get("HUB_TOKEN")
    if not expected and TOKEN_FILE.exists():
        expected = TOKEN_FILE.read_text().strip()
    if not expected:
        raise HTTPException(500, "hub token not configured")
    if creds is None or creds.credentials != expected:
        raise HTTPException(401, "invalid token")


def _safe(path_str: str, *, allow_list) -> Path:
    p = Path(path_str).expanduser().resolve()
    # must live under one of the allowed roots
    for root in allow_list:
        try:
            p.relative_to(root.resolve())
            return p
        except ValueError:
            continue
    raise HTTPException(403, f"path outside allowed roots: {p}")


class ReadReq(BaseModel):
    path: str
    max_bytes: Optional[int] = MAX_READ_BYTES


class WriteReq(BaseModel):
    path: str
    content: str
    mode: str = "text"   # text | base64


class ListReq(BaseModel):
    path: str
    glob: Optional[str] = None


@router.post("/read", dependencies=[Depends(_auth)])
def read_file(req: ReadReq):
    p = _safe(req.path, allow_list=READ_ALLOW)
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "file not found")
    cap = min(req.max_bytes or MAX_READ_BYTES, MAX_READ_BYTES)
    data = p.read_bytes()[:cap]
    try:
        text = data.decode("utf-8")
        return {"path": str(p), "size": p.stat().st_size, "truncated": p.stat().st_size > cap, "content": text}
    except UnicodeDecodeError:
        return {"path": str(p), "size": p.stat().st_size, "truncated": p.stat().st_size > cap,
                "content_base64": base64.b64encode(data).decode()}


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
def _ruff_check(path, text):
    """Reject Python writes that don't compile."""
    if not str(path).endswith(".py"):
        return None
    try:
        compile(text, str(path), "exec")
        return None
    except SyntaxError as e:
        return f"SyntaxError line {e.lineno}: {e.msg} (offset {e.offset})"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


@router.post("/write", dependencies=[Depends(_auth)])
def write_file(req: WriteReq):
    p = _safe(req.path, allow_list=WRITE_ALLOW)
    if req.mode == "base64":
        data = base64.b64decode(req.content)
    else:
        data = req.content.encode("utf-8")
    if len(data) > MAX_WRITE_BYTES:
        raise HTTPException(413, f"content too large ({len(data)} > {MAX_WRITE_BYTES})")
    text_for_lint = data.decode("utf-8", "replace")
    lint_err = _ruff_check(p, text_for_lint)
    if lint_err:
        raise HTTPException(400, f"refusing to write invalid Python: {lint_err}")
    if str(p).endswith(".py") and os.environ.get("AGENT_AUTOFIX", "1") == "1":
        fixed, changes = _ruff_autofix(text_for_lint)
        if changes:
            _log_autofix("deepseek-web", os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                         p, changes)
            data = fixed.encode()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    try:
        os.chmod(p, 0o600)
    except Exception:
        pass
    return {"path": str(p), "bytes": len(data)}


@router.post("/list", dependencies=[Depends(_auth)])
def list_dir(req: ListReq):
    p = _safe(req.path, allow_list=READ_ALLOW)
    if not p.exists() or not p.is_dir():
        raise HTTPException(404, "dir not found")
    entries = []
    for child in sorted(p.iterdir()):
        try:
            st = child.stat()
            entries.append({
                "name": child.name,
                "type": "dir" if child.is_dir() else "file",
                "size": st.st_size,
                "mtime": int(st.st_mtime),
            })
        except Exception:
            pass
    return {"path": str(p), "entries": entries[:500]}


@router.post("/glob", dependencies=[Depends(_auth)])
def glob_paths(req: ListReq):
    if not req.glob:
        raise HTTPException(400, "glob pattern required")
    base = _safe(req.path, allow_list=READ_ALLOW)
    hits = []
    for f in base.glob(req.glob):
        try:
            hits.append(str(f.relative_to(base)))
        except Exception:
            hits.append(str(f))
        if len(hits) >= 500: break
    return {"base": str(base), "matches": hits}

class GhPutReq(BaseModel):
    repo: str                      # "owner/name"
    path: str                      # ".github/workflows/x.yml"
    content: str
    message: str = "update via agent"
    branch: str = "master"

class B64Req(BaseModel):
    data: str

@router.post("/gh_put", dependencies=[Depends(_auth)])
def gh_put(req: GhPutReq):
    """Commit content to repo via GitHub API. Auto-detects existing sha."""
    import base64 as _b64, json as _json, subprocess as _sp
    # 1. existing sha (if file exists)
    r = _sp.run(["gh", "api", f"repos/{req.repo}/contents/{req.path}?ref={req.branch}",
                 "--jq", ".sha"], capture_output=True, text=True)
    sha = r.stdout.strip() if r.returncode == 0 else ""
    # 2. build body
    body = {"message": req.message,
            "content": _b64.b64encode(req.content.encode()).decode(),
            "branch": req.branch}
    if sha and sha != "null" and sha:
        body["sha"] = sha
    # 3. PUT
    r = _sp.run(["gh", "api", f"repos/{req.repo}/contents/{req.path}",
                 "-X", "PUT", "--input", "-"],
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

@router.post("/b64_decode", dependencies=[Depends(_auth)])
def b64_decode(req: B64Req):
    import base64 as _b64
    s = "".join(req.data.split())
    s += "=" * ((-len(s)) % 4)   # add padding
    try:
        return {"text": _b64.b64decode(s).decode("utf-8", "replace")}
    except Exception as e:
        return {"error": str(e), "input_len": len(s)}


class GhGetReq(BaseModel):
    repo: str
    path: str
    ref: str = "master"


@router.post("/gh_get_file", dependencies=[Depends(_auth)])
def gh_get_file(req: GhGetReq):
    """Fetch a repo file and return decoded text + sha in one call."""
    import base64 as _b64, json as _json, subprocess as _sp
    r = _sp.run(["gh", "api", f"repos/{req.repo}/contents/{req.path}?ref={req.ref}"],
                capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": r.stderr[-400:]}
    try:
        d = _json.loads(r.stdout)
    except Exception as e:
        return {"error": f"json: {e}", "raw": r.stdout[:200]}
    b64 = (d.get("content") or "").replace("\n", "").replace(" ", "")
    b64 += "=" * ((-len(b64)) % 4)
    try:
        text = _b64.b64decode(b64).decode("utf-8", "replace")
    except Exception as e:
        return {"error": f"b64: {e}"}
    return {"path": d.get("path"), "sha": d.get("sha"),
            "size": d.get("size"), "content": text}

class GhEditReq(BaseModel):
    repo: str
    path: str
    edits: list
    message: str = ""
    branch: str = "master"
    create_if_missing: bool = False


@router.post("/gh_edit_file", dependencies=[Depends(_auth)])
def gh_edit_file(req: GhEditReq):
    """Fetch, apply {old,new} edits, push. Server-side read-modify-write."""
    import subprocess as _sp, json as _json, base64 as _b64
    if not req.message:
        req.message = f"edit {req.path}"
    r = _sp.run(["gh", "api", f"repos/{req.repo}/contents/{req.path}?ref={req.branch}"],
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
    elif req.create_if_missing and req.edits and not req.edits[0].get("old"):
        text = req.edits[0].get("new", "")
    else:
        return {"error": f"file not found: {req.path}"}

    applied, errors = [], []
    for i, ed in enumerate(req.edits):
        old = ed.get("old", ""); new = ed.get("new", "")
        if not old and not req.create_if_missing:
            errors.append(f"edit[{i}]: missing old (use gh_put to create)"); continue
        n = text.count(old)
        if n == 0:
            errors.append(f"edit[{i}]: old not found"); continue
        if n > 1:
            errors.append(f"edit[{i}]: old appears {n}x — must be unique"); continue
        text = text.replace(old, new, 1); applied.append(i)

    if errors and not applied:
        return {"error": "no edits applied", "details": errors}
    if not applied:
        return {"error": "no edits specified"}

    body = {"message": req.message,
            "content": _b64.b64encode(text.encode()).decode(),
            "branch": req.branch}
    if cur_sha:
        body["sha"] = cur_sha
    r = _sp.run(["gh", "api", f"repos/{req.repo}/contents/{req.path}", "-X", "PUT", "--input", "-"],
                input=_json.dumps(body), capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": f"PUT failed: {r.stderr[-400:]}", "applied": applied, "errors": errors}
    resp = _json.loads(r.stdout)
    c = resp.get("content", {})
    return {"path": c.get("path"), "sha": c.get("sha"),
            "html_url": c.get("html_url"),
            "commit": resp.get("commit", {}).get("sha"),
            "applied": applied, "errors": errors}
