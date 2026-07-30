import os, json, yaml
from pathlib import Path
from typing import Any

class SessionManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        self.config = {}
        if Path(config_path).exists():
            with open(config_path) as f:
                self.config = yaml.safe_load(f) or {}

    def get(self, provider: str, key: str, default=None) -> Any:
        return self.config.get(provider, {}).get(key, default)

    def get_token(self, provider: str) -> str:
        token_path = self.get(provider, "token_path")
        if token_path:
            expanded = os.path.expanduser(token_path)
            if os.path.exists(expanded):
                with open(expanded) as f:
                    return f.read().strip()
        return None
