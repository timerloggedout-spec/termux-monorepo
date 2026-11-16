#!/usr/bin/env python3
"""
Auto‑refactor trigger for account 2 – sandboxed.
Usage: python3 auto_refactor.py [--execute]
"""
import json, sys, subprocess, argparse
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
COMP_PROV = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
LOG_FILE = HOME / "cli-synthegration/workspace/account2_expert/refactor_log.json"
ORCHESTRATOR = HOME / "termux-multi-agent/src/orchestrator.py"

EXCLUDE_PREFIXES = [
    "cli-synthegration/workspace/",
    "cli-synthegration/codex/",
    "termux-multi-agent/workspace/",
    "synthegration-cli/target/",
    "deepseek-cli/browser-data/",
    "deepseek-cli/workspace/",
    "cli-synthegration/metrics/",
]
CODE_EXTENSIONS = {".py", ".js", ".ts", ".sh", ".rs", ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg"}

def is_excluded(fname):
    if any(fname.startswith(p) for p in EXCLUDE_PREFIXES):
        return True
    ext = Path(fname).suffix
    return ext not in CODE_EXTENSIONS

parser = argparse.ArgumentParser(description="Account-2 expert refactor trigger")
parser.add_argument("--execute", action="store_true", help="Actually run the refactor (default: dry-run)")
args = parser.parse_args()

if not COMP_PROV.exists():
    print("Comprehensive provenance missing."); sys.exit(1)

with open(COMP_PROV) as f:
    comp = json.load(f)

worst_file = None; worst_delay = 0
for fname, versions in comp.items():
    if is_excluded(fname): continue
    if versions and versions[0].get('delay_s', 0) > worst_delay:
        worst_delay = versions[0]['delay_s']
        worst_file = fname

if not worst_file:
    print("No production code bottleneck found."); sys.exit(0)

print(f"Production bottleneck: {worst_file} ({worst_delay:.0f}s)")

cmd = ["python3", str(ORCHESTRATOR), "--file", worst_file, "--cedar", "--account", "cookies2"]
print(f"Command: {' '.join(cmd)}")

status = "executed" if args.execute else "dry-run"
result = None
if args.execute:
    print("Executing refactor...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("Refactor failed:", result.stderr)
        status = "failed"
    else:
        status = "success"

entries = []
if LOG_FILE.exists():
    with open(LOG_FILE) as f: entries = json.load(f)
entries.append({
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'file': worst_file, 'delay_s': worst_delay,
    'account': 2, 'status': status,
    'command': ' '.join(cmd),
    'returncode': result.returncode if result else None
})
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(LOG_FILE, 'w') as f: json.dump(entries, f, indent=2)
print(f"Status: {status} | Logged to {LOG_FILE}")
