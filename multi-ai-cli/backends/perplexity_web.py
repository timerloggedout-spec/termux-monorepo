import os, json
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    import requests as curl_requests

from .base import ChatBackend

class PerplexityWebBackend(ChatBackend):
    """
    Headless Web API Backend for Perplexity AI.
    Bypasses browser automation by emulating internal web endpoints.
    """
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.base_url = "https://www.perplexity.ai/api/chat"
        
        # Load cookies from session manager or environment
        self.cookies = session_manager.get_token("perplexity_cookies")
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
            "origin": "https://www.perplexity.ai",
            "referer": "https://www.perplexity.ai/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        # Build messages from context
        messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in context if m.get("role") != "meta"]
        messages.append({"role": "user", "content": message})

        payload = {
            "version": "2.0",
            "source": "web",
            "model": "llama-3-sonar-large-32k-online",
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
            # Perplexity often uses Socket.IO or specific SSE formats
            # This is a simplified parser for their internal API
            for line in resp.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    try:
                        # Internal API lines often start with specific prefixes
                        if decoded_line.startswith("42"): # Socket.IO message
                            data = json.loads(decoded_line[2:])
                            if data[0] == "query_answered":
                                return data[1].get("text", "")
                        elif decoded_line.startswith("data:"):
                            data_str = decoded_line[5:].strip()
                            json_data = json.loads(data_str)
                            chunk = json_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            full_response += chunk
                    except:
                        continue
            
            return full_response.strip() if full_response else "[No content returned from Perplexity]"

        except Exception as e:
            return f"Error calling Perplexity Web API: {str(e)}"
