import os
import sys
import yaml
from pathlib import Path
import pytest

def _get_sm():
    try:
        import multi_ai_cli.core.session_manager as sm
        return sm
    except ModuleNotFoundError:
        sys.path.insert(0, os.path.abspath("multi-ai-cli"))
        import core.session_manager as sm
        return sm


def test_session_manager_symlink_config_rejection(tmp_path):
    sm = _get_sm()
    real_config = tmp_path / "config.yaml"
    real_config.write_text("deepseek:\n  token_path: /tmp/dummy_token.txt\n")

    symlink_config = tmp_path / "symlink_config.yaml"
    symlink_config.symlink_to(real_config)

    with pytest.raises(ValueError, match="Symlink config path"):
        sm.SessionManager(config_path=symlink_config)


def test_session_manager_token_path_traversal_rejection(tmp_path):
    sm = _get_sm()
    config_file = tmp_path / "config.yaml"
    config_file.write_text("deepseek:\n  token_path: ../../etc/passwd\n")

    mgr = sm.SessionManager(config_path=config_file)
    with pytest.raises(ValueError, match="Path traversal detected"):
        mgr.get_token("deepseek")


def test_session_manager_token_symlink_rejection(tmp_path):
    sm = _get_sm()
    sensitive_file = tmp_path / "sensitive.txt"
    sensitive_file.write_text("secret_data")

    symlink_token = tmp_path / "symlinked_token.txt"
    symlink_token.symlink_to(sensitive_file)

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"deepseek:\n  token_path: {symlink_token}\n")

    mgr = sm.SessionManager(config_path=config_file)
    with pytest.raises(ValueError, match="Symlink token path"):
        mgr.get_token("deepseek")


def test_session_manager_valid_token_reading(tmp_path):
    sm = _get_sm()
    token_file = tmp_path / "valid_token.txt"
    token_file.write_text("  my_secret_token_123  \n")

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"deepseek:\n  token_path: {token_file}\n")

    mgr = sm.SessionManager(config_path=config_file)
    assert mgr.get_token("deepseek") == "my_secret_token_123"


def test_session_manager_windows_path_compatibility(tmp_path):
    sm = _get_sm()
    # Test that Windows style backslash paths do not trigger false positive path traversal errors
    windows_path_str = r"C:\Users\Username\.config\token.txt"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"deepseek:\n  token_path: '{windows_path_str}'\n")

    mgr = sm.SessionManager(config_path=config_file)
    # File doesn't exist so get_token returns None, but must NOT raise ValueError for '\\'
    assert mgr.get_token("deepseek") is None


def test_session_manager_cookie_path_traversal_rejection(tmp_path):
    sm = _get_sm()
    config_file = tmp_path / "config.yaml"
    config_file.write_text("deepseek:\n  cookie_path: ../../etc/passwd\n")

    mgr = sm.SessionManager(config_path=config_file)
    with pytest.raises(ValueError, match="Path traversal detected in cookie_path"):
        mgr.get_cookies("deepseek")


def test_session_manager_cookie_symlink_rejection(tmp_path):
    sm = _get_sm()
    sensitive_file = tmp_path / "sensitive_cookies.json"
    sensitive_file.write_text('[{"name": "ds_session_id", "value": "secret"}]')

    symlink_cookie = tmp_path / "symlinked_cookie.json"
    symlink_cookie.symlink_to(sensitive_file)

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"deepseek:\n  cookie_path: {symlink_cookie}\n")

    mgr = sm.SessionManager(config_path=config_file)
    with pytest.raises(ValueError, match="Symlink cookie path"):
        mgr.get_cookies("deepseek")


def test_session_manager_valid_cookies_reading(tmp_path):
    sm = _get_sm()
    cookie_file = tmp_path / "valid_cookies.json"
    cookie_file.write_text('[{"name": "ds_session_id", "value": "abc123val"}]')

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"deepseek:\n  cookie_path: {cookie_file}\n")

    mgr = sm.SessionManager(config_path=config_file)
    cookies = mgr.get_cookies("deepseek")
    assert len(cookies) == 1
    assert cookies[0]["name"] == "ds_session_id"
    assert cookies[0]["value"] == "abc123val"
