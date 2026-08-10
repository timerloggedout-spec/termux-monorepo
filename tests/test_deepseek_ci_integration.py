import os
import json
import time
import tempfile
import shutil
from pathlib import Path
import pytest

import sys
from pathlib import Path
# Insert deepcli package directory directly to bypass package __init__ execution
sys.path.insert(0, str(Path(__file__).parent.parent / "deepcli" / "deepcli"))

from router import score_provider, select_peer
from session_manager import ensure_session

def test_score_provider():
    # Test router scoring based on API keys
    assert score_provider('openrouter', {}) == 999
    assert score_provider('openrouter', {'OPENROUTER_API_KEY': 'test_key'}) == 10

    assert score_provider('omni', {}) == 999
    assert score_provider('omni', {'OMNI_API_KEY': 'test_key'}) == 15

    assert score_provider('deepseek', {}) == 20
    assert score_provider('invalid', {}) == 999

def test_select_peer():
    # Test routing with OpenRouter
    env = {'OPENROUTER_API_KEY': 'open_key'}
    peer = select_peer({}, env=env)
    assert peer['provider'] == 'openrouter'
    assert peer['endpoint'] == 'https://openrouter.ai/api/v1/chat/completions'
    assert peer['api_key'] == 'open_key'

    # Test routing with Omni
    env = {'OMNI_API_KEY': 'omni_key'}
    peer = select_peer({}, env=env)
    assert peer['provider'] == 'omni'
    assert peer['endpoint'] == 'https://api.omni.ai/v1/chat/completions'
    assert peer['api_key'] == 'omni_key'

    # Test routing with Omni Custom Endpoint
    env = {'OMNI_API_KEY': 'omni_key', 'OMNI_BASE_URL': 'https://custom.omni.ai'}
    peer = select_peer({}, env=env)
    assert peer['provider'] == 'omni'
    assert peer['endpoint'] == 'https://custom.omni.ai'

    # Test routing default to deepseek web wrapper if no keys exist
    peer = select_peer({}, env={})
    assert peer['provider'] == 'deepseek'
    assert peer['endpoint'] is None

def test_session_manager_permissions(monkeypatch):
    # Mock get_new_session to return a mock dictionary so we run offline/locally
    monkeypatch.setattr(
        "session_manager.get_new_session",
        lambda *args, **kwargs: {
            'cookies': {'foo': 'bar'},
            'headers': {'baz': 'qux'},
            'token': 'mock_token_123',
            'expires': time.time() + 3600,
        }
    )

    # Create a secure temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        cache_dir = Path(temp_dir) / 'cache'

        # Call ensure_session which should create cache_dir with 0o700
        # and session.json with 0o600
        session = ensure_session(cache_dir=str(cache_dir))

        assert session is not None
        assert 'token' in session
        assert session['token'] == 'mock_token_123'

        # Verify Directory Permission (must be 0o700)
        dir_stat = os.stat(cache_dir)
        # We mask with 0o777 to get permission bits
        assert (dir_stat.st_mode & 0o777) == 0o700

        # Verify File Permission (must be 0o600)
        session_file = cache_dir / 'session.json'
        assert session_file.exists()
        file_stat = os.stat(session_file)
        assert (file_stat.st_mode & 0o777) == 0o600

    finally:
        shutil.rmtree(temp_dir)
