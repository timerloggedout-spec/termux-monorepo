"""jules-ade bridge — thin helpers for config + dispatch planning.

No network I/O at import time. Secrets only via environment.
"""

from .config import BridgeConfig, load_config

__all__ = ["BridgeConfig", "load_config"]
