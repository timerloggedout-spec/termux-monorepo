"""tools.py — TOOLS spec, DISPATCH, REQUIRED, execute, feedback, finish-validation.

Extracted from deepagent.py. File-op handlers live here; edit/lint/retry/runtime
symbols are imported from siblings rather than re-copied.
"""

import json
import os
import sys

from .runtime import (
    HOME,
    READ_ALLOW,
    WRITE_ALLOW,
    MAX_RW_BYTES,
    RUN_ALLOWED_BINS,
    SKILL_ROOTS,
    _safe,
    _is_protected,
)
from .lint import _ruff_check, _ruff_autofix, _log_autofix
from .edit import (
    _gh_put,
    _gh_get_file,
    _gh_edit_file,
    _gh_worktree,
    _b64_decode,
)

_AUTOFIX_ENABLED = os.environ.get("AGENT_AUTOFIX", "1") == "1"
_CURRENT_SESSION_CTX = {}
_AUTO_FEEDBACK = os.environ.get("AGENT_AUTO_FEEDBACK", "0") == "1"
_AUTO_FEEDBACK_SKIP_OK = os.environ.get("AGENT_AUTO_FEEDBACK_SKIP_OK", "1") == "1"
_AUTO_FEEDBACK_CAT = {
    "ratelimit": ("service-stability", "rate-limited; reply interrupted"),
    "transport": ("service-stability", "transport error; reply interrupted"),
    "truncation": ("task-result", "stream ended without FINISHED marker"),
}

try:
    from deepcli._v1_hindsight import build_hindsight_tools as _hs_build

    _HINDSIGHT_AVAILABLE = True
except Exception:
    _HINDSIGHT_AVAILABLE = False


def _hindsight_active():
    return _HINDSIGHT_AVAILABLE and os.environ.get("HINDSIGHT_BASE_URL")


_gh = None


def _broker():
    global _gh
    if _gh is None:
        from src.gh_broker import GhBroker

        _gh = GhBroker()
    return _gh


def _spec(name, desc, props, required=None):
    fn = {
        "name": name,
        "description": desc,
        "parameters": {"type": "object", "properties": props},
    }
    if required:
        fn["parameters"]["required"] = required
    return {"type": "function", "function": fn}


