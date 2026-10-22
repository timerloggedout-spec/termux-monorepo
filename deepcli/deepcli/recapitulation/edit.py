"""edit — gh_put / gh_get_file / gh_edit_file / gh_worktree / b64_decode."""

from .runtime import (
    WORKTREE_ROOT,
    _wt_git,
    _wt_safe,
    _wt_default_repo,  # noqa: F401
)


def _gh_edit_file(a):
    """Fetch a file, apply {old->new} replacements, push. Server-side RMW."""
    import subprocess as _sp
    import json as _json
    import base64 as _b64

    repo = a["repo"]
    path = a["path"]
    edits = a.get("edits") or []
    msg = a.get("message", f"edit {path}")
    branch = a.get("branch", "master")
    create = bool(a.get("create_if_missing"))

    r = _sp.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}"],
        capture_output=True,
        text=True,
    )
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

    applied, errors = [], []
    for i, ed in enumerate(edits):
        old = ed.get("old", "")
        new = ed.get("new", "")
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

    body = {
        "message": msg,
        "content": _b64.b64encode(text.encode()).decode(),
        "branch": branch,
    }
    if cur_sha:
        body["sha"] = cur_sha
    r = _sp.run(
        ["gh", "api", f"repos/{repo}/contents/{path}", "-X", "PUT", "--input", "-"],
        input=_json.dumps(body),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return {
            "error": f"PUT failed: {r.stderr[-400:]}",
            "applied": applied,
            "errors": errors,
        }
    resp = _json.loads(r.stdout)
    c = resp.get("content", {})
    return {
        "path": c.get("path"),
        "sha": c.get("sha"),
        "html_url": c.get("html_url"),
        "commit": resp.get("commit", {}).get("sha"),
        "applied": applied,
        "errors": errors,
    }


def _gh_put(a):
    """Commit content to repo via gh api PUT. Auto-detects existing sha."""
    import base64 as _b64
    import json as _json
    import subprocess as _sp

    repo = a["repo"]
    path = a["path"]
    content = a["content"]
    msg = a.get("message", f"update {path}")
    branch = a.get("branch", "master")
    r = _sp.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}", "--jq", ".sha"],
        capture_output=True,
        text=True,
    )
    sha = r.stdout.strip() if r.returncode == 0 else ""
    body = {
        "message": msg,
        "content": _b64.b64encode(content.encode()).decode(),
        "branch": branch,
    }
    if sha and sha != "null":
        body["sha"] = sha
    r = _sp.run(
        ["gh", "api", f"repos/{repo}/contents/{path}", "-X", "PUT", "--input", "-"],
        input=_json.dumps(body),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return {"error": f"gh api PUT failed: {r.stderr[-500:]}"}
    try:
        resp = _json.loads(r.stdout)
        c = resp.get("content", {})
        return {
            "path": c.get("path"),
            "sha": c.get("sha"),
            "html_url": c.get("html_url"),
            "commit": resp.get("commit", {}).get("sha"),
        }
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
    import base64 as _b64
    import subprocess as _sp
    import json as _json

    repo = a["repo"]
    path = a["path"]
    ref = a.get("ref", "master")
    r = _sp.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}"],
        capture_output=True,
        text=True,
    )
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
    return {
        "path": d.get("path"),
        "sha": d.get("sha"),
        "size": d.get("size"),
        "content": text,
    }


from .worktree import _gh_worktree  # noqa: F401,E402  (CAB B->A: machinery moved to worktree.py)
