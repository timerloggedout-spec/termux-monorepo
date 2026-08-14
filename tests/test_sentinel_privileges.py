import os
import sys
import shutil
from pathlib import Path
import pytest

# Ensure deepcli is in path - modified to break loop and update commit sha
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../deepcli")))

def test_sentinel_privileges_enforcement(tmp_path, monkeypatch):
    # Set up test directories under tmp_path
    test_config_dir = tmp_path / ".deepcli"
    test_config_file = test_config_dir / "config.json"

    # Mock CONFIG_DIR and CONFIG_FILE in deepcli.core
    import deepcli.core as dc
    monkeypatch.setattr(dc, "CONFIG_DIR", test_config_dir)
    monkeypatch.setattr(dc, "CONFIG_FILE", test_config_file)

    # 1. Test directory creation privileges
    test_config_dir.mkdir(parents=True, exist_ok=True)
    if not test_config_dir.is_symlink():
        try:
            test_config_dir.chmod(0o700)
        except Exception:
            pass

    # Check permissions (on Unix-like systems)
    if os.name != "nt":
        assert (test_config_dir.stat().st_mode & 0o777) == 0o700

    # 2. Test CONFIG_FILE save privileges
    dc.save_config({"token": "secret_token"})
    assert test_config_file.exists()
    if os.name != "nt":
        assert (test_config_file.stat().st_mode & 0o777) == 0o600

    # 3. Test Cache Directories and Cache Files privileges
    session_id = "test_session_uuid"
    messages = [{"role": "user", "content": "hello"}]

    # Mocking Path.home or ~/.deepcli paths internally
    monkeypatch.setattr(os.path, "expanduser", lambda path: path.replace("~", str(tmp_path)))

    cache_path_str = dc._cache_path(session_id, account="test_account")
    cache_path = Path(cache_path_str)

    # Ensure directory is created with 0o700
    assert cache_path.parent.exists()
    if os.name != "nt":
        assert (cache_path.parent.stat().st_mode & 0o777) == 0o700
        assert (cache_path.parent.parent.stat().st_mode & 0o777) == 0o700

    # Save cache
    dc._cache_save(session_id, messages, account="test_account")
    assert cache_path.exists()
    if os.name != "nt":
        assert (cache_path.stat().st_mode & 0o777) == 0o600


def test_sentinel_privileges_symlink_safety(tmp_path, monkeypatch):
    # Ensure that symlinks are skipped and not followed / modified
    import deepcli.core as dc

    # Create a dummy target file
    target_file = tmp_path / "target_file.txt"
    target_file.write_text("sensitvedata")
    if os.name != "nt":
        target_file.chmod(0o644)

    # Create a symlink pointing to target_file
    symlink_file = tmp_path / "symlink_file.json"
    symlink_file.symlink_to(target_file)

    # Let's verify our is_symlink() safety check
    monkeypatch.setattr(dc, "CONFIG_FILE", symlink_file)
    dc.save_config({"token": "some_token"})

    # Because symlink_file is a symlink, the target file's permissions should NOT have changed to 0o600
    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_sentinel_privileges_path_traversal_prevention(tmp_path, monkeypatch):
    # Ensure that path traversal attempts are detected and raise ValueError or are sanitized.
    import deepcli.core as dc

    # Mocking ~/.deepcli path
    monkeypatch.setattr(os.path, "expanduser", lambda path: path.replace("~", str(tmp_path)))

    # Test that malicious path traversal UUIDs/SIDs raise ValueError or get sanitized safely
    with pytest.raises(ValueError):
        dc._cache_path("../../../etc/passwd")

    with pytest.raises(ValueError):
        dc._cache_path("/absolute/path/traversal")

    # Safe SIDs with safe chars should succeed and have sanitized names
    safe_path_str = dc._cache_path("session-123_abc.dot")
    assert "session-123_abc.dot.json" in safe_path_str

    # SIDs with unsafe chars should have them sanitized to underscores
    unsanitized_path_str = dc._cache_path("session$#*!123")
    assert "session____123.json" in unsanitized_path_str
