"""
DeepTerm Integration Module for Multi-AI CLI

This module provides integration with the deepterm_fork architecture,
bridging the JavaScript-based DeepTerm with our Python multi-ai-cli.

Key Features:
- WASM PoW solver integration
- DeepSeek API compatibility
- Browser impersonation headers
- Request signing and authentication
- Integration with curl_cffi for high-performance HTTP

The deepterm_fork provides:
- deepseek.wasm: WASM-based Proof of Work solver
- deepterm-core.js: Core functionality (PoW solving, API headers, session management)
- deepterm-api.js: API server for DeepSeek
- deepterm: CLI interface

This Python module adapts these capabilities for use in multi-ai-cli.
"""

import os
import sys
import json
import base64
import subprocess
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.core import CurlCffiSession, DeepTermWebWrapper, get_wrapper
from backends.base import ChatBackend


# DeepTerm configuration
DEEPTERM_DIR = Path.home() / "deepterm_fork"
DEEPSEEK_WASM = DEEPTERM_DIR / "deepseek.wasm"
DEEPSEEK_BASE_URL = "https://chat.deepseek.com"

# Browser impersonation settings from deepterm-core.js
DEEPTERM_HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.0.0", "Brave";v="138.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'x-app-version': '20241129.1',
    'x-client-locale': 'en_US',
    'x-client-platform': 'web',
    'x-client-version': '1.3.0-auto-resume'
}


