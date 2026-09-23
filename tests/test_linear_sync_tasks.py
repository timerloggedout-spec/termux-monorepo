"""Minimal unit tests for the file-reading helpers in archwiz/linear_sync.py.

No network calls: get_tasks() and get_done_tasks() only touch the
filesystem, so we monkeypatch the module-level ARCHWIZ_DIR / WORKSPACE_DIR
constants to point at pytest tmp_path fixtures.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from archwiz import linear_sync  # noqa: E402


def test_get_tasks_missing_file_returns_empty_list(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path)
    assert linear_sync.get_tasks() == []


def test_get_tasks_reads_plain_list(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path)
    tasks = [{"id": "TER-1", "title": "First"}, {"id": "TER-2", "title": "Second"}]
    (tmp_path / "master_tasks.json").write_text(json.dumps(tasks), encoding="utf-8")
    result = linear_sync.get_tasks()
    assert result == tasks


def test_get_tasks_reads_dict_with_tasks_key(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path)
    payload = {"tasks": [{"id": "TER-3", "title": "Third"}], "meta": {"generated": True}}
    (tmp_path / "master_tasks.json").write_text(json.dumps(payload), encoding="utf-8")
    result = linear_sync.get_tasks()
    assert result == [{"id": "TER-3", "title": "Third"}]


def test_get_tasks_ignores_non_dict_entries(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path)
    payload = [{"id": "TER-4"}, "not-a-dict", 42, {"id": "TER-5"}]
    (tmp_path / "master_tasks.json").write_text(json.dumps(payload), encoding="utf-8")
    result = linear_sync.get_tasks()
    assert result == [{"id": "TER-4"}, {"id": "TER-5"}]


def test_get_tasks_handles_invalid_json_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path)
    (tmp_path / "master_tasks.json").write_text("{not valid json", encoding="utf-8")
    assert linear_sync.get_tasks() == []


def test_get_tasks_handles_unexpected_shape_gracefully(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path)
    (tmp_path / "master_tasks.json").write_text(json.dumps("just a string"), encoding="utf-8")
    assert linear_sync.get_tasks() == []


def test_get_done_tasks_missing_files_returns_empty_list(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "WORKSPACE_DIR", tmp_path)
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path / "archwiz-missing")
    assert linear_sync.get_done_tasks() == []


def test_get_done_tasks_reads_primary_location(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "WORKSPACE_DIR", tmp_path)
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", tmp_path / "archwiz-unused")
    primary_dir = tmp_path / "termux-multi-agent"
    primary_dir.mkdir(parents=True)
    (primary_dir / "taDone.md").write_text("TER-1\nTER-2\n", encoding="utf-8")
    assert linear_sync.get_done_tasks() == ["TER-1", "TER-2"]


def test_get_done_tasks_falls_back_to_archwiz_location(monkeypatch, tmp_path):
    monkeypatch.setattr(linear_sync, "WORKSPACE_DIR", tmp_path / "workspace-missing")
    archwiz_dir = tmp_path / "archwiz"
    archwiz_dir.mkdir(parents=True)
    (archwiz_dir / "taDone.md").write_text("TER-9\n", encoding="utf-8")
    monkeypatch.setattr(linear_sync, "ARCHWIZ_DIR", archwiz_dir)
    assert linear_sync.get_done_tasks() == ["TER-9"]