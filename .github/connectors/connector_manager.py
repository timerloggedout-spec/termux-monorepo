#!/usr/bin/env python3
"""
Connector Management System for termux-monorepo
Manages API connectors, webhooks, and external service integrations
"""

import os
import yaml
import json
import requests
import hashlib
import hmac
import time
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from typing import Union

# Type definitions
ConnectorConfig = Dict[str, Any]
ConnectorList = Dict[str, ConnectorConfig]

@dataclass
class ConnectorInfo:
    """Information about a connector"""
    name: str
    type: str
    enabled: bool
    description: str = ""
    config: ConnectorConfig = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "enabled": self.enabled,
            "description": self.description,
            "config": self.config
        }

class ConnectorManager:
    """
    Main connector management class
    Loads, manages, and provides access to all connector configurations
    """
    
    def __init__(self, connectors_dir: Optional[Path] = None):
        """
        Initialize the connector manager
        
        Args:
            connectors_dir: Path to connectors directory. Defaults to .github/connectors
        """
        if connectors_dir is None:
            # Try to find connectors directory
            possible_paths = [
                Path(__file__).parent,
                Path.cwd() / ".github" / "connectors",
                Path.cwd() / ".github/connectors",
                Path.home() / ".termux-monorepo" / ".github" / "connectors"
            ]
            
            for path in possible_paths:
                if path.exists() and path.is_dir():
                    self.connectors_dir = path
                    break
            else:
                raise FileNotFoundError("Could not find connectors directory")
        else:
            self.connectors_dir = connectors_dir
        
        self.connectors: Dict[str, ConnectorList] = {}
        self.connector_info: Dict[str, ConnectorInfo] = {}
        self.load_connectors()
    
    def load_connectors(self):
        """Load all connector configurations from YAML files"""
        if not self.connectors_dir.exists():
            raise FileNotFoundError(f"Connectors directory not found: {self.connectors_dir}")
        
        for config_file in self.connectors_dir.glob("*.yaml"):
            if config_file.name.startswith("_"):
                continue
            
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                if config is None:
                    continue
                
                # Store the raw configuration
                config_key = config_file.stem
                self.connectors[config_key] = config
                
                # Extract connector information
                self._extract_connector_info(config_key, config)
                
            except Exception as e:
                print(f"Warning: Could not load {config_file}: {e}")
    
    def _extract_connector_info(self, config_key: str, config: Dict[str, Any]):
        """Extract connector information from configuration"""
        if config_key == "llm_providers":
            for provider_name, provider_config in config.get("llm_providers", {}).items():
                key = f"llm:{provider_name}"
                self.connector_info[key] = ConnectorInfo(
                    name=provider_name,
                    type="llm_provider",
                    enabled=provider_config.get("enabled", False),
                    description=f"LLM Provider: {provider_name}",
                    config=provider_config
                )
        
        elif config_key == "exchanges":
            for exchange_name, exchange_config in config.get("exchanges", {}).items():
                key = f"exchange:{exchange_name}"
                self.connector_info[key] = ConnectorInfo(
                    name=exchange_name,
                    type="exchange",
                    enabled=exchange_config.get("enabled", False),
                    description=f"Exchange: {exchange_name}",
                    config=exchange_config
                )
        
        elif config_key == "github":
            github_config = config.get("github", {})
            
            # Main GitHub connector
            self.connector_info["github:api"] = ConnectorInfo(
                name="github_api",
                type="platform",
                enabled=True,
                description="GitHub API",
                config=github_config.get("api", {})
            )
            
            # Webhooks
            webhooks_config = github_config.get("webhooks", {})
            if webhooks_config.get("enabled", False):
                self.connector_info["github:webhooks"] = ConnectorInfo(
                    name="github_webhooks",
                    type="webhook",
                    enabled=True,
                    description="GitHub Webhooks",
                    config=webhooks_config
                )
            
            # Agents
            agents_config = github_config.get("agents", {})
            for agent_name, agent_config in agents_config.items():
                if agent_config.get("enabled", False):
                    key = f"github:agent:{agent_name}"
                    self.connector_info[key] = ConnectorInfo(
                        name=agent_name,
                        type="agent",
                        enabled=True,
                        description=f"GitHub Agent: {agent_name}",
                        config=agent_config
                    )
        
        elif config_key == "webhooks":
            webhooks_config = config.get("webhooks", {})
            
            # GitHub webhooks
            github_webhooks = webhooks_config.get("github", {}).get("endpoints", [])
            for webhook in github_webhooks:
                if webhook.get("active", False):
                    key = f"webhook:github:{webhook.get('name', 'unknown')}"
                    self.connector_info[key] = ConnectorInfo(
                        name=webhook.get("name", "unknown"),
                        type="webhook",
                        enabled=True,
                        description=f"GitHub Webhook: {webhook.get('name', 'unknown')}",
                        config=webhook
                    )
            
            # Agent webhooks
            agents_webhooks = webhooks_config.get("agents", {})
            for agent_name, agent_config in agents_webhooks.items():
                if agent_config.get("enabled", False):
                    key = f"webhook:agent:{agent_name}"
                    self.connector_info[key] = ConnectorInfo(
                        name=agent_name,
                        type="webhook",
                        enabled=True,
                        description=f"Agent Webhook: {agent_name}",
                        config=agent_config
                    )
    
    def get_connector(self, connector_type: str, connector_name: str) -> Optional[Dict]:
        """
        Get a specific connector configuration

        Args:
            connector_type: Type of connector (llm_providers, exchanges, etc.)
            connector_name: Name of the connector

        Returns:
            Connector configuration or None if not found
        """
        if connector_type in self.connectors:
            config = self.connectors[connector_type]

            # Unwrap nested YAML documents where the mapping is nested under connector_type
            # e.g., {"llm_providers": {...}} -> {...}
            if isinstance(config, dict) and connector_type in config:
                config = config[connector_type]

            if isinstance(config, dict) and connector_name in config:
                return config[connector_name]
            elif connector_name == connector_type:
                return config
        return None
    
    def get_connector_info(self, connector_key: str) -> Optional[ConnectorInfo]:
        """
        Get connector information by key
        
        Args:
            connector_key: Key of the connector (e.g., "llm:deepseek", "exchange:yobit")
            
        Returns:
            ConnectorInfo object or None if not found
        """
        return self.connector_info.get(connector_key)
    
    def list_connectors(self) -> Dict[str, List[str]]:
        """
        List all available connectors by type
        
        Returns:
            Dictionary mapping connector types to lists of connector names
        """
        result = {}
        
        # LLM Providers
        llm_config = self.connectors.get("llm_providers", {})
        if llm_config:
            result["llm_providers"] = list(llm_config.get("llm_providers", {}).keys())
        
        # Exchanges
        exchange_config = self.connectors.get("exchanges", {})
        if exchange_config:
            result["exchanges"] = list(exchange_config.get("exchanges", {}).keys())
        
        # GitHub
        github_config = self.connectors.get("github", {})
        if github_config:
            result["github"] = ["api", "webhooks"]
            agents = list(github_config.get("github", {}).get("agents", {}).keys())
            if agents:
                result["github_agents"] = agents
        
        # Webhooks
        webhooks_config = self.connectors.get("webhooks", {})
        if webhooks_config:
            github_webhooks = webhooks_config.get("webhooks", {}).get("github", {}).get("endpoints", [])
            result["github_webhooks"] = [w.get("name", "unknown") for w in github_webhooks if w.get("active", False)]
        
        return result
    
    def list_all_connectors(self) -> List[ConnectorInfo]:
        """
        List all connectors with their information
        
        Returns:
            List of ConnectorInfo objects
        """
        return list(self.connector_info.values())
    
    def get_llm_provider(self, provider_name: str) -> Optional[Dict]:
        """
        Get LLM provider configuration
        
        Args:
            provider_name: Name of the LLM provider
            
        Returns:
            Provider configuration or None if not found
        """
        return self.get_connector("llm_providers", provider_name)
    
    def get_exchange(self, exchange_name: str) -> Optional[Dict]:
        """
        Get exchange API configuration
        
        Args:
            exchange_name: Name of the exchange
            
        Returns:
            Exchange configuration or None if not found
        """
        return self.get_connector("exchanges", exchange_name)
    
    def get_github_config(self) -> Optional[Dict]:
        """
        Get GitHub configuration
        
        Returns:
            GitHub configuration or None if not found
        """
        return self.connectors.get("github", {}).get("github")
    
    def get_webhook_config(self) -> Optional[Dict]:
        """
        Get webhook configuration
        
        Returns:
            Webhook configuration or None if not found
        """
        return self.connectors.get("webhooks", {}).get("webhooks")
    
    def is_enabled(self, connector_type: str, connector_name: str) -> bool:
        """
        Check if a connector is enabled
        
        Args:
            connector_type: Type of connector
            connector_name: Name of the connector
            
        Returns:
            True if enabled, False otherwise
        """
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            return False
        return connector.get("enabled", False)
    
    def get_api_key(self, connector_type: str, connector_name: str) -> Optional[str]:
        """
        Get the API key for a connector from environment variables
        
        Args:
            connector_type: Type of connector
            connector_name: Name of the connector
            
        Returns:
            API key or None if not found
        """
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            return None
        
        api_key_env = connector.get("api_key_env")
        if api_key_env:
            return os.environ.get(api_key_env)
        
        # Try common patterns
        env_var = f"{connector_name.upper()}_API_KEY"
        return os.environ.get(env_var)
    
    def create_authenticated_request(self, connector_type: str, connector_name: str, 
                                   method: str = "GET", url: str = "", 
                                   params: Optional[Dict] = None, 
                                   data: Optional[Dict] = None) -> requests.Request:
        """
        Create an authenticated request for a connector
        
        Args:
            connector_type: Type of connector
            connector_name: Name of the connector
            method: HTTP method
            url: URL to request
            params: Query parameters
            data: Request body
            
        Returns:
            Prepared request object
        """
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            raise ValueError(f"Connector {connector_type}:{connector_name} not found")
        
        # Resolve endpoint templates before joining with base URL
        if url:
            # Get template values from connector config or params
            api_version = connector.get("api_version", "")
            pair = params.get("pair", "") if params else ""

            # Replace placeholders in the endpoint
            url = url.replace("{api_version}", api_version)

            # Validate required placeholders
            if "{pair}" in url:
                if not pair:
                    raise ValueError(f"Endpoint '{url}' requires 'pair' parameter but none was provided")
                url = url.replace("{pair}", pair)

        # Get base URL and join with resolved endpoint
        base_url = connector.get("base_url", "")
        if not url.startswith("http") and base_url:
            url = f"{base_url}{url}" if url.startswith("/") else f"{base_url}/{url}"
        
        # Get headers
        headers = connector.get("headers", {}).copy()
        
        # Add authentication
        auth_method = connector.get("auth_method")

        if auth_method == "bearer":
            api_key = self.get_api_key(connector_type, connector_name)
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        elif auth_method == "hmac":
            # For HMAC authentication (used by exchanges like Yobit)
            api_key = self.get_api_key(connector_type, connector_name)
            api_secret_env = connector.get("api_secret_env", "")
            api_secret = os.environ.get(api_secret_env) if api_secret_env else None

            if api_key and api_secret:
                # Yobit HMAC signing
                nonce = str(int(time.time() * 1000))

                # Build the payload for signing (form-encoded)
                payload_dict = {"nonce": nonce}
                if data:
                    payload_dict.update(data)

                # Create canonical form-encoded payload string
                import urllib.parse
                hmac_payload = urllib.parse.urlencode(sorted(payload_dict.items()))

                # Sign the payload
                hash_algorithm = connector.get("hash_algorithm", "sha512")
                if hash_algorithm == "sha512":
                    signature = hmac.new(
                        api_secret.encode(),
                        hmac_payload.encode(),
                        hashlib.sha512
                    ).hexdigest()
                elif hash_algorithm == "sha256":
                    signature = hmac.new(
                        api_secret.encode(),
                        hmac_payload.encode(),
                        hashlib.sha256
                    ).hexdigest()
                else:
                    raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

                headers["Key"] = api_key
                headers["Sign"] = signature
                # Store the canonical payload to use as request body
                data = hmac_payload
            elif url and not url.endswith(("/info", "/ticker", "/depth", "/trades")):
                # Private operation requires credentials
                raise ValueError(f"HMAC authentication requires both api_key and api_secret for private operations")

        elif auth_method == "jwt":
            # KuCoin JWT authentication
            api_key = self.get_api_key(connector_type, connector_name)
            api_secret_env = connector.get("api_secret_env", "")
            api_secret = os.environ.get(api_secret_env) if api_secret_env else None
            passphrase_env = connector.get("passphrase_env", "")
            passphrase = os.environ.get(passphrase_env) if passphrase_env else None

            if api_key and api_secret and passphrase:
                # Generate KuCoin signature
                timestamp = str(int(time.time() * 1000))
                str_to_sign = timestamp + method + url.replace(connector.get("base_url", ""), "")
                if data:
                    str_to_sign += json.dumps(data)

                signature = hmac.new(
                    api_secret.encode(),
                    str_to_sign.encode(),
                    hashlib.sha256
                ).digest()
                signature_b64 = base64.b64encode(signature).decode()

                passphrase_signature = hmac.new(
                    api_secret.encode(),
                    passphrase.encode(),
                    hashlib.sha256
                ).digest()
                passphrase_b64 = base64.b64encode(passphrase_signature).decode()

                headers["KC-API-KEY"] = api_key
                headers["KC-API-SIGN"] = signature_b64
                headers["KC-API-TIMESTAMP"] = timestamp
                headers["KC-API-PASSPHRASE"] = passphrase_b64
                headers["KC-API-KEY-VERSION"] = "2"
            else:
                raise ValueError(f"JWT authentication requires api_key, api_secret, and passphrase")

        elif not auth_method:
            # GitHub API uses token_env when no auth_method is set
            token_env = connector.get("token_env", "")
            if token_env:
                token = os.environ.get(token_env)
                if token:
                    headers["Authorization"] = f"token {token}"
        
        # Create request
        # For HMAC auth, data is already form-encoded string; for others, send as JSON
        if auth_method == "hmac" and isinstance(data, str):
            req = requests.Request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data
            )
        else:
            req = requests.Request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
        
        return req.prepare()
    
    def send_request(self, connector_type: str, connector_name: str,
                    method: str = "GET", endpoint: str = "",
                    params: Optional[Dict] = None, 
                    data: Optional[Dict] = None) -> requests.Response:
        """
        Send a request to a connector
        
        Args:
            connector_type: Type of connector
            connector_name: Name of the connector
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            
        Returns:
            Response object
        """
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            raise ValueError(f"Connector {connector_type}:{connector_name} not found")
        
        # Prepare request
        req = self.create_authenticated_request(
            connector_type, connector_name, method, endpoint, params, data
        )
        
        # Get timeout
        timeout = connector.get("timeout", 30)
        
        # Send request with retry logic
        # Retries are enabled by default only for idempotent HTTP methods
        idempotent_methods = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
        retry_attempts = connector.get("retry_attempts", 3)
        retry_delay = connector.get("retry_delay", 1)

        # Check if this is a non-idempotent operation
        if method.upper() not in idempotent_methods:
            # For non-idempotent operations (POST, PATCH), check for connector-configured idempotency field
            has_idempotency_key = False
            idempotency_key_field = connector.get("idempotency_key_field")

            if idempotency_key_field and data and isinstance(data, dict):
                # Check if the configured idempotency field is present and non-empty
                has_idempotency_key = bool(data.get(idempotency_key_field))

            # Only allow single attempt for non-idempotent operations without idempotency key
            if not has_idempotency_key:
                retry_attempts = 1

        last_exception = None
        for attempt in range(retry_attempts):
            try:
                session = requests.Session()
                response = session.send(req, timeout=timeout)

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", retry_delay))
                    if attempt < retry_attempts - 1:
                        time.sleep(retry_after)
                        continue

                return response

            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                    continue
                raise

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                    continue
                raise

        # If we exhausted all retries, raise the last exception or generic error
        if last_exception:
            raise last_exception
        raise Exception("Max retry attempts exceeded")
    
    def test_connector(self, connector_type: str, connector_name: str) -> bool:
        """
        Test a connector by making a simple API call

        Args:
            connector_type: Type of connector
            connector_name: Name of the connector

        Returns:
            True if test succeeds, False otherwise
        """
        try:
            connector = self.get_connector(connector_type, connector_name)
            if not connector:
                return False

            # For GitHub API connector, enablement is implicit (no enabled field required)
            # For other connectors, check the enabled field
            if connector_type == "github" and connector_name == "api":
                # GitHub API is enabled if it has a base_url
                if not connector.get("base_url"):
                    return False
            else:
                # Other connectors require explicit enabled flag
                if not connector.get("enabled", False):
                    return False
            
            # Different test for different connector types
            if connector_type == "llm_providers":
                # Test LLM provider with a simple completion
                response = self.send_request(
                    connector_type, connector_name,
                    method="POST",
                    endpoint=connector.get("endpoints", {}).get("chat_completions", "/chat/completions"),
                    data={
                        "model": connector.get("models", [{}])[0].get("id", ""),
                        "messages": [{"role": "user", "content": "Test"}],
                        "max_tokens": 10
                    }
                )
                return response.status_code == 200
            
            elif connector_type == "exchanges":
                # Test exchange with a public endpoint
                public_endpoints = ["info", "ticker", "symbols", "ping", "server_time"]
                for endpoint in public_endpoints:
                    if endpoint in connector.get("endpoints", {}):
                        response = self.send_request(
                            connector_type, connector_name,
                            method="GET",
                            endpoint=connector["endpoints"][endpoint]
                        )
                        return response.status_code == 200
                
                # If no public endpoints found, try the first one
                endpoints = connector.get("endpoints", {})
                if endpoints:
                    first_endpoint = list(endpoints.values())[0]
                    response = self.send_request(
                        connector_type, connector_name,
                        method="GET",
                        endpoint=first_endpoint
                    )
                    return response.status_code == 200
            
            elif connector_type == "github":
                # Test GitHub API
                response = self.send_request(
                    connector_type, connector_name,
                    method="GET",
                    endpoint="/repos/timerloggedout-spec/termux-monorepo"
                )
                return response.status_code == 200
            
            return False
            
        except Exception as e:
            print(f"Error testing connector {connector_type}:{connector_name}: {e}")
            return False

