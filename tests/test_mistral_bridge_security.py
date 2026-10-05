import os
import pytest
import importlib.util
from pathlib import Path

# Dynamically import multi-ai-cli/bridge/mistral_bridge.py
spec = importlib.util.spec_from_file_location(
    "mistral_bridge", "multi-ai-cli/bridge/mistral_bridge.py"
)
mistral_bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mistral_bridge)


def test_write_token_securely_creates_file_and_permissions(tmp_path, monkeypatch):
    token_dir = tmp_path / ".multi-ai-tokens"
    token_file = token_dir / "mistral_token.txt"
    monkeypatch.setattr(mistral_bridge, "token_file", token_file)

    mistral_bridge._write_token_securely("secret-mistral-token-123")

    assert token_file.exists()
    assert token_file.read_text(encoding="utf-8") == "secret-mistral-token-123"

    if os.name == "posix":
        dir_mode = token_dir.stat().st_mode & 0o777
        file_mode = token_file.stat().st_mode & 0o777
        assert dir_mode == 0o700
        assert file_mode == 0o600


def test_write_token_securely_rejects_symlink_file(tmp_path, monkeypatch):
    token_dir = tmp_path / ".multi-ai-tokens"
    token_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

    target_file = tmp_path / "sensitive_target.txt"
    target_file.write_text("original content", encoding="utf-8")

    token_file = token_dir / "mistral_token.txt"
    token_file.symlink_to(target_file)

    monkeypatch.setattr(mistral_bridge, "token_file", token_file)

    with pytest.raises(ValueError, match="symlink"):
        mistral_bridge._write_token_securely("malicious-token")

    # Verify target file was not modified
    assert target_file.read_text(encoding="utf-8") == "original content"


def test_write_token_securely_rejects_symlink_dir(tmp_path, monkeypatch):
    target_dir = tmp_path / "real_dir"
    target_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

    token_dir = tmp_path / ".multi-ai-tokens"
    token_dir.symlink_to(target_dir)

    token_file = token_dir / "mistral_token.txt"
    monkeypatch.setattr(mistral_bridge, "token_file", token_file)

    with pytest.raises(ValueError, match="symlink"):
        mistral_bridge._write_token_securely("malicious-token")
