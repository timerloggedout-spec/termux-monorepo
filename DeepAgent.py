#!/usr/bin/env python3
"""Canonical DeepAgent entry point and non-mutating runtime doctor.

"Admin" in this repository identifies a collaborator, not an execution
permission tier. This wrapper deliberately delegates authorization to the
existing DeepCLI tool allowlists and GitHub credentials.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
AGENT = ROOT / "deepcli" / "deepagent.py"
ROLES = ROOT / "deepcli" / "roles.json"


def doctor() -> int:
    """Report runtime readiness without contacting providers or printing secrets."""
    checks = {
        "agent_entrypoint": AGENT.is_file(),
        "role_registry": ROLES.is_file(),
        "session_store": (ROOT / "deepcli" / "session_store.py").is_file(),
        "python": bool(sys.executable),
        "deepseek_token_configured": bool(os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DEEPCLI_TOKEN")),
    }
    try:
        roles = json.loads(ROLES.read_text(encoding="utf-8"))
        checks["role_registry_valid"] = isinstance(roles, dict) and bool(roles)
        checks["available_roles"] = sorted(roles) if checks["role_registry_valid"] else []
    except (OSError, ValueError):
        checks["role_registry_valid"] = False
        checks["available_roles"] = []
    checks["admin_is_privilege"] = False
    report = {
        "ok": all(checks[k] for k in ("agent_entrypoint", "role_registry", "session_store", "python", "role_registry_valid")),
        "checks": checks,
        "notes": [
            "A collaborator name or Administrator label does not grant execution privileges.",
            "Tool and repository permissions remain enforced by DeepCLI and the configured GitHub identity.",
            "Credentials are checked by presence only and are never displayed.",
        ],
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doctor", action="store_true", help="check local DeepAgent runtime readiness")
    args, remaining = parser.parse_known_args(argv)
    if args.doctor:
        if remaining:
            parser.error("--doctor cannot be combined with task arguments")
        return doctor()
    if not AGENT.is_file():
        parser.error(f"DeepCLI agent implementation not found: {AGENT}")
    return subprocess.call([sys.executable, str(AGENT), *remaining], cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
