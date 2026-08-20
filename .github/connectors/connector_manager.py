#!/usr/bin/env python3
"""Connector Management System for termux-monorepo"""

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
from urllib.parse import urlparse, urlencode

ConnectorConfig = Dict[str, Any]
ConnectorList = Dict[str, ConnectorConfig]

@dataclass
class ConnectorInfo:
    name: str
    type: str
    enabled: bool
    description: str = ""
    config: ConnectorConfig = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.type, "enabled": self.enabled,
                "description": self.description, "config": self.config}

class ConnectorManager:
    _ALLOWED_ENV_NAMES = frozenset({
        "DEEPSEEK_API_KEY", "MISTRAL_API_KEY", "CLAUDE_API_KEY", "GROK_API_KEY",
        "GITHUB_TOKEN", "GITHUB_WEBHOOK_SECRET",
        "JULES_API_KEY", "CODERABBIT_API_KEY", "DEVIN_API_KEY",
        "YOBIT_API_KEY", "YOBIT_API_SECRET",
        "KUCOIN_API_KEY", "KUCOIN_API_SECRET", "KUCOIN_PASSPHRASE",
        "BINANCE_API_KEY", "BINANCE_API_SECRET",
        "WEBHOOK_RECEIVER_BASE_URL",
    })

    def __init__(self, connectors_dir: Optional[Path] = None):
        if connectors_dir is None:
            possible_paths = [
                Path(__file__).parent,
                Path.cwd() / ".github" / "connectors",
                Path.cwd() / ".github/connectors",
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
        self._load_errors: List[str] = []
        self._load_failed: bool = False
        self.load_connectors()

    def load_connectors(self):
        if not self.connectors_dir.exists():
            raise FileNotFoundError(f"Connectors directory not found: {self.connectors_dir}")
        for config_file in self.connectors_dir.glob("*.yaml"):
            if config_file.name.startswith("_"):
                continue
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                if config is None:
                    continue
                config_key = config_file.stem
                self.connectors[config_key] = config
                self._extract_connector_info(config_key, config)
            except Exception as e:
                msg = f"Could not load {config_file}: {e}"
                print(f"Error: {msg}")
                self._load_errors.append(msg)
        if self._load_errors:
            self._load_failed = True

    def _extract_connector_info(self, config_key: str, config: Dict[str, Any]):
        if config_key == "llm_providers":
            for name, cfg in config.get("llm_providers", {}).items():
                self.connector_info[f"llm:{name}"] = ConnectorInfo(
                    name=name, type="llm_provider", enabled=cfg.get("enabled", False),
                    description=f"LLM Provider: {name}", config=cfg)
        elif config_key == "exchanges":
            for name, cfg in config.get("exchanges", {}).items():
                self.connector_info[f"exchange:{name}"] = ConnectorInfo(
                    name=name, type="exchange", enabled=cfg.get("enabled", False),
                    description=f"Exchange: {name}", config=cfg)
        elif config_key == "github":
            gh = config.get("github", {})
            api_cfg = gh.get("api", {})
            self.connector_info["github:api"] = ConnectorInfo(
                name="github_api", type="platform", enabled=api_cfg.get("enabled", True),
                description="GitHub API", config=api_cfg)
            wh = gh.get("webhooks", {})
            if wh.get("enabled", False):
                self.connector_info["github:webhooks"] = ConnectorInfo(
                    name="github_webhooks", type="webhook", enabled=True,
                    description="GitHub Webhooks", config=wh)
            for agent_name, agent_cfg in gh.get("agents", {}).items():
                if agent_cfg.get("enabled", False):
                    self.connector_info[f"github:agent:{agent_name}"] = ConnectorInfo(
                        name=agent_name, type="agent", enabled=True,
                        description=f"GitHub Agent: {agent_name}", config=agent_cfg)
        elif config_key == "webhooks":
            wh_cfg = config.get("webhooks", {})
            for webhook in wh_cfg.get("github", {}).get("endpoints", []):
                if webhook.get("active", False):
                    n = webhook.get("name", "unknown")
                    self.connector_info[f"webhook:github:{n}"] = ConnectorInfo(
                        name=n, type="webhook", enabled=True,
                        description=f"GitHub Webhook: {n}", config=webhook)

    def get_connector(self, connector_type: str, connector_name: str) -> Optional[Dict]:
        if connector_type not in self.connectors:
            return None
        config = self.connectors[connector_type]
        if isinstance(config, dict) and connector_type in config:
            config = config[connector_type]
        if isinstance(config, dict) and connector_name in config:
            return config[connector_name]
        if connector_name == connector_type:
            return config
        return None

    def get_connector_info(self, connector_key: str) -> Optional[ConnectorInfo]:
        return self.connector_info.get(connector_key)

    def list_connectors(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        llm = self.connectors.get("llm_providers", {})
        if llm:
            result["llm_providers"] = list(llm.get("llm_providers", {}).keys())
        ex = self.connectors.get("exchanges", {})
        if ex:
            result["exchanges"] = list(ex.get("exchanges", {}).keys())
        gh = self.connectors.get("github", {})
        if gh:
            result["github"] = ["api", "webhooks"]
            agents = list(gh.get("github", {}).get("agents", {}).keys())
            if agents:
                result["github_agents"] = agents
        wh = self.connectors.get("webhooks", {})
        if wh:
            endpoints = wh.get("webhooks", {}).get("github", {}).get("endpoints", [])
            result["github_webhooks"] = [w.get("name", "unknown") for w in endpoints if w.get("active", False)]
        return result

    def list_all_connectors(self) -> List[ConnectorInfo]:
        return list(self.connector_info.values())

    def get_llm_provider(self, provider_name: str) -> Optional[Dict]:
        return self.get_connector("llm_providers", provider_name)

    def get_exchange(self, exchange_name: str) -> Optional[Dict]:
        return self.get_connector("exchanges", exchange_name)

    def get_github_config(self) -> Optional[Dict]:
        return self.connectors.get("github", {}).get("github")

    def get_webhook_config(self) -> Optional[Dict]:
        return self.connectors.get("webhooks", {}).get("webhooks")

    def is_enabled(self, connector_type: str, connector_name: str) -> bool:
        info_key = None
        if connector_type == "github_agents":
            info_key = f"github:agent:{connector_name}"
        elif connector_type == "github" and connector_name in ("api", "webhooks"):
            info_key = f"github:{connector_name}"
        elif connector_type == "github_webhooks":
            info_key = f"webhook:github:{connector_name}"
        if info_key and info_key in self.connector_info:
            return self.connector_info[info_key].enabled
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            return False
        if "enabled" not in connector:
            return True
        return connector.get("enabled", False)

    def _safe_getenv(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        if name not in self._ALLOWED_ENV_NAMES:
            raise ValueError(f"Environment variable {name!r} is not on the connector allowlist")
        return os.environ.get(name)

    def get_api_key(self, connector_type: str, connector_name: str) -> Optional[str]:
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            return None
        api_key_env = connector.get("api_key_env")
        if api_key_env:
            return self._safe_getenv(api_key_env)
        env_var = f"{connector_name.upper()}_API_KEY"
        if env_var in self._ALLOWED_ENV_NAMES:
            return os.environ.get(env_var)
        return None

    def _is_public_endpoint(self, connector: Dict, url: str) -> bool:
        parsed = urlparse(url)
        path = parsed.path or url
        public_names = connector.get("public_endpoints", [])
        endpoints = connector.get("endpoints", {})
        api_version = connector.get("api_version", "")
        for name in public_names:
            ep = endpoints.get(name, "").replace("{api_version}", api_version)
            if ep and path.rstrip("/") == ep.rstrip("/"):
                return True
        if "/market/" in path:
            return True
        if path.rstrip("/").endswith(("/symbols", "/currencies")):
            return True
        return False

    def create_authenticated_request(self, connector_type: str, connector_name: str,
                                   method: str = "GET", url: str = "",
                                   params: Optional[Dict] = None,
                                   data: Optional[Dict] = None):
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            raise ValueError(f"Connector {connector_type}:{connector_name} not found")
        if url:
            api_version = connector.get("api_version", "")
            pair = params.get("pair", "") if params else ""
            url = url.replace("{api_version}", api_version)
            if "{pair}" in url:
                if not pair:
                    raise ValueError(f"Endpoint '{url}' requires 'pair' parameter")
                url = url.replace("{pair}", pair)
                if params is not None and "pair" in params:
                    params = {k: v for k, v in params.items() if k != "pair"}
        base_url = connector.get("base_url", "")
        if url.startswith("http"):
            if not base_url:
                raise ValueError("Absolute endpoint requires connector base_url for origin check")
            base_p, tgt_p = urlparse(base_url), urlparse(url)
            if (tgt_p.scheme, tgt_p.netloc) != (base_p.scheme, base_p.netloc):
                raise ValueError(
                    f"Cross-origin absolute endpoint rejected: {tgt_p.scheme}://{tgt_p.netloc} "
                    f"!= {base_p.scheme}://{base_p.netloc}")
        elif base_url:
            url = f"{base_url}{url}" if url.startswith("/") else f"{base_url}/{url}"
        headers = connector.get("headers", {}).copy()
        auth_method = connector.get("auth_method")
        if auth_method == "bearer":
            api_key = self.get_api_key(connector_type, connector_name)
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        elif auth_method == "hmac":
            api_key = self.get_api_key(connector_type, connector_name)
            api_secret = self._safe_getenv(connector.get("api_secret_env", "")) if connector.get("api_secret_env") else None
            if api_key and api_secret:
                nonce = str(int(time.time() * 1000))
                payload_dict = {"nonce": nonce}
                if data:
                    payload_dict.update(data)
                hmac_payload = urlencode(sorted(payload_dict.items()))
                algo = connector.get("hash_algorithm", "sha512")
                digest = hashlib.sha512 if algo == "sha512" else hashlib.sha256
                if algo not in ("sha512", "sha256"):
                    raise ValueError(f"Unsupported hash algorithm: {algo}")
                signature = hmac.new(api_secret.encode(), hmac_payload.encode(), digest).hexdigest()
                headers["Key"] = api_key
                headers["Sign"] = signature
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                data = hmac_payload
            elif url and not url.endswith(("/info", "/ticker", "/depth", "/trades")):
                raise ValueError("HMAC authentication requires api_key and api_secret for private operations")
        elif auth_method == "jwt":
            api_key = self.get_api_key(connector_type, connector_name)
            api_secret = self._safe_getenv(connector.get("api_secret_env", "")) if connector.get("api_secret_env") else None
            passphrase = self._safe_getenv(connector.get("passphrase_env", "")) if connector.get("passphrase_env") else None
            if api_key and api_secret and passphrase:
                timestamp = str(int(time.time() * 1000))
                request_path = url.replace(connector.get("base_url", ""), "")
                query_string = ""
                if params:
                    params = dict(sorted(params.items()))
                    query_string = "?" + urlencode(params)
                str_to_sign = timestamp + method.upper() + request_path + query_string
                if data:
                    str_to_sign += json.dumps(data, separators=(",", ":"))
                signature = hmac.new(api_secret.encode(), str_to_sign.encode(), hashlib.sha256).digest()
                # lgtm[py/weak-sensitive-data-hashing] KuCoin API v2 mandates HMAC-SHA256 here; this is a request-authentication transform, not password storage.
                passphrase_sig = hmac.new(api_secret.encode(), passphrase.encode(), hashlib.sha256).digest()
                headers["KC-API-KEY"] = api_key
                headers["KC-API-SIGN"] = base64.b64encode(signature).decode()
                headers["KC-API-TIMESTAMP"] = timestamp
                headers["KC-API-PASSPHRASE"] = base64.b64encode(passphrase_sig).decode()
                headers["KC-API-KEY-VERSION"] = "2"
            elif not self._is_public_endpoint(connector, url):
                raise ValueError("JWT authentication requires api_key, api_secret, and passphrase for private endpoints")
        elif not auth_method:
            token_env = connector.get("token_env", "")
            if token_env:
                token = self._safe_getenv(token_env)
                if token:
                    headers["Authorization"] = f"token {token}"
        if auth_method == "hmac" and isinstance(data, str):
            req = requests.Request(method=method, url=url, headers=headers, params=params, data=data)
        else:
            req = requests.Request(method=method, url=url, headers=headers, params=params, json=data)
        return req.prepare()

    def send_request(self, connector_type: str, connector_name: str,
                    method: str = "GET", endpoint: str = "",
                    params: Optional[Dict] = None,
                    data: Optional[Dict] = None) -> requests.Response:
        connector = self.get_connector(connector_type, connector_name)
        if connector is None:
            raise ValueError(f"Connector {connector_type}:{connector_name} not found")
        req = self.create_authenticated_request(connector_type, connector_name, method, endpoint, params, data)
        timeout = connector.get("timeout", 30)
        idempotent = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
        retry_attempts = connector.get("retry_attempts", 3)
        retry_delay = connector.get("retry_delay", 1)
        if method.upper() not in idempotent:
            field = connector.get("idempotency_key_field")
            if not (field and data and isinstance(data, dict) and data.get(field)):
                retry_attempts = 1
        last_exception = None
        session = requests.Session()
        try:
            for attempt in range(retry_attempts):
                try:
                    response = session.send(req, timeout=timeout)
                    if response.status_code == 429:
                        raw = response.headers.get("Retry-After", str(retry_delay))
                        try:
                            wait = int(raw)
                        except (ValueError, TypeError):
                            wait = retry_delay
                        if attempt < retry_attempts - 1:
                            time.sleep(wait)
                            req = self.create_authenticated_request(
                                connector_type, connector_name, method, endpoint, params, data)
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
            if last_exception:
                raise last_exception
            raise Exception("Max retry attempts exceeded")
        finally:
            session.close()

    def verify_webhook_signature(self, payload_body: bytes, signature_header: str,
                                 secret_env: str = "GITHUB_WEBHOOK_SECRET") -> bool:
        try:
            secret = self._safe_getenv(secret_env)
        except ValueError:
            return False
        if not secret or not signature_header or not signature_header.startswith("sha256="):
            return False
        expected = signature_header[7:]
        computed = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, computed)

    def test_connector(self, connector_type: str, connector_name: str) -> bool:
        try:
            connector = self.get_connector(connector_type, connector_name)
            if not connector:
                return False
            if connector_type == "github" and connector_name == "api":
                if not connector.get("base_url"):
                    return False
            elif not connector.get("enabled", False):
                return False
            if connector_type == "llm_providers":
                response = self.send_request(
                    connector_type, connector_name, method="POST",
                    endpoint=connector.get("endpoints", {}).get("chat_completions", "/chat/completions"),
                    data={"model": connector.get("models", [{}])[0].get("id", ""),
                          "messages": [{"role": "user", "content": "Test"}], "max_tokens": 10})
                return response.status_code == 200
            if connector_type == "exchanges":
                for ep in ["info", "ticker", "symbols", "ping", "server_time"]:
                    if ep in connector.get("endpoints", {}):
                        response = self.send_request(connector_type, connector_name, method="GET",
                                                     endpoint=connector["endpoints"][ep])
                        return response.status_code == 200
                endpoints = connector.get("endpoints", {})
                if endpoints:
                    response = self.send_request(connector_type, connector_name, method="GET",
                                                 endpoint=list(endpoints.values())[0])
                    return response.status_code == 200
                return False
            if connector_type == "github":
                response = self.send_request(connector_type, connector_name, method="GET",
                                             endpoint="/repos/timerloggedout-spec/termux-monorepo")
                return response.status_code == 200
            return False
        except Exception as e:
            print(f"Error testing connector {connector_type}:{connector_name}: {type(e).__name__}")
            return False


def get_connector_manager() -> ConnectorManager:
    if not hasattr(get_connector_manager, "_instance"):
        get_connector_manager._instance = ConnectorManager()
    return get_connector_manager._instance

def list_connectors() -> Dict[str, List[str]]:
    return get_connector_manager().list_connectors()

def get_llm_provider(provider_name: str) -> Optional[Dict]:
    return get_connector_manager().get_llm_provider(provider_name)

def get_exchange(exchange_name: str) -> Optional[Dict]:
    return get_connector_manager().get_exchange(exchange_name)

if __name__ == "__main__":
    import sys
    manager = ConnectorManager()
    if manager._load_failed:
        print("LOAD ERRORS:", manager._load_errors)
        sys.exit(1)
    connectors = manager.list_connectors()
    for conn_type, names in connectors.items():
        print(f"{conn_type}:")
        for n in names:
            print(f"  - {n}: {'enabled' if manager.is_enabled(conn_type, n) else 'disabled'}")
    if "--test" in sys.argv:
        for p in connectors.get("llm_providers", []):
            if manager.is_enabled("llm_providers", p):
                print(f"  {p}: {'OK' if manager.test_connector('llm_providers', p) else 'FAILED'}")
        if "github" in connectors:
            print(f"  GitHub API: {'OK' if manager.test_connector('github', 'api') else 'FAILED'}")
    else:
        print("(Use --test for live network tests)")
