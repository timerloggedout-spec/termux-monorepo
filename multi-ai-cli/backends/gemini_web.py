import os, json
from curl_cffi import requests as curl_requests
from .base import ChatBackend

class GeminiWebBackend(ChatBackend):
    def __init__(self, session_manager):
        self.token = session_manager.get_token("gemini") or os.environ.get("GEMINI_TOKEN")
        self.cookie_path = session_manager.get("gemini", "cookie_path")
        self.session = None

    def is_available(self):
        self._ensure_session()
        try:
            return self.session.get("https://gemini.google.com/api/chat").status_code == 200
        except:
            return False

    def _ensure_session(self):
        if self.session is None:
            self.session = curl_requests.Session(impersonate="chrome110")
            if self.cookie_path:
                p = os.path.expanduser(self.cookie_path)
                if os.path.exists(p):
                    with open(p) as f:
                        for c in json.load(f):
                            self.session.cookies.set(c["name"], c["value"], domain=c.get("domain", ".google.com"), path=c.get("path", "/"))
            if self.token:
                self.session.headers["Authorization"] = f"Bearer {self.token}"

    def send_message(self, message: str, context: list[dict]) -> str:
        self._ensure_session()
        payload = {"contents": [{"role": "user", "parts": [{"text": message}]}]}
        resp = self.session.post("https://gemini.google.com/api/chat", json=payload)
        if resp.status_code != 200:
            resp = self.session.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                json=payload, params={"key": self.token}
            )
        resp.raise_for_status()
        data = resp.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return data.get("text") or json.dumps(data)
