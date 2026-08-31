import os, json, time
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    import requests as curl_requests

from .base import ChatBackend

class GrokWebBackend(ChatBackend):
    """
    Headless Web API Backend for Grok (xAI).
    Bypasses browser automation by emulating internal web endpoints.
    """
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.base_url = "https://grok.com/rest/app-chat/conversations/new"
        
        # Load cookies from session manager or environment
        self.cookies = session_manager.get_token("grok_cookies")
        if isinstance(self.cookies, str):
            try:
                self.cookies = json.loads(self.cookies)
            except:
                self.cookies = {}
        
        if not self.cookies:
            # Fallback to individual env vars
            self.cookies = {
                "x-anonuserid": os.environ.get("GROK_ANON_ID"),
                "x-challenge": os.environ.get("GROK_CHALLENGE"),
                "x-signature": os.environ.get("GROK_SIGNATURE"),
                "sso": os.environ.get("GROK_SSO"),
                "sso-rw": os.environ.get("GROK_SSO_RW")
            }

    def is_available(self):
        return all(self.cookies.values())

    def send_message(self, message: str, context: list[dict], **kwargs) -> str:
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://grok.com",
            "referer": "https://grok.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        search_enabled = kwargs.get("search", True)
        is_reasoning = kwargs.get("thinking", False)

        payload = {
            "temporary": False,
            "modelName": "grok-3",
            "message": message,
            "fileAttachments": [],
            "imageAttachments": [],
            "disableSearch": not search_enabled,
            "enableImageGeneration": True,
            "returnImageBytes": False,
            "returnRawGrokInXaiRequest": False,
            "enableImageStreaming": True,
            "imageGenerationCount": 2,
            "forceConcise": False,
            "toolOverrides": {},
            "enableSideBySide": True,
            "isPreset": False,
            "sendFinalMetadata": True,
            "customInstructions": "",
            "deepsearchPreset": "deepsearch" if search_enabled and is_reasoning else "",
            "isReasoning": is_reasoning
        }

        try:
            # Use impersonate if using curl_cffi for better WAF bypass
            kwargs = {"headers": headers, "json": payload, "cookies": self.cookies, "stream": True}
            if hasattr(curl_requests, "Session"):
                s = curl_requests.Session()
                if hasattr(s, "impersonate"):
                    resp = s.post(self.base_url, impersonate="chrome120", **kwargs)
                else:
                    resp = s.post(self.base_url, **kwargs)
            else:
                resp = curl_requests.post(self.base_url, **kwargs)

            resp.raise_for_status()

            full_response = ""
            for line in resp.iter_lines():
                if line:
                    try:
                        decoded_line = line.decode('utf-8')
                        json_data = json.loads(decoded_line)
                        result = json_data.get("result", {})
                        response_data = result.get("response", {})
                        
                        # Handle full message in one go if available
                        if "modelResponse" in response_data:
                            return response_data["modelResponse"]["message"]
                            
                        # Handle streaming tokens
                        token = response_data.get("token", "")
                        if token:
                            full_response += token
                    except:
                        continue
            
            return full_response.strip() if full_response else "[No content returned from Grok]"

        except Exception as e:
            return f"Error calling Grok Web API: {str(e)}"
