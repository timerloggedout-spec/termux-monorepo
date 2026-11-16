import os, sys, json, subprocess, base64
from pathlib import Path
try:
    from curl_cffi import requests as curl_requests
except Exception:
    import requests as standard_requests
    class MockCurlSession(standard_requests.Session):
        def __init__(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            super().__init__(*args, **kwargs)
        def request(self, method, url, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return super().request(method, url, *args, **kwargs)

    class CurlRequestsFallback:
        Session = MockCurlSession
        def get(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.get(*args, **kwargs)
        def post(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.post(*args, **kwargs)
        def put(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.put(*args, **kwargs)
        def delete(self, *args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.delete(*args, **kwargs)

    curl_requests = CurlRequestsFallback()

from .base import ChatBackend

BASE_URL = "https://chat.deepseek.com"
WASM_SOLVER = Path.home() / "deepcli" / "pow_solver.js"

class DeepSeekBackend(ChatBackend):
    def __init__(self, session_manager):
        # token
        self.token = session_manager.get_token("deepseek")
        if not self.token:
            self.token = os.environ.get("DEEPSEEK_TOKEN")
        if not self.token:
            try:
                sys.path.insert(0, str(Path.home() / "harmony_hub"))
                from src.token_provider_v2 import get_token
                self.token = get_token("primary")
            except: pass
        if not self.token:
            raise RuntimeError("No DeepSeek token found.")

        # cookie
        self.cookie = None
        cookie_path = session_manager.get("deepseek", "cookie_path")
        if cookie_path:
            cp = os.path.expanduser(cookie_path)
            if os.path.exists(cp):
                with open(cp) as f:
                    data = json.load(f)
                cookies = data if isinstance(data, list) else data.get('cookies', [])
                for c in cookies:
                    if c.get("name") == "ds_session_id":
                        self.cookie = c.get("value")
                        break
        self._session = None

    def is_available(self):
        return bool(self.token)

    def _get_session(self):
        if self._session is None:
            s = curl_requests.Session()
            s.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
                "Authorization": f"Bearer {self.token}",
                "X-Client-Platform": "web",
                "X-Client-Version": "1.3.0-auto-resume",
                "X-App-Version": "20241129.1",
                "X-Client-Locale": "en_US",
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}/",
            })
            if self.cookie:
                s.cookies.set("ds_session_id", self.cookie)
            self._session = s
        return self._session

    def solve_pow(self, challenge: dict) -> str:
        inp = json.dumps(challenge)
        proc = subprocess.run(["node", str(WASM_SOLVER)], input=inp,
                              capture_output=True, text=True, timeout=10)
        if proc.returncode != 0:
            raise RuntimeError(f"POW error: {proc.stderr.strip()}")
        answer = int(proc.stdout.strip())
        payload = {
            "algorithm": challenge.get("algorithm", "DeepSeekHashV1"),
            "challenge": challenge["challenge"],
            "salt": challenge["salt"],
            "answer": answer,
            "signature": challenge["signature"],
            "target_path": challenge.get("target_path", "/api/v0/chat/completion")
        }
        return base64.b64encode(json.dumps(payload).encode()).decode()

    def get_pow_challenge(self):
        s = self._get_session()
        r = s.post(f"{BASE_URL}/api/v0/chat/create_pow_challenge",
                   json={"target_path": "/api/v0/chat/completion"})
        r.raise_for_status()
        return r.json()["data"]["biz_data"]["challenge"]

    def create_session(self, model_type="expert"):
        s = self._get_session()
        r = s.post(f"{BASE_URL}/api/v0/chat_session/create",
                   json={"character_id": None, "model_type": model_type})
        r.raise_for_status()
        return r.json()["data"]["biz_data"]["id"]

    def send_message(self, message: str, context: list[dict]) -> str:
        challenge = self.get_pow_challenge()
        pow_header = self.solve_pow(challenge)

        # reuse or create session id
        session_id = None
        for m in context:
            if isinstance(m, dict) and m.get("__session_id"):
                session_id = m["__session_id"]
                break
        if not session_id:
            session_id = self.create_session()
            context.insert(0, {"role": "meta", "__session_id": session_id})

        payload = {
            "chat_session_id": session_id,
            "parent_message_id": None,
            "prompt": message,
            "ref_file_ids": [],
            "thinking_enabled": True,
            "search_enabled": False,
            "stream": False,  # server ignores this, always SSE
        }
        s = self._get_session()
        headers = s.headers.copy()
        headers["X-Ds-Pow-Response"] = pow_header
        headers["Content-Type"] = "application/json"

        resp = curl_requests.post(
            f"{BASE_URL}/api/v0/chat/completion",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()

        # --- parse SSE manually (server always streams) ---
        final_content = ""
        for line in resp.text.split("\n"):
            if line.startswith("data:"):
                try:
                    data = json.loads(line[5:].strip())
                    # The "v" object contains the actual message chunk
                    if isinstance(data, dict) and "v" in data:
                        v = data["v"]
                        if isinstance(v, dict) and "response" in v:
                            content = v["response"].get("content", "")
                            final_content += content
                except json.JSONDecodeError:
                    pass

        if not final_content:
            # fallback: maybe response structure is different
            for line in resp.text.split("\n"):
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if isinstance(data, dict) and "content" in data:
                            final_content += data["content"]
                    except:
                        pass

        return final_content if final_content else "[No content returned]"
