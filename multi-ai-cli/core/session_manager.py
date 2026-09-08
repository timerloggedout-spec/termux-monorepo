import os, json, yaml
from pathlib import Path
from typing import Any

class SessionManager:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        self.config = {}
        cfg_path = Path(config_path)
        if cfg_path.is_symlink():
            raise ValueError(f"Symlink config path {config_path} rejected for security")
        if cfg_path.exists():
            with open(cfg_path) as f:
                self.config = yaml.safe_load(f) or {}

    def get(self, provider: str, key: str, default=None) -> Any:
        return self.config.get(provider, {}).get(key, default)

    def get_token(self, provider: str) -> str:
        token_path = self.get(provider, "token_path")
        if token_path:
            token_str = str(token_path)
            if ".." in Path(token_str).parts:
                raise ValueError(f"Path traversal detected in token_path for '{provider}'")
            expanded = Path(os.path.expanduser(token_str))
            if expanded.is_symlink():
                raise ValueError(f"Symlink token path {expanded} rejected for security")
            if expanded.exists():
                with open(expanded) as f:
                    return f.read().strip()
        return None
