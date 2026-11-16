#!/usr/bin/env python3
"""agent.py — SHIM. Real code lives in recapitulation/http_loop.py.

Re-exports the HTTP-hop loop entry point. Callers that did
`import agent; agent.main(...)` continue to work.
"""
import sys
from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent
if str(_pkg_dir) not in sys.path:
    sys.path.insert(0, str(_pkg_dir))

# Re-export everything from http_loop
from recapitulation.http_loop import *  # noqa: F401,F403
from recapitulation.http_loop import (  # noqa: F401
    HUB,
    TOK,
)


if __name__ == "__main__":
    # Delegate to http_loop's __main__ body via runpy if present
    import runpy
    runpy.run_module("recapitulation.http_loop", run_name="__main__")