@dataclass
class DeepTermConfig:
    """Configuration for DeepTerm integration"""
    token: Optional[str] = None
    wasm_path: Path = DEEPSEEK_WASM
    base_url: str = DEEPSEEK_BASE_URL
    impersonate: str = "chrome120"
    use_wasm_solver: bool = True
    
    def get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get headers with optional authorization"""
        headers = DEEPTERM_HEADERS.copy()
        if token or self.token:
            headers['authorization'] = f"Bearer {token or self.token}"
        return headers


class WasmPowSolver:
    """
    WASM-based Proof of Work solver
    
    Uses the deepseek.wasm file from deepterm_fork to solve
    DeepSeek's PoW challenges efficiently.
    """
    
    def __init__(self, wasm_path: Optional[Path] = None):
        self.wasm_path = wasm_path or DEEPSEEK_WASM
        self._wasm_initialized = False
        self._wasm_instance = None
        self._memory = None
        self._malloc = None
        self._stack_ptr = None
    
    def _initialize_wasm(self):
        """Initialize WASM module"""
        if self._wasm_initialized:
            return
        
        if not self.wasm_path.exists():
            raise FileNotFoundError(
                f"WASM file not found: {self.wasm_path}. "
                "Please ensure deepterm_fork is cloned and deepseek.wasm is available."
            )
        
        try:
            import wasmtime
            
            # Read WASM file
            with open(self.wasm_path, 'rb') as f:
                wasm_bytes = f.read()
            
            # Initialize WASM
            engine = wasmtime.Engine()
            module = wasmtime.Module.from_binary(engine, wasm_bytes)
            
            # Create store and instance
            store = wasmtime.Store(engine)
            self._wasm_instance = wasmtime.Instance(store, module, [])
            
            # Get exports
            self._memory = self._wasm_instance.exports(store, "memory")
            self._malloc = self._wasm_instance.exports(store, "__wbindgen_export_0")
            self._stack_ptr = self._wasm_instance.exports(store, "__wbindgen_add_to_stack_pointer")
            
            self._wasm_initialized = True
            
        except ImportError:
            # Fallback: try using node to run the WASM
            print("Warning: wasmtime not available, falling back to node-based solver", 
                  file=sys.stderr)
            self._wasm_initialized = False
    
    def _alloc_utf8(self, string: str) -> tuple:
        """Allocate UTF-8 string in WASM memory"""
        if not self._wasm_initialized:
            raise RuntimeError("WASM not initialized")
        
        encoder = text_encoder() if hasattr(text_encoder, '__call__') else None
        if encoder is None:
            # Python 3.11+ has TextEncoder in codecs
            import codecs
            encoder = codecs.lookup('utf-8').incrementalencoder()
        
        bytes_data = string.encode('utf-8')
        ptr = self._malloc(len(bytes_data), 1)
        view = memoryview(self._memory.buffer)
        view[ptr:ptr+len(bytes_data)] = bytes_data
        return (ptr, len(bytes_data))
    
    def solve(self, challenge: Dict[str, Any]) -> str:
        """
        Solve a PoW challenge using WASM
        
        Args:
            challenge: PoW challenge dictionary containing:
                - challenge: The challenge string
                - salt: Salt value
                - expireAt: Expiration timestamp
                - difficulty: Difficulty level
                - signature: Challenge signature
                - target_path: Target path
                - algorithm: Algorithm name (default: DeepSeekHashV1)
        
        Returns:
            Base64-encoded PoW response
        """
        try:
            self._initialize_wasm()
            
            if not self._wasm_initialized:
                # Fallback to node-based solver
                return self._solve_with_node(challenge)
            
            # Extract challenge parameters
            challenge_str = challenge.get("challenge", "")
            salt = challenge.get("salt", "")
            expire_at = challenge.get("expireAt", "")
            difficulty = challenge.get("difficulty", 1)
            
            # Create prefix
            prefix = f"{salt}_{expire_at}_"
            
            # Allocate strings in WASM memory
            challenge_ptr, challenge_len = self._alloc_utf8(challenge_str)
            prefix_ptr, prefix_len = self._alloc_utf8(prefix)
            
            # Call WASM solver
            wasm_solve = self._wasm_instance.exports("_ZN12wasm_solveEv")
            
            # This is a simplified approach - actual implementation
            # would need proper WASM function calling
            # For now, fall back to node
            return self._solve_with_node(challenge)
            
        except Exception as e:
            print(f"WASM solver failed: {e}", file=sys.stderr)
            return self._solve_with_node(challenge)
    
    def _solve_with_node(self, challenge: Dict[str, Any]) -> str:
        """Solve PoW using Node.js and the deepterm wasm file"""
        try:
            # Prepare input for node
            inp = json.dumps(challenge)
            
            # Find node executable
            node_executable = "node"
            if not self._check_command(node_executable):
                # Try alternative paths
                for path in ["/usr/bin/node", "/usr/local/bin/node", "/opt/node/bin/node"]:
                    if self._check_command(path):
                        node_executable = path
                        break
                else:
                    raise RuntimeError("Node.js not found")
            
            # Find the pow_solver.js from deepcli
            solver_path = Path.home() / "deepcli" / "pow_solver.js"
            if not solver_path.exists():
                # Try deepterm_fork
                solver_path = DEEPTERM_DIR / "pow_solver.js"
            
            if not solver_path.exists():
                raise FileNotFoundError(
                    "pow_solver.js not found. Please ensure deepcli or deepterm_fork is available."
                )
            
            # Execute node with solver
            cmd = [node_executable, str(solver_path)]
            proc = subprocess.run(
                cmd, input=inp, capture_output=True, text=True, timeout=30
            )
            
            if proc.returncode != 0:
                raise RuntimeError(f"Node solver failed: {proc.stderr}")
            
            answer = int(proc.stdout.strip())
            
            # Build response payload
            payload = {
                "algorithm": challenge.get("algorithm", "DeepSeekHashV1"),
                "challenge": challenge["challenge"],
                "salt": challenge["salt"],
                "answer": answer,
                "signature": challenge["signature"],
                "target_path": challenge.get("target_path", "/api/v0/chat/completion")
            }
            
            return base64.b64encode(json.dumps(payload).encode()).decode()
            
        except Exception as e:
            print(f"Node-based solver failed: {e}", file=sys.stderr)
            raise
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


class DeepTermSession:
    """
    DeepTerm session manager
    
    Manages chat sessions with DeepSeek, including PoW challenges,
    session creation, and message sending.
    """
    
    def __init__(self, config: Optional[DeepTermConfig] = None):
        self.config = config or DeepTermConfig()
        self.session = CurlCffiSession(impersonate=self.config.impersonate)
        self.pow_solver = WasmPowSolver()
        self._chat_session_id: Optional[str] = None
        self._parent_message_id: Optional[str] = None
    
    def set_token(self, token: str):
        """Set the authentication token"""
        self.config.token = token
        self.session._session.headers.update({
            'authorization': f"Bearer {token}"
        })
    
    def get_pow_challenge(self) -> Dict[str, Any]:
        """Get a PoW challenge from DeepSeek"""
        headers = self.config.get_headers(self.config.token)
        headers.update({
            'Content-Type': 'application/json',
        })
        
        response = self.session.post(
            f"{self.config.base_url}/api/v0/chat/create_pow_challenge",
            json={"target_path": "/api/v0/chat/completion"},
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data.get("data", {}).get("biz_data", {}).get("challenge", {})
    
    def solve_pow(self, challenge: Dict[str, Any]) -> str:
        """Solve a PoW challenge"""
        return self.pow_solver.solve(challenge)
    
    def create_session(self) -> str:
        """Create a new chat session"""
        headers = self.config.get_headers(self.config.token)
        headers.update({
            'Content-Type': 'application/json',
        })
        
        response = self.session.post(
            f"{self.config.base_url}/api/v0/chat_session/create",
            json={"character_id": None, "model_type": "expert"},
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        session_id = data.get("data", {}).get("biz_data", {}).get("id")
        if session_id:
            self._chat_session_id = session_id
            self._parent_message_id = None
        
        return session_id
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get chat history for current session"""
        if not self._chat_session_id:
            return []
        
        headers = self.config.get_headers(self.config.token)
        
        response = self.session.get(
            f"{self.config.base_url}/api/v0/chat_session/{self._chat_session_id}/messages",
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        messages = data.get("data", {}).get("biz_data", {}).get("chat_messages", [])
        
        # Update parent message ID
        if messages:
            self._parent_message_id = messages[-1].get("message_id")
        
        return messages
    
    def send_message(self, message: str, 
                     session_id: Optional[str] = None,
                     parent_id: Optional[str] = None) -> str:
        """Send a message and get response"""
        # Use provided session ID or create new one
        chat_session_id = session_id or self._chat_session_id
        if not chat_session_id:
            chat_session_id = self.create_session()
        
        # Get parent message ID
        parent_message_id = parent_id or self._parent_message_id
        
        # Get PoW challenge
        challenge = self.get_pow_challenge()
        pow_response = self.solve_pow(challenge)
        
        # Build headers
        headers = self.config.get_headers(self.config.token)
        headers.update({
            'Content-Type': 'application/json',
            'X-Ds-Pow-Response': pow_response
        })
        
        # Build payload
        payload = {
            "chat_session_id": chat_session_id,
            "parent_message_id": parent_message_id,
            "prompt": message,
            "ref_file_ids": [],
            "thinking_enabled": True,
            "search_enabled": False,
            "stream": False
        }
        
        # Send request
        response = self.session.post(
            f"{self.config.base_url}/api/v0/chat/completion",
            json=payload,
            headers=headers
        )
        
        response.raise_for_status()
        
        # Parse response (handles both streaming and non-streaming)
        data = response.json()
        
        # Extract content
        if "data" in data:
            biz_data = data["data"].get("biz_data", {})
            if "content" in biz_data:
                content = biz_data["content"]
            elif "response" in biz_data:
                content = biz_data["response"].get("content", "")
            else:
                content = str(data)
        elif "choices" in data:
            content = data["choices"][0].get("message", {}).get("content", "")
        else:
            content = str(data)
        
        # Update parent message ID
        if "message_id" in data.get("data", {}).get("biz_data", {}):
            self._parent_message_id = data["data"]["biz_data"]["message_id"]
        
        return content


class DeepTermBackend(ChatBackend):
    """
    DeepTerm-based backend for multi-ai-cli
    
    Integrates deepterm_fork's capabilities with the multi-ai-cli
    architecture, providing DeepSeek access with PoW solving.
    """
    
    def __init__(self, session_manager):
        super().__init__(session_manager)
        self.config = DeepTermConfig()
        self._deepterm_session = None
        
        # Initialize token
        token = session_manager.get_token("deepseek")
        if token:
            self.config.token = token
        else:
            token = os.environ.get("DEEPSEEK_TOKEN")
            if token:
                self.config.token = token
        
        if not self.config.token:
            raise RuntimeError("DeepSeek token required for DeepTerm backend")
        
        self._deepterm_session = DeepTermSession(self.config)
    
    def is_available(self) -> bool:
        """Check if backend is available"""
        return bool(self.config.token)
    
    def send_message(self, message: str, context: List[Dict]) -> str:
        """Send message and get response"""
        # Extract session information from context
        session_id = None
        parent_id = None
        
        for msg in context:
            if isinstance(msg, dict):
                if "__session_id" in msg:
                    session_id = msg["__session_id"]
                if "__parent_id" in msg:
                    parent_id = msg["__parent_id"]
        
        # Send message
        response = self._deepterm_session.send_message(
            message, session_id, parent_id
        )
        
        # Update context with session information
        if not session_id:
            session_id = self._deepterm_session._chat_session_id
        if not parent_id:
            parent_id = self._deepterm_session._parent_message_id
        
        # Add session info to context for next request
        context.insert(0, {
            "role": "meta",
            "__session_id": session_id,
            "__parent_id": parent_id
        })
        
        return response
    
    def get_session(self) -> DeepTermSession:
        """Get the underlying DeepTerm session"""
        return self._deepterm_session
    
    def solve_pow(self, challenge: Dict[str, Any]) -> str:
        """Solve a PoW challenge"""
        return self._deepterm_session.solve_pow(challenge)


class DeepTermIntegration:
    """
    Main integration class for DeepTerm
    
    Provides a unified interface for integrating deepterm_fork
    capabilities into multi-ai-cli.
    """
    
    def __init__(self):
        self.config = DeepTermConfig()
        self.pow_solver = WasmPowSolver()
        self.session_manager = DeepTermSession(self.config)
    
    def initialize(self, token: Optional[str] = None):
        """Initialize with a token"""
        if token:
            self.config.token = token
            self.session_manager.set_token(token)
    
    def create_backend(self, session_manager) -> DeepTermBackend:
        """Create a DeepTerm backend for multi-ai-cli"""
        return DeepTermBackend(session_manager)
    
    def get_headers(self) -> Dict[str, str]:
        """Get DeepTerm-style headers"""
        return self.config.get_headers()
    
    def solve_pow(self, challenge: Dict[str, Any]) -> str:
        """Solve a PoW challenge"""
        return self.pow_solver.solve(challenge)
    
    def check_availability(self) -> Dict[str, bool]:
        """Check which components are available"""
        return {
            "wasm_file": DEEPSEEK_WASM.exists(),
            "node": self._check_command("node"),
            "token": bool(self.config.token)
        }
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False


# Global integration instance
_integration: Optional[DeepTermIntegration] = None


def get_integration() -> DeepTermIntegration:
    """Get or create the global DeepTermIntegration instance"""
    global _integration
    if _integration is None:
        _integration = DeepTermIntegration()
    return _integration


def reset_integration():
    """Reset the global integration instance"""
    global _integration
    _integration = None


if __name__ == "__main__":
    # Example usage
    print("DeepTerm Integration Test")
    print("=" * 50)
    
    integration = get_integration()
    
    # Check availability
    availability = integration.check_availability()
    print(f"Availability: {availability}")
    
    # Try to create a backend (will fail without token)
    try:
        from core.session_manager import SessionManager
        mgr = SessionManager()
        backend = integration.create_backend(mgr)
        print(f"Backend available: {backend.is_available()}")
    except Exception as e:
        print(f"Backend creation failed (expected without token): {e}")
    
    # Test PoW solver
    try:
        test_challenge = {
            "challenge": "test_challenge_string",
            "salt": "test_salt",
            "expireAt": "2025-01-15T00:00:00Z",
            "difficulty": 1,
            "signature": "test_signature",
            "target_path": "/api/v0/chat/completion",
            "algorithm": "DeepSeekHashV1"
        }
        # Note: This will likely fail without actual challenge data
        # pow_response = integration.solve_pow(test_challenge)
        # print(f"PoW response: {pow_response[:50]}...")
    except Exception as e:
        print(f"PoW test skipped: {e}")
