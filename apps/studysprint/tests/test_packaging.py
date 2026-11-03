"""Packaging contract (#4436): the TUI installs as a command.

Pins the pyproject so the pipx one-liner cannot silently break:
the entry point targets tui:main, the module list covers every
sibling the TUI imports, the example course ships as data files,
and the distribution version is read from TUI_VERSION itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
tomllib = pytest.importorskip("tomllib")


def _project() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())


def test_entry_point_installs_the_tui_command():
    scripts = _project()["project"]["scripts"]
    assert scripts == {"studysprint-tui": "tui:main"}


def test_version_is_dynamic_from_tui_version():
    project = _project()["project"]
    assert "version" not in project
    assert project["dynamic"] == ["version"]
    dyn = _project()["tool"]["setuptools"]["dynamic"]["version"]
    assert dyn["attr"] == "tui.TUI_VERSION"


def test_modules_cover_the_tui_import_chain():
    mods = set(_project()["tool"]["setuptools"]["py-modules"])
    # every sibling tui.py imports at module level
    for needed in ("tui", "study_reader", "study_sr", "study_tools",
                   "study_calendar", "study_memory"):
        assert needed in mods, needed
    # each listed module exists in the tree
    for name in mods:
        assert (ROOT / f"{name}.py").exists(), name
    # the CLI pair stays clone-route only (vendored-oracle path)
    assert "agent" not in mods and "demo" not in mods


def test_example_course_ships_as_data_files():
    files = _project()["tool"]["setuptools"]["data-files"]["examples"]
    for name in ("syllabus.json", "practice_set.json",
                 "readings.json"):
        assert f"examples/{name}" in files
        assert (ROOT / "examples" / name).exists(), name


def test_runtime_dependencies_named():
    deps = set(_project()["project"]["dependencies"])
    assert {"textual", "fsrs", "genanki"} <= deps


def test_data_root_fallback_exists():
    sys.path.insert(0, str(ROOT))
    try:
        import tui
        assert tui._data_root() == tui.APP_ROOT  # repo checkout
        state = tui.build_state()
        assert state["syllabus"] or state["plan"]
    finally:
        sys.path.remove(str(ROOT))
