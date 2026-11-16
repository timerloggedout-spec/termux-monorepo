import os, json
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

class ClaudeWebBackend(ChatBackend):
    def __init__(self, session_manager):
        raw = session_manager.get_token("claude") or os.environ.get("CLAUDE_TOKEN")
        self.token = None
        self.org_id = None
        if raw:
            try:
                data = json.loads(raw)
                self.token = data.get("token")
                self.org_id = data.get("org_id")
            except:
                self.token = raw
        self.session = None

    def is_available(self):
        return bool(self.token)

    def send_message(self, message: str, context: list[dict]) -> str:
        if not self.session:
            self.session = curl_requests.Session()
            h = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Origin": "https://claude.ai",
                "Referer": "https://claude.ai/",
            }
            if self.org_id:
                h["anthropic-organization-id"] = self.org_id
            self.session.headers.update(h)

        msgs = [{"role": m["role"], "content": m["content"]} for m in context if m["role"] in ("user", "assistant")]
        msgs.append({"role": "user", "content": message})
        payload = {"model": "claude-3-7-sonnet-20250219", "max_tokens": 4096, "messages": msgs}
        resp = self.session.post("https://api.anthropic.com/v1/messages", json=payload)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
