#!/usr/bin/env python3
"""Add GET /health to the ROOT FastAPI app in ~/deepcli/server.py.

Positive contract: after running, GET /health returns 200 on the root app.
Scoped gate: matches route declarations on the ROOT app variable only,
never on mounted sub-routers.
"""
from __future__ import annotations
import ast, datetime, pathlib, re, shutil

HOME = pathlib.Path.home()
SRC  = HOME / "deepcli" / "server.py"
TS   = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

def find_root_app(text: str) -> str | None:
    m = re.search(r"^(\w+)\s*=\s*FastAPI\s*\(", text, re.M)
    return m.group(1) if m else None

def root_decl(app: str) -> re.Pattern[str]:
    return re.compile(
        r"@" + re.escape(app) + r"\.(?:get|route)\s*\(\s*[\"']/?health[\"']",
        re.I,
    )

def render(app: str) -> str:
    return (
        "\n\n# shell-forge: root /health route (idempotent, added " + TS + ")\n"
        "@" + app + ".get(\"/health\")\n"
        "def _shellforge_root_health():\n"
        "    return {\"ok\": True, \"service\": \"hub\", \"plane\": \"root\"}\n"
    )

def main() -> int:
    if not SRC.exists():
        print("present:false path:" + str(SRC)); return 1
    text = SRC.read_text(errors="replace")
    app = find_root_app(text)
    if app is None:
        print("root-app:not-found"); return 2
    print("root-app:" + app)
    m = root_decl(app).search(text)
    if m:
        print("present:true action:noop matched:" + repr(m.group(0)))
        return 0
    try:
        ast.parse(text)
    except SyntaxError as exc:
        print("gate:existing-syntax-fail line:" + str(exc.lineno)); return 3
    patched = text.rstrip() + "\n" + render(app)
    try:
        ast.parse(patched)
    except SyntaxError as exc:
        print("gate:patched-syntax-fail line:" + str(exc.lineno)); return 4
    bak = SRC.with_suffix(".py.bak." + TS)
    shutil.copy2(SRC, bak)
    SRC.write_text(patched)
    print("backup:" + str(bak))
    print("present:true action:written")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
