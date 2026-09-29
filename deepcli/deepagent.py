#!/usr/bin/env python3
"""deepagent.py — SHIM. Real code lives in recapitulation/.

This file is a compatibility shim. It re-exports the public surface so
existing callers (server.py, _v1_agent.py, dsh CLI) keep working.
Protected by recapitulation.runtime.PROTECTED_PATHS.
"""
import sys
from pathlib import Path

# Ensure recapitulation package is importable when loaded by path
_pkg_dir = Path(__file__).resolve().parent
if str(_pkg_dir) not in sys.path:
    sys.path.insert(0, str(_pkg_dir))

from recapitulation.tools import (  # noqa: F401
    TOOLS,
    DISPATCH,
    REQUIRED,
    execute,
    _feedback_call,
    _auto_feedback,
    _CURRENT_SESSION_CTX,
    _AUTO_FEEDBACK_CAT,
    _validate_finish_summary,
    _FINISH_PLACEHOLDERS,
    _maybe_continue,
    _MAYBE_CONTINUE_MAX,
)
from recapitulation.loop import loop  # noqa: F401


def _main():
    """CLI entry: parse argv, run loop()."""
    argv = sys.argv[1:]
    dry = False
    fresh = False
    task_path = None
    if "--dry-run" in argv:
        dry = True
        argv.remove("--dry-run")
    if "--fresh" in argv:
        fresh = True
        argv.remove("--fresh")
    if "--task-file" in argv:
        i = argv.index("--task-file")
        if i + 1 < len(argv):
            task_path = argv[i + 1]
            del argv[i : i + 2]
    if not argv:
        print("usage: deepagent.py [--dry-run] [--fresh] [--task-file P] \"<task>\"")
        sys.exit(2)
    loop(" ".join(argv), dry_run=dry, task_path=task_path, fresh=fresh)


if __name__ == "__main__":
    _main()
