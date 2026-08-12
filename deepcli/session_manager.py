"""
Manages DeepSeek web session: PoW, cookies, chat_session_id, multi-account.

Template webWrapper accounts (from token_provider_v2 / cedar_forge PLAN):
  primary   / account-1  — interactive operator path
  secondary / account-2  — CI check runs (cookies_2.json lineage)

Session dir: 0o700 · session.json: 0o600
"""
import os
import json
import subprocess
import time
from pathlib import Path
import requests

DEEPSEEK_BASE = "https://chat.deepseek.com"
WASM_DIR = Path(__file__).parent / "wasm"

# Alias map: CI-friendly names → template names
ACCOUNT_ALIASES = {
    "account-1": "primary",
    "account1": "primary",
    "1": "primary",
    "primary": "primary",
    "account-2": "secondary",
    "account2": "secondary",
    "2": "secondary",
    "secondary": "secondary",
}


def normalize_account(name: str | None) -> str:
    raw = (name or os.environ.get("DEEPSEEK_ACCOUNT") or "secondary").strip().lower()
    return ACCOUNT_ALIASES.get(raw, raw if raw in ("primary", "secondary") else "secondary")


def solve_pow():
    """
    Fetch PoW challenge from DeepSeek and solve it using WASM solver.
    Returns dict with 'answer' and 'signature' keys.
    """
    wasm_path = WASM_DIR / "deepseek.wasm"
    solver_script = WASM_DIR / "pow_solver.js"

    if not wasm_path.exists():
        raise FileNotFoundError(f"WASM file not found: {wasm_path}")
    if not solver_script.exists():
        raise FileNotFoundError(f"Solver script not found: {solver_script}")

    # Get challenge from DeepSeek (anonymous path)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    
    try:
        resp = session.post(
            f"{DEEPSEEK_BASE}/api/v0/chat/create_pow_challenge",
            json={"target_path": "/api/v0/chat/completion"},
            timeout=30,
        )
        resp.raise_for_status()
        
        # Debug: print response details
        print(f"::debug::PoW API status={resp.status_code} content-type={resp.headers.get('content-type')}")
        print(f"::debug::PoW API response body length={len(resp.text)}")
        
        if not resp.text:
            raise RuntimeError("PoW challenge API returned empty response body")
        
        resp_data = resp.json()
        print(f"::debug::PoW API resp_data type={type(resp_data)} value={resp_data}")
        
        if resp_data is None:
            raise RuntimeError("PoW challenge API json() returned None")
        
        if not isinstance(resp_data, dict):
            raise RuntimeError(f"PoW challenge API returned non-dict: {type(resp_data)} = {resp_data}")
        
        # Try different response structures
        challenge_data = (
            resp_data.get("data", {}).get("biz_data", {}).get("challenge")
            or resp_data.get("challenge")
            or (resp_data if all(k in resp_data for k in ["algorithm", "challenge", "salt"]) else None)
        )
        
        if not challenge_data or not isinstance(challenge_data, dict):
            raise RuntimeError(f"Invalid PoW challenge response structure. Keys: {list(resp_data.keys()) if isinstance(resp_data, dict) else 'N/A'}")
            
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"PoW challenge API request failed: {e}")

    # Pass challenge JSON to pow_solver.js via stdin
    challenge_json = json.dumps(challenge_data)
    result = subprocess.run(
        ["node", str(solver_script), str(wasm_path)],
        input=challenge_json,
        text=True,
        capture_output=True,
        timeout=60,
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"PoW solver failed: {result.stderr}")
    
    # pow_solver.js outputs just the answer number, we need to return full structure
    answer = int(result.stdout.strip())
    return {
        "answer": answer,
        "signature": challenge_data.get("signature", ""),
        "challenge": challenge_data.get("challenge", ""),
        "salt": challenge_data.get("salt", ""),
        "expire_at": challenge_data.get("expire_at", 0),
        "difficulty": challenge_data.get("difficulty", 0),
    }


def _token_from_env(account: str) -> str | None:
    """Resolve bearer token for account from env / secrets-exported vars."""
    # token_provider_v2 style
    specific = os.environ.get(f"DEEPSEEK_TOKEN_{account.upper()}")
    if specific:
        return specific.strip()

    if account == "secondary":
        for key in (
            "DEEPSEEK_TOKEN_SECONDARY",
            "DEEPSEEK_ACCOUNT_2",
            "DEEPSEEK_ACCOUNT2",
            "DeepSeek_account-2",
        ):
            v = os.environ.get(key)
            if v:
                return v.strip()
        # cookies_2 lineage: raw cookie value or JSON array in env
        raw = os.environ.get("DEEPSEEK_COOKIES_2") or os.environ.get("COOKIES_2")
        if raw:
            raw = raw.strip()
            if raw.startswith("[") or raw.startswith("{"):
                try:
                    data = json.loads(raw)
                    cookies = data if isinstance(data, list) else data.get("cookies", [])
                    for c in cookies:
                        if c.get("name") == "ds_session_id":
                            return c.get("value")
                except json.JSONDecodeError:
                    pass
            return raw  # plain ds_session_id value

    # primary / account-1
    for key in (
        "DEEPSEEK_TOKEN_PRIMARY",
        "DEEPSEEK_TOKEN",
        "DEEPSEEK_ACCOUNT_1",
        "DeepSeek_account-1",
    ):
        v = os.environ.get(key)
        if v:
            return v.strip()
    return None


