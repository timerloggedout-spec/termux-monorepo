import json, os, re
from pathlib import Path
from curl_cffi import requests as curl_requests

COOKIE_FILE = Path.home() / ".multi-ai-tokens" / "mistral_cookies.json"
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
        if not COOKIE_FILE.exists():
            return
        with open(COOKIE_FILE) as f:
            data = json.load(f)
        cookies = data.get("cookies", data if isinstance(data, list) else [])
        for c in cookies:
            self.session.cookies.set(
                c["name"], c["value"],
                domain=c.get("domain", ".mistral.ai"),
                path=c.get("path", "/")
            )

    def is_available(self):
        try:
            r = self.session.get(f"{BASE}/api/auth/session")
            if r.ok:
                data = r.json()
                return "user" in data and data["user"] is not None
            return False
        except:
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
        for c in self.session.cookies:
            if c.name == "csrftoken":
                csrf = c.value
                break
        headers = {}
        if csrf:
            headers["X-CSRFToken"] = csrf

        payload = {
            "messages": msgs,
            "model": "mistral-large-latest",
            "stream": False,
        }
        # Primary endpoint (may change; we adapt)
        for endpoint in ["/api/chat/completions", "/api/chat", "/api/v1/chat"]:
            r = self.session.post(f"{BASE}{endpoint}", json=payload, headers=headers)
            if r.status_code == 200:
                break
        else:
            r.raise_for_status()

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
