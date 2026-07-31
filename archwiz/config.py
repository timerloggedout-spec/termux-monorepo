from pathlib import Path
import os
import json

# archwiz/config.py
# Environment-aware configuration for ArchWiz / termux-monorepo
# Primary environment: Termux. Falls back to Replit/local when Termux not detected.

HOME = Path.home()

USER_CONFIG_DIR = HOME / ".archwiz"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"

# Defaults
_defaults = {
    "archwiz_env": "auto",  # auto | termux | replit | local
    "archwiz_root": None,    # if None, auto-detected
    "multi_ai_tokens_dir": str(HOME / ".multi-ai-tokens"),
    "session_store": str(HOME / ".deepcli" / "session_store"),
}

class Config:
    def __init__(self):
        # Ensure config dir exists
        USER_CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._cfg = dict(_defaults)
        # Load saved user config if present
        if USER_CONFIG_FILE.exists():
            try:
                data = json.loads(USER_CONFIG_FILE.read_text())
                if isinstance(data, dict):
                    self._cfg.update(data)
            except Exception:
                # If config unreadable, move it aside to avoid repeated failures
                try:
                    USER_CONFIG_FILE.rename(USER_CONFIG_FILE.with_suffix('.broken'))
                except Exception:
                    pass
        self._apply_auto_detection()

    def _apply_auto_detection(self):
        ev = self._cfg.get("archwiz_env", "auto")
        if ev == "auto":
            # Detect Termux
            termux_flag = Path('/data/data/com.termux').exists()
            if termux_flag:
                ev = 'termux'
            else:
                # Detect Replit by environment variable or typical home path
                repl_env = os.environ.get('REPLIT_DB_URL') or os.environ.get('REPL_OWNER')
                ev = 'replit' if repl_env else 'local'
            self._cfg['archwiz_env'] = ev

        # archwiz_root
        if not self._cfg.get('archwiz_root'):
            if self._cfg['archwiz_env'] == 'termux':
                # Keep Termux primary root
                self._cfg['archwiz_root'] = '/data/data/com.termux/files/home'
            else:
                self._cfg['archwiz_root'] = str(HOME)

        # Ensure token dir and session store are Path strings
        self._cfg.setdefault('multi_ai_tokens_dir', _defaults['multi_ai_tokens_dir'])
        self._cfg.setdefault('session_store', _defaults['session_store'])

    def save(self):
        USER_CONFIG_FILE.write_text(json.dumps(self._cfg, indent=2))
        USER_CONFIG_FILE.chmod(0o600)

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def set(self, key, value):
        self._cfg[key] = value
        self.save()

    @property
    def archwiz_env(self):
        return self._cfg.get('archwiz_env')

    @property
    def archwiz_root(self):
        return Path(self._cfg.get('archwiz_root'))

    @property
    def MULTI_AI_TOKENS_DIR(self):
        p = Path(self._cfg.get('multi_ai_tokens_dir'))
        p.mkdir(mode=0o700, parents=True, exist_ok=True)
        return p

    @property
    def SESSION_STORE(self):
        p = Path(self._cfg.get('session_store'))
        p.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        p.mkdir(mode=0o700, parents=True, exist_ok=True)
        return p

# Global config instance
_config = Config()

# Convenience functions for external callers

def get_tokens_dir():
    return _config.MULTI_AI_TOKENS_DIR


def get_session_store():
    return _config.SESSION_STORE


def set_tokens_dir(path):
    _config.set('multi_ai_tokens_dir', str(path))


def set_session_store(path):
    _config.set('session_store', str(path))


def ensure_dirs():
    _ = get_tokens_dir()
    _ = get_session_store()

