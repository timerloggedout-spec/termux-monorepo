import os
import sys
import json
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath("cli-synthegration"))
import account_manager as am

def test_account_manager_path_traversal_prevention(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".deepcli"
    monkeypatch.setattr(am, "CONFIG_DIR", test_config_dir)

    # Test invalid account names raise ValueError
    invalid_names = [
        "../traversal",
        "/absolute/path",
        "account;injection",
        "account name",
        "acc*!$",
        ""
    ]

    for name in invalid_names:
        with pytest.raises(ValueError, match="Invalid account name"):
            am.import_account("/tmp/dummy_cookies.json", name)

        with pytest.raises(ValueError, match="Invalid account name"):
            am.get_token(name)


def test_account_manager_symlink_safety(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".deepcli"
    test_config_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(am, "CONFIG_DIR", test_config_dir)

    # Mock subprocess node extract script execution
    def mock_run(*args, **kwargs):
        class Proc:
            returncode = 0
            stdout = "mock_bearer_token\n"
            stderr = ""
        return Proc()

    monkeypatch.setattr(am.subprocess, "run", mock_run)

    # 1. Reject symlinked CONFIG_DIR
    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.symlink_to(test_config_dir, target_is_directory=True)
    monkeypatch.setattr(am, "CONFIG_DIR", symlink_dir)

    with pytest.raises(ValueError, match="Symlink CONFIG_DIR rejected"):
        am.import_account("/tmp/dummy_cookies.json", "valid_account")

    # Restore CONFIG_DIR
    monkeypatch.setattr(am, "CONFIG_DIR", test_config_dir)

    # 2. Reject symlinked config file
    target_file = tmp_path / "sensitive_target.json"
    target_file.write_text("sensitivedata")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_config = test_config_dir / "config_hacked_account.json"
    symlink_config.symlink_to(target_file)

    with pytest.raises(ValueError, match="Symlink config path"):
        am.import_account("/tmp/dummy_cookies.json", "hacked_account")

    with pytest.raises(ValueError, match="Symlink config file"):
        am.get_token("hacked_account")


def test_account_manager_privileges_and_retrieval(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".deepcli"
    monkeypatch.setattr(am, "CONFIG_DIR", test_config_dir)

    def mock_run(*args, **kwargs):
        class Proc:
            returncode = 0
            stdout = "valid_secret_token_123\n"
            stderr = ""
        return Proc()

    monkeypatch.setattr(am.subprocess, "run", mock_run)

    # Import account
    success = am.import_account("/tmp/dummy_cookies.json", "user1")
    assert success is True

    # Check permissions
    if os.name != "nt":
        assert (test_config_dir.stat().st_mode & 0o777) == 0o700
        config_file = test_config_dir / "config_user1.json"
        assert config_file.exists()
        assert (config_file.stat().st_mode & 0o777) == 0o600

    # Get token
    token = am.get_token("user1")
    assert token == "valid_secret_token_123"