TOOLS = [
    _spec(
        "feedback",
        "Submit GOOD/BAD/None feedback + optional comment + category for an assistant message. category only meaningful when rating=BAD. Args: rating, message_id (optional, defaults to last assistant), category (optional), content (optional).",
        {
            "rating": {
                "type": "string",
                "enum": ["GOOD", "BAD", "NONE", "LIKE", "DISLIKE"],
            },
            "message_id": {"type": "integer"},
            "category": {
                "type": "string",
                "enum": [
                    "task-result",
                    "instruction-following",
                    "product-interaction",
                    "service-stability",
                    "resource-cost",
                    "security-privacy-permission",
                    "other",
                ],
            },
            "content": {"type": "string"},
        },
        ["rating"],
    ),
    _spec(
        "gh",
        "Run a GitHub CLI command. argv = list of gh args.",
        {"argv": {"type": "array", "items": {"type": "string"}}},
        ["argv"],
    ),
    _spec(
        "run",
        "Run a shell command on Termux. First argv element in allowlist.",
        {
            "argv": {"type": "array", "items": {"type": "string"}},
            "cwd": {"type": "string"},
            "idle_timeout_s": {"type": "integer"},
            "hard_timeout_s": {"type": "integer"},
        },
        ["argv"],
    ),
    _spec(
        "read_file",
        "Read a file under $HOME.",
        {"path": {"type": "string"}, "max_bytes": {"type": "integer"}},
        ["path"],
    ),
    _spec(
        "write_file",
        "Write to a file under $HOME/.deepcli, $HOME/deepcli/tasks, or $HOME/deepcli/agent_workspaces.",
        {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "mode": {"type": "string", "enum": ["text", "base64"]},
        },
        ["path", "content"],
    ),
    _spec(
        "list_dir",
        "List entries in a directory under $HOME.",
        {"path": {"type": "string"}},
        ["path"],
    ),
    _spec(
        "glob",
        "Glob a pattern under a base dir.",
        {"path": {"type": "string"}, "glob": {"type": "string"}},
        ["path", "glob"],
    ),
    _spec("list_skills", "List installed skills.", {}),
    _spec(
        "read_skill",
        "Read a skill's SKILL.md and its files.",
        {"name": {"type": "string"}},
        ["name"],
    ),
    _spec("logs_sync", "Push ~/.deepcli/logs/* to the repo via Git tree API.", {}),
    _spec(
        "gh_get_file",
        "Fetch a file from a GitHub repo. Returns {path, sha, size, content} where content is the DECODED text. Use THIS instead of gh api ... --jq .content + b64_decode. Args: repo='owner/name', path='.github/workflows/x.yml', ref='master'.",
        {
            "repo": {"type": "string"},
            "path": {"type": "string"},
            "ref": {"type": "string"},
        },
        ["repo", "path"],
    ),
    _spec(
        "gh_edit_file",
        "Surgical edit of a repo file. Fetches, applies each {old,new} replacement (each 'old' must appear exactly once), pushes. Use this INSTEAD of gh_get_file+gh_put when you only need to change a few lines. Args: repo, path, edits=[{old,new}], message, branch (default master).",
        {
            "repo": {"type": "string"},
            "path": {"type": "string"},
            "edits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "old": {"type": "string"},
                        "new": {"type": "string"},
                    },
                    "required": ["old", "new"],
                },
            },
            "message": {"type": "string"},
            "branch": {"type": "string"},
            "create_if_missing": {"type": "boolean"},
        },
        ["repo", "path", "edits"],
    ),
    _spec(
        "gh_worktree",
        "Manage git worktrees for PR-based changes. Actions: (1) action='create' branch=<name> base=master -> makes ~/.deepcli/worktrees/<branch>; edit files there; (2) action='commit_push_pr' branch=<name> message=<commit msg> title=<pr title> body=<pr body> -> commit, push, open PR; (3) action='remove' branch=<name> -> clean up; (4) action='list'. Use this for multi-file changes or anything needing a local test run; use gh_edit_file for tiny single-file fixes.",
        {
            "action": {
                "type": "string",
                "enum": ["create", "commit_push_pr", "remove", "list"],
            },
            "branch": {"type": "string"},
            "base": {"type": "string"},
            "message": {"type": "string"},
            "title": {"type": "string"},
            "body": {"type": "string"},
            "repo": {"type": "string"},
            "draft": {"type": "boolean"},
            "force": {"type": "boolean"},
        },
        ["action"],
    ),
    _spec(
        "gh_put",
        "Commit a file to a GitHub repo via API. Handles base64 + existing sha detection automatically. Use THIS instead of shelling out to base64/curl. Args: repo='owner/name', path='.github/workflows/x.yml', content='<full file text>', message='<commit msg>', branch='master'.",
        {
            "repo": {"type": "string"},
            "path": {"type": "string"},
            "content": {"type": "string"},
            "message": {"type": "string"},
            "branch": {"type": "string"},
        },
        ["repo", "path", "content"],
    ),
    _spec(
        "b64_decode",
        "Decode a base64 string to UTF-8 text. Use after gh api ... --jq .content to get the file body. Args: data='<base64>'.",
        {"data": {"type": "string"}},
        ["data"],
    ),
    *([] if not _hindsight_active() else [spec.schema for spec in _hs_build()]),
    _spec(
        "finish",
        "Call when done. Pass 'summary'. No tool calls after.",
        {"summary": {"type": "string"}},
        ["summary"],
    ),
]


def _gh_call(a):
    r = _broker().run(a.get("argv", []))
    return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr}


