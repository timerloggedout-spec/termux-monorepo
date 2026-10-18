import os
import stat
from pathlib import Path
import pytest
import importlib.util

spec = importlib.util.spec_from_file_location("mistral_bridge", "multi-ai-cli/bridge/mistral_bridge.py")
mistral_bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mistral_bridge)


def test_mistral_bridge_write_token_securely_permissions(tmp_path, monkeypatch):
    test_token_dir = tmp_path / ".multi-ai-tokens"
    test_token_file = test_token_dir / "mistral_token.txt"

    monkeypatch.setattr(mistral_bridge, "token_file", test_token_file)

    mistral_bridge._write_token_securely("test_secret_token_123")

    assert test_token_file.exists()
    assert test_token_file.read_text(encoding="utf-8") == "test_secret_token_123"

    if os.name != "nt":
        dir_mode = stat.S_IMODE(os.stat(test_token_dir).st_mode)
        file_mode = stat.S_IMODE(os.stat(test_token_file).st_mode)
        assert dir_mode == 0o700
        assert file_mode == 0o600


def test_mistral_bridge_symlink_file_rejected(tmp_path, monkeypatch):
    target_file = tmp_path / "actual_file.txt"
    target_file.write_text("old_content", encoding="utf-8")

    symlink_file = tmp_path / "symlink_token.txt"
    symlink_file.symlink_to(target_file)

    monkeypatch.setattr(mistral_bridge, "token_file", symlink_file)

    with pytest.raises(ValueError, match="Symlink token path rejected for security"):
        mistral_bridge._write_token_securely("malicious_token")

    assert target_file.read_text(encoding="utf-8") == "old_content"


def test_mistral_bridge_symlink_dir_rejected(tmp_path, monkeypatch):
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.symlink_to(real_dir)

    symlink_token_file = symlink_dir / "mistral_token.txt"
    monkeypatch.setattr(mistral_bridge, "token_file", symlink_token_file)

    with pytest.raises(ValueError, match="Symlink token path rejected for security"):
        mistral_bridge._write_token_securely("malicious_token")
