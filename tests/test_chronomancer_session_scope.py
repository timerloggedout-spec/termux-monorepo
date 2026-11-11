"""Regression tests for session-scoped ChronoMancer fork selection."""

import importlib.util
import sqlite3
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "harmony_hub" / "workspace" / "agent" / "chronomancer.py"


@pytest.fixture
def chronomancer_module(monkeypatch, tmp_path):
    # The production module imports Termux-local runtime dependencies at import
    # time. Stub only those adapters; the selection logic and SQLite query stay real.
    deepcli = types.ModuleType("deepcli")
    deepcli.__path__ = []
    core = types.ModuleType("deepcli.core")
    core.get_token = lambda *args, **kwargs: None
    core.get_history = lambda *args, **kwargs: []
    core.branch_conversation = lambda *args, **kwargs: None
    provider = types.ModuleType("token_provider_v2")
    provider.get_token = lambda *args, **kwargs: None

    monkeypatch.setitem(sys.modules, "deepcli", deepcli)
    monkeypatch.setitem(sys.modules, "deepcli.core", core)
    monkeypatch.setitem(sys.modules, "token_provider_v2", provider)

    spec = importlib.util.spec_from_file_location("chronomancer_under_test", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    db_path = tmp_path / "local_repo.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """CREATE TABLE run_history (
                session_id TEXT,
                account TEXT,
                timestamp TEXT,
                validated INTEGER,
                target_file TEXT,
                attempt_number INTEGER,
                patch_content TEXT,
                verdict TEXT
            )"""
        )
    module.DB = db_path
    return module, db_path


def test_fork_selection_ignores_newer_validation_from_another_session(
    chronomancer_module, monkeypatch
):
    module, db_path = chronomancer_module
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """INSERT INTO run_history
               (session_id, account, timestamp, validated, target_file,
                attempt_number, patch_content, verdict)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("session-a", "primary", "2026-11-10T10:30:00+00:00", 1,
                 "task-a", 1, "validated-a", "PASS"),
                ("session-b", "primary", "2026-11-10T11:30:00+00:00", 1,
                 "task-b", 1, "validated-b", "PASS"),
            ],
        )

    messages = [
        {"message_id": 101, "role": "assistant",
         "create_time": "2026-11-10T10:00:00+00:00"},
        {"message_id": 102, "role": "assistant",
         "create_time": "2026-11-10T11:00:00+00:00"},
    ]
    monkeypatch.setattr(module, "get_token_v2", lambda account: "token")
    monkeypatch.setattr(module, "get_history", lambda token, sid: messages)

    assert module.find_best_fork_point("session-a", "primary") == 101


def test_fork_selection_returns_none_without_validation_for_requested_session(
    chronomancer_module, monkeypatch, capsys
):
    module, db_path = chronomancer_module
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """INSERT INTO run_history
               (session_id, account, timestamp, validated, target_file,
                attempt_number, patch_content, verdict)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ("other-session", "primary", "2026-11-10T11:30:00+00:00", 1,
             "task", 1, "validated", "PASS"),
        )

    monkeypatch.setattr(module, "get_token_v2", lambda account: "token")
    monkeypatch.setattr(
        module, "get_history",
        lambda token, sid: [{"message_id": 101, "role": "assistant",
                             "create_time": "2026-11-10T10:00:00+00:00"}],
    )

    assert module.find_best_fork_point("requested-session", "primary") is None
    assert "this session and account" in capsys.readouterr().out


def test_fork_selection_is_account_scoped_too(chronomancer_module, monkeypatch):
    module, db_path = chronomancer_module
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """INSERT INTO run_history
               (session_id, account, timestamp, validated, target_file,
                attempt_number, patch_content, verdict)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ("session-a", "secondary", "2026-11-10T10:30:00+00:00", 1,
                 "task-a", 1, "validated-a", "PASS"),
                ("session-a", "primary", "2026-11-10T09:30:00+00:00", 1,
                 "task-a", 1, "validated-b", "PASS"),
            ],
        )

    monkeypatch.setattr(module, "get_token_v2", lambda account: "token")
    monkeypatch.setattr(
        module, "get_history",
        lambda token, sid: [
            {"message_id": 101, "role": "assistant",
             "create_time": "2026-11-10T09:00:00+00:00"},
            {"message_id": 102, "role": "assistant",
             "create_time": "2026-11-10T10:00:00+00:00"},
        ],
    )

    assert module.find_best_fork_point("session-a", "primary") == 101
