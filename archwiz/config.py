from pathlib import Path
import os
import json

# archwiz/config.py
# Environment-aware configuration for ArchWiz / termux-monorepo.
# Single source of truth for all runtime paths — import this instead of
# hard-coding os.path.expanduser('~/archwiz/...') at every call site.
#
# Environments detected (in priority order):
#   termux  — /data/data/com.termux exists on the filesystem
#   replit  — REPL_ID or REPLIT_DOMAINS env var is present
#   local   — everything else (Linux desktop, CI, etc.)
#
# Override detection with ARCHWIZ_ENV=termux|replit|local in the shell,
# or by writing {"archwiz_env": "..."} to ~/.archwiz/config.json.

HOME = Path.home()

USER_CONFIG_DIR  = HOME / ".archwiz"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"

# Defaults — all overridable via ~/.archwiz/config.json or ARCHWIZ_ENV
_defaults: dict = {
    "archwiz_env":        "auto",   # auto | termux | replit | local
    "archwiz_root":       None,     # None → auto-detected from env
    "multi_ai_tokens_dir": str(HOME / ".multi-ai-tokens"),
    "session_store":      str(HOME / ".deepcli" / "session_store"),
    "log_dir":            str(HOME / ".archwiz" / "logs"),
}


class Config:
    def __init__(self):
        USER_CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._cfg = dict(_defaults)

        # Load persisted user config, silently retire broken files
        if USER_CONFIG_FILE.exists():
            try:
                data = json.loads(USER_CONFIG_FILE.read_text())
                if isinstance(data, dict):
                    self._cfg.update(data)
            except Exception:
                try:
                    USER_CONFIG_FILE.rename(USER_CONFIG_FILE.with_suffix(".broken"))
                except Exception:
                    pass

        # Shell override takes highest priority
        shell_env = os.environ.get("ARCHWIZ_ENV", "").strip().lower()
        if shell_env in ("termux", "replit", "local"):
            self._cfg["archwiz_env"] = shell_env

        self._apply_auto_detection()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_auto_detection(self):
        ev = self._cfg.get("archwiz_env", "auto")
        if ev == "auto":
            if Path("/data/data/com.termux").exists():
                ev = "termux"
            elif (
                os.environ.get("REPL_ID")
                or os.environ.get("REPLIT_DOMAINS")
                or os.environ.get("REPLIT_DB_URL")
            ):
                ev = "replit"
            else:
                ev = "local"
            self._cfg["archwiz_env"] = ev

        if not self._cfg.get("archwiz_root"):
            if ev == "termux":
                self._cfg["archwiz_root"] = "/data/data/com.termux/files/home"
            else:
                self._cfg["archwiz_root"] = str(HOME)

        self._cfg.setdefault("multi_ai_tokens_dir", _defaults["multi_ai_tokens_dir"])
        self._cfg.setdefault("session_store",       _defaults["session_store"])
        self._cfg.setdefault("log_dir",             _defaults["log_dir"])

    def _mkdir(self, p: Path, mode: int = 0o700) -> Path:
        p.mkdir(mode=mode, parents=True, exist_ok=True)
        return p

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self):
        USER_CONFIG_FILE.write_text(json.dumps(self._cfg, indent=2))
        USER_CONFIG_FILE.chmod(0o600)

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def set(self, key, value):
        self._cfg[key] = value
        self.save()

    # ------------------------------------------------------------------
    # Core path properties — used by archwiz.py and all sub-tools
    # ------------------------------------------------------------------

    @property
    def archwiz_env(self) -> str:
        return self._cfg.get("archwiz_env", "local")

    @property
    def archwiz_root(self) -> Path:
        """Root home directory for this environment."""
        return Path(self._cfg["archwiz_root"])

    @property
    def ARCHWIZ_DIR(self) -> Path:
        """~/archwiz/ — cockpit, listener, sentinel, etc."""
        return self._mkdir(self.archwiz_root / "archwiz")

    @property
    def DEEPCLI_DIR(self) -> Path:
        """~/deepcli/ — DeepSeek CLI package."""
        return self.archwiz_root / "deepcli"

    @property
    def WORKSPACE_DIR(self) -> Path:
        """~/workspace/ — llm_map, provenance, etc."""
        return self.archwiz_root / "workspace"

    @property
    def SESSION_STORE(self) -> Path:
        """~/.deepcli/session_store/ — per-session JSON cache."""
        p = Path(self._cfg["session_store"])
        self._mkdir(p.parent)
        self._mkdir(p)
        return p

    @property
    def MULTI_AI_TOKENS_DIR(self) -> Path:
        """~/.multi-ai-tokens/ — bearer tokens for all AI providers."""
        return self._mkdir(Path(self._cfg["multi_ai_tokens_dir"]))

    @property
    def LOG_DIR(self) -> Path:
        """~/.archwiz/logs/ — pipeline + debug logs."""
        return self._mkdir(Path(self._cfg["log_dir"]))


# ---------------------------------------------------------------------------
# Module-level singleton — import and use directly:
#   from archwiz.config import ARCHWIZ_DIR, SESSION_STORE
#   from archwiz import config as cfg; cfg.ARCHWIZ_DIR
# ---------------------------------------------------------------------------

_config = Config()

# Flat convenience constants — drop-in replacements for expanduser() calls
ARCHWIZ_DIR        = _config.ARCHWIZ_DIR
DEEPCLI_DIR        = _config.DEEPCLI_DIR
WORKSPACE_DIR      = _config.WORKSPACE_DIR
SESSION_STORE      = _config.SESSION_STORE
MULTI_AI_TOKENS_DIR = _config.MULTI_AI_TOKENS_DIR
LOG_DIR            = _config.LOG_DIR
ARCHWIZ_ENV        = _config.archwiz_env
ARCHWIZ_ROOT       = _config.archwiz_root


# ---------------------------------------------------------------------------
# Convenience functions — kept for API compat with mistral/fixes-config-security
# ---------------------------------------------------------------------------

def get_tokens_dir() -> Path:
    return _config.MULTI_AI_TOKENS_DIR


def get_session_store() -> Path:
    return _config.SESSION_STORE


def set_tokens_dir(path):
    _config.set("multi_ai_tokens_dir", str(path))


def set_session_store(path):
    _config.set("session_store", str(path))


def ensure_dirs():
    """Pre-create all runtime directories. Call once at startup."""
    _ = _config.ARCHWIZ_DIR
    _ = _config.SESSION_STORE
    _ = _config.MULTI_AI_TOKENS_DIR
    _ = _config.LOG_DIR
