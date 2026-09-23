"""Minimal unit tests for archwiz/linear_client.py.

These tests avoid any real network calls: command handlers (cmd_status,
cmd_start, cmd_done, cmd_comment, cmd_create) are monkeypatched so we only
exercise argument parsing / dispatch in main(), plus the _api_key() guard.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from archwiz import linear_client  # noqa: E402


def test_api_key_missing_exits_nonzero(monkeypatch):
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.delenv("LINEAR_API_TOKEN", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        linear_client._api_key()
    assert exc_info.value.code == 2


def test_api_key_present_returns_value(monkeypatch):
    monkeypatch.setenv("LINEAR_API_KEY", "lin_api_test_123")
    assert linear_client._api_key() == "lin_api_test_123"


def test_api_key_falls_back_to_token_env(monkeypatch):
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    monkeypatch.setenv("LINEAR_API_TOKEN", "lin_api_token_456")
    assert linear_client._api_key() == "lin_api_token_456"


def test_main_dispatches_status(monkeypatch):
    calls = {}

    def fake_cmd_status(identifier):
        calls["identifier"] = identifier
        return 0

    monkeypatch.setattr(linear_client, "cmd_status", fake_cmd_status)
    rc = linear_client.main(["status", "TER-14"])
    assert rc == 0
    assert calls["identifier"] == "TER-14"


def test_main_dispatches_start(monkeypatch):
    calls = {}

    def fake_cmd_start(identifier):
        calls["identifier"] = identifier
        return 0

    monkeypatch.setattr(linear_client, "cmd_start", fake_cmd_start)
    rc = linear_client.main(["start", "TER-15"])
    assert rc == 0
    assert calls["identifier"] == "TER-15"


def test_main_dispatches_done_with_pr(monkeypatch):
    calls = {}

    def fake_cmd_done(identifier, pr):
        calls["identifier"] = identifier
        calls["pr"] = pr
        return 0

    monkeypatch.setattr(linear_client, "cmd_done", fake_cmd_done)
    rc = linear_client.main(["done", "TER-16", "--pr", "16"])
    assert rc == 0
    assert calls["identifier"] == "TER-16"
    assert calls["pr"] == 16


def test_main_dispatches_done_without_pr_defaults_to_none(monkeypatch):
    calls = {}

    def fake_cmd_done(identifier, pr):
        calls["identifier"] = identifier
        calls["pr"] = pr
        return 0

    monkeypatch.setattr(linear_client, "cmd_done", fake_cmd_done)
    rc = linear_client.main(["done", "TER-16"])
    assert rc == 0
    assert calls["pr"] is None


def test_main_dispatches_comment(monkeypatch):
    calls = {}

    def fake_cmd_comment(identifier, body):
        calls["identifier"] = identifier
        calls["body"] = body
        return 0

    monkeypatch.setattr(linear_client, "cmd_comment", fake_cmd_comment)
    rc = linear_client.main(["comment", "TER-14", "PR opened: https://example.com/16"])
    assert rc == 0
    assert calls["identifier"] == "TER-14"
    assert calls["body"] == "PR opened: https://example.com/16"


def test_main_dispatches_create_with_defaults(monkeypatch):
    calls = {}

    def fake_cmd_create(title, description, priority):
        calls["title"] = title
        calls["description"] = description
        calls["priority"] = priority
        return 0

    monkeypatch.setattr(linear_client, "cmd_create", fake_cmd_create)
    rc = linear_client.main(["create", "--title", "New issue"])
    assert rc == 0
    assert calls["title"] == "New issue"
    assert calls["description"] == ""
    assert calls["priority"] == 0


def test_main_dispatches_create_with_all_args(monkeypatch):
    calls = {}

    def fake_cmd_create(title, description, priority):
        calls["title"] = title
        calls["description"] = description
        calls["priority"] = priority
        return 0

    monkeypatch.setattr(linear_client, "cmd_create", fake_cmd_create)
    rc = linear_client.main(
        ["create", "--title", "New issue", "--description", "details here", "--priority", "2"]
    )
    assert rc == 0
    assert calls["title"] == "New issue"
    assert calls["description"] == "details here"
    assert calls["priority"] == 2


def test_main_requires_a_subcommand():
    with pytest.raises(SystemExit):
        linear_client.main([])


def test_main_rejects_unknown_subcommand():
    with pytest.raises(SystemExit):
        linear_client.main(["frobnicate", "TER-1"])


def test_main_catches_handler_exception_and_returns_1(monkeypatch):
    def fake_cmd_status(identifier):
        raise RuntimeError("boom")

    monkeypatch.setattr(linear_client, "cmd_status", fake_cmd_status)
    monkeypatch.setattr(linear_client, "capture_exception", lambda exc: None)
    rc = linear_client.main(["status", "TER-14"])
    assert rc == 1