#!/usr/bin/env python3
"""Extract token and conversations from DeepSeek official data export ZIP.
Usage: python extract_from_official_export.py <export.zip> [--account <name>]
Outputs: token saved to ~/.deepcli/config_<name>.json, conversations to ~/storage/downloads/synthegration_exports/"""
import sys, os, json, re, zipfile, shutil
from pathlib import Path
from datetime import datetime

HOME = Path.home()
SAFE_ACCOUNT_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")
EXPORT_ZIP = Path(sys.argv[1]) if len(sys.argv) > 1 else None
ACCOUNT = sys.argv[sys.argv.index('--account')+1] if '--account' in sys.argv else 'default'

if ACCOUNT != 'default' and not SAFE_ACCOUNT_REGEX.match(ACCOUNT):
    raise ValueError(f"Invalid account name '{ACCOUNT}': must contain only alphanumeric characters, underscores, or hyphens.")

if not EXPORT_ZIP or not EXPORT_ZIP.exists():
    print("Usage: extract_from_official_export.py <export.zip> [--account <name>]")
    sys.exit(1)

TMP = HOME / '.cache' / 'deepseek_export_extract'
TMP.mkdir(parents=True, exist_ok=True)

# Extract ZIP
with zipfile.ZipFile(EXPORT_ZIP, 'r') as zf:
    zf.extractall(TMP)

print(f"Extracted to {TMP}")
print("Contents:")
for f in sorted(TMP.rglob('*')):
    if f.is_file():
        print(f"  {f.relative_to(TMP)}")

# Search for token in config files or cookies
token = None
for f in TMP.rglob('*'):
    if f.suffix in ('.json', '.txt') and f.is_file():
        try:
            data = json.loads(f.read_text())
            if isinstance(data, dict):
                if 'token' in data:
                    token = data['token']
                    print(f"Found token in {f.relative_to(TMP)}")
                    break
                if 'userToken' in data:
                    token = data['userToken']
                    break
        except:
            pass

if token:
    config_dir = HOME / '.deepcli'
    config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    if config_dir.is_symlink():
        raise ValueError(f"Symlink config directory {config_dir} rejected for security")
    try:
        os.chmod(str(config_dir), 0o700)
    except OSError:
        pass

    config_file = config_dir / (f'config_{ACCOUNT}.json' if ACCOUNT != 'default' else 'config.json')
    if config_file.is_symlink():
        raise ValueError(f"Symlink config file {config_file} rejected for security")

    fd = os.open(str(config_file), os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
    if hasattr(os, "fchmod"):
        try:
            os.fchmod(fd, 0o600)
        except OSError:
            pass
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump({'token': token}, f, indent=2)
    except Exception:
        if not f.closed:
            f.close()
        raise
    print(f"Token saved to {config_file}")
else:
    print("No token found in export. Searching for alternatives...")
    # Look for cookies or session data that can be used
    for f in TMP.rglob('*.json'):
        try:
            data = json.loads(f.read_text())
            if isinstance(data, dict) and 'cookies' in data:
                print(f"Cookies found in {f.relative_to(TMP)} — use extract_bearer_from_cookies.js")
        except:
            pass

# Copy conversations to exports directory
for f in TMP.rglob('conversations.json'):
    dest = HOME / 'storage' / 'downloads' / 'synthegration_exports' / '_official_export'
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(f, dest / f.name)
    print(f"Conversations copied to {dest / f.name}")

# Cleanup
shutil.rmtree(TMP)
print("Done.")