# Utility functions
def get_connector_manager() -> ConnectorManager:
    """
    Get a singleton ConnectorManager instance
    
    Returns:
        ConnectorManager instance
    """
    if not hasattr(get_connector_manager, "_instance"):
        get_connector_manager._instance = ConnectorManager()
    return get_connector_manager._instance

def list_connectors() -> Dict[str, List[str]]:
    """
    List all available connectors
    
    Returns:
        Dictionary mapping connector types to lists of connector names
    """
    manager = get_connector_manager()
    return manager.list_connectors()

def get_llm_provider(provider_name: str) -> Optional[Dict]:
    """
    Get LLM provider configuration
    
    Args:
        provider_name: Name of the LLM provider
        
    Returns:
        Provider configuration or None if not found
    """
    manager = get_connector_manager()
    return manager.get_llm_provider(provider_name)

def get_exchange(exchange_name: str) -> Optional[Dict]:
    """
    Get exchange API configuration
    
    Args:
        exchange_name: Name of the exchange
        
    Returns:
        Exchange configuration or None if not found
    """
    manager = get_connector_manager()
    return manager.get_exchange(exchange_name)

# Usage example
if __name__ == "__main__":
    import sys

    manager = ConnectorManager()

    # Check for --test flag
    run_tests = "--test" in sys.argv

    print("=== Available Connectors ===")
    connectors = manager.list_connectors()
    for conn_type, conn_list in connectors.items():
        print(f"\n{conn_type}:")
        for conn_name in conn_list:
            enabled = manager.is_enabled(conn_type, conn_name)
            print(f"  - {conn_name}: {'enabled' if enabled else 'disabled'}")

    print("\n=== All Connector Info ===")
    all_connectors = manager.list_all_connectors()
    for conn in all_connectors:
        print(f"\n{conn.name} ({conn.type}):")
        print(f"  Enabled: {conn.enabled}")
        print(f"  Description: {conn.description}")

    # Only run tests if --test flag is provided
    if run_tests:
        print("\n=== Testing Connectors ===")
        # Test LLM providers
        for provider in connectors.get("llm_providers", []):
            if manager.is_enabled("llm_providers", provider):
                result = manager.test_connector("llm_providers", provider)
                print(f"  {provider}: {'OK' if result else 'FAILED'}")

        # Test exchanges
        for exchange in connectors.get("exchanges", []):
            if manager.is_enabled("exchanges", exchange):
                result = manager.test_connector("exchanges", exchange)
                print(f"  {exchange}: {'OK' if result else 'FAILED'}")

        # Test GitHub
        if "github" in connectors:
            result = manager.test_connector("github", "api")
            print(f"  GitHub API: {'OK' if result else 'FAILED'}")
    else:
        print("\n(Use --test flag to run live network tests)")
