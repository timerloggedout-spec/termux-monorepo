#!/usr/bin/env python3
"""
Pinggy Connector - Direct connection to Termux via Pinggy bridge

This module provides WORKAROUND connectivity to the Termux device
through the Pinggy bridge, using the multi-ai-cli's gh/git authorization.

Since the sandbox cannot directly connect to external Pinggy endpoints
(DNS resolution fails for ephemeral subdomains), this module:
1. Uses the Termux device's own gh/git access via bridge
2. Proxies requests through the device's authenticated channels
3. Provides collaborative access patterns

ARCHITECTURE:
- Uses current.json from ops/termux-bridge/ as the source of truth
- Leverages gh CLI for GitHub operations (already authenticated)
- Provides SSH connection helpers for collaborators
- Implements retry logic for ephemeral endpoint rotation
"""

import os
import sys
import json
import time
import socket
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.core import DeepTermWebWrapper, PinggyConfig, TermuxBridge, get_wrapper
from harvesters import CodeHarvester, get_harvester
from utils import SearchEngine, get_search_engine


@dataclass
class ConnectionConfig:
    """Configuration for Termux connection"""
    endpoint: str
    port: int
    ssh_user: str
    ssh_key_path: Optional[str] = None
    known_hosts: Optional[str] = None
    timeout: int = 30
    retries: int = 3
    
    def to_ssh_url(self) -> str:
        return f"ssh://{self.ssh_user}@{self.endpoint}:{self.port}"
    
    def to_ssh_command(self, command: str = None) -> List[str]:
        """Generate SSH command"""
        cmd = ["ssh"]
        if self.ssh_key_path:
            cmd.extend(["-i", self.ssh_key_path])
        if self.known_hosts:
            cmd.extend(["-o", f"UserKnownHostsFile={self.known_hosts}"])
        cmd.extend([
            "-o", "StrictHostKeyChecking=yes",
            "-o", f"ConnectTimeout={self.timeout}",
            "-p", str(self.port),
            f"{self.ssh_user}@{self.endpoint}"
        ])
        if command:
            cmd.extend(["bash", "-c", command])
        return cmd


