#!/usr/bin/env python3
"""
auto_refactor.py – Trigger CEDARscript refactor on bottleneck files.
Uses second-account token from cookies_2.json for DeepSeek API calls.
"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
SESS_PROD = HOME / "cli-synthegration/workspace/time_loop_accelerator/session_productivity.json"
COOKIES_FILE = HOME / "storage/downloads/_doing/_1-build/DeepSeek/exports/cookies_2.json"
CEDAR_SPEC = HOME / "cli-synthegration/workspace/cedarscript/cedarscript_api_spec.json"

# --- 1. Load bottleneck from session productivity ---
if not SESS_PROD.exists():
    print("Run session_productivity.py first.")
    sys.exit(1)
with open(SESS_PROD) as f:
    sessions = json.load(f)
if not sessions:
    print("No session data.")
    sys.exit(1)

# Find the file with the highest delay (bottleneck)
# We need per-file delay from comprehensive_provenance.json, but session_productivity has top-level files per session.
# Quick approach: load comprehensive and pick worst delay file.
COMP_PROV = HOME / "cli-synthegration/workspace/provenance/comprehensive_provenance.json"
if not COMP_PROV.exists():
    print("Comprehensive provenance missing.")
    sys.exit(1)
with open(COMP_PROV) as f:
    comp = json.load(f)

# Find the file with the largest first delay
worst_file = None
worst_delay = 0
for fname, versions in comp.items():
    if versions and versions[0].get('delay_s', 0) > worst_delay:
        worst_delay = versions[0]['delay_s']
        worst_file = fname
if worst_file:
    print(f"Bottleneck file: {worst_file} (delay: {worst_delay:.0f}s)")
else:
    print("No bottleneck found.")
    sys.exit(0)

# --- 2. Extract second-account token from cookies_2.json ---
token2 = None
if COOKIES_FILE.exists():
    try:
        with open(COOKIES_FILE) as f:
            cookies = json.load(f)
        # Cookies file may be a list of cookie objects or a dict. Adapt accordingly.
        if isinstance(cookies, list):
            for c in cookies:
                if c.get('name') == '__Secure-next-auth.session-token' or c.get('name') == 'token':
                    token2 = c.get('value')
                    break
        elif isinstance(cookies, dict):
            token2 = cookies.get('token') or cookies.get('__Secure-next-auth.session-token')
        if token2:
            print("Second-account token loaded from cookies_2.json")
        else:
            print("No suitable token found in cookies_2.json, using default token provider.")
    except Exception as e:
        print(f"Error reading cookies_2.json: {e}")
else:
    print("cookies_2.json not found; will use default token provider.")

# --- 3. Invoke CEDARscript refactor ---
# The actual refactor is performed by termux-multi-agent/src/orchestrator.py's parse_and_apply_cedar_diff.
# We'll call it as a subprocess, passing the bottleneck file and token.
# The orchestrator expects: python3 orchestrator.py --file <path> --token <token> --cedar
orchestrator = HOME / "termux-multi-agent/src/orchestrator.py"
if not orchestrator.exists():
    print("Orchestrator not found.")
    sys.exit(1)

cmd = [
    "python3", str(orchestrator),
    "--file", worst_file,
    "--cedar"
]
if token2:
    cmd += ["--token", token2]

print(f"Running: {' '.join(cmd)}")
# Actually run it (uncomment for real run; we'll simulate for now)
# result = subprocess.run(cmd, capture_output=True, text=True)
# print(result.stdout)
# if result.returncode != 0:
#     print("Refactor failed:", result.stderr)

print("Refactor trigger prepared. (Uncomment subprocess.run to execute)")
print(f"Command would be: {' '.join(cmd)}")

# --- 4. Log the action ---
log_dir = HOME / "cli-synthegration/workspace/time_loop_accelerator"
log_file = log_dir / "refactor_log.json"
entries = []
if log_file.exists():
    with open(log_file) as f:
        entries = json.load(f)
entries.append({
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'file': worst_file,
    'delay_s': worst_delay,
    'token_used': bool(token2),
    'status': 'triggered'
})
with open(log_file, 'w') as f:
    json.dump(entries, f, indent=2)
print(f"Logged to {log_file}")
