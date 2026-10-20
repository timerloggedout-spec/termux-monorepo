import json
import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "deepcli"))
import session_store as ss

def test_session_store_privileges_and_symlink_safety(tmp_path, monkeypatch):
    test_store_dir = tmp_path / ".deepcli"
    test_store_file = test_store_dir / "sessions.json"

    monkeypatch.setattr(ss, "STORE", test_store_file)

    # 1. Test normal save and load
    ss.save("task_key_1", "sess_123", meta={"last_task": "test_task"})
    assert test_store_file.exists()
    if os.name != "nt":
        assert (test_store_dir.stat().st_mode & 0o777) == 0o700
        assert (test_store_file.stat().st_mode & 0o777) == 0o600

    rec = ss.load("task_key_1")
    assert rec is not None
    assert rec["session_id"] == "sess_123"

    # 2. Symlink safety on sessions.json
    target_file = tmp_path / "sensitive.txt"
    target_file.write_text("sensitive_data")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_file = tmp_path / ".deepcli" / "sessions_sym.json"
    symlink_file.symlink_to(target_file)

    monkeypatch.setattr(ss, "STORE", symlink_file)
    ss.save("task_key_2", "sess_456")

    # Target file should not be modified or re-permissioned
    assert target_file.read_text() == "sensitive_data"
    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_session_store_run_state_path_traversal_and_symlinks(tmp_path, monkeypatch):
    test_store_dir = tmp_path / ".deepcli"
    test_store_file = test_store_dir / "sessions.json"
    monkeypatch.setattr(ss, "STORE", test_store_file)

    # 1. Test path traversal rejection in run_state key
    for bad_key in ["../etc", "/etc/passwd", "sub/dir", "key\\test"]:
        with pytest.raises(ValueError, match="Invalid key"):
            ss._runs_dir(bad_key)

    # 2. Test safe run state save and load
    key = "valid_key_1"
    state = {"step": 3, "data": "run_data"}
    final_path = ss.save_run_state(key, state)
    assert final_path.exists()
    if os.name != "nt":
        assert (final_path.parent.stat().st_mode & 0o777) == 0o700
        assert (final_path.stat().st_mode & 0o777) == 0o600

    loaded = ss.load_run_state(key)
    assert loaded == state

    # 3. Clear run state
    ss.clear_run_state(key)
    assert not final_path.exists()

    # 4. Symlink safety on state file
    runs_dir = test_store_dir / "runs" / "sym_key"
    runs_dir.mkdir(parents=True, exist_ok=True)
    state_file = runs_dir / "state.json"
    target_file = tmp_path / "target_state.txt"
    target_file.write_text("target_content")
    state_file.symlink_to(target_file)

    with pytest.raises(ValueError, match="State path is symlink"):
        ss.save_run_state("sym_key", {"step": 1})

    # load_run_state on symlink returns None
    assert ss.load_run_state("sym_key") is None
