#!/usr/bin/env python3
"""Tests for core module."""
import pytest
import os
import tempfile
import json
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.core import MistralCore, load_config, save_config
from core.session_manager import SessionManager
from core.cache import cache_load, cache_save


class TestCore:
    """Test core functionality."""
    
    def test_load_config(self):
        """Test loading configuration."""
        # Create a temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"test_key": "test_value", "token": "test_token"}
            json.dump(config, f)
            config_path = f.name
        
        try:
            # Mock the config file location
            original_config_file = Path(__file__).parent.parent / "core" / "config.json"
            
            # Test with non-existent file
            result = load_config()
            assert isinstance(result, dict)
            
        finally:
            os.unlink(config_path)
    
    def test_save_config(self):
        """Test saving configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily change the config file path
            import core.core as core_module
            original_config_file = core_module.CONFIG_FILE
            core_module.CONFIG_FILE = Path(tmpdir) / "config.json"
            
            try:
                # Save a config
                config = {"test": "value"}
                save_config(config)
                
                # Verify it was saved
                config_file = core_module.CONFIG_FILE
                assert config_file.exists()
                with open(config_file) as f:
                    import json
                    saved_config = json.load(f)
                assert saved_config == config
            finally:
                core_module.CONFIG_FILE = original_config_file
    
    def test_session_manager(self):
        """Test session manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary config
            config_path = Path(tmpdir) / "config.yaml"
            config_content = """
mistral:
  cookie_path: /tmp/mistral_cookies.json
  token_path: /tmp/mistral_token.txt
"""
            config_path.write_text(config_content)
            
            # Create session manager
            manager = SessionManager(str(config_path))
            
            # Test getting config
            cookie_path = manager.get("mistral", "cookie_path")
            assert cookie_path == "/tmp/mistral_cookies.json"
    
    def test_cache_functions(self):
        """Test cache functions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set cache directory
            os.environ["HOME"] = tmpdir
            
            # Test cache save and load
            session_id = "test_session"
            messages = [{"role": "user", "content": "test"}]
            
            cache_save(session_id, messages)
            loaded = cache_load(session_id)
            
            assert loaded == messages


class TestMistralCore:
    """Test MistralCore class."""
    
    def test_initialization(self):
        """Test MistralCore initialization."""
        # This will fail without a token, but we can test the error handling
        with pytest.raises(SystemExit):
            core = MistralCore()
    
    def test_with_mock_token(self):
        """Test with a mock token."""
        # Set a mock token
        os.environ["MISTRALAI_TOKEN"] = "mock_token"
        
        try:
            core = MistralCore()
            assert core.token == "mock_token"
        finally:
            del os.environ["MISTRALAI_TOKEN"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
