import os
import json
from pathlib import Path
import pytest


def test_token_provider_privileges_enforcement(tmp_path, monkeypatch):
    test_vault_dir = tmp_path / ".synthegration"
    test_vault_file = test_vault_dir / "vault.json"
    upload_file = tmp_path / "deepseek-cli" / "upload-api.json"
    upload_file.parent.mkdir(parents=True, exist_ok=True)
    upload_file.write_text(json.dumps({"authorization": "test_bearer_token"}))

    import token_provider_v2 as tp

    monkeypatch.setattr(tp, "VAULT_DIR", test_vault_dir)
    monkeypatch.setattr(tp, "VAULT", test_vault_file)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    token = tp.get_token("primary")
    assert token == "test_bearer_token"
    assert test_vault_file.exists()
    if os.name != "nt":
        assert (test_vault_file.stat().st_mode & 0o777) == 0o600


def test_token_provider_symlink_safety(tmp_path, monkeypatch):
    test_vault_dir = tmp_path / ".synthegration"
    test_vault_dir.mkdir(parents=True, exist_ok=True)
    test_vault_file = test_vault_dir / "vault.json"

    upload_file = tmp_path / "deepseek-cli" / "upload-api.json"
    upload_file.parent.mkdir(parents=True, exist_ok=True)
    upload_file.write_text(json.dumps({"authorization": "test_bearer_token"}))

    target_file = tmp_path / "sensitive_target.txt"
    target_file.write_text("sensitive_content")
    if os.name != "nt":
        target_file.chmod(0o644)

    test_vault_file.symlink_to(target_file)

    import token_provider_v2 as tp

    monkeypatch.setattr(tp, "VAULT_DIR", test_vault_dir)
    monkeypatch.setattr(tp, "VAULT", test_vault_file)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    with pytest.raises(ValueError, match="Symlink vault path rejected"):
        tp.get_token("primary")

    assert target_file.read_text() == "sensitive_content"
    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644
