import os
import sys
from pathlib import Path

# Ensure harmony_hub/src is on sys.path for direct pytest invocation
SRC_DIR = Path(__file__).resolve().parents[1] / "harmony_hub" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from patch_router import apply_patch

def test_apply_patch_path_traversal_rejection(tmp_path):
    target = tmp_path / "subdir" / ".." / "target.txt"
    res = apply_patch(str(target), "content = content.replace('a', 'b')", method="python")
    assert res is False

def test_apply_patch_symlink_rejection(tmp_path):
    real_target = tmp_path / "real_target.txt"
    real_target.write_text("hello world")
    symlink_target = tmp_path / "sym_target.txt"
    symlink_target.symlink_to(real_target)

    res = apply_patch(str(symlink_target), "content = content.replace('hello', 'hi')", method="python")
    assert res is False
    assert real_target.read_text() == "hello world"

def test_apply_patch_python_success(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("hello world")

    res = apply_patch(str(target), "content = content.replace('hello', 'hi')", method="python")
    assert res is True
    assert target.read_text() == "hi world"
    tmp_script = tmp_path / "_patch_tmp.py"
    assert not tmp_script.exists()
