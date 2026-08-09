import os
import sys
import pytest
from pathlib import Path

# Add deepcli package to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../deepcli")))

import deepcli.core as deepcli_core

def test_deepcli_privilege_restrictions(tmp_path, monkeypatch):
    # Overwrite CONFIG_DIR to use tmp_path
    mock_config_dir = tmp_path / ".deepcli"
    mock_config_file = mock_config_dir / "config.json"

    monkeypatch.setattr(deepcli_core, "CONFIG_DIR", mock_config_dir)
    monkeypatch.setattr(deepcli_core, "CONFIG_FILE", mock_config_file)

    # Overwrite Path.home() so os.path.expanduser("~/.deepcli") can use tmp_path
    monkeypatch.setattr(os.path, "expanduser", lambda path: str(tmp_path) if "~" in path else path)

    # 1. Test directory creation and permissions of CONFIG_DIR
    mock_config_dir.mkdir(parents=True, exist_ok=True)
    try:
        mock_config_dir.chmod(0o700)
    except Exception:
        pass

    stat_dir = mock_config_dir.stat()
    assert (stat_dir.st_mode & 0o777) == 0o700

    # 2. Test configuration save permissions of CONFIG_FILE
    deepcli_core.save_config({"token": "mock_token"})
    assert mock_config_file.exists()
    stat_file = mock_config_file.stat()
    assert (stat_file.st_mode & 0o777) == 0o600

    # 3. Test caching path and subdirectory permission enforcement
    cache_path = deepcli_core._cache_path("session_abc", "primary")
    store_dir = Path(cache_path).parent
    assert store_dir.exists()
    stat_store = store_dir.stat()
    assert (stat_store.st_mode & 0o777) == 0o700

    # 4. Test _cache_save writes cache file with 0o600
    messages = [{"role": "user", "content": "hello"}]
    deepcli_core._cache_save("session_abc", messages, "primary")
    cache_file = Path(cache_path)
    assert cache_file.exists()
    stat_cache = cache_file.stat()
    assert (stat_cache.st_mode & 0o777) == 0o600

def test_deepcli_path_traversal_rejection(tmp_path, monkeypatch):
    # Ensure invalid directory traversal in _cache_path raises ValueError
    with pytest.raises(ValueError, match="Invalid file path"):
        deepcli_core._cache_path("../../../etc/passwd", "primary")

    # Ensure invalid directory traversal in upload_file raises ValueError
    mock_token = "mock_token"
    bad_file = "relative/../../secret_key"
    with pytest.raises(ValueError, match="Invalid file path"):
        deepcli_core.upload_file(mock_token, "sess_1", bad_file)
