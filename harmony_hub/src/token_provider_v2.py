
import json, os
from pathlib import Path

VAULT_DIR = Path.home() / '.synthegration'
VAULT_DIR.mkdir(exist_ok=True)
VAULT = VAULT_DIR / 'vault.json'

def _load_json(path):
    if path.exists():
        if path.is_symlink():
            raise ValueError(f"Symlink vault path rejected for security: {path}")
        with open(path) as f:
            return json.load(f)
    return None

def _extract_from_cookies(cookies_path):
    """Extract bearer token from a Puppeteer cookies JSON array."""
    data = _load_json(cookies_path)
    if not data:
        return None
    cookies = data if isinstance(data, list) else data.get('cookies', [])
    for c in cookies:
        if c.get('name') == 'ds_session_id':
            return c.get('value')
    return None

def get_token(account='primary'):
    # Environment override
    env_key = f'DEEPSEEK_TOKEN_{account.upper()}'
    if env_key in os.environ:
        return os.environ[env_key]

    # Cache in vault (account-aware)
    if VAULT.exists():
        vault_data = _load_json(VAULT)
        if vault_data and account in vault_data:
            return vault_data[account]

    # Primary: upload-api.json
    if account == 'primary':
        up = Path.home() / 'deepseek-cli' / 'upload-api.json'
        data = _load_json(up)
        token = None
        if data:
            # Support both nested and flat structures
            token = data.get('authorization')
            if not token:
                upload_req = data.get('uploadRequest', {})
                token = upload_req.get('authorization') or upload_req.get('headers', {}).get('authorization')

    # Secondary: cookies_2.json
    elif account == 'secondary':
        # Secondary token is now stored directly in vault
        # (extracted from Firefox localStorage via bookmarklet)
        pass  # will fall through to vault check below

    else:
        raise ValueError(f"Unknown account: {account}")

    if token:
        if VAULT.is_symlink():
            raise ValueError(f"Symlink vault path rejected for security: {VAULT}")
        VAULT_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Save to vault
        current = _load_json(VAULT) or {}
        current[account] = token
        with open(VAULT, 'w') as f:
            json.dump(current, f)
        if not VAULT.is_symlink():
            os.chmod(VAULT, 0o600)
        return token

    raise RuntimeError(f"No token found for account '{account}'")
