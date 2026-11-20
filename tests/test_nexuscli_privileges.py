import os
import sys
import shutil
from pathlib import Path
import pytest

def test_nexuscli_privileges_enforcement(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".nexuscli"
    test_config_file = test_config_dir / "config.json"

    import nexuscli.core.api as nc
    monkeypatch.setattr(nc, "CONFIG_DIR", test_config_dir)
    monkeypatch.setattr(nc, "CONFIG_FILE", test_config_file)

    test_config_dir.mkdir(parents=True, exist_ok=True)
    if not test_config_dir.is_symlink():
        try:
            test_config_dir.chmod(0o700)
        except Exception:
            pass

    if os.name != "nt":
        assert (test_config_dir.stat().st_mode & 0o777) == 0o700

    nc.save_config({"token": "secret_token"})
    assert test_config_file.exists()
    if os.name != "nt":
        assert (test_config_file.stat().st_mode & 0o777) == 0o600

    session_id = "test_session_uuid"
    messages = [{"role": "user", "content": "hello"}]

    monkeypatch.setattr(os.path, "expanduser", lambda path: path.replace("~", str(tmp_path)))

    cache_path_str = nc._cache_path(session_id, account="test_account")
    cache_path = Path(cache_path_str)

    assert cache_path.parent.exists()
    if os.name != "nt":
        assert (cache_path.parent.stat().st_mode & 0o777) == 0o700
        assert (cache_path.parent.parent.stat().st_mode & 0o777) == 0o700

    nc._cache_save(session_id, messages, account="test_account")
    assert cache_path.exists()
    if os.name != "nt":
        assert (cache_path.stat().st_mode & 0o777) == 0o600


def test_nexuscli_privileges_symlink_safety(tmp_path, monkeypatch):
    import nexuscli.core.api as nc

    target_file = tmp_path / "target_file.txt"
    target_file.write_text("sensitvedata")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_file = tmp_path / "symlink_file.json"
    symlink_file.symlink_to(target_file)

    monkeypatch.setattr(nc, "CONFIG_FILE", symlink_file)
    nc.save_config({"token": "some_token"})

    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_nexuscli_privileges_path_traversal_prevention(tmp_path, monkeypatch):
    import nexuscli.core.api as nc

    monkeypatch.setattr(os.path, "expanduser", lambda path: path.replace("~", str(tmp_path)))

    with pytest.raises(ValueError):
        nc._cache_path("../../../etc/passwd")

    with pytest.raises(ValueError):
        nc._cache_path("/absolute/path/traversal")

    safe_path_str = nc._cache_path("session-123_abc.dot")
    assert "session-123_abc.dot.json" in safe_path_str

    unsanitized_path_str = nc._cache_path("session$#*!123")
    assert "session____123.json" in unsanitized_path_str

    with pytest.raises(ValueError):
        nc._cache_path("session1", account="../../etc")

    with pytest.raises(ValueError):
        nc._cache_path("session1", account="/absolute/account")

    acc_path_str = nc._cache_path("session1", account="acc$#*!123")
    assert "acc____123" in acc_path_str
