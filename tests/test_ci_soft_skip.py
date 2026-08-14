import pytest
import sys
from pathlib import Path

# Namespace hygiene: Temporarily remove deepcli nested path to import the outer package,
# then restore sys.path and clear the deepcli sys.modules cache so other tests
# (like test_sentinel_privileges) can load the inner deepcli subpackage cleanly.
original_path = sys.path.copy()
deepcli_dir = str(Path(__file__).resolve().parent.parent / "deepcli")
while deepcli_dir in sys.path:
    sys.path.remove(deepcli_dir)

try:
    from deepcli.ci_agent import is_soft_skippable_error
    from deepcli.ci_mode import sanitize_error_msg
finally:
    sys.path = original_path
    if "deepcli" in sys.modules:
        del sys.modules["deepcli"]

def test_is_soft_skippable_error():
    # Authentication errors should be skippable
    assert is_soft_skippable_error(RuntimeError("Authorization Failed (invalid token)")) is True
    assert is_soft_skippable_error(RuntimeError("code=40003 msg='invalid token'")) is True
    assert is_soft_skippable_error(RuntimeError("HTTP 401: Unauthorized")) is True
    assert is_soft_skippable_error(RuntimeError("HTTP 403: Forbidden")) is True

    # Connection/timeout errors should be skippable
    assert is_soft_skippable_error(ConnectionError("Max retries exceeded with url")) is True
    assert is_soft_skippable_error(TimeoutError("Connection timed out")) is True
    assert is_soft_skippable_error(RuntimeError("Failed to resolve host")) is True

    # Internal code bugs / empty SSE streams / other things should NOT be skippable
    assert is_soft_skippable_error(KeyError("missing some key")) is False
    assert is_soft_skippable_error(RuntimeError("Empty SSE stream")) is False
    assert is_soft_skippable_error(ValueError("Invalid payload syntax")) is False

def test_sanitize_error_msg():
    # Sanitizer prevents credential leaking
    auth_sanitized = sanitize_error_msg("Authorization Failed: secret_token_abc123")
    assert "secret_token_abc123" not in auth_sanitized
    assert "Authentication failure" in auth_sanitized

    conn_sanitized = sanitize_error_msg("Failed to resolve host chat.deepseek.com")
    assert "Network connection failure" in conn_sanitized

    generic_err = sanitize_error_msg("Unknown error: some random crash")
    assert "Unknown error" in generic_err