def _auth_session_headers(token: str, cookies: dict | None = None) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "*/*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Client-Platform": "web",
        "X-Client-Version": "1.3.0-auto-resume",
        "X-App-Version": "20241129.1",
        "X-Client-Locale": "en_US",
        "Origin": DEEPSEEK_BASE,
        "Referer": f"{DEEPSEEK_BASE}/",
    })
    if cookies:
        s.cookies.update(cookies)
        if "ds_session_id" in cookies:
            s.cookies.set("ds_session_id", cookies["ds_session_id"])
    return s


def create_chat_session(token: str, cookies: dict | None = None, model_type: str = "expert") -> str:
    """
    Create a DeepSeek chat_session_id (required for /api/v0/chat/completion).
    Matches deepcli.core.create_session / multi-ai-cli backends.
    """
    s = _auth_session_headers(token, cookies)
    r = s.post(
        f"{DEEPSEEK_BASE}/api/v0/chat_session/create",
        json={"character_id": None, "model_type": model_type},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    sid = (
        data.get("data", {}).get("biz_data", {}).get("id")
        or data.get("id")
        or data.get("chat_session_id")
    )
    if not sid:
        raise RuntimeError(f"create_chat_session: no id in response keys={list(data) if isinstance(data, dict) else type(data)}")
    return str(sid)


def get_pow_challenge(token: str, cookies: dict | None = None, target_path: str = "/api/v0/chat/completion") -> dict:
    s = _auth_session_headers(token, cookies)
    r = s.post(
        f"{DEEPSEEK_BASE}/api/v0/chat/create_pow_challenge",
        json={"target_path": target_path},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]["biz_data"]["challenge"]


def get_new_session(account: str = "secondary"):
    """
    Build a full session dict for the given account.
    Prefer env/secret token; fall back to PoW web handshake when no token.
    Always attaches a fresh chat_session_id when possible.
    """
    account = normalize_account(account)
    token = _token_from_env(account)
    cookies = {}

    if not token:
        # Anonymous / PoW handshake path (legacy CI bootstrap)
        pow_result = solve_pow()
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        resp = session.get(f"{DEEPSEEK_BASE}/api/chat", timeout=30)
        resp.raise_for_status()
        auth_payload = {
            "pow_answer": pow_result["answer"],
            "pow_signature": pow_result["signature"],
        }
        auth_resp = session.post(f"{DEEPSEEK_BASE}/api/auth", json=auth_payload, timeout=30)
        auth_resp.raise_for_status()
        token_data = auth_resp.json()
        token = token_data.get("token")
        if not token:
            raise RuntimeError("No token received from DeepSeek auth")
        cookies = session.cookies.get_dict()
        lifetime = 3600 * 24
    else:
        if account == "secondary":
            cookies["ds_session_id"] = token  # often the cookie value itself
        lifetime = 3600 * 24

    chat_session_id = None
    try:
        chat_session_id = create_chat_session(token, cookies=cookies or None, model_type="expert")
        print(f"::notice::Created chat_session_id={chat_session_id} account={account}")
    except Exception as e:
        print(f"::warning::create_chat_session failed ({e}); completion may still work if server allocates")

    return {
        "account": account,
        "cookies": cookies,
        "token": token,
        "chat_session_id": chat_session_id,
        "parent_message_id": None,
        "expires": time.time() + lifetime,
    }


def ensure_session(cache_dir, account: str | None = None):
    account = normalize_account(account)
    cache_dir_path = Path(cache_dir) / account
    cache_dir_path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(cache_dir_path, 0o700)
    except OSError:
        pass

    cache_path = cache_dir_path / "session.json"

    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                session = json.load(f)
            if (
                isinstance(session, dict)
                and session.get("expires", 0) > time.time()
                and session.get("token")
            ):
                # Refresh chat_session_id if missing (important for completion API)
                if not session.get("chat_session_id"):
                    try:
                        session["chat_session_id"] = create_chat_session(
                            session["token"],
                            cookies=session.get("cookies") or None,
                            model_type="expert",
                        )
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(session, f)
                        os.chmod(cache_path, 0o600)
                    except Exception as e:
                        print(f"::warning::Could not attach chat_session_id: {e}")
                session["account"] = account
                return session
        except (OSError, json.JSONDecodeError, TypeError):
            pass

    session = get_new_session(account=account)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(session, f)
    try:
        os.chmod(cache_path, 0o600)
    except OSError:
        pass
    return session
