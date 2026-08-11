"""
Manages DeepSeek web session: PoW solving (real WASM from termux-monorepo),
cookie rotation, and persistence.
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
        text=True
    )
    return json.loads(result)


def get_new_session():
    pow_result = solve_pow()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    })

    resp = session.get(f"{DEEPSEEK_BASE}/api/chat")
    resp.raise_for_status()

    auth_payload = {
        'pow_answer': pow_result['answer'],
        'pow_signature': pow_result['signature'],
    }
    auth_resp = session.post(f"{DEEPSEEK_BASE}/api/auth", json=auth_payload)
    auth_resp.raise_for_status()

    token_data = auth_resp.json()
    token = token_data.get('token')
    if not token:
        raise RuntimeError("No token received from DeepSeek auth")

    session.headers['Authorization'] = f'Bearer {token}'

    return {
        'cookies': session.cookies.get_dict(),
        'headers': dict(session.headers),
        'token': token,
        'expires': time.time() + 3600 * 24,
    }


def ensure_session(cache_dir):
    cache_path = Path(cache_dir) / 'session.json'
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        with open(cache_path, 'r') as f:
            session = json.load(f)
        if session.get('expires', 0) > time.time():
            return session

    session = get_new_session()
    with open(cache_path, 'w') as f:
        json.dump(session, f)
    return session
