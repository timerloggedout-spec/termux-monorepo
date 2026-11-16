import sys, json, base64, subprocess
from pathlib import Path
from curl_cffi import requests as curl_requests

# ------------------------------------------------------------
# Copy the exact setup from the backend (token, cookie, headers)
# ------------------------------------------------------------
TOKEN = open(Path.home() / "deepseek-cli" / "token_account2.txt").read().strip()
COOKIES_FILE = Path.home() / "deepseek-cli" / "cookies_2.json"
BASE_URL = "https://chat.deepseek.com"
WASM_SOLVER = Path.home() / "deepcli" / "pow_solver.js"

# load cookie
cookies_data = json.loads(COOKIES_FILE.read_text())
cookies = cookies_data if isinstance(cookies_data, list) else cookies_data.get("cookies", [])
ds_session = next((c["value"] for c in cookies if c.get("name") == "ds_session_id"), None)
print(f"Token: {TOKEN[:30]}...")
print(f"Cookie: {ds_session}")

# build session
s = curl_requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Authorization": f"Bearer {TOKEN}",
    "X-Client-Platform": "web",
    "X-Client-Version": "1.3.0-auto-resume",
    "X-App-Version": "20241129.1",
    "X-Client-Locale": "en_US",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/",
})
if ds_session:
    s.cookies.set("ds_session_id", ds_session)

# ------------------------------------------------------------
# Step 1 — POW challenge
# ------------------------------------------------------------
print("\n[1] Getting POW challenge...")
r = s.post(f"{BASE_URL}/api/v0/chat/create_pow_challenge",
           json={"target_path": "/api/v0/chat/completion"})
print(f"    Status: {r.status_code}")
print(f"    Body: {r.text[:300]}")
if r.status_code != 200:
    sys.exit("POW challenge failed")
challenge = r.json()["data"]["biz_data"]["challenge"]

# ------------------------------------------------------------
# Step 2 — Solve POW
# ------------------------------------------------------------
print("\n[2] Solving POW...")
inp = json.dumps(challenge)
proc = subprocess.run(["node", str(WASM_SOLVER)], input=inp,
                      capture_output=True, text=True, timeout=10)
if proc.returncode != 0:
    sys.exit(f"POW solver error: {proc.stderr.strip()}")
answer = int(proc.stdout.strip())
print(f"    Answer: {answer}")

pow_payload = {
    "algorithm": challenge.get("algorithm", "DeepSeekHashV1"),
    "challenge": challenge["challenge"],
    "salt": challenge["salt"],
    "answer": answer,
    "signature": challenge["signature"],
    "target_path": challenge.get("target_path", "/api/v0/chat/completion")
}
pow_header = base64.b64encode(json.dumps(pow_payload).encode()).decode()
print(f"    POW header: {pow_header[:60]}...")

# ------------------------------------------------------------
# Step 3 — Create chat session
# ------------------------------------------------------------
print("\n[3] Creating chat session...")
r = s.post(f"{BASE_URL}/api/v0/chat_session/create",
           json={"character_id": None, "model_type": "expert"})
print(f"    Status: {r.status_code}")
print(f"    Body: {r.text[:400]}")
if r.status_code != 200:
    sys.exit("Session creation failed")
session_id = r.json()["data"]["biz_data"]["id"]
print(f"    Session ID: {session_id}")

# ------------------------------------------------------------
# Step 4 — Send message
# ------------------------------------------------------------
print("\n[4] Sending message...")
payload = {
    "chat_session_id": session_id,
    "parent_message_id": None,
    "prompt": "Write a haiku about Termux",
    "ref_file_ids": [],
    "thinking_enabled": True,
    "search_enabled": False,
    "stream": False,
}
headers = s.headers.copy()
headers["X-Ds-Pow-Response"] = pow_header
headers["Content-Type"] = "application/json"
r = curl_requests.post(f"{BASE_URL}/api/v0/chat/completion",
                       json=payload, headers=headers)
print(f"    Status: {r.status_code}")
print(f"    Body (first 500 chars): {r.text[:500]}")
