"""Tests for the observatory dispatch entry point: endpoint parsing and
the free-only policy gate."""
import pytest

from deepcli.observatory.dispatch import (
    assert_free_only, failure_annotations, parse_endpoint)


def test_parse_endpoint_splits_on_first_colon():
    assert parse_endpoint("gemini:gemini-2.5-flash") == ("gemini",
                                                          "gemini-2.5-flash")
    assert parse_endpoint("openrouter:meta-llama/x:free") == (
        "openrouter", "meta-llama/x:free")


def test_parse_endpoint_rejects_malformed():
    with pytest.raises(ValueError):
        parse_endpoint("gemini")
    with pytest.raises(ValueError):
        parse_endpoint(":model")


def test_free_only_allows_free_routes():
    assert_free_only([("gemini", "gemini-2.5-flash")],
                     ("openrouter", "openrouter/free"), allow_paid=False)
    assert_free_only([("openrouter", "some/model:free")],
                     ("gemini", "gemini-2.5-flash"), allow_paid=False)


def test_free_only_refuses_paid_openrouter_model():
    with pytest.raises(SystemExit):
        assert_free_only([("gemini", "gemini-2.5-flash")],
                         ("openrouter", "openai/gpt-4o"), allow_paid=False)


def test_free_only_refuses_unlisted_provider():
    with pytest.raises(SystemExit):
        assert_free_only([("anthropic", "claude-x")],
                         ("openrouter", "openrouter/free"), allow_paid=False)


def test_allow_paid_bypasses_gate():
    assert_free_only([("anthropic", "claude-x")],
                     ("openai", "gpt-x"), allow_paid=True)


def test_failure_annotations_cover_failed_stages():
    record = {
        "artifacts": [{"provider": "gemini", "model": "m", "ok": False,
                       "error": "HTTP Error 400: bad\nrequest"}],
        "jevs": [{"ok": False, "rationale": "HTTP Error 401"}],
        "winner": {},
    }
    lines = failure_annotations(record)
    assert len(lines) == 3
    assert all(l.startswith("::error") for l in lines)
    assert "producer failed" in lines[0] and "bad%0Arequest" in lines[0]
    assert "judge failed" in lines[1]
    assert "no winner" in lines[2]


def test_failure_annotations_empty_on_success():
    record = {"artifacts": [{"ok": True}], "jevs": [{"ok": True}],
              "winner": {"provider": "gemini"}}
    assert failure_annotations(record) == []
