import os
from pathlib import Path
import pytest


def test_multi_ai_cache_privileges_enforcement(tmp_path, monkeypatch):
    test_cache_dir = tmp_path / ".multi-ai-cache"

    import core.cache as mc
    monkeypatch.setattr(mc, "CACHE_DIR", test_cache_dir)

    test_cache_dir.mkdir(parents=True, exist_ok=True)
    if not test_cache_dir.is_symlink():
        try:
            test_cache_dir.chmod(0o700)
        except Exception:
            pass

    if os.name != "nt":
        assert (test_cache_dir.stat().st_mode & 0o777) == 0o700

    session_id = "test_session_123"
    messages = [{"role": "user", "content": "hello multi-ai"}]

    cache_path_str = mc.cache_path(session_id)
    cache_path = Path(cache_path_str)

    mc.cache_save(session_id, messages)
    assert cache_path.exists()
    if os.name != "nt":
        assert (cache_path.stat().st_mode & 0o777) == 0o600

    loaded = mc.cache_load(session_id)
    assert loaded == messages


def test_multi_ai_cache_symlink_safety(tmp_path, monkeypatch):
    test_cache_dir = tmp_path / ".multi-ai-cache"
    test_cache_dir.mkdir(parents=True, exist_ok=True)

    import core.cache as mc
    monkeypatch.setattr(mc, "CACHE_DIR", test_cache_dir)

    target_file = tmp_path / "sensitive_target.txt"
    target_file.write_text("sensitvedata")
    if os.name != "nt":
        target_file.chmod(0o644)

    symlink_file = test_cache_dir / "symlink_session.json"
    symlink_file.symlink_to(target_file)

    messages = [{"role": "user", "content": "symlink test"}]
    with pytest.raises(ValueError, match="Symlink cache path rejected for security"):
        mc.cache_save("symlink_session", messages)

    if os.name != "nt":
        assert (target_file.stat().st_mode & 0o777) == 0o644


def test_multi_ai_cache_path_traversal_prevention(tmp_path, monkeypatch):
    test_cache_dir = tmp_path / ".multi-ai-cache"
    test_cache_dir.mkdir(parents=True, exist_ok=True)

    import core.cache as mc
    monkeypatch.setattr(mc, "CACHE_DIR", test_cache_dir)

    with pytest.raises(ValueError):
        mc.cache_path("../../../etc/passwd")

    with pytest.raises(ValueError):
        mc.cache_path("/absolute/path/traversal")

    safe_path_str = mc.cache_path("session-123_abc.dot")
    assert "session-123_abc.dot.json" in safe_path_str

    unsanitized_path_str = mc.cache_path("session$#*!123")
    assert "session____123.json" in unsanitized_path_str
