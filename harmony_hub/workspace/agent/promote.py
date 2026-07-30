#!/usr/bin/env python3
"""Promote a sandbox file to its original location with backup."""
import sys, shutil
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: promote.py <target_file>")
    print("Looks for sandbox: ~/termux-multi-agent/workspace/refactor_target<ext>")
    sys.exit(1)

target_original = Path(sys.argv[1]).expanduser().resolve()
sandbox = Path.home() / "termux-multi-agent" / "workspace" / f"refactor_target{target_original.suffix}"

if not sandbox.exists():
    print(f"❌ Sandbox not found: {sandbox}")
    sys.exit(1)

# Validate
if target_original.suffix in ('.js', '.mjs'):
    import subprocess
    result = subprocess.run(["node", "--check", str(sandbox)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Validation failed:\n{result.stderr}")
        sys.exit(1)
else:
    import subprocess
    result = subprocess.run(["python", "-m", "py_compile", str(sandbox)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Validation failed:\n{result.stderr}")
        sys.exit(1)

# Backup original
backup = target_original.with_suffix(target_original.suffix + f'.promoted_{Path(sys.argv[0]).stat().st_mtime:.0f}.bak')
shutil.copy2(target_original, backup)
print(f"Backup: {backup}")

# Promote
shutil.copy2(sandbox, target_original)
print(f"✅ Promoted: {sandbox} -> {target_original}")
