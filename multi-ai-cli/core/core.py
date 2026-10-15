#!/usr/bin/env python3
"""
Core DeepTerm WebWrapper Architecture for Mistralai Vibe Code

This module provides the foundational architecture for integrating Mistralai
with the Termux environment via Pinggy proxy. It combines the best practices
from deepcli, ChapitoAI, and deepterm_fork to create a unified, safe,
sandboxed environment for AI operations.

Architecture Overview:
- Uses curl_cffi for custom HTTP requests with browser-like headers
- Integrates with Termux SSH reverse tunnels via Pinggy
- Provides Shell CLI access with gh & git authorization
- Supports code harvest/extraction and search capabilities
- Maintains security boundaries with proper sandboxing
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

# Security constants
SANDBOX_ROOT = Path("/workspace")
MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB
FORBIDDEN_PATHS = ["/etc", "/root", "/home", "/var", "/usr", "/bin", "/sbin"]


@dataclass
class SecurityConfig:
    """Security configuration for sandboxed operations"""
    allow_network: bool = True
    allow_file_write: bool = True
    allow_file_read: bool = True
    allow_subprocess: bool = False
    max_execution_time: int = 300
    forbidden_paths: List[str] = field(default_factory=lambda: FORBIDDEN_PATHS.copy())
    
    def validate_path(self, path: str) -> bool:
        """Validate that a path is within sandbox boundaries"""
        path_obj = Path(path).resolve()
        sandbox = SANDBOX_ROOT.resolve()
        
        # Check if path is within sandbox
        try:
            path_obj.relative_to(sandbox)
            return True
        except ValueError:
            return False
        
        # Check against forbidden paths
        for forbidden in self.forbidden_paths:
            if str(path_obj).startswith(forbidden):
                return False
        
        return True


@dataclass
class PinggyConfig:
    """Configuration for Pinggy proxy integration"""
    endpoint: Optional[str] = None
    port: Optional[int] = None
    ssh_user: Optional[str] = None
    remote_target: str = "127.0.0.1:8022"
    transport: str = "pinggy-tcp-over-ssh"
    ttl_minutes: int = 60
    status: str = "unknown"
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "PinggyConfig":
        """Create PinggyConfig from JSON data (e.g., from current.json)"""
        return cls(
            endpoint=json_data.get("endpoint"),
            port=json_data.get("port"),
            ssh_user=json_data.get("ssh_user"),
            remote_target=json_data.get("remote_target", "127.0.0.1:8022"),
            transport=json_data.get("transport", "pinggy-tcp-over-ssh"),
            ttl_minutes=json_data.get("ttl_minutes", 60),
            status=json_data.get("status", "unknown")
        )
    
    def to_ssh_url(self) -> Optional[str]:
        """Generate SSH connection URL"""
        if self.endpoint and self.port and self.ssh_user:
            return f"ssh://{self.ssh_user}@{self.endpoint}:{self.port}"
        return None


class TermuxBridge:
    """
    Termux Bridge Manager for Pinggy reverse-SSH integration
    
    Provides connectivity to Termux environment via Pinggy proxy,
    enabling secure access to device resources through SSH tunneling.
    """
    
    def __init__(self, repo: str = "timerloggedout-spec/termux-monorepo", 
                 branch: str = "master", 
                 path_in_repo: str = "ops/termux-bridge/current.json"):
        self.repo = repo
        self.branch = branch
        self.path_in_repo = path_in_repo
        self._config: Optional[PinggyConfig] = None
        self._gh_available = self._check_gh_available()
    
    def _check_gh_available(self) -> bool:
        """Check if gh CLI is available"""
        try:
            result = subprocess.run(["gh", "--version"], 
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_ssh_available(self) -> bool:
        """Check if ssh CLI is available"""
        try:
            result = subprocess.run(["ssh", "-V"], 
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def fetch_bridge_config(self) -> PinggyConfig:
        """
        Fetch current bridge configuration from GitHub
        
        Uses gh CLI to retrieve the current.json file containing
        Pinggy endpoint information.
        """
        if not self._gh_available:
            raise RuntimeError("gh CLI is required but not available")
        
        try:
            # Fetch the current.json file from GitHub
            cmd = [
                "gh", "api", 
                f"repos/{self.repo}/contents/{self.path_in_repo}?ref={self.branch}",
                "--jq", ".content"
            ]
            result = subprocess.run(cmd, capture_output=True, 
                                  timeout=30, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to fetch bridge config: {result.stderr}")
            
            # Decode base64 content
            import base64
            encoded_content = result.stdout.strip()
            if not encoded_content:
                raise RuntimeError("Empty response from GitHub API")
            
            decoded_content = base64.b64decode(encoded_content).decode('utf-8')
            config_data = json.loads(decoded_content)
            
            self._config = PinggyConfig.from_json(config_data)
            return self._config
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, 
                base64.binascii.Error) as e:
            raise RuntimeError(f"Failed to parse bridge config: {e}")
    
    def get_connection_string(self) -> str:
        """Get SSH connection string for the bridge"""
        if not self._config:
            self.fetch_bridge_config()
        
        if not self._config:
            raise RuntimeError("Bridge configuration not available")
        
        if self._config.status != "active":
            raise RuntimeError(f"Bridge is {self._config.status}, not active")
        
        if not self._config.endpoint or not self._config.port or not self._config.ssh_user:
            raise RuntimeError("Bridge configuration incomplete")
        
        return f"{self._config.ssh_user}@{self._config.endpoint}:{self._config.port}"
    
    def test_connection(self, ssh_key_path: Optional[str] = None) -> bool:
        """Test SSH connection to the bridge"""
        if not self._check_ssh_available():
            raise RuntimeError("SSH is required but not available")
        
        connection_str = self.get_connection_string()
        
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no", 
               "-o", "ConnectTimeout=10"]
        
        if ssh_key_path:
            cmd.extend(["-i", ssh_key_path])
        
        cmd.append(connection_str)
        cmd.extend(["echo", "connection_test_successful"])
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            return result.returncode == 0 and "connection_test_successful" in result.stdout.decode()
        except subprocess.TimeoutExpired:
            return False
    
    def execute_remote(self, command: str, ssh_key_path: Optional[str] = None) -> str:
        """
        Execute a command on the remote Termux device via bridge
        
        WARNING: This method should be used with extreme caution as it
        allows arbitrary command execution on the remote device.
        """
        if not self.test_connection(ssh_key_path):
            raise RuntimeError("Cannot establish connection to bridge")
        
        connection_str = self.get_connection_string()
        
        cmd = ["ssh"]
        if ssh_key_path:
            cmd.extend(["-i", ssh_key_path])
        cmd.extend(["-o", "StrictHostKeyChecking=no", connection_str])
        cmd.extend(["bash", "-c", command])
        
        try:
            result = subprocess.run(cmd, capture_output=True, 
                                  timeout=300, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Remote command failed: {result.stderr}")
            return result.stdout
        except subprocess.TimeoutExpired:
            raise RuntimeError("Remote command execution timed out")


class CurlCffiSession:
    """
    Custom curl_cffi session with browser-like headers and impersonation
    
    Provides a high-performance HTTP client with curl_cffi for browser
    impersonation, essential for accessing web-based AI services.
    """
    
    def __init__(self, impersonate: str = "chrome120", 
                 user_agent: Optional[str] = None):
        self.impersonate = impersonate
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self._session = None
        self._init_session()
    
    def _init_session(self):
        """Initialize curl_cffi session with impersonation"""
        try:
            from curl_cffi import requests
            self._session = requests.Session(
                impersonate=self.impersonate
            )
            self._session.headers.update({
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            })
        except ImportError:
            # Fallback to requests if curl_cffi not available
            import requests as std_requests
            self._session = std_requests.Session()
            self._session.headers.update({
                "User-Agent": self.user_agent,
            })
    
    def get(self, url: str, **kwargs) -> Any:
        """GET request with browser impersonation"""
        if self._session is None:
            self._init_session()
        return self._session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Any:
        """POST request with browser impersonation"""
        if self._session is None:
            self._init_session()
        return self._session.post(url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Any:
        """PUT request with browser impersonation"""
        if self._session is None:
            self._init_session()
        return self._session.put(url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Any:
        """DELETE request with browser impersonation"""
        if self._session is None:
            self._init_session()
        return self._session.delete(url, **kwargs)


class DeepTermWebWrapper:
    """
    DeepTerm WebWrapper for Mistralai integration
    
    This is the main integration point that combines:
    - curl_cffi for web requests
    - Termux/Pinggy bridge for device access
    - Security sandboxing
    - Code harvest/extraction capabilities
    """
    
    def __init__(self, security_config: Optional[SecurityConfig] = None):
        self.security = security_config or SecurityConfig()
        self.bridge = TermuxBridge()
        self.session = CurlCffiSession()
        self._harvesters = {}
        self._search_index = {}
    
    def initialize_bridge(self) -> bool:
        """Initialize connection to Termux bridge"""
        try:
            config = self.bridge.fetch_bridge_config()
            print(f"Bridge initialized: {config.endpoint}:{config.port}")
            return True
        except Exception as e:
            print(f"Failed to initialize bridge: {e}")
            return False
    
    def execute_shell_command(self, command: str, 
                              ssh_key_path: Optional[str] = None) -> str:
        """
        Execute a shell command on the remote Termux device
        
        This provides Shell CLI access with proper authorization.
        """
        # Security validation
        if not self.security.allow_subprocess:
            raise PermissionError("Subprocess execution is disabled by security policy")
        
        # Validate command doesn't contain dangerous patterns
        dangerous_patterns = [";", "|", "&&", "||", "`", "$", ">", "<"]
        for pattern in dangerous_patterns:
            if pattern in command:
                raise ValueError(f"Command contains disallowed character: {pattern}")
        
        return self.bridge.execute_remote(command, ssh_key_path)
    
    def get_gh_authorization(self) -> Optional[str]:
        """Get GitHub authorization token"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status", "--show-token"],
                capture_output=True, timeout=10, text=True
            )
            if result.returncode == 0:
                # Parse token from output
                for line in result.stdout.split('\n'):
                    if 'Token:' in line:
                        return line.split('Token:')[1].strip()
            return None
        except Exception:
            return None
    
    def get_git_authorization(self) -> Optional[Dict[str, str]]:
        """Get Git authorization information"""
        try:
            result = subprocess.run(
                ["git", "config", "--list"],
                capture_output=True, timeout=10, text=True
            )
            if result.returncode == 0:
                config = {}
                for line in result.stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
                return config
            return None
        except Exception:
            return None
    
    def make_request(self, url: str, method: str = "GET", 
                    data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None) -> Any:
        """
        Make HTTP request with curl_cffi browser impersonation
        
        This is the primary method for accessing Mistralai and other
        web-based AI services.
        """
        request_headers = headers or {}
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=request_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response
            
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")
    
    def register_harvester(self, name: str, harvester_class):
        """Register a code harvester module"""
        self._harvesters[name] = harvester_class(self)
    
    def get_harvester(self, name: str):
        """Get a registered code harvester"""
        return self._harvesters.get(name)
    
    def register_search_index(self, name: str, index_data: Dict):
        """Register a search index for code/search capabilities"""
        self._search_index[name] = index_data
    
    def search(self, query: str, index_name: str = "default") -> List[Any]:
        """Search the registered index"""
        index = self._search_index.get(index_name, {})
        results = []
        
        for key, value in index.items():
            if query.lower() in str(key).lower() or query.lower() in str(value).lower():
                results.append({"key": key, "value": value})
        
        return results


# Global instance for convenience
_wrapper: Optional[DeepTermWebWrapper] = None


def get_wrapper() -> DeepTermWebWrapper:
    """Get or create the global DeepTermWebWrapper instance"""
    global _wrapper
    if _wrapper is None:
        _wrapper = DeepTermWebWrapper()
    return _wrapper


def reset_wrapper():
    """Reset the global wrapper instance"""
    global _wrapper
    _wrapper = None


if __name__ == "__main__":
    # Example usage
    wrapper = get_wrapper()
    
    # Initialize bridge
    if wrapper.initialize_bridge():
        print("Bridge initialized successfully")
        
        # Test connection
        try:
            if wrapper.bridge.test_connection():
                print("Connection test successful")
        except Exception as e:
            print(f"Connection test failed: {e}")
    
    # Get authorization info
    gh_token = wrapper.get_gh_authorization()
    if gh_token:
        print(f"GitHub token available: {gh_token[:8]}...")
    
    git_config = wrapper.get_git_authorization()
    if git_config:
        print(f"Git config available: {list(git_config.keys())}")
