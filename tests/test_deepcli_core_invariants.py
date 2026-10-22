"""Offline coverage for deepcli.deepcli.core path-safety + session-key invariants.

Load-bearing pure helpers in deepcli/deepcli/core.py:
  * _cache_path        -- must confine every write under ~/.deepcli/session_store
  * _session_cache_key -- must be collision-resistant over (token, cookie)

No network, no node, no curl_cffi required: we import the module and only
call the pure helpers. Bootstrap is checkout-relative (matches iteration
45-58 convention) so the suite runs from any CWD.
"""

import importlib
import os
import sys
from pathlib import Path

import pytest

# --- checkout-relative sys.path bootstrap ---------------------------------
_ROOT = Path(__file__).resolve().parents[1]
_DEEPCLI = _ROOT / "deepcli"
if str(_DEEPCLI) not in sys.path:
    sys.path.insert(0, str(_DEEPCLI))

core = importlib.import_module("deepcli.core")


def test_session_cache_key_is_stable_and_hex():
    k1 = core._session_cache_key("tok-abc", None)
    k2 = core._session_cache_key("tok-abc", None)
    assert k1 == k2
    assert len(k1) == 64
    int(k1, 16)


def test_session_cache_key_distinguishes_token_and_cookie():
    a = core._session_cache_key("tok", None)
    b = core._session_cache_key("tok", "ds_session_id=x")
    c = core._session_cache_key("tok2", None)
    assert a != b
    assert a != c


def test_session_cache_key_null_separator_avoids_concat_collision():
    assert core._session_cache_key("ab", "c") != core._session_cache_key("a", "bc")


def test_cache_path_is_under_session_store(tmp_path, monkeypatch):
    base = tmp_path / ".deepcli" / "session_store"
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda p: str(base) if p == "~/.deepcli/session_store" else p,
    )
    p = core._cache_path("sess-1")
    assert p.startswith(str(base))
    assert p.endswith("sess-1.json")


def test_cache_path_rejects_traversal_account(tmp_path, monkeypatch):
    base = tmp_path / "session_store"
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda p: str(base) if p == "~/.deepcli/session_store" else p,
    )
    for bad in ["..", "../evil", "/etc", "a\\b"]:
        with pytest.raises(ValueError):
            core._cache_path("sess-1", account=bad)


def test_cache_path_rejects_traversal_session_id(tmp_path, monkeypatch):
    base = tmp_path / "session_store"
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda p: str(base) if p == "~/.deepcli/session_store" else p,
    )
    for bad in ["..", "../evil", "/etc/passwd", "a\\b"]:
        with pytest.raises(ValueError):
            core._cache_path(bad)


def test_cache_path_sanitizes_weird_chars(tmp_path, monkeypatch):
    base = tmp_path / "session_store"
    monkeypatch.setattr(
        os.path,
        "expanduser",
        lambda p: str(base) if p == "~/.deepcli/session_store" else p,
    )
    p = core._cache_path("a b/c:d*e")
    assert os.path.basename(p) == "a_b_c_d_e.json"
    assert os.path.dirname(p).startswith(str(base))
