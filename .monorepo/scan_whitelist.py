#!/usr/bin/env python3
import subprocess
import json
import os
import sys
import shutil
from pathlib import Path
import datetime

PROJECTS_FILE = os.path.expanduser("~/.monorepo/projects.json")
REPORT_FILE = os.path.expanduser("~/.monorepo/scan_report.txt")

def run_cmd(cmd, cwd=None, timeout=60, env=None):
    """Run a command and return stdout+stderr, or error message."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return f"TIMEOUT: command exceeded {timeout} seconds"
    except Exception as e:
        return f"ERROR: {str(e)}"

def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return []
    with open(PROJECTS_FILE) as f:
        return json.load(f)

def scan_project(project):
    path = project["path"]
    lang = project["language"]
    report = []
    report.append(f"\n--- {project['name']} ({lang}) @ {path} ---")

    if lang == "npm":
        out = run_cmd(["npm", "audit", "--json"], cwd=path, timeout=120)
        report.append("npm audit:\n" + out[:3000])
    elif lang == "cargo":
        # Check if cargo-audit is installed
        if shutil.which("cargo-audit") is None:
            report.append("cargo audit: command not found. Install with: cargo install cargo-audit")
        else:
            # Use offline mode
            env = os.environ.copy()
            env["CARGO_AUDIT_OFFLINE"] = "true"
            out = run_cmd(["cargo", "audit", "--no-fetch"], cwd=path, env=env, timeout=120)
            report.append("cargo audit:\n" + out[:3000])
    elif lang == "python":
        if shutil.which("bandit") is None:
            report.append("bandit: command not found. Install with: pip install bandit")
        else:
            out = run_cmd(["bandit", "-r", path, "-f", "txt", "-ll"], cwd=path, timeout=120)
            report.append("bandit:\n" + out[:3000])
    elif lang == "go":
        out = run_cmd(["go", "vet", "./..."], cwd=path, timeout=120)
        report.append("go vet:\n" + out[:3000])

    # Secret grep (only on non-excluded files)
    secret_cmd = [
        "grep", "-r", "-I", "-n",
        "-E", "api[_-]?key|token|secret|password|private_key|credential",
        "--exclude-dir=node_modules",
        "--exclude-dir=.git",
        "--exclude=*.jsonl",
        "--exclude=*.log",
        "--exclude=*.md",
        "--exclude=*.txt",
        "--exclude=*.cookies",
        "--exclude=*_api_key",
        "--exclude=*.env",
        "--exclude=*.local",
        "--exclude=*.pem",
        "--exclude=*.key",
        "--exclude=*.secret",
        "--exclude=*token*",
        "--exclude=*credential*",
        "--exclude=*_history",
        "--exclude=*.deepcli_tui_history",
        "--exclude=.mapper_state.json",
        path
    ]
    out = run_cmd(secret_cmd, timeout=30)
    report.append("Secret grep (suspicious patterns):\n" + out[:3000])

    return "\n".join(report)

def main():
    projects = load_projects()
    if not projects:
        print("No projects found. Run discover_projects.py first.")
        sys.exit(1)

    full_report = "MONOREPO SECURITY SCAN REPORT\n"
    full_report += f"Generated: {datetime.datetime.now()}\n"
    full_report += f"Projects scanned: {len(projects)}\n"
    full_report += "="*80 + "\n"

    for p in projects:
        full_report += scan_project(p)

    with open(REPORT_FILE, "w") as f:
        f.write(full_report)

    print(f"Report saved to {REPORT_FILE}")

    # Copy summary to clipboard (first 500 chars)
    summary = full_report[:500] + "\n... (full report in file)"
    try:
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True)
        p.communicate(summary, timeout=5)
        print("Summary copied to clipboard.")
    except Exception:
        print("Clipboard copy failed. Use: cat ~/.monorepo/scan_report.txt")

if __name__ == "__main__":
    main()
