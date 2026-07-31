import json, os, re
from pathlib import Path
from curl_cffi import requests as curl_requests

# Use archwiz config for token/cookie paths and environment detection
from archwiz import config as aw_config

COOKIE_FILE = aw_config.get_tokens_dir() / "mistral_cookies.json"
BASE = "https://chat.mistral.ai"

class MistralV1Backend:
    def __init__(self):
        self.session = curl_requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Android 14; Mobile; rv:151.0) Gecko/151.0 Firefox/151.0",
            "Accept": "application/json",
            "Origin": BASE,
            "Referer": f"{BASE}/",
        })
        self._load_cookies()

    def _load_cookies(self):
        try:
            if not COOKIE_FILE.exists():
                return
            with open(COOKIE_FILE) as f:
                data = json.load(f)
            cookies = data.get("cookies", data if isinstance(data, list) else [])
            for c in cookies:
                # Defensive: ensure required fields exist
                name = c.get('name')
                value = c.get('value')
                if name is None or value is None:
                    continue
                domain = c.get('domain', '.mistral.ai')
                path = c.get('path', '/')
                self.session.cookies.set(name, value, domain=domain, path=path)
        except Exception as e:
            print(f"[mistral] error loading cookies: {e}")

    def is_available(self):
        try:
            r = self.session.get(f"{BASE}/api/auth/session", timeout=10)
            if r.ok:
                data = r.json()
                return "user" in data and data["user"] is not None
            return False
        except Exception as e:
            print(f"[mistral] availability check failed: {e}")
            return False

    def send_message(self, message: str, context: list) -> str:
        # Build Mistral web chat payload (observed from network tab)
        msgs = []
        for m in context:
            role = m.get("role", "")
            if role in ("user", "assistant"):
                msgs.append({"role": role, "content": m.get("content", "")})
        msgs.append({"role": "user", "content": message})

        # Get CSRF token from cookies
        csrf = None
        try:
            for c in self.session.cookies:
                if getattr(c, 'name', None) == "csrftoken" or (hasattr(c, 'name') and c.name == 'csrftoken'):
                    csrf = c.value
                    break
        except Exception:
            csrf = None

        headers = {}
        if csrf:
            headers["X-CSRFToken"] = csrf

        payload = {
            "messages": msgs,
            "model": "mistral-large-latest",
            "stream": False,
        }
        # Primary endpoint (may change; we adapt)
        last_exc = None
        for endpoint in ["/api/chat/completions", "/api/chat", "/api/v1/chat"]:
            try:
                r = self.session.post(f"{BASE}{endpoint}", json=payload, headers=headers, timeout=20)
                if r.status_code == 200:
                    break
            except Exception as e:
                last_exc = e
                continue
        else:
            if last_exc:
                raise last_exc
            raise RuntimeError("No endpoint responded with 200")

        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "content" in data:
            return data["content"]
        elif "message" in data:
            return data["message"]
        else:
            # Dump unknown structure for debugging
            return json.dumps(data)

backend = MistralV1Backend()
