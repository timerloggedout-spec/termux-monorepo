#!/usr/bin/env python3
"""Ensure ~/deepcli/server.py declares a GET /health route returning 200.

Positive contract: after running, GET /health returns 200.
Strict gate: matches ROUTE DECLARATIONS, never bare substrings.
Idempotent: second run reports present:true action:noop.
"""
from __future__ import annotations
import ast, datetime, pathlib, re, shutil, sys

HOME = pathlib.Path.home()
SRC  = HOME / "deepcli" / "server.py"
TS   = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

# Real route declaration — decorator or explicit add_get call.
DECL = re.compile(
    r'(?:'
    r'@\w+\.(?:get|route|add_get)\s*\(\s*["\']/?health["\']'
    r'|'
    r'\w+\.router\.add_get\s*\(\s*["\']/?health["\']'
    r')',
    re.I,
)

def render(app: str) -> str:
    return (
        "\n\n# shell-forge: /health route (idempotent, added " + TS + ")\n"
        "@" + app + ".get(\"/health\")\n"
        "def _shellforge_health():\n"
        "    return {\"ok\": True, \"service\": \"hub\"}\n"
    )

def main() -> int:
    if not SRC.exists():
        print("present:false path:" + str(SRC)); return 1
    text = SRC.read_text(errors="replace")
    m = DECL.search(text)
    if m:
        print("present:true action:noop matched:" + repr(m.group(0)))
        return 0
    m = re.search(r"^(\w+)\s*=\s*FastAPI\s*\(", text, re.M)
    app = m.group(1) if m else "app"
    print("app:" + app)
    try:
        ast.parse(text)
    except SyntaxError as exc:
        print("gate:existing-syntax-fail line:" + str(exc.lineno)); return 2
    patched = text.rstrip() + "\n" + render(app)
    try:
        ast.parse(patched)
    except SyntaxError as exc:
        print("gate:patched-syntax-fail line:" + str(exc.lineno)); return 3
    bak = SRC.with_suffix(".py.bak." + TS)
    shutil.copy2(SRC, bak)
    SRC.write_text(patched)
    print("backup:" + str(bak))
    print("present:true action:written")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
