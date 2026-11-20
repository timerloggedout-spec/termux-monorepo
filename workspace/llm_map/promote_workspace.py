#!/usr/bin/env python3
"""Promote a workspace from sandbox to graduated."""
import sys, shutil, subprocess, json
from pathlib import Path

HOME = Path.home()
SANDBOX = HOME / "sandbox_workspace"
GRADUATED = HOME / "graduated_workspaces"
VALIDATOR = HOME / "workspace" / "llm_map" / "validate_promotion.py"

def promote(name: str) -> bool:
    src = SANDBOX / name
    if not src.is_dir():
        print(f"ERROR: sandbox workspace '{name}' not found.")
        return False

    # Run validator on every .py file inside
    for f in src.rglob("*.py"):
        result = subprocess.run(
            ["python3", str(VALIDATOR), str(f.relative_to(HOME))],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Validation failed for {f}:\n{result.stderr}")
            return False
        print(result.stdout)

    # Move to graduated
    dst = GRADUATED / name
    if dst.exists():
        print(f"ERROR: {dst} already exists. Remove or rename first.")
        return False
    shutil.move(str(src), str(dst))
    print(f"Promoted '{name}' to graduated workspaces.")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: promote_workspace.py <workspace_name>")
        sys.exit(1)
    promote(sys.argv[1])
