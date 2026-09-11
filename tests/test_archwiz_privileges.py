import os
import sys
from pathlib import Path
import pytest

import archwiz.config as ac


def test_archwiz_privileges_enforcement(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".archwiz"
    test_config_file = test_config_dir / "config.json"

    monkeypatch.setattr(ac, "USER_CONFIG_DIR", test_config_dir)
    monkeypatch.setattr(ac, "USER_CONFIG_FILE", test_config_file)

    cfg = ac.Config()

    # 1. Test USER_CONFIG_DIR permissions
    if os.name != "nt":
        assert (test_config_dir.stat().st_mode & 0o777) == 0o700

    # 2. Test USER_CONFIG_FILE save permissions
    cfg.save()
    assert test_config_file.exists()
    if os.name != "nt":
        assert (test_config_file.stat().st_mode & 0o777) == 0o600

    # 3. Test _mkdir permissions
    sub_dir = tmp_path / "sub_dir"
    cfg._mkdir(sub_dir, mode=0o700)
    assert sub_dir.exists()
    if os.name != "nt":
        assert (sub_dir.stat().st_mode & 0o777) == 0o700


def test_archwiz_symlink_safety(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".archwiz"
    test_config_dir.mkdir(parents=True, exist_ok=True)

    # 1. Reject symlinked USER_CONFIG_DIR
    symlink_dir = tmp_path / "symlink_dir"
    symlink_dir.symlink_to(test_config_dir, target_is_directory=True)

    monkeypatch.setattr(ac, "USER_CONFIG_DIR", symlink_dir)
    monkeypatch.setattr(ac, "USER_CONFIG_FILE", symlink_dir / "config.json")

    with pytest.raises(ValueError, match="Symlink USER_CONFIG_DIR rejected"):
        ac.Config()

    # Restore USER_CONFIG_DIR
    monkeypatch.setattr(ac, "USER_CONFIG_DIR", test_config_dir)

    # 2. Reject symlinked USER_CONFIG_FILE in Config() and save()
    target_file = tmp_path / "target_file.json"
    target_file.write_text("sensitvedata")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_file = test_config_dir / "config.json"
    symlink_file.symlink_to(target_file)

    monkeypatch.setattr(ac, "USER_CONFIG_FILE", symlink_file)

    with pytest.raises(ValueError, match="Symlink USER_CONFIG_FILE rejected"):
        ac.Config()

    cfg = ac.Config.__new__(ac.Config)
    cfg._cfg = dict(ac._defaults)

    with pytest.raises(ValueError, match="Target config file is a symlink"):
        cfg.save()

    # Verify target file permissions were not altered
    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644

    # 3. Reject symlinked directory in _mkdir
    symlink_target_dir = tmp_path / "target_dir"
    symlink_target_dir.mkdir()
    symlink_mkdir = tmp_path / "symlink_mkdir"
    symlink_mkdir.symlink_to(symlink_target_dir, target_is_directory=True)

    with pytest.raises(ValueError, match="Target directory is a symlink"):
        cfg._mkdir(symlink_mkdir)


def test_archwiz_path_traversal_prevention(tmp_path, monkeypatch):
    test_config_dir = tmp_path / ".archwiz"
    test_config_file = test_config_dir / "config.json"
    monkeypatch.setattr(ac, "USER_CONFIG_DIR", test_config_dir)
    monkeypatch.setattr(ac, "USER_CONFIG_FILE", test_config_file)

    invalid_paths = [
        "../traversal",
        "../../etc/passwd",
        "foo/../../bar"
    ]

    for path in invalid_paths:
        with pytest.raises(ValueError, match="Path traversal detected"):
            ac.set_tokens_dir(path)

        with pytest.raises(ValueError, match="Path traversal detected"):
            ac.set_session_store(path)


def test_activity_listener_symlink_safety(tmp_path, monkeypatch):
    import archwiz.activity_listener as al

    sandbox_dir = tmp_path / "sandbox"
    monkeypatch.setattr(al, "SANDBOX", sandbox_dir)

    target_file = tmp_path / "target_script.sh"
    target_file.write_text("echo unsafe")
    if os.name != "nt":
        target_file.chmod(0o644)

    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # Force script path to point to a symlink
    symlink_script = sandbox_dir / "block_000000.sh"
    symlink_script.symlink_to(target_file)

    def mock_now():
        class FixedTime:
            def strftime(self, fmt):
                return "000000"
        return FixedTime()

    monkeypatch.setattr(al, "datetime", type("MockDateTime", (), {"now": staticmethod(mock_now)}))

    with pytest.raises(ValueError, match="Symlink execution script rejected"):
        al.run_code("echo test")

    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644
