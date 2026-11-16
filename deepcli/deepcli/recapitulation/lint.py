"""lint — syntax + ruff static checks, safe autofix, autofix metrics log."""

import os
from .runtime import HOME  # noqa: F401


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

    import shutil
    import subprocess
    import tempfile
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
            [
                ruff,
                "check",
                "--isolated",
                "--select",
                "E9,F401,F811,F841,F821,F822,F823",
                "--output-format",
                "concise",
                tmp,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r.returncode != 0 and r.stdout.strip():
            return r.stdout.strip().replace(tmp, str(path))[:600]
        return None
    except Exception as e:
        return f"ruff-exec-error: {type(e).__name__}: {e}"
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except Exception:
                pass


def _ruff_autofix(text: str) -> tuple[str, list[str]]:
    """Run `ruff check --fix` and `ruff format` on Python text.
    Returns (fixed_text, list_of_changes). Empty list = no changes needed."""
    import shutil
    import subprocess
    import tempfile
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
        r1 = subprocess.run(
            [
                ruff,
                "check",
                "--isolated",
                "--fix",
                "--exit-zero",
                "--select",
                "E9,F401,F811,F841,F821,F822,F823",
                "--output-format",
                "concise",
                tmp,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r1.stdout.strip():
            changes.extend(line for line in r1.stdout.splitlines() if line.strip())
        # pass 2: formatter
        r2 = subprocess.run(
            [ruff, "format", "--isolated", tmp],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r2.returncode == 0 and r2.stdout.strip():
            changes.append("formatted (ruff format)")
        return _P(tmp).read_text(), changes
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def _log_autofix(provider: str, model: str, path: str, changes: list[str]):
    """Append one row to the autofix metrics log. Provider/model keyed."""
    import json as _j
    import datetime as _dt
    from pathlib import Path as _P

    log = _P.home() / ".deepcli" / "logs" / "autofix_metrics.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "path": str(path),
        "n_changes": len(changes),
        "changes": changes[:20],
    }
    with log.open("a") as f:
        f.write(_j.dumps(row) + "\n")
