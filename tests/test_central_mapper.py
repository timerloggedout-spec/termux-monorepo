import os
import json
import tempfile
from pathlib import Path
from central_mapper_v420 import CentralMapper, BLOAT_REGEX

def test_bloat_regex_and_size():
    mapper = CentralMapper()
    # Test bloat pattern regex
    assert mapper.is_bloat(Path("concat_work_123_456"), size=100) is True
    assert mapper.is_bloat(Path("sigs_py.txt"), size=100) is True
    assert mapper.is_bloat(Path("my_script.py"), size=100) is False
    # Test size threshold (>5MB)
    assert mapper.is_bloat(Path("my_script.py"), size=6_000_000) is True

def test_central_mapper_state_caching(monkeypatch, tmp_path):
    # Setup temporary home structure
    home_dir = tmp_path / "fake_home"
    home_dir.mkdir()
    monkeypatch.setattr("central_mapper_v420.HOME", home_dir)

    test_file = home_dir / "sample.py"
    test_file.write_text("print('hello world')")

    mapper = CentralMapper()
    mapper.ast_available = False
    mapper.scan()

    assert mapper.new_files == 1
    assert mapper.modified_files == 0
    assert len(mapper.index) == 1
    original_sha = mapper.index[0]["sha"]

    # Save state to disk
    mapper.save_state()

    # Second scan: file is unchanged
    hash_call_count = 0
    original_hash_file = mapper.hash_file

    def counting_hash_file(path):
        nonlocal hash_call_count
        hash_call_count += 1
        return original_hash_file(path)

    mapper2 = CentralMapper()
    mapper2.ast_available = False
    monkeypatch.setattr(mapper2, "hash_file", counting_hash_file)
    mapper2.scan()

    assert mapper2.new_files == 0
    assert mapper2.modified_files == 0
    # hash_file should NOT have been called because mtime and size matched state!
    assert hash_call_count == 0
    assert mapper2.index[0]["sha"] == original_sha

    # Modify file content and mtime
    test_file.write_text("print('hello updated')")

    mapper3 = CentralMapper()
    mapper3.ast_available = False
    mapper3.scan()

    assert mapper3.new_files == 0
    assert mapper3.modified_files == 1
    assert mapper3.index[0]["sha"] != original_sha
