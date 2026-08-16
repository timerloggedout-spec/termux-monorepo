import os
import sys
import shutil
from pathlib import Path
import pytest

def test_sentinel_privileges_enforcement(tmp_path, monkeypatch):
    # Set up test directories under tmp_path
    test_config_dir = tmp_path / ".deepcli"
    test_config_file = test_config_dir / "config.json"

    # Mock CONFIG_DIR and CONFIG_FILE in deepcli.deepcli.core
    import deepcli.deepcli.core as dc
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
    import deepcli.deepcli.core as dc

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
    import deepcli.deepcli.core as dc

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

    # Test malicious account names raise ValueError or get sanitized safely
    with pytest.raises(ValueError):
        dc._cache_path("session1", account="../../etc")

    with pytest.raises(ValueError):
        dc._cache_path("session1", account="/absolute/account")

    # Safe account with special chars gets sanitized
    acc_path_str = dc._cache_path("session1", account="acc$#*!123")
    assert "acc____123" in acc_path_str


def test_sentinel_session_cache_key_collision_and_header_isolation(tmp_path, monkeypatch):
    import deepcli.deepcli.core as dc

    # 1. Test session cache key uniqueness across tokens sharing prefixes
    token1 = "token_prefix_1234567890_AAA"
    token2 = "token_prefix_1234567890_BBB"
    key1 = dc._session_cache_key(token1)
    key2 = dc._session_cache_key(token2)
    assert key1 != key2

    # 2. Test get_session clears stale POW response header
    sess = dc.get_session(token1)
    sess.headers["X-Ds-Pow-Response"] = "stale_pow_header"

    # Subsequent retrieval of same session must purge X-Ds-Pow-Response
    retrieved_sess = dc.get_session(token1)
    assert "X-Ds-Pow-Response" not in retrieved_sess.headers

    # 3. Test upload_file header isolation on dummy file
    dummy_file = tmp_path / "test.txt"
    dummy_file.write_text("hello world")

    # Mock get_pow_challenge, solve_pow, and http_requests.post
    monkeypatch.setattr(dc, "get_pow_challenge", lambda token, path: {"challenge": "c"})
    monkeypatch.setattr(dc, "solve_pow", lambda challenge: "fresh_pow_header")

    captured_headers = {}

    def mock_post(url, files, headers):
        nonlocal captured_headers
        captured_headers = headers
        class MockResp:
            def raise_for_status(self): pass
            def json(self): return {"data": {"biz_data": {"id": "uploaded_file_id"}}}
        return MockResp()

    monkeypatch.setattr(dc.http_requests, "post", mock_post)

    file_id = dc.upload_file(token1, "session_123", str(dummy_file))
    assert file_id == "uploaded_file_id"
    assert captured_headers.get("X-Ds-Pow-Response") == "fresh_pow_header"

    # Shared session headers in _session should NOT contain X-Ds-Pow-Response
    sess_after = dc.get_session(token1)
    assert "X-Ds-Pow-Response" not in sess_after.headers
