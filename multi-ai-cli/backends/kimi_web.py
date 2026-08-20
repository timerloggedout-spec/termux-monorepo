import os, json
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    import requests as curl_requests

from .base import ChatBackend

class KimiWebBackend(ChatBackend):
    """
    Headless Web API Backend for Moonshot Kimi.
    Bypasses browser automation by emulating internal web endpoints.
    """
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.base_url = "https://kimi.moonshot.cn/api/chat"
        
        # Load cookies from session manager or environment
        self.cookies = session_manager.get_token("kimi_cookies")
        if isinstance(self.cookies, str):
            try:
                self.cookies = json.loads(self.cookies)
            except:
                self.cookies = {}

    def is_available(self):
        return bool(self.cookies)

    def send_message(self, message: str, context: list[dict]) -> str:
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://kimi.moonshot.cn",
            "referer": "https://kimi.moonshot.cn/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        # Build messages from context
        messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in context if m.get("role") != "meta"]
        messages.append({"role": "user", "content": message})

        payload = {
            "model": "kimi-v1",
            "messages": messages,
            "stream": True
        }

        try:
            kwargs = {"headers": headers, "json": payload, "cookies": self.cookies, "stream": True}
            if hasattr(curl_requests, "Session"):
                s = curl_requests.Session()
                resp = s.post(self.base_url, impersonate="chrome120", **kwargs)
            else:
                resp = curl_requests.post(self.base_url, **kwargs)

            resp.raise_for_status()

            full_response = ""
            for line in resp.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line.startswith("data:"):
                        data_str = decoded_line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            json_data = json.loads(data_str)
                            chunk = json_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            full_response += chunk
                        except:
                            continue
            
            return full_response.strip() if full_response else "[No content returned from Kimi]"

        except Exception as e:
            return f"Error calling Kimi Web API: {str(e)}"
