"""
Mistral AI Web Backend with curl_cffi support

This module provides integration with Mistral AI's web interface,
using curl_cffi for browser impersonation to access the service
similar to how ChapitoAI and DeepSeek integrations work.

Features:
- Browser impersonation via curl_cffi
- Token and cookie management
- Chat completion with streaming support
- Code extraction and harvest capabilities
- Integration with Termux/Pinggy bridge
"""

import os
import sys
import json
import base64
import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from curl_cffi import requests as curl_requests
except ImportError:
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
        
        @staticmethod
        def get(*args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.get(*args, **kwargs)
        
        @staticmethod
        def post(*args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.post(*args, **kwargs)
        
        @staticmethod
        def put(*args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.put(*args, **kwargs)
        
        @staticmethod
        def delete(*args, **kwargs):
            kwargs.pop("impersonate", None)
            return standard_requests.delete(*args, **kwargs)
    
    curl_requests = CurlRequestsFallback()

from .base import ChatBackend
from core.core import DeepTermWebWrapper, get_wrapper


# Mistral AI API endpoints
MISTRAL_BASE_URL = "https://chat.mistral.ai"
MISTRAL_API_URL = "https://api.mistral.ai"
MISTRAL_CHAT_URL = f"{MISTRAL_BASE_URL}/api/chat"
MISTRAL_COMPLETION_URL = f"{MISTRAL_API_URL}/v1/chat/completions"

# Browser impersonation settings
MISTRAL_IMPERSONATE = "chrome120"
MISTRAL_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class MistralWebBackend(ChatBackend):
    """
    Mistral AI Web Backend implementation
    
    Provides integration with Mistral AI's web interface using
    curl_cffi for browser impersonation.
    """
    
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.token = None
        self.cookies = {}
        self.session = None
        self.model = "mistral-large"
        self._wrapper = None
        self._bridge_initialized = False
        
        # Initialize from session manager or environment
        self._initialize_auth()
        self._initialize_session()
    
    def _initialize_auth(self):
        """Initialize authentication from various sources"""
        # Try session manager first
        self.token = self.session_manager.get_token("mistral")
        
        # Try environment variable
        if not self.token:
            self.token = os.environ.get("MISTRAL_TOKEN")
        
        # Try environment variable alternative
        if not self.token:
            self.token = os.environ.get("MISTRAL_API_KEY")
        
        # Try harmony_hub token provider
        if not self.token:
            try:
                sys.path.insert(0, str(Path.home() / "harmony_hub"))
                from src.token_provider_v2 import get_token
                self.token = get_token("mistral")
            except Exception:
                pass
        
        # Try to load cookies
        self._load_cookies()
    
    def _load_cookies(self):
        """Load cookies from session manager or file"""
        cookie_path = self.session_manager.get("mistral", "cookie_path")
        if cookie_path:
            try:
                cp = os.path.expanduser(cookie_path)
                if os.path.exists(cp):
                    with open(cp) as f:
                        data = json.load(f)
                    cookies = data if isinstance(data, list) else data.get('cookies', [])
                    for c in cookies:
                        self.cookies[c.get("name")] = c.get("value")
            except Exception as e:
                print(f"Warning: Failed to load cookies: {e}", file=sys.stderr)
    
    def _initialize_session(self):
        """Initialize curl_cffi session with proper headers"""
        self.session = curl_requests.Session(impersonate=MISTRAL_IMPERSONATE)
        self.session.headers.update({
            "User-Agent": MISTRAL_USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Origin": MISTRAL_BASE_URL,
            "Referer": f"{MISTRAL_BASE_URL}/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        })
        
        # Add authorization header if token available
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        
        # Add cookies if available
        if self.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            self.session.headers["Cookie"] = cookie_str
    
    def is_available(self) -> bool:
        """Check if backend is available"""
        return bool(self.token or self.cookies)
    
    def _get_wrapper(self) -> DeepTermWebWrapper:
        """Get or initialize the DeepTermWebWrapper"""
        if self._wrapper is None:
            self._wrapper = get_wrapper()
            try:
                self._bridge_initialized = self._wrapper.initialize_bridge()
            except Exception as e:
                print(f"Warning: Failed to initialize bridge: {e}", file=sys.stderr)
                self._bridge_initialized = False
        return self._wrapper
    
    def _get_pow_challenge(self) -> Optional[Dict]:
        """
        Get Proof of Work challenge (if required by Mistral)
        
        Note: Mistral may or may not require PoW depending on the endpoint.
        This method provides a template for PoW handling similar to DeepSeek.
        """
        try:
            # This is a placeholder - Mistral's actual PoW requirements may differ
            response = self.session.post(
                f"{MISTRAL_BASE_URL}/api/pow/challenge",
                json={"target_path": "/api/chat"}
            )
            if response.status_code == 200:
                return response.json().get("data", {}).get("biz_data", {}).get("challenge")
            return None
        except Exception:
            return None
    
    def _solve_pow(self, challenge: Dict) -> Optional[str]:
        """
        Solve Proof of Work challenge
        
        Uses the WASM solver from deepterm_fork if available.
        """
        if not challenge:
            return None
        
        try:
            # Try to use deepterm's WASM solver
            wasm_solver = Path.home() / "deepcli" / "pow_solver.js"
            if wasm_solver.exists():
                import subprocess
                inp = json.dumps(challenge)
                proc = subprocess.run(
                    ["node", str(wasm_solver)], 
                    input=inp, capture_output=True, text=True, timeout=10
                )
                if proc.returncode == 0:
                    answer = int(proc.stdout.strip())
                    payload = {
                        "algorithm": challenge.get("algorithm", "MistralHashV1"),
                        "challenge": challenge["challenge"],
                        "salt": challenge["salt"],
                        "answer": answer,
                        "signature": challenge["signature"],
                        "target_path": challenge.get("target_path", "/api/chat")
                    }
                    return base64.b64encode(json.dumps(payload).encode()).decode()
            
            # Fallback: try to use harmony_hub's solver
            try:
                sys.path.insert(0, str(Path.home() / "harmony_hub"))
                from src.pow_solver import solve_pow
                return solve_pow(challenge)
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            print(f"Warning: Failed to solve PoW: {e}", file=sys.stderr)
            return None
    
    def create_chat_session(self) -> Optional[str]:
        """Create a new chat session"""
        try:
            response = self.session.post(
                f"{MISTRAL_BASE_URL}/api/chat/session",
                json={"model": self.model}
            )
            if response.status_code == 200:
                return response.json().get("data", {}).get("id")
            return None
        except Exception as e:
            print(f"Warning: Failed to create chat session: {e}", file=sys.stderr)
            return None
    
    def send_message(self, message: str, context: List[Dict]) -> str:
        """
        Send a message and get a response from Mistral AI
        
        This is the main method for chat completion, supporting
        both API and web interface approaches.
        """
        # Try API endpoint first
        try:
            return self._send_via_api(message, context)
        except Exception as api_error:
            print(f"API endpoint failed, trying web interface: {api_error}", 
                  file=sys.stderr)
            try:
                return self._send_via_web(message, context)
            except Exception as web_error:
                print(f"Web interface also failed: {web_error}", file=sys.stderr)
                raise RuntimeError(f"Both API and web interfaces failed: {api_error}, {web_error}")
    
    def _send_via_api(self, message: str, context: List[Dict]) -> str:
        """Send message via Mistral API endpoint"""
        # Build messages array from context
        messages = []
        for msg in context:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})
        
        # Add the new message
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False,
        }
        
        response = self.session.post(
            MISTRAL_COMPLETION_URL,
            json=payload
        )
        
        response.raise_for_status()
        
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        
        # Handle error responses
        if "error" in data:
            raise RuntimeError(f"Mistral API error: {data['error']}")
        
        raise RuntimeError("Unexpected response format from Mistral API")
    
    def _send_via_web(self, message: str, context: List[Dict]) -> str:
        """Send message via Mistral web interface"""
        # Get PoW challenge if required
        challenge = self._get_pow_challenge()
        pow_header = None
        if challenge:
            pow_header = self._solve_pow(challenge)
        
        # Build headers
        headers = self.session.headers.copy()
        if pow_header:
            headers["X-Mistral-Pow-Response"] = pow_header
        
        # Find or create session ID from context
        session_id = None
        for msg in context:
            if isinstance(msg, dict) and msg.get("__session_id"):
                session_id = msg["__session_id"]
                break
        
        if not session_id:
            session_id = self.create_chat_session()
            if session_id:
                context.insert(0, {"role": "meta", "__session_id": session_id})
        
        # Prepare payload
        payload = {
            "session_id": session_id,
            "message": message,
            "model": self.model,
        }
        
        # Send request
        response = self.session.post(
            MISTRAL_CHAT_URL,
            json=payload,
            headers=headers
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        # Extract content from response
        # Handle different response formats
        if "data" in data:
            content = data["data"].get("content", "")
        elif "choices" in data:
            content = data["choices"][0].get("message", {}).get("content", "")
        elif "response" in data:
            content = data["response"].get("content", "")
        else:
            content = str(data)
        
        if not content:
            raise RuntimeError("No content in response from Mistral web interface")
        
        return content
    
    def extract_code(self, text: str) -> List[Dict]:
        """
        Extract code blocks from text
        
        This method identifies and extracts code blocks from
        Mistral AI responses, supporting multiple languages.
        """
        code_blocks = []
        
        # Pattern for markdown code blocks
        code_pattern = r'```(\w*)\n([\s\S]*?)```'
        matches = re.findall(code_pattern, text)
        
        for lang, code in matches:
            code_blocks.append({
                "language": lang.strip() if lang.strip() else "text",
                "code": code.strip(),
                "type": "code_block"
            })
        
        # Pattern for inline code
        inline_pattern = r'`([^`\n]+)`'
        inline_matches = re.findall(inline_pattern, text)
        
        for code in inline_matches:
            code_blocks.append({
                "language": "text",
                "code": code.strip(),
                "type": "inline_code"
            })
        
        return code_blocks
    
    def search_codebase(self, query: str, 
                       repo: str = "timerloggedout-spec/termux-monorepo",
                       branch: str = "master") -> List[Dict]:
        """
        Search codebase using GitHub API via gh CLI
        
        This provides search capabilities across the repository,
        leveraging the Termux/Pinggy bridge for access.
        """
        results = []
        
        try:
            # Use gh CLI to search
            import subprocess
            cmd = [
                "gh", "search", "code", query,
                "--repo", repo,
                "--json", "path,lineNumber,text"
            ]
            
            if branch:
                cmd.extend(["--branch", branch])
            
            result = subprocess.run(cmd, capture_output=True, 
                                  timeout=60, text=True)
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list):
                        for item in data:
                            results.append({
                                "path": item.get("path", ""),
                                "line": item.get("lineNumber", 0),
                                "text": item.get("text", ""),
                                "repo": repo,
                                "branch": branch
                            })
                except json.JSONDecodeError:
                    # Parse as text
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            results.append({
                                "path": "",
                                "line": 0,
                                "text": line,
                                "repo": repo,
                                "branch": branch
                            })
        
        except Exception as e:
            print(f"Warning: Code search failed: {e}", file=sys.stderr)
        
        return results
    
    def harvest_code(self, path: str, 
                     repo: str = "timerloggedout-spec/termux-monorepo",
                     branch: str = "master") -> Optional[str]:
        """
        Harvest code from a specific file path
        
        Uses the Termux/Pinggy bridge to access files via
        GitHub or direct SSH access.
        """
        try:
            # Try via gh CLI first
            import subprocess
            cmd = [
                "gh", "api",
                f"repos/{repo}/contents/{path}?ref={branch}",
                "--jq", ".content"
            ]
            
            result = subprocess.run(cmd, capture_output=True, 
                                  timeout=30, text=True)
            
            if result.returncode == 0:
                import base64
                encoded = result.stdout.strip()
                if encoded:
                    return base64.b64decode(encoded).decode('utf-8')
            
            # Try via bridge if available
            wrapper = self._get_wrapper()
            if self._bridge_initialized:
                # Execute remote command to read file
                remote_path = f"/data/data/com.termux/files/home/{path}"
                try:
                    content = wrapper.execute_shell_command(
                        f"cat {remote_path}"
                    )
                    return content
                except Exception:
                    pass
            
        except Exception as e:
            print(f"Warning: Code harvest failed: {e}", file=sys.stderr)
        
        return None
    
    def execute_remote(self, command: str, 
                      ssh_key_path: Optional[str] = None) -> str:
        """
        Execute a command on the remote Termux device
        
        This provides direct access to the Termux environment
        via the Pinggy bridge.
        """
        wrapper = self._get_wrapper()
        if not self._bridge_initialized:
            raise RuntimeError("Bridge not initialized")
        
        return wrapper.execute_shell_command(command, ssh_key_path)
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Get the current bridge status"""
        try:
            wrapper = self._get_wrapper()
            if self._bridge_initialized:
                config = wrapper.bridge.fetch_bridge_config()
                return {
                    "status": config.status,
                    "endpoint": config.endpoint,
                    "port": config.port,
                    "ssh_user": config.ssh_user,
                    "transport": config.transport,
                    "ttl_minutes": config.ttl_minutes
                }
        except Exception:
            pass
        
        return {"status": "unavailable"}


# Compatibility with existing backend interface
class MistralBackend(ChatBackend):
    """Alias for MistralWebBackend for compatibility"""
    
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self._web_backend = MistralWebBackend(session_manager)
    
    def is_available(self) -> bool:
        return self._web_backend.is_available()
    
    def send_message(self, message: str, context: List[Dict]) -> str:
        return self._web_backend.send_message(message, context)


if __name__ == "__main__":
    # Test the backend
    from core.session_manager import SessionManager
    
    mgr = SessionManager()
    backend = MistralWebBackend(mgr)
    
    print(f"Backend available: {backend.is_available()}")
    
    # Test bridge
    if backend._bridge_initialized:
        print(f"Bridge status: {backend.get_bridge_status()}")
    
    # Test code extraction
    test_text = """
Here's some Python code:

```python
def hello():
    print("Hello, World!")
```

And some JavaScript:

```javascript
function test() {
    console.log("test");
}
```
"""
    
    code_blocks = backend.extract_code(test_text)
    print(f"Extracted {len(code_blocks)} code blocks")
    for block in code_blocks:
        print(f"  - {block['language']}: {block['code'][:50]}...")
