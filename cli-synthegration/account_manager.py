#!/usr/bin/env python3
"""Manage multiple DeepSeek accounts for synthegration."""
import sys, os, subprocess, json
from pathlib import Path
HOME = Path.home()
CONFIG_DIR = HOME / ".deepcli"

def import_account(cookies_file: str, account_name: str):
    """Extract Bearer token from cookies JSON and save as config_<account>.json."""
    extract_script = HOME / "deepseek-cli" / "extract_token_from_cookies.cjs"
    proc = subprocess.run(
        ["node", str(extract_script), cookies_file],
        capture_output=True, text=True, timeout=60
    )
    if proc.returncode != 0:
        print(f"Extraction failed: {proc.stderr}")
        return False
    token = proc.stdout.strip()
    # SECURITY ENHANCEMENT: Enforce strict directory permissions (700) and file permissions (600) on token config - Fail-closed on OSError
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(str(CONFIG_DIR), 0o700)
    except OSError as e:
        raise PermissionError(f"Fail-closed: Failed to enforce 0o700 permissions on {CONFIG_DIR}: {e}")
    config = CONFIG_DIR / f"config_{account_name}.json"
    fd = os.open(str(config), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump({"token": token}, f, indent=2)
    print(f"[+] Token for '{account_name}' saved to {config}")
    return True

def get_token(account_name: str = "default") -> str:
    """Return token for account. 'default' reads config.json, others read config_<name>.json."""
    if account_name == "default":
        cfg_file = CONFIG_DIR / "config.json"
    else:
        cfg_file = CONFIG_DIR / f"config_{account_name}.json"
    if not cfg_file.exists():
        raise FileNotFoundError(f"No config for account '{account_name}'. Run import first.")
    return json.loads(cfg_file.read_text()).get("token")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: account_manager.py import <cookies_file> <account_name>")
        print("       account_manager.py token <account_name>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "import":
        cookies_file = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else "account2"
        import_account(cookies_file, name)
    elif cmd == "token":
        name = sys.argv[2] if len(sys.argv) > 2 else "default"
        print(get_token(name))
