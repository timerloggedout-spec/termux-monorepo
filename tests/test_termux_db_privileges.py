import os
import pytest
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("termux_db", "termux-multi-agent/src/db.py")
db_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_mod)

def test_ensure_secure_db_path_symlink_rejection(tmp_path):
    target = tmp_path / "target.db"
    target.touch()
    symlink_db = tmp_path / "symlink.db"
    symlink_db.symlink_to(target)

    with pytest.raises(RuntimeError, match="Symlink database path"):
        db_mod._ensure_secure_db_path(symlink_db)

def test_ensure_secure_db_path_parent_symlink_rejection(tmp_path):
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    sym_dir = tmp_path / "sym_dir"
    sym_dir.symlink_to(real_dir)
    db_path = sym_dir / "test.db"

    with pytest.raises(RuntimeError, match="Symlink parent directory"):
        db_mod._ensure_secure_db_path(db_path)

def test_ensure_secure_db_path_permissions(tmp_path):
    sub_dir = tmp_path / "secure_dir"
    db_path = sub_dir / "secure.db"
    db_path.parent.mkdir()
    db_path.touch()

    db_mod._ensure_secure_db_path(db_path)

    if os.name != "nt":
        dir_mode = sub_dir.stat().st_mode & 0o777
        file_mode = db_path.stat().st_mode & 0o777
        assert dir_mode == 0o700
        assert file_mode == 0o600
