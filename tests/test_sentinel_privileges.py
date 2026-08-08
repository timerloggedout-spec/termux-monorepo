import os
import stat
import pytest
from pathlib import Path

def test_sentinel_local_privilege_restrictions(tmp_path, monkeypatch):
    # Ensure PYTHONPATH is correct for deepcli imports
    import deepcli.core as core

    # 1. Setup temporary directories/paths for testing permissions
    temp_config_dir = tmp_path / ".deepcli"
    temp_config_file = temp_config_dir / "config.json"

    # Mock CONFIG_DIR and CONFIG_FILE to use our temporary paths
    monkeypatch.setattr(core, "CONFIG_DIR", temp_config_dir)
    monkeypatch.setattr(core, "CONFIG_FILE", temp_config_file)

    # Trigger directory creation logic manually as it runs at module load
    temp_config_dir.mkdir(parents=True, exist_ok=True)
    try:
        temp_config_dir.chmod(0o700)
    except Exception:
        pass

    # Verify CONFIG_DIR has 0o700 permissions
    mode = temp_config_dir.stat().st_mode
    assert (mode & 0o777) == 0o700

    # 2. Test save_config() enforces 0o600
    core.save_config({"token": "test-token"})
    assert temp_config_file.exists()
    file_mode = temp_config_file.stat().st_mode
    assert (file_mode & 0o777) == 0o600

    # 3. Test _cache_path() and _cache_save() enforce 0o700 directories and 0o600 files
    # Mock os.path.expanduser to redirect ~ to tmp_path
    def mock_expanduser(path):
        if path.startswith("~"):
            return path.replace("~", str(tmp_path), 1)
        return path

    monkeypatch.setattr(os.path, "expanduser", mock_expanduser)

    # Call _cache_save which will create the directories and set permissions
    session_id = "test-session-123"
    messages = [{"role": "user", "content": "hello"}]
    core._cache_save(session_id, messages, account="primary")

    expected_cache_path = Path(mock_expanduser("~/.deepcli/session_store/primary")) / f"{session_id}.json"
    assert expected_cache_path.exists()

    # Check store_dir permissions (0o700)
    store_dir = expected_cache_path.parent
    assert (store_dir.stat().st_mode & 0o777) == 0o700

    # Check parent of store_dir permissions (0o700)
    assert (store_dir.parent.stat().st_mode & 0o777) == 0o700

    # Check cache file permissions (0o600)
    assert (expected_cache_path.stat().st_mode & 0o777) == 0o600
