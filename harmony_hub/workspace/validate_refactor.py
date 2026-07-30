
#!/usr/bin/env python3
import subprocess, sys, json, os
from pathlib import Path

# Load project config (could be in harmony_hub/config)
VALIDATORS = {
    "deepcli": "pytest tests/",
    "termux-multi-agent": "python -m py_compile workspace/test_script.py",
    "default": "python -c 'import py_compile; py_compile.compile(sys.argv[1])'"
}

def validate(project, file_path=None):
    cmd = VALIDATORS.get(project, VALIDATORS["default"])
    if file_path and "{file}" in cmd:
        cmd = cmd.replace("{file}", file_path)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr

if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "default"
    file = sys.argv[2] if len(sys.argv) > 2 else None
    success, output = validate(project, file)
    print(f"Validation {'passed' if success else 'failed'}")
    if output:
        print(output)
    sys.exit(0 if success else 1)