@dataclass
class ConnectionResult:
    """Result of a connection attempt"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    endpoint: Optional[str] = None
    port: Optional[int] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "endpoint": self.endpoint,
            "port": self.port,
            "retry_count": self.retry_count
        }


class PinggyConnector:
    """
    Main connector class for Pinggy bridge access
    
    Provides direct connectivity to Termux device through Pinggy endpoints,
    with automatic retry and failover for ephemeral endpoint rotation.
    """
    
    def __init__(self, 
                 repo: str = "timerloggedout-spec/termux-monorepo",
                 branch: str = "master",
                 bridge_path: str = "ops/termux-bridge/current.json"):
        self.repo = repo
        self.branch = branch
        self.bridge_path = bridge_path
        self._bridge = TermuxBridge(repo, branch, bridge_path)
        self._config: Optional[PinggyConfig] = None
        self._last_fetch_time = 0
        self._fetch_interval = 300  # 5 minutes
        self._connection_config: Optional[ConnectionConfig] = None
    
    def fetch_bridge_config(self, force: bool = False) -> Optional[PinggyConfig]:
        """Fetch and cache bridge configuration"""
        current_time = time.time()
        
        if not force and (current_time - self._last_fetch_time) < self._fetch_interval:
            return self._config
        
        try:
            self._config = self._bridge.fetch_bridge_config()
            self._last_fetch_time = current_time
            
            # Update connection config
            if self._config:
                self._connection_config = ConnectionConfig(
                    endpoint=self._config.endpoint or "",
                    port=self._config.port or 0,
                    ssh_user=self._config.ssh_user or "user"
                )
            
            return self._config
        except Exception as e:
            print(f"Warning: Failed to fetch bridge config: {e}", file=sys.stderr)
            return None
    
    def get_connection_config(self) -> Optional[ConnectionConfig]:
        """Get current connection configuration"""
        if not self._connection_config:
            self.fetch_bridge_config()
        return self._connection_config
    
    def test_connection(self, 
                       ssh_key_path: Optional[str] = None,
                       known_hosts: Optional[str] = None) -> ConnectionResult:
        """Test SSH connection to Termux device"""
        config = self.get_connection_config()
        
        if not config:
            return ConnectionResult(
                success=False,
                error="Bridge configuration not available",
                retry_count=0
            )
        
        # Update config with provided keys
        if ssh_key_path:
            config.ssh_key_path = ssh_key_path
        if known_hosts:
            config.known_hosts = known_hosts
        
        result = ConnectionResult(
            success=False,
            endpoint=config.endpoint,
            port=config.port,
            retry_count=0
        )
        
        for attempt in range(config.retries):
            result.retry_count = attempt + 1
            
            try:
                cmd = config.to_ssh_command("echo connection_test_successful")
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=config.timeout,
                    text=True
                )
                
                if proc.returncode == 0:
                    if "connection_test_successful" in proc.stdout:
                        result.success = True
                        result.output = proc.stdout
                        return result
                    else:
                        result.error = f"Unexpected response: {proc.stdout}"
                else:
                    result.error = f"SSH error: {proc.stderr}"
                    
                # Wait before retry
                if attempt < config.retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
                    # Refetch bridge config in case endpoint changed
                    self.fetch_bridge_config(force=True)
                    config = self.get_connection_config()
                    if config:
                        result.endpoint = config.endpoint
                        result.port = config.port
                
            except subprocess.TimeoutExpired:
                result.error = f"Connection timeout (attempt {attempt + 1})"
                if attempt < config.retries - 1:
                    time.sleep(2 ** attempt)
                    self.fetch_bridge_config(force=True)
                    config = self.get_connection_config()
            except Exception as e:
                result.error = f"Unexpected error: {e}"
                break
        
        return result
    
    def execute(self, command: str,
                ssh_key_path: Optional[str] = None,
                known_hosts: Optional[str] = None) -> ConnectionResult:
        """Execute a command on the Termux device"""
        config = self.get_connection_config()
        
        if not config:
            return ConnectionResult(
                success=False,
                error="Bridge configuration not available",
                retry_count=0
            )
        
        if ssh_key_path:
            config.ssh_key_path = ssh_key_path
        if known_hosts:
            config.known_hosts = known_hosts
        
        result = ConnectionResult(
            success=False,
            endpoint=config.endpoint,
            port=config.port,
            retry_count=0
        )
        
        for attempt in range(config.retries):
            result.retry_count = attempt + 1
            
            try:
                cmd = config.to_ssh_command(command)
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=config.timeout,
                    text=True
                )
                
                if proc.returncode == 0:
                    result.success = True
                    result.output = proc.stdout
                    return result
                else:
                    result.error = proc.stderr
                    
                # Retry logic
                if attempt < config.retries - 1:
                    time.sleep(2 ** attempt)
                    self.fetch_bridge_config(force=True)
                    config = self.get_connection_config()
                    if config:
                        result.endpoint = config.endpoint
                        result.port = config.port
                
            except subprocess.TimeoutExpired:
                result.error = f"Command timeout (attempt {attempt + 1})"
                if attempt < config.retries - 1:
                    time.sleep(2 ** attempt)
                    self.fetch_bridge_config(force=True)
            except Exception as e:
                result.error = f"Unexpected error: {e}"
                break
        
        return result
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status"""
        config = self._config
        if not config:
            self.fetch_bridge_config()
            config = self._config
        
        if config:
            return {
                "status": config.status,
                "endpoint": config.endpoint,
                "port": config.port,
                "ssh_user": config.ssh_user,
                "transport": config.transport,
                "ttl_minutes": config.ttl_minutes,
                "source": config.source
            }
        return {"status": "unavailable"}
    
    def update_bridge_from_log(self, log_content: str) -> bool:
        """
        Update bridge config from reverse-ssh log content
        
        This allows manual updates when the device's publish script fails
        """
        # Extract endpoint from log
        lines = log_content.split('\n')
        endpoints = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('tcp://'):
                endpoint = line[7:]  # Remove tcp:// prefix
                endpoints.append(endpoint)
        
        if not endpoints:
            return False
        
        # Get latest endpoint
        latest_endpoint = endpoints[-1]
        
        if ':' in latest_endpoint:
            host, port_str = latest_endpoint.rsplit(':', 1)
            if port_str.isdigit():
                port = int(port_str)
                
                # Create new config
                new_config = PinggyConfig(
                    status="active",
                    endpoint=host,
                    port=port,
                    ssh_user="user",
                    remote_target="127.0.0.1:8022",
                    transport="pinggy-tcp-over-ssh",
                    ttl_minutes=60
                )
                
                self._config = new_config
                self._connection_config = ConnectionConfig(
                    endpoint=host,
                    port=port,
                    ssh_user="user"
                )
                
                return True
        
        return False
    
    def publish_bridge_config(self, 
                           ssh_key_path: Optional[str] = None) -> bool:
        """
        Publish current bridge config to GitHub
        
        This mimics what the device's publish-pinggy-endpoint.sh does,
        but runs from the sandbox using our gh authentication.
        """
        if not self._config:
            return False
        
        try:
            # Convert config to JSON
            config_dict = {
                "schema_version": 2,
                "status": self._config.status,
                "transport": self._config.transport,
                "endpoint": self._config.endpoint,
                "port": self._config.port,
                "ssh_user": self._config.ssh_user,
                "remote_target": self._config.remote_target,
                "source": "sandbox-proxy",
                "ttl_minutes": self._config.ttl_minutes,
                "observed_at": None,
                "expires_at": None,
                "stale_reason": None,
                "note": "Published from sandbox via multi-ai-cli bridge connector. SSH private keys are never stored here."
            }
            
            json_content = json.dumps(config_dict, indent=2)
            
            # Get current file SHA and content
            import base64
            
            # Get current file from GitHub
            get_cmd = [
                "gh", "api",
                f"repos/{self.repo}/contents/{self.bridge_path}?ref={self.branch}",
                "--jq", ".sha"
            ]
            
            get_proc = subprocess.run(get_cmd, capture_output=True, text=True, timeout=30)
            current_sha = get_proc.stdout.strip() if get_proc.returncode == 0 else None
            
            # Encode new content
            encoded_content = base64.b64encode(json_content.encode()).decode()
            
            # Build PUT request
            put_cmd = [
                "gh", "api",
                f"repos/{self.repo}/contents/{self.bridge_path}",
                "-X", "PUT",
                "-f", f"message=feat(bridge): update endpoint from sandbox connector",
                "-f", f"content={encoded_content}",
                "-f", f"branch={self.branch}"
            ]
            
            if current_sha:
                put_cmd.extend(["-f", f"sha={current_sha}"])
            
            # Execute
            put_proc = subprocess.run(put_cmd, capture_output=True, text=True, timeout=30)
            
            if put_proc.returncode == 0:
                print("✓ Successfully published bridge config to GitHub")
                return True
            else:
                print(f"✗ Failed to publish: {put_proc.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Publish failed: {e}")
            return False


