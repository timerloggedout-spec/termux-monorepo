from pathlib import Path
from mapper_graph import resolve_import_to_file

def test_resolve_import_to_file_fallback(tmp_path, monkeypatch):
    home_dir = tmp_path / "fake_home"
    home_dir.mkdir()
    monkeypatch.setattr("mapper_graph.HOME", home_dir)

    target_file = home_dir / "project" / "helper.py"
    target_file.parent.mkdir(parents=True)
    target_file.write_text("def help(): pass")

    rel_target = "project/helper.py"
    file_set = {"project/helper.py", "main.py"}
    name_map = {"helper.py": "project/helper.py", "main.py": "main.py"}

    current_file = home_dir / "main.py"

    resolved = resolve_import_to_file("helper", current_file, file_set, name_map=name_map)
    assert resolved == target_file

def test_resolve_import_to_file_without_name_map(tmp_path, monkeypatch):
    home_dir = tmp_path / "fake_home"
    home_dir.mkdir()
    monkeypatch.setattr("mapper_graph.HOME", home_dir)

    target_file = home_dir / "project" / "utils.py"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("X = 1")

    file_set = {"project/utils.py"}
    current_file = home_dir / "app.py"

    resolved = resolve_import_to_file("utils", current_file, file_set)
    assert resolved == target_file
