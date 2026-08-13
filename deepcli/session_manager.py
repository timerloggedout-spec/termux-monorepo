"""
Manages DeepSeek web session: PoW, cookies, chat_session_id, multi-account.

Template webWrapper accounts (from token_provider_v2 / cedar_forge PLAN):
  primary   / account-1  — PRIORITY (default)
  secondary / account-2  — alternate / cookies_2.json lineage

Session dir: 0o700 · session.json: 0o600

Credential resolution (Issue #184 catalog + docs/ops/DEEPSEEK-CI.md):
  Prefer explicit bearer tokens; fall back to imported cookie blobs
  (ds_session_id extracted when JSON). Never invent secret names —
  only consume what is already provisioned in repo secrets.
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
    # Account-1 / primary is PRIORITY default
    raw = (name or os.environ.get("DEEPSEEK_ACCOUNT") or "primary").strip().lower()
    return ACCOUNT_ALIASES.get(raw, raw if raw in ("primary", "secondary") else "primary")


def _extract_ds_session_id(raw: str) -> str | None:
    """If raw looks like a cookie dump (JSON list/dict), pull ds_session_id; else None."""
    raw = (raw or "").strip()
    if not raw:
        return None
    if not (raw.startswith("[") or raw.startswith("{")):
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    cookies = data if isinstance(data, list) else data.get("cookies", [])
    if isinstance(cookies, dict):
        # { "ds_session_id": "..." } form
        v = cookies.get("ds_session_id")
        return str(v).strip() if v else None
    for c in cookies or []:
        if isinstance(c, dict) and c.get("name") == "ds_session_id":
            v = c.get("value")
            return str(v).strip() if v else None
    return None


def _first_env(*keys: str) -> str | None:
    for key in keys:
        v = os.environ.get(key)
        if v and str(v).strip():
            return str(v).strip()
    return None


def solve_pow(token: str, cookies: dict | None = None, target_path: str = "/api/v0/chat/completion"):
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

    try:
        challenge_data = get_pow_challenge(token, cookies=cookies, target_path=target_path)
    except Exception as e:
        raise RuntimeError(f"Failed to get PoW challenge: {e}")

    challenge_json = json.dumps(challenge_data)
    result = subprocess.run(
        ["node", str(solver_script), str(wasm_path)],
        input=challenge_json,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f"PoW solver failed (rc={result.returncode}): {result.stderr[:200]}")

    output = result.stdout.strip()
    if not output.isdigit():
        raise RuntimeError(
            f"PoW solver returned non-numeric output: stdout={result.stdout[:100]!r}, "
            f"stderr={result.stderr[:100]!r}"
        )

    answer = int(output)
    return {
        "answer": answer,
        "signature": challenge_data.get("signature", ""),
        "challenge": challenge_data.get("challenge", ""),
        "salt": challenge_data.get("salt", ""),
        "expire_at": challenge_data.get("expire_at", 0),
        "difficulty": challenge_data.get("difficulty", 0),
    }


def _token_from_env(account: str) -> str | None:
    """
    Resolve bearer token / session id for account from env / secrets-exported vars.

    Names align with docs/ops/DEEPSEEK-CI.md and Issue #184 credential catalog.
    Cookie blobs are accepted: JSON cookie dumps yield ds_session_id; plain
    strings are used as-is (caller may treat them as ds_session_id).
    """
    specific = os.environ.get(f"DEEPSEEK_TOKEN_{account.upper()}")
    if specific and specific.strip():
        return specific.strip()

    if account == "secondary":
        v = _first_env(
            "DEEPSEEK_TOKEN_SECONDARY",
            "DEEPSEEK_TOKEN_ACCOUNT_2",
            "DEEPSEEK_ACCOUNT_2",
            "DEEPSEEK_ACCOUNT2",
            "DeepSeek_account-2",
        )
        if v:
            return v
        raw = _first_env("DEEPSEEK_COOKIES_2", "COOKIES_2", "DEEPSEEK_COOKIES")
        if raw:
            sid = _extract_ds_session_id(raw)
            return sid or raw
        return None

    # primary / account-1 — PRIORITY path
    # Order matches DEEPSEEK-CI.md SSOT + workflow mappings + #184 names.
    v = _first_env(
        "DEEPSEEK_TOKEN_PRIMARY",
        "DEEPSEEK_TOKEN_ACCOUNT_1",
        "DEEPSEEK_TOKEN",
        "DEEPSEEK_API_KEY",          # documented model-auth alias
        "DEEPSEEK_AUTH_TOKEN",       # documented model-auth alias
        "NEXUSCLI_TOKEN",            # documented model-auth alias
        "DEEPSEEK_ACCOUNT_1",
        "DeepSeek_account-1",
    )
    if v:
        # If someone stored a cookie dump under a token-named secret, unwrap it.
        sid = _extract_ds_session_id(v)
        return sid or v

    # Cookie-only primary secrets (imported cookies path)
    raw = _first_env(
        "DEEPSEEK_COOKIES",
        "DEEPSEEK_COOKIES_1",
        "COOKIES",
        "COOKIES_1",
        "DEEPSEEK_SESSION",
        "DEEPSEEK_DS_SESSION_ID",
    )
    if raw:
        sid = _extract_ds_session_id(raw)
        return sid or raw

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
        raise RuntimeError(
            f"create_chat_session: no id in response keys="
            f"{list(data) if isinstance(data, dict) else type(data)}"
        )
    return str(sid)


def get_pow_challenge(
    token: str,
    cookies: dict | None = None,
    target_path: str = "/api/v0/chat/completion",
) -> dict:
    s = _auth_session_headers(token, cookies)
    r = s.post(
        f"{DEEPSEEK_BASE}/api/v0/chat/create_pow_challenge",
        json={"target_path": target_path},
        timeout=30,
    )
    r.raise_for_status()
    resp_data = r.json()
    try:
        return resp_data["data"]["biz_data"]["challenge"]
    except (KeyError, TypeError) as e:
        code = resp_data.get("code") if isinstance(resp_data, dict) else None
        msg = resp_data.get("msg") if isinstance(resp_data, dict) else None
        raise RuntimeError(
            f"PoW challenge response missing expected structure: {e}. "
            f"Response code={code}, msg={msg}, keys="
            f"{list(resp_data.keys()) if isinstance(resp_data, dict) else type(resp_data)}"
        )


def get_new_session(account: str = "primary"):
    """
    Build a full session dict for the given account.
    Prefer env/secret token. Always attaches a fresh chat_session_id when possible.
    Cookie-derived values are attached as ds_session_id for both accounts.
    """
    account = normalize_account(account)
    token = _token_from_env(account)
    cookies: dict = {}

    if not token:
        raise RuntimeError(
            f"No token available for account={account}. "
            "Set one of: DEEPSEEK_TOKEN / DEEPSEEK_TOKEN_PRIMARY / DEEPSEEK_API_KEY / "
            "DEEPSEEK_AUTH_TOKEN / NEXUSCLI_TOKEN / DEEPSEEK_COOKIES "
            "(or SECONDARY / DEEPSEEK_COOKIES_2 for account-2). "
            "See docs/ops/DEEPSEEK-CI.md and Issue #184."
        )

    # Web-wrapper sessions treat the resolved value as both Bearer material and
    # the ds_session_id cookie when it originated from a cookie import.
    cookies["ds_session_id"] = token
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
                if not session.get("chat_session_id"):
                    try:
                        session["chat_session_id"] = create_chat_session(
                            session["token"],
                            cookies=session.get("cookies") or None,
                            model_type="expert",
                        )
                        fd = os.open(cache_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                        with os.fdopen(fd, "w", encoding="utf-8") as f:
                            json.dump(session, f)
                    except Exception as e:
                        print(f"::warning::Could not attach chat_session_id: {e}")
                session["account"] = account
                return session
        except (OSError, json.JSONDecodeError, TypeError):
            pass

    session = get_new_session(account=account)
    fd = os.open(cache_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(session, f)
    return session
