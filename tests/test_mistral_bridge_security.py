import os
import sys
from pathlib import Path
import pytest

# Ensure multi-ai-cli directory is on sys.path
BRIDGE_DIR = Path(__file__).resolve().parents[1] / "multi-ai-cli" / "bridge"
if str(BRIDGE_DIR) not in sys.path:
    sys.path.insert(0, str(BRIDGE_DIR))

from mistral_bridge import _write_token_securely

def test_write_token_securely_creates_file_with_strict_permissions(tmp_path):
    tokens_dir = tmp_path / ".multi-ai-tokens"
    token_file = tokens_dir / "mistral_token.txt"

    _write_token_securely("test_secret_token_123", target_file=token_file)

    assert token_file.exists()
    assert token_file.read_text(encoding="utf-8") == "test_secret_token_123"

    if os.name != "nt":
        assert (tokens_dir.stat().st_mode & 0o777) == 0o700
        assert (token_file.stat().st_mode & 0o777) == 0o600

def test_write_token_securely_rejects_file_symlink(tmp_path):
    tokens_dir = tmp_path / ".multi-ai-tokens"
    tokens_dir.mkdir(parents=True, exist_ok=True)

    target = tmp_path / "target.txt"
    target.write_text("dummy")

    symlink_file = tokens_dir / "mistral_token.txt"
    symlink_file.symlink_to(target)

    with pytest.raises(ValueError, match="Symlink token file rejected for security"):
        _write_token_securely("pawned_token", target_file=symlink_file)

    assert target.read_text() == "dummy"

def test_write_token_securely_rejects_parent_dir_symlink(tmp_path):
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir(parents=True, exist_ok=True)

    symlink_dir = tmp_path / ".multi-ai-tokens"
    symlink_dir.symlink_to(real_dir)

    token_file = symlink_dir / "mistral_token.txt"

    with pytest.raises(ValueError, match="Symlink token directory rejected for security"):
        _write_token_securely("pawned_token", target_file=token_file)
