#!/usr/bin/env python3
"""Tests for tools module."""
import pytest
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.file_utils import FileUtils
from tools.git_utils import GitUtils
from tools.network_utils import NetworkUtils


class TestFileUtils:
    """Test file utilities."""
    
    def test_read_write_file(self):
        """Test reading and writing files."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_content = "Hello, World!"
            f.write(test_content)
            file_path = f.name
        
        try:
            # Test read
            content = FileUtils.read_file(file_path)
            assert content == test_content
            
            # Test write
            new_content = "New content"
            assert FileUtils.write_file(file_path, new_content)
            
            # Verify write
            content = FileUtils.read_file(file_path)
            assert content == new_content
        finally:
            os.unlink(file_path)
    
    def test_read_write_json(self):
        """Test reading and writing JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {"key": "value", "number": 42}
            json.dump(test_data, f)
            file_path = f.name
        
        try:
            # Test read
            data = FileUtils.read_json(file_path)
            assert data == test_data
            
            # Test write
            new_data = {"new_key": "new_value"}
            assert FileUtils.write_json(file_path, new_data)
            
            # Verify write
            data = FileUtils.read_json(file_path)
            assert data == new_data
        finally:
            os.unlink(file_path)
    
    def test_list_files(self):
        """Test listing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            file1 = Path(tmpdir) / "file1.txt"
            file2 = Path(tmpdir) / "file2.py"
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            file3 = subdir / "file3.js"
            
            file1.write_text("content1")
            file2.write_text("content2")
            file3.write_text("content3")
            
            # Test non-recursive
            files = FileUtils.list_files(tmpdir, recursive=False)
            assert len(files) == 2
            
            # Test recursive
            files = FileUtils.list_files(tmpdir, recursive=True)
            assert len(files) == 3
            
            # Test with patterns
            files = FileUtils.list_files(tmpdir, recursive=True, patterns=[".py"])
            assert len(files) == 1
            assert files[0].endswith(".py")
    
    def test_file_info(self):
        """Test getting file information."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            file_path = f.name
        
        try:
            info = FileUtils.get_file_info(file_path)
            assert info is not None
            assert info["path"] == file_path
            assert info["size"] == 12  # Length of "test content"
            assert info["is_file"] is True
        finally:
            os.unlink(file_path)
    
    def test_create_remove_directory(self):
        """Test creating and removing directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_dir"
            
            # Test create
            assert FileUtils.create_directory(str(test_dir))
            assert test_dir.exists()
            
            # Test remove
            assert FileUtils.remove_directory(str(test_dir))
            assert not test_dir.exists()


class TestGitUtils:
    """Test Git utilities."""
    
    def test_is_git_repo(self):
        """Test checking if directory is a Git repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Not a git repo
            assert not GitUtils.is_git_repo(tmpdir)
            
            # Initialize git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            
            # Now it should be a git repo
            assert GitUtils.is_git_repo(tmpdir)
    
    def test_get_git_root(self):
        """Test getting Git root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            
            root = GitUtils.get_git_root(tmpdir)
            assert root == tmpdir
    
    def test_get_current_branch(self):
        """Test getting current branch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, capture_output=True)
            
            # Default branch is usually main or master
            branch = GitUtils.get_current_branch(tmpdir)
            assert branch in ["main", "master"]


class TestNetworkUtils:
    """Test network utilities."""
    
    def test_network_utils_initialization(self):
        """Test NetworkUtils initialization."""
        net = NetworkUtils()
        assert net.session is not None
    
    def test_set_headers(self):
        """Test setting headers."""
        net = NetworkUtils()
        net.set_header("X-Test-Header", "test-value")
        assert "X-Test-Header" in net.session.headers
        assert net.session.headers["X-Test-Header"] == "test-value"
    
    def test_clear_headers(self):
        """Test clearing headers."""
        net = NetworkUtils()
        net.set_header("X-Test-Header", "test-value")
        net.clear_headers()
        # After clear, default headers should be restored
        assert "User-Agent" in net.session.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
