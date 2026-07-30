python3 << 'PYEOF'
import sys, json, subprocess, os
from pathlib import Path
HOME = Path.home()
sys.path.insert(0, str(HOME / 'deepcli'))
from deepapi import DeepAPI
cfg = json.loads((HOME / '.deepcli/config.json').read_text())
api = DeepAPI(cfg['token'])
reply = api.send_message("Direct deepapi test", "417ddd6d-9711-465d-ab90-c92cc04aeabf", None, thinking=False, search=False)
print(f"STDOUT: {reply[:300] if reply else '(empty)'}")
# Also capture stderr from the bridge
stderr_output = api.proc.stderr.read() if api.proc and api.proc.stderr else ''
if stderr_output:
    print(f"STDERR: {stderr_output[:500]}")
api.close()
PYEOF