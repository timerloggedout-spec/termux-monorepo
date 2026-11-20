#!/usr/bin/env python3
"""Auto-scaffold a new account from a cookies JSON file."""
import sys, json, os
from pathlib import Path

def scaffold(cookies_path: str, account_name: str):
    cookies_file = Path(cookies_path)
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
    vault_dir.mkdir(exist_ok=True)
    vault_file = vault_dir / 'vault.json'
    vault = {}
    if vault_file.exists():
        with open(vault_file) as f:
            vault = json.load(f)
    vault[account_name] = token
    with open(vault_file, 'w') as f:
        json.dump(vault, f)
    os.chmod(vault_file, 0o600)

    # Copy cookies to standard location
    dest = Path.home() / 'deepseek-cli' / f'cookies_{account_name}.json'
    shutil.copy2(cookies_file, dest)

    # Add to accounts.json
    accounts_file = Path.home() / 'harmony_hub' / 'workspace' / 'accounts.json'
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
    accounts_file.parent.mkdir(parents=True, exist_ok=True)
    with open(accounts_file, 'w') as f:
        json.dump(accounts, f, indent=2)

    print(f"✅ Account '{account_name}' scaffolded.")
    print(f"   Token: {token[:4]}...{token[-4:]}")
    print(f"   Cookies: {dest}")
    print(f"   Vault: {vault_file}")

if __name__ == '__main__':
    import shutil, datetime
    if len(sys.argv) < 3:
        print("Usage: scaffold_account.py <cookies.json> <account_name>")
        sys.exit(1)
    scaffold(sys.argv[1], sys.argv[2])
