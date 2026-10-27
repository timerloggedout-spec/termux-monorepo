"""Tests for the observatory dispatch entry point: endpoint parsing and
the free-only policy gate."""
import pytest

from deepcli.observatory.dispatch import assert_free_only, parse_endpoint


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
