"""Paths used by the Codex bridge."""

import os
import shutil
from pathlib import Path
from typing import Optional


BRIDGE_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BRIDGE_DIR.parent
CODEX_ROOT = BRIDGE_DIR / "codex-termux_fork"


def home() -> Path:
    return Path(os.environ.get("HOME", str(Path.home()))).expanduser()


def deepcli_store() -> Path:
    return Path(
        os.environ.get("DEEPCLI_STORE", str(home() / ".deepcli" / "session_store"))
    ).expanduser()


def synthegration_dir() -> Path:
    return Path(
        os.environ.get("SYNTHEGRATION_DIR", str(home() / "cli-synthegration"))
    ).expanduser()


def codex_index() -> Path:
    return synthegration_dir() / "codex" / "codex_index.json"


def configured_binary() -> Optional[Path]:
    value = os.environ.get("TERMUX_CODEX_BIN")
    return Path(value).expanduser() if value else None


def codex_binary() -> Optional[Path]:
    configured = configured_binary()
    if configured:
        return configured
    for profile in ("release", "debug"):
        candidate = CODEX_ROOT / "codex-rs" / "target" / profile / "codex"
        if candidate.is_file():
            return candidate
    system_binary = shutil.which("codex")
    if system_binary:
        return Path(system_binary)
    return None
