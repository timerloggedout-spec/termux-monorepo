#!/usr/bin/env python3
"""Auto-scaffold a new account from a cookies JSON file."""
import sys, json, os, shutil, datetime
from pathlib import Path

def _check_symlink(path: Path):
    if path.is_symlink():
        raise ValueError(f"Symlink target rejected for security: {path}")

def scaffold(cookies_path: str, account_name: str):
    cookies_file = Path(cookies_path)
    _check_symlink(cookies_file)
    if not cookies_file.exists():
        print(f"❌ Cookies file not found: {cookies_path}")
        return

    with open(cookies_file) as f:
        data = json.load(f)
    cookies = data if isinstance(data, list) else data.get('cookies', [])

    # Extract session token
    token = None
    for c in cookies:
        if c.get('name') == 'ds_session_id':
            token = c.get('value')
            break
    if not token:
        print("❌ No ds_session_id cookie found")
        return

    # Save to vault
    vault_dir = Path.home() / '.synthegration'
    _check_symlink(vault_dir)
    vault_dir.mkdir(exist_ok=True)
    if not vault_dir.is_symlink():
        os.chmod(vault_dir, 0o700)

    vault_file = vault_dir / 'vault.json'
    _check_symlink(vault_file)
    vault = {}
    if vault_file.exists():
        with open(vault_file) as f:
            vault = json.load(f)
    vault[account_name] = token
    with open(vault_file, 'w') as f:
        json.dump(vault, f)
    if not vault_file.is_symlink():
        os.chmod(vault_file, 0o600)

    # Copy cookies to standard location
    dest_dir = Path.home() / 'deepseek-cli'
    _check_symlink(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not dest_dir.is_symlink():
        os.chmod(dest_dir, 0o700)

    dest = dest_dir / f'cookies_{account_name}.json'
    _check_symlink(dest)
    shutil.copy2(cookies_file, dest)
    if not dest.is_symlink():
        os.chmod(dest, 0o600)

    # Add to accounts.json
    accounts_file = Path.home() / 'harmony_hub' / 'workspace' / 'accounts.json'
    _check_symlink(accounts_file.parent)
    accounts_file.parent.mkdir(parents=True, exist_ok=True)
    if not accounts_file.parent.is_symlink():
        os.chmod(accounts_file.parent, 0o700)

    _check_symlink(accounts_file)
    accounts = {}
    if accounts_file.exists():
        with open(accounts_file) as f:
            accounts = json.load(f)
    if 'accounts' not in accounts:
        accounts['accounts'] = {}
    accounts['accounts'][account_name] = {
        'type': 'agent',
        'token_source': str(dest),
        'created': str(datetime.datetime.now()),
        'default_signature': {
            'agent': account_name,
            'director': 'ArchWizard',
            'project': 'synthegration'
        }
    }
    with open(accounts_file, 'w') as f:
        json.dump(accounts, f, indent=2)
    if not accounts_file.is_symlink():
        os.chmod(accounts_file, 0o600)

    print(f"✅ Account '{account_name}' scaffolded.")
    print(f"   Token: {token[:4]}...{token[-4:]}")
    print(f"   Cookies: {dest}")
    print(f"   Vault: {vault_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: scaffold_account.py <cookies.json> <account_name>")
        sys.exit(1)
    scaffold(sys.argv[1], sys.argv[2])
