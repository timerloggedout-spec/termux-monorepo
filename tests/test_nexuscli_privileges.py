import os
import sys
import shutil
from pathlib import Path
import pytest

def _get_nc():
    if os.path.abspath(".") not in sys.path:
        sys.path.insert(0, os.path.abspath("."))
    try:
        import nexuscli.core.api as nc
        return nc
    except ModuleNotFoundError:
        sys.path.insert(0, os.path.abspath("nexuscli"))
        import core.api as nc
        return nc

def _get_nexus_cli_main():
    if os.path.abspath(".") not in sys.path:
        sys.path.insert(0, os.path.abspath("."))
    import importlib
    nc = _get_nc()
    sys.modules["core.api"] = nc
    return importlib.import_module("nexuscli.cli.main")

def test_nexuscli_privileges_enforcement(tmp_path, monkeypatch):
    nc = _get_nc()
    test_config_dir = tmp_path / ".nexuscli"
    test_config_file = test_config_dir / "config.json"

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
    nc = _get_nc()

    target_file = tmp_path / "target_file.txt"
    target_file.write_text("sensitvedata")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_file = tmp_path / "symlink_file.json"
    symlink_file.symlink_to(target_file)

    monkeypatch.setattr(nc, "CONFIG_FILE", symlink_file)
    with pytest.raises(ValueError, match="Config file target cannot be a symlink"):
        nc.save_config({"token": "some_token"})

    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_nexuscli_cmd_export_symlink_safety(tmp_path, monkeypatch):
    nexus_cli_main = _get_nexus_cli_main()

    target_file = tmp_path / "export_target.txt"
    target_file.write_text("sensitive")
    symlink_export = tmp_path / "export_symlink.md"
    symlink_export.symlink_to(target_file)

    monkeypatch.setattr(nexus_cli_main, "get_token", lambda: "fake_token")
    monkeypatch.setattr(nexus_cli_main, "export_markdown", lambda token, session_id: "# History")

    class Args:
        session_id = "sess_123"
        last = False
        format = "markdown"
        output = str(symlink_export)

    with pytest.raises(ValueError, match="Symlink targets are not permitted for exports"):
        nexus_cli_main.cmd_export(Args())

    # Normal export test to verify file creation and 0o600 permissions
    valid_output = tmp_path / "valid_export.md"
    Args.output = str(valid_output)
    nexus_cli_main.cmd_export(Args())

    assert valid_output.exists()
    assert valid_output.read_text() == "# History"
    if os.name != "nt":
        assert (valid_output.stat().st_mode & 0o777) == 0o600


def test_nexuscli_privileges_path_traversal_prevention(tmp_path, monkeypatch):
    nc = _get_nc()

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


def test_nexuscli_upload_file_path_traversal_prevention():
    nc = _get_nc()
    with pytest.raises(ValueError, match="Invalid file path"):
        nc.upload_file("token", "session_123", "../../../etc/passwd")

    with pytest.raises(ValueError, match="Invalid file path"):
        nc.upload_file("token", "session_123", "foo/../bar.txt")


def test_nexuscli_cmd_new_session_symlink_safety(tmp_path, monkeypatch):
    nc = _get_nc()
    nexus_cli_main = _get_nexus_cli_main()

    test_config_dir = tmp_path / ".nexuscli"
    test_config_dir.mkdir(parents=True, exist_ok=True)

    target_file = tmp_path / "symlink_target_config.json"
    target_file.write_text("{}")
    symlink_config = test_config_dir / "config.json"
    symlink_config.symlink_to(target_file)

    monkeypatch.setattr("nexuscli.core.api.CONFIG_DIR", test_config_dir)
    monkeypatch.setattr("nexuscli.core.api.CONFIG_FILE", symlink_config)
    try:
        import core.api as core_nc
        monkeypatch.setattr(core_nc, "CONFIG_DIR", test_config_dir)
        monkeypatch.setattr(core_nc, "CONFIG_FILE", symlink_config)
    except ModuleNotFoundError:
        pass

    monkeypatch.setattr(nexus_cli_main, "get_token", lambda: "fake_token")
    monkeypatch.setattr(nexus_cli_main, "create_session", lambda token, model_type="expert": "sess_new_123")

    class Args:
        model = "expert"
        save = True

    with pytest.raises(ValueError, match="Config file target cannot be a symlink"):
        nexus_cli_main.cmd_new_session(Args())

    # Replace symlink with real config file and verify save & load works
    symlink_config.unlink()
    nexus_cli_main.cmd_new_session(Args())

    assert symlink_config.exists()
    assert not symlink_config.is_symlink()
    assert nexus_cli_main.get_last_session() == "sess_new_123"
    if os.name != "nt":
        assert (symlink_config.stat().st_mode & 0o777) == 0o600
