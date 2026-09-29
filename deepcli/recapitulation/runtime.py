"""runtime — home paths, allowlists, protection, notifications, snapshots."""

import os
import sys
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / "deepcli"))
sys.path.insert(0, str(HOME))

READ_ALLOW = [HOME]
WRITE_ALLOW = [
    HOME / ".deepcli",
    HOME / "deepcli" / "tasks",
    HOME / "deepcli" / "agent_workspaces",
    HOME / ".deepcli" / "logs",
]
MAX_RW_BYTES = 512 * 1024

RUN_ALLOWED_BINS = {
    "git",
    "gh",
    "python3",
    "pip3",
    "node",
    "npm",
    "rg",
    "fd",
    "jq",
    "yq",
    "ls",
    "cat",
    "head",
    "tail",
    "wc",
    "find",
    "grep",
    "sed",
    "awk",
    "sort",
    "uniq",
    "curl",
    "adb",
    "echo",
    "pwd",
    "which",
    "stat",
    "df",
    "du",
    "date",
    "termux-notification",
    "termux-toast",
    "termux-clipboard-get",
    "termux-battery-status",
    "mkdir",
    "printf",
    "env",
    "uname",
    "id",
    "whoami",
    "base64",
    "touch",
    "sleep",
}

SKILL_ROOTS = [
    HOME / ".agents" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".pi" / "skills",
]

WORKTREE_ROOT = HOME / ".deepcli" / "worktrees"


def _safe(p, allow):
    q = Path(p).expanduser().resolve()
    for root in allow:
        try:
            q.relative_to(root.resolve())
            return q
        except ValueError:
            continue
    raise PermissionError(f"path outside allowed roots: {q}")


# ─── load-bearing file protection ────────────────────────────────────
# These files are the agent's own implementation. They are NOT writable
# by the agent's own write_file tool. Changes go through a worktree+PR.
PKG_DIR = Path(__file__).resolve().parent

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
    # every file under the package itself
    PKG_DIR / "__init__.py",
    PKG_DIR / "loop.py",
    PKG_DIR / "tools.py",
    PKG_DIR / "edit.py",
    PKG_DIR / "lint.py",
    PKG_DIR / "retry.py",
    PKG_DIR / "runtime.py",
    PKG_DIR / "http_loop.py",
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


def _notify(kind: str, title: str, content: str, *, priority: str = "default"):
    """Best-effort Termux:API notification. Uses fixed id so start→finish replaces."""
    import subprocess as _sp
    import shutil as _sh

    if not _sh.which("termux-notification"):
        return
    try:
        _sp.Popen(
            [
                "termux-notification",
                "--id",
                f"deepagent-{kind}",
                "--channel",
                "deepagent",
                "--title",
                title,
                "--content",
                content[:400],
                "--priority",
                priority,
            ],
            stdout=_sp.DEVNULL,
            stderr=_sp.DEVNULL,
        )
    except Exception:
        pass


def _autosnapshot(reason: str = "auto"):
    """Spawn agent-snapshot in background; snapshot tool itself handles diff-gating."""
    import subprocess as _sp
    import shutil as _sh

    exe = _sh.which("agent-snapshot")
    if not exe:
        return
    try:
        _sp.Popen([exe, "--reason", reason], stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
    except Exception:
        pass


def _wt_safe(branch: str) -> str:
    return branch.replace("/", "-").replace(":", "-").replace(" ", "-")[:60]


def _wt_git(args, cwd, timeout=60):
    import subprocess as _sp

    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    return _sp.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _wt_default_repo():
    """Parse origin URL in $HOME to get owner/name."""
    r = _wt_git(["config", "--get", "remote.origin.url"], str(HOME))
    if r.returncode != 0:
        return None
    url = r.stdout.strip()
    import re as _re

    m = _re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None
