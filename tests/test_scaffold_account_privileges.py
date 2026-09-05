import os
import json
import pytest
from pathlib import Path
from harmony_hub.src.scaffold_account import scaffold

def test_scaffold_account_privileges_enforcement(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    cookies_file = tmp_path / "cookies_test.json"
    cookies_data = [{"name": "ds_session_id", "value": "test_session_token_12345"}]
    cookies_file.write_text(json.dumps(cookies_data))

    scaffold(str(cookies_file), "test_account")

    vault_dir = tmp_path / ".synthegration"
    vault_file = vault_dir / "vault.json"
    dest_dir = tmp_path / "deepseek-cli"
    dest_file = dest_dir / "cookies_test_account.json"
    accounts_file = tmp_path / "harmony_hub" / "workspace" / "accounts.json"

    assert vault_dir.exists()
    assert oct(vault_dir.stat().st_mode & 0o777) == "0o700"

    assert vault_file.exists()
    assert oct(vault_file.stat().st_mode & 0o777) == "0o600"

    assert dest_dir.exists()
    assert oct(dest_dir.stat().st_mode & 0o777) == "0o700"

    assert dest_file.exists()
    assert oct(dest_file.stat().st_mode & 0o777) == "0o600"

    assert accounts_file.exists()
    assert oct(accounts_file.stat().st_mode & 0o777) == "0o600"

def test_scaffold_account_symlink_safety(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    target_file = tmp_path / "target.txt"
    target_file.write_text("sensitive")

    symlink_cookies = tmp_path / "cookies_sym.json"
    symlink_cookies.symlink_to(target_file)

    with pytest.raises(ValueError, match="Symlink target rejected"):
        scaffold(str(symlink_cookies), "test_account")

    cookies_file = tmp_path / "cookies_valid.json"
    cookies_data = [{"name": "ds_session_id", "value": "test_session_token_12345"}]
    cookies_file.write_text(json.dumps(cookies_data))

    vault_dir = tmp_path / ".synthegration"
    vault_dir.mkdir(parents=True, exist_ok=True)
    vault_symlink = vault_dir / "vault.json"
    vault_symlink.symlink_to(target_file)

    with pytest.raises(ValueError, match="Symlink target rejected"):
        scaffold(str(cookies_file), "test_account")