def _run_call(a):
    import subprocess
    import signal
    import time as _t

    argv = a.get("argv", [])
    if not argv:
        return {"rc": -1, "error": "argv empty"}
    binname = argv[0].rsplit("/", 1)[-1]
    if binname not in RUN_ALLOWED_BINS:
        return {"rc": -1, "error": f"binary '{binname}' not allowlisted"}
    cwd = a.get("cwd") or str(HOME)
    if not cwd.startswith(str(HOME)):
        return {"rc": -1, "error": "cwd outside home"}
    idle = int(a.get("idle_timeout_s", 30))
    hard = int(a.get("hard_timeout_s", 300))
    p = subprocess.Popen(
        argv,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        preexec_fn=os.setsid,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
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
                os.killpg(p.pid, signal.SIGKILL)
                break
            for key, _ in sel.select(timeout=1.0):
                line = key.fileobj.readline()
                if not line:
                    sel.unregister(key.fileobj)
                    continue
                last = _t.monotonic()
                (out if key.data == "o" else err).append(line)
            if _t.monotonic() - last > idle:
                try:
                    os.killpg(p.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(p.pid, signal.SIGTERM)
                        p.wait(3)
                    except Exception:
                        os.killpg(p.pid, signal.SIGKILL)
                break
    finally:
        try:
            p.wait(timeout=3)
        except Exception:
            pass
    return {
        "rc": p.returncode,
        "stdout": "".join(out)[-8000:],
        "stderr": "".join(err)[-2000:],
    }


def _read(a):
    q = _safe(a["path"], READ_ALLOW)
    if not q.is_file():
        return {"error": "not a file", "path": str(q)}
    cap = min(int(a.get("max_bytes") or MAX_RW_BYTES), MAX_RW_BYTES)
    data = q.read_bytes()[:cap]
    try:
        return {"path": str(q), "content": data.decode()}
    except UnicodeDecodeError:
        import base64

        return {"path": str(q), "content_base64": base64.b64encode(data).decode()}


def _write(a):
    import base64

    if _is_protected(a["path"]):
        return {
            "error": "BLOCKED: this file is load-bearing (agent core); changes require a worktree+PR",
            "path": str(a["path"]),
            "hint": "use gh_worktree action=create, edit there, then action=commit_push_pr",
        }
    q = _safe(a["path"], WRITE_ALLOW)
    data = (
        base64.b64decode(a["content"])
        if a.get("mode") == "base64"
        else a["content"].encode()
    )
    if len(data) > MAX_RW_BYTES:
        raise ValueError(f"content too large: {len(data)}")
    text_for_lint = (
        data.decode("utf-8", "replace") if isinstance(data, bytes) else str(data)
    )
    lint_err = _ruff_check(q, text_for_lint)
    if lint_err:
        return {
            "error": f"refusing to write invalid Python: {lint_err}",
            "path": str(q),
        }
    if str(q).endswith(".py") and _AUTOFIX_ENABLED:
        fixed, changes = _ruff_autofix(text_for_lint)
        if changes:
            _log_autofix(
                "deepseek-web",
                os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                q,
                changes,
            )
            data = fixed.encode()
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(data)
    try:
        os.chmod(q, 0o600)
    except Exception:
        pass
    return {"path": str(q), "bytes": len(data)}


def _list_dir(a):
    q = _safe(a["path"], READ_ALLOW)
    if not q.is_dir():
        return {"error": "not a dir"}
    return {
        "path": str(q),
        "entries": sorted(
            [
                {
                    "name": c.name,
                    "type": "dir" if c.is_dir() else "file",
                    "size": c.stat().st_size,
                }
                for c in q.iterdir()
                if not c.is_symlink() or c.exists()
            ],
            key=lambda x: x["name"],
        )[:500],
    }


def _glob(a):
    q = _safe(a["path"], READ_ALLOW)
    hits = []
    for f in q.glob(a["glob"]):
        try:
            hits.append(str(f.relative_to(q)))
        except ValueError:
            hits.append(str(f))
        if len(hits) >= 500:
            break
    return {"base": str(q), "matches": hits}


def _list_skills(_a=None):
    seen = {}
    for root in SKILL_ROOTS:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
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
                                if line.startswith("name:"):
                                    name = (
                                        line.split(":", 1)[1]
                                        .strip()
                                        .strip('"')
                                        .strip("'")
                                    )
                                if line.startswith("description:"):
                                    desc = (
                                        line.split(":", 1)[1]
                                        .strip()
                                        .strip('"')
                                        .strip("'")[:200]
                                    )
                        except Exception:
                            pass
                    if name not in seen:
                        seen[name] = {"name": name, "dir": str(d), "description": desc}
                    break
    return {"skills": sorted(seen.values(), key=lambda x: x["name"])}


def _read_skill(a):
    name = a["name"]
    for root in SKILL_ROOTS:
        d = root / name
        if not d.is_dir():
            continue
        for fn in ("SKILL.md", "skill.md"):
            f = d / fn
            if f.exists():
                return {
                    "name": name,
                    "dir": str(d),
                    "body": f.read_text(errors="replace")[: 256 * 1024],
                    "files": [
                        str(x.relative_to(d)) for x in d.rglob("*") if x.is_file()
                    ][:50],
                }
    raise FileNotFoundError(name)


def _logs_sync(_a=None):
    import subprocess

    r = subprocess.run(
        [sys.executable, str(HOME / "deepcli" / "logs_sync.py")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr[-500:]}


def _feedback_call(a):
    """Handler for the feedback tool. Uses _CURRENT_SESSION_CTX set by _chat_once."""
    ctx = _CURRENT_SESSION_CTX or {}
    tok = ctx.get("token")
    sid = ctx.get("sid")
    if not tok or not sid:
        return {"error": "no active session context"}
    from deepcli.core import submit_feedback, get_last_assistant_message_id

    mid = a.get("message_id")
    if mid is None:
        mid = get_last_assistant_message_id(tok, sid)
        if mid is None:
            return {"error": "no assistant message_id available"}
    try:
        return submit_feedback(
            tok,
            sid,
            int(mid),
            rating=a.get("rating", "BAD"),
            content=a.get("content"),
            category=a.get("category"),
        )
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


def _auto_feedback(tok, sid, kind):
    """Env-gated auto-BAD on interrupted turns. Silent on any failure."""
    if not _AUTO_FEEDBACK:
        return None
    if kind == "ok" and _AUTO_FEEDBACK_SKIP_OK:
        return None
    if kind not in _AUTO_FEEDBACK_CAT:
        return None
    cat, default_msg = _AUTO_FEEDBACK_CAT[kind]
    try:
        from deepcli.core import submit_feedback, get_last_assistant_message_id

        mid = get_last_assistant_message_id(tok, sid)
        if mid is None:
            return None
        return submit_feedback(
            tok, sid, int(mid), rating="BAD", category=cat, content=default_msg
        )
    except Exception:
        return None


DISPATCH = {
    "feedback": _feedback_call,
    "gh": _gh_call,
    "run": _run_call,
    "read_file": _read,
    "write_file": _write,
    "list_dir": _list_dir,
    "glob": _glob,
    "list_skills": _list_skills,
    "read_skill": _read_skill,
    "gh_put": _gh_put,
    "gh_worktree": _gh_worktree,
    "gh_edit_file": _gh_edit_file,
    "gh_get_file": _gh_get_file,
    "b64_decode": _b64_decode,
    "logs_sync": _logs_sync,
    **(
        {}
        if not _hindsight_active()
        else {spec.name: spec.handler for spec in _hs_build()}
    ),
}
REQUIRED = {
    "feedback": ["rating"],
    "gh": ["argv"],
    "run": ["argv"],
    "read_file": ["path"],
    "write_file": ["path", "content"],
    "list_dir": ["path"],
    "glob": ["path", "glob"],
    "read_skill": ["name"],
    "gh_put": ["repo", "path", "content"],
    "gh_worktree": ["action"],
    "gh_edit_file": ["repo", "path", "edits"],
    "gh_get_file": ["repo", "path"],
    "b64_decode": ["data"],
}


def _log_tool_error(fn, args, exc):
    """Append tool-implementation errors (not policy blocks) to a jsonl for post-mortem.
    Policy blocks (PermissionError, FileNotFoundError, HTTPException 4xx) do NOT go here."""
    import traceback as _tb
    import datetime as _dt
    import json as _j
    from pathlib import Path as _P

    log = _P.home() / ".deepcli" / "logs" / "tool_errors.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    try:
        args_head = (
            _j.dumps(args)[:300] if not isinstance(args, str) else str(args)[:300]
        )
    except Exception:
        args_head = str(args)[:300]
    row = {
        "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "pid": os.getpid(),
        "tool": fn,
        "args_head": args_head,
        "exc": type(exc).__name__,
        "msg": str(exc)[:500],
        "tb": _tb.format_exc()[-2000:],
    }
    with log.open("a") as f:
        f.write(_j.dumps(row) + "\n")
    try:
        log.chmod(0o600)
    except Exception:
        pass


_FINISH_PLACEHOLDERS = {
    "placeholder",
    "todo",
    "tbd",
    "test",
    "done",
    "ok",
    "n/a",
    "none",
    "finished",
    "complete",
    "completed",
    "success",
}

_MAYBE_CONTINUE_MAX = int(os.environ.get("AGENT_CONTINUE_MAX", "3"))


def _validate_finish_summary(summary):
    """Reject placeholder / too-short / signal-free finish summaries.
    Returns None if acceptable, or a string explaining the rejection."""
    s = (summary or "").strip()
    if len(s) < 20:
        return f"summary too short ({len(s)} chars, need >=20): {s!r}"
    if s.lower() in _FINISH_PLACEHOLDERS:
        return f"summary is a placeholder: {s!r}"
    signals = [
        "{",
        "}",
        "pr",
        "branch",
        "pkg",
        "files",
        "shims",
        "commit",
        "invariant",
        "http",
        "worktree",
        "merged",
        "opened",
    ]
    low = s.lower()
    if not any(sig in low for sig in signals):
        return (
            f"summary lacks any completion signal (need one of {signals}): {s[:80]!r}"
        )
    return None


def _maybe_continue(tok, sid, reply):
    """If the last assistant message is not FINISHED, continue it.

    Loops up to _MAYBE_CONTINUE_MAX times so a chain of interruptions
    can be stitched back together in one logical turn.
    Returns the full concatenated text (original reply + continuations).
    """
    if not reply:
        return reply
    try:
        from deepcli.core import get_history as _hist
        from deepcli.core import continue_completion as _cont
    except Exception as e:
        print(f"    [continue] import failed: {type(e).__name__}: {e}")
        return reply

    full = reply
    for attempt in range(_MAYBE_CONTINUE_MAX):
        last = None
        try:
            h = _hist(tok, sid, force_refresh=True)
        except Exception as e:
            print(f"    [continue] history fetch failed: {type(e).__name__}")
            return full
        for m in reversed(h or []):
            if (m.get("role") or "").upper() == "ASSISTANT":
                last = m
                break
        if not last:
            return full
        status = (last.get("status") or "").upper()
        mid = last.get("message_id")
        if status in ("FINISHED", "STOP", "COMPLETED", ""):
            return full
        if mid is None:
            return full
        try:
            extra = _cont(tok, sid, int(mid))
        except Exception as e:
            print(
                f"    [continue #{attempt + 1}] failed: {type(e).__name__}: {str(e)[:120]}"
            )
            return full
        if extra is None:
            print(f"    [continue #{attempt + 1}] server says nothing to continue")
            return full
        if not extra:
            print(f"    [continue #{attempt + 1}] empty continuation")
            return full
        print(
            f"    [continue #{attempt + 1}] +{len(extra)} bytes (status was {status})"
        )
        full = full + extra
    print(f"    [continue] hit _MAYBE_CONTINUE_MAX={_MAYBE_CONTINUE_MAX}")
    return full


def execute(call):
    fn = call["function"]["name"]
    try:
        args = json.loads(call["function"]["arguments"] or "{}")
    except Exception as e:
        return f"ERROR parsing args: {e}"
    if fn == "finish":
        _sum = args.get("summary", "")
        _err = _validate_finish_summary(_sum)
        if _err:
            return {
                "finished": False,
                "error": "REJECTED: " + _err,
                "hint": 'Provide a real summary naming what shipped. Example: {"pkg":"recapitulation","files_added":8,"shims":2,"branch":"refactor/split-agent-deepagent","pr":"https://github.com/..."}. The loop will NOT terminate on a rejected finish.',
            }
        return {"finished": True, "summary": _sum}
    missing = [
        k for k in REQUIRED.get(fn, []) if k not in args or args[k] in (None, "", [])
    ]
    if missing:
        return f"ERROR {fn}: missing required {missing}"
    h = DISPATCH.get(fn)
    if not h:
        return f"ERROR unknown tool: {fn}"
    try:
        return h(args)
    except (PermissionError, FileNotFoundError) as e:
        return f"BLOCKED: {type(e).__name__}: {e}"
    except Exception as e:
        _log_tool_error(fn, args, e)
        return f"ERROR {type(e).__name__}: {e}"
