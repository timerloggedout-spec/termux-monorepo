# Write a tiny Python send helper that calls deepapi.py
cat > ~/archwiz/send_helper.py << 'PYEOF'
#!/usr/bin/env python3
"""Send messages via deepapi.py (Node bridge – already works)."""
import sys, subprocess, json, os, time
from pathlib import Path

HOME = Path.home()
SEND_SESSION = '417ddd6d-9711-465d-ab90-c92cc04aeabf'
DEEPAPI = HOME / 'deepcli/deepapi.py'
BRIDGE = HOME / 'deepseek-cli/deepterm/bridge.js'
TOKEN = None

def get_token():
    global TOKEN
    if not TOKEN:
        cfg = HOME / '.deepcli/config.json'
        if cfg.exists():
            TOKEN = json.loads(cfg.read_text()).get('token','')
    return TOKEN

def send_message(text):
    script = f'''
import sys, json, subprocess
sys.path.insert(0, "{HOME}/deepcli")
from deepapi import DeepAPI
api = DeepAPI("{get_token()}")
try:
    reply = api.send_message("""{text}""", "{SEND_SESSION}", None, thinking=False, search=False)
    if reply:
        print("Sent.")
    else:
        print("Sent (no reply).")
except Exception as e:
    print(f"Send error: {{e}}")
finally:
    api.close()
'''
    subprocess.run(['python3', '-c', script])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        send_message(' '.join(sys.argv[1:]))
    else:
        send_message(sys.stdin.read().strip())
PYEOF