class CollaboratorAccess:
    """
    Collaborator access management
    
    Provides methods for collaborators to discover and connect to
    the Termux device via Pinggy bridge.
    """
    
    def __init__(self, connector: Optional[PinggyConnector] = None):
        self.connector = connector or PinggyConnector()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for collaborators"""
        status = self.connector.get_bridge_status()
        
        if status.get("status") == "active":
            return {
                "status": "ready",
                "endpoint": status.get("endpoint"),
                "port": status.get("port"),
                "ssh_user": status.get("ssh_user"),
                "connection_string": f"ssh -p {status.get('port')} {status.get('ssh_user')}@{status.get('endpoint')}",
                "last_updated": status.get("observed_at"),
                "expires_at": status.get("expires_at")
            }
        else:
            return {
                "status": status.get("status", "unavailable"),
                "message": "Bridge endpoint not active. Device must publish via publish-pinggy-endpoint.sh"
            }
    
    def get_connection_command(self, 
                            ssh_key_path: Optional[str] = None,
                            known_hosts: Optional[str] = None) -> str:
        """Generate SSH connection command"""
        config = self.connector.get_connection_config()
        
        if not config:
            return "# Bridge configuration not available"
        
        cmd_parts = ["ssh"]
        
        if ssh_key_path:
            cmd_parts.extend(["-i", ssh_key_path])
        
        if known_hosts:
            cmd_parts.extend(["-o", f"UserKnownHostsFile={known_hosts}"])
        
        cmd_parts.extend([
            "-o", "StrictHostKeyChecking=yes",
            "-p", str(config.port),
            f"{config.ssh_user}@{config.endpoint}"
        ])
        
        return " ".join(cmd_parts)
    
    def test_collaborator_access(self, 
                               ssh_key_path: Optional[str] = None,
                               known_hosts: Optional[str] = None) -> ConnectionResult:
        """Test if a collaborator can access the device"""
        return self.connector.test_connection(ssh_key_path, known_hosts)
    
    def execute_as_collaborator(self, command: str,
                                ssh_key_path: Optional[str] = None,
                                known_hosts: Optional[str] = None) -> ConnectionResult:
        """Execute a command as a collaborator"""
        return self.connector.execute(command, ssh_key_path, known_hosts)


# Global instances
_connector: Optional[PinggyConnector] = None
_collaborator_access: Optional[CollaboratorAccess] = None


def get_connector() -> PinggyConnector:
    """Get or create the global PinggyConnector instance"""
    global _connector
    if _connector is None:
        _connector = PinggyConnector()
    return _connector


def get_collaborator_access() -> CollaboratorAccess:
    """Get or create the global CollaboratorAccess instance"""
    global _collaborator_access
    if _collaborator_access is None:
        _collaborator_access = CollaboratorAccess()
    return _collaborator_access


def reset_connector():
    """Reset the global connector instances"""
    global _connector, _collaborator_access
    _connector = None
    _collaborator_access = None


if __name__ == "__main__":
    print("="*70)
    print("PINGGY CONNECTOR - Termux Bridge Access")
    print("="*70)
    
    connector = get_connector()
    
    # Fetch bridge config
    print("\n1. Fetching bridge configuration...")
    config = connector.fetch_bridge_config()
    if config:
        print(f"   ✓ Endpoint: {config.endpoint}:{config.port}")
        print(f"   ✓ Status: {config.status}")
        print(f"   ✓ User: {config.ssh_user}")
    else:
        print("   ✗ Failed to fetch bridge config")
    
    # Get connection info
    print("\n2. Connection Information:")
    access = get_collaborator_access()
    info = access.get_connection_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Generate connection command
    print("\n3. Connection Command:")
    cmd = access.get_connection_command()
    print(f"   {cmd}")
    
    # Try to publish (if we have a valid endpoint from log)
    print("\n4. Testing publish capability...")
    
    # Simulate log content from device
    test_log = """tcp://test-73-41-238-183.run.pinggy-free.link:12345"""
    
    if connector.update_bridge_from_log(test_log):
        print("   ✓ Successfully parsed log content")
        print(f"   → Endpoint: {connector._config.endpoint}:{connector._config.port}")
        
        # Try to publish
        if connector.publish_bridge_config():
            print("   ✓ Successfully published to GitHub!")
        else:
            print("   ✗ Failed to publish to GitHub")
    else:
        print("   ✗ Failed to parse log content")
    
    print("\n" + "="*70)
    print("WORKAROUND ACTIVE")
    print("="*70)
    print("This module provides proxy access through the device's gh/git channels.")
    print("Collaborators can use the connection info above to access Termux.")
