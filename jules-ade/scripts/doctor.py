#!/usr/bin/env python3
"""Offline health check for jules-ade package (stdlib only, no network)."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONOREPO = ROOT.parent


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def check_layout() -> bool:
    required = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "roster.yaml",
        ROOT / "bridge" / "config.py",
        ROOT / "bridge" / "dispatch.py",
        ROOT / "scripts" / "doctor.py",
        ROOT / "tasks" / "queue",
    ]
    good = True
    for path in required:
        if not path.exists():
            fail(f"missing {path.relative_to(MONOREPO)}")
            good = False
        else:
            ok(f"found {path.relative_to(MONOREPO)}")
    return good


def check_compile() -> bool:
    good = True
    for py in (ROOT / "bridge").glob("*.py"):
        try:
            src = py.read_text(encoding="utf-8")
            ast.parse(src, filename=str(py))
            ok(f"compile {py.relative_to(MONOREPO)}")
        except SyntaxError as e:
            fail(f"syntax {py}: {e}")
            good = False
    try:
        ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)
        ok("compile scripts/doctor.py")
    except SyntaxError as e:
        fail(f"syntax doctor.py: {e}")
        good = False
    return good


def check_bridge_logic() -> bool:
    sys.path.insert(0, str(ROOT))
    try:
        from bridge.config import load_config
        from bridge.dispatch import plan_task
    except Exception as e:
        fail(f"import bridge: {e}")
        return False

    cfg = load_config()
    ok(f"home_repo={cfg.home_repo}")
    ok(f"default_branch={cfg.default_branch}")
    ok(f"jules_api_key_present={cfg.jules_api_key_present}")

    plan = plan_task(
        "doctor-sample",
        "noop research plan",
        starting_branch="master",
        config=cfg,
    )
    if cfg.prefer_staging and plan.starting_branch != "master-staging":
        fail(f"prefer_staging did not rewrite master → got {plan.starting_branch}")
        return False
    ok(f"plan branch={plan.starting_branch}")
    return True


def check_tasks() -> bool:
    queue = ROOT / "tasks" / "queue"
    files = list(queue.glob("*.yaml")) + list(queue.glob("*.yml"))
    if not files:
        fail("no task yaml in tasks/queue")
        return False
    ok(f"task files={len(files)}")
    return True


def main() -> int:
    print("jules-ade doctor (offline)")
    print(f"package root: {ROOT}")
    results = [check_layout(), check_compile(), check_bridge_logic(), check_tasks()]
    if all(results):
        print(json.dumps({"ok": True, "package": "jules-ade"}))
        return 0
    print(json.dumps({"ok": False, "package": "jules-ade"}))
    return 1


if __name__ == "__main__":
    sys.exit(main())
