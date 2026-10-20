import os
import sys
from pathlib import Path
import pytest

# Add parent directory to path to import mistral_bridge directly or via importlib
bridge_path = Path(__file__).parent.parent / "multi-ai-cli" / "bridge"
if str(bridge_path) not in sys.path:
    sys.path.insert(0, str(bridge_path))

import mistral_bridge


def test_write_token_securely_enforcement(tmp_path):
    token_dir = tmp_path / ".multi-ai-tokens"
    token_file = token_dir / "mistral_token.txt"

    mistral_bridge._write_token_securely("test_secret_token_123", target_path=token_file)

    assert token_file.exists()
    assert token_file.read_text(encoding="utf-8") == "test_secret_token_123"

    if os.name != "nt":
        assert (token_dir.stat().st_mode & 0o777) == 0o700
        assert (token_file.stat().st_mode & 0o777) == 0o600


def test_write_token_securely_symlink_file_rejection(tmp_path):
    token_dir = tmp_path / ".multi-ai-tokens"
    token_dir.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        token_dir.chmod(0o700)

    target_file = tmp_path / "sensitive_system_file.txt"
    target_file.write_text("sensitive_data", encoding="utf-8")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_file = token_dir / "mistral_token.txt"
    symlink_file.symlink_to(target_file)

    with pytest.raises(ValueError, match="Symlink token path rejected"):
        mistral_bridge._write_token_securely("malicious_token_payload", target_path=symlink_file)

    # Ensure target file content and permissions remain untouched
    assert target_file.read_text(encoding="utf-8") == "sensitive_data"
    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_write_token_securely_symlink_dir_rejection(tmp_path):
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir(parents=True, exist_ok=True)

    symlink_dir = tmp_path / ".multi-ai-tokens"
    symlink_dir.symlink_to(real_dir)

    token_file = symlink_dir / "mistral_token.txt"

    with pytest.raises(ValueError, match="Symlink directory rejected"):
        mistral_bridge._write_token_securely("malicious_token_payload", target_path=token_file)

