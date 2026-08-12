"""
Manages DeepSeek web session: PoW solving (real WASM),
cookie rotation, and cross-run persistence (operator-required).

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


def solve_pow():
    wasm_path = WASM_DIR / "deepseek.wasm"
    solver_script = WASM_DIR / "pow_solver.js"

    if not wasm_path.exists():
        raise FileNotFoundError(f"WASM file not found: {wasm_path}")
    if not solver_script.exists():
        raise FileNotFoundError(f"Solver script not found: {solver_script}")

    result = subprocess.check_output(
        ['node', str(solver_script), str(wasm_path)],
        text=True,
        timeout=60,
    )
    parsed = json.loads(result)
    if not isinstance(parsed, dict) or 'answer' not in parsed or 'signature' not in parsed:
        raise RuntimeError(f"PoW solver returned invalid shape: {parsed!r}")
    return parsed


def get_new_session():
    pow_result = solve_pow()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    })

    resp = session.get(f"{DEEPSEEK_BASE}/api/chat", timeout=30)
    resp.raise_for_status()

    auth_payload = {
        'pow_answer': pow_result['answer'],
        'pow_signature': pow_result['signature'],
    }
    auth_resp = session.post(f"{DEEPSEEK_BASE}/api/auth", json=auth_payload, timeout=30)
    auth_resp.raise_for_status()

    token_data = auth_resp.json()
    token = token_data.get('token')
    if not token:
        raise RuntimeError("No token received from DeepSeek auth")

    session.headers['Authorization'] = f'Bearer {token}'

    # Prefer server-provided lifetime when present
    lifetime = token_data.get('expires_in') or token_data.get('lifetime') or (3600 * 24)
    try:
        lifetime = int(lifetime)
    except (TypeError, ValueError):
        lifetime = 3600 * 24

    return {
        'cookies': session.cookies.get_dict(),
        'headers': {k: v for k, v in session.headers.items() if k.lower() != 'authorization'},
        'token': token,
        'expires': time.time() + lifetime,
    }


def ensure_session(cache_dir):
    cache_dir_path = Path(cache_dir)
    cache_dir_path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(cache_dir_path, 0o700)
    except OSError:
        pass

    cache_path = cache_dir_path / 'session.json'

    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                session = json.load(f)
            if isinstance(session, dict) and session.get('expires', 0) > time.time() and session.get('token'):
                return session
        except (OSError, json.JSONDecodeError, TypeError):
            pass  # refresh below

    session = get_new_session()
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(session, f)
    try:
        os.chmod(cache_path, 0o600)
    except OSError:
        pass
    return session
