#!/usr/bin/env python3
"""File utilities for the CLI."""
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Union
from rich.console import Console

console = Console()

class FileUtils:
    """Utilities for file operations."""
    
    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read file content."""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]File not found: {file_path}[/]")
            return None
        
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding='latin-1')
            except Exception as e:
                console.print(f"[red]Failed to read {file_path}: {e}[/]")
                return None
    
    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Write content to file."""
        path = Path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)
            return True
        except Exception as e:
            console.print(f"[red]Failed to write {file_path}: {e}[/]")
            return False
    
    @staticmethod
    def read_json(file_path: str) -> Optional[Dict]:
        """Read JSON file."""
        content = FileUtils.read_file(file_path)
        if content is None:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in {file_path}: {e}[/]")
            return None
    
    @staticmethod
    def write_json(file_path: str, data: Dict, indent: int = 2) -> bool:
        """Write JSON to file."""
        try:
            content = json.dumps(data, indent=indent)
            return FileUtils.write_file(file_path, content)
        except Exception as e:
            console.print(f"[red]Failed to write JSON to {file_path}: {e}[/]")
            return False
    
    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """Copy file from src to dst."""
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            console.print(f"[red]Failed to copy {src} to {dst}: {e}[/]")
            return False
    
    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """Move file from src to dst."""
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            return True
        except Exception as e:
            console.print(f"[red]Failed to move {src} to {dst}: {e}[/]")
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file."""
        path = Path(file_path)
        if not path.exists():
            console.print(f"[yellow]File not found: {file_path}[/]")
            return True
        try:
            path.unlink()
            return True
        except Exception as e:
            console.print(f"[red]Failed to delete {file_path}: {e}[/]")
            return False
    
    @staticmethod
    def list_files(directory: str, recursive: bool = False, patterns: List[str] = None) -> List[str]:
        """List files in directory."""
        path = Path(directory)
        if not path.exists():
            console.print(f"[red]Directory not found: {directory}[/]")
            return []
        
        files = []
        
        if recursive:
            for file in path.rglob('*'):
                if file.is_file():
                    if patterns is None or any(file.name.endswith(p) for p in patterns):
                        files.append(str(file))
        else:
            for file in path.iterdir():
                if file.is_file():
                    if patterns is None or any(file.name.endswith(p) for p in patterns):
                        files.append(str(file))
        
        return files
    
    @staticmethod
    def find_files(directory: str, name: str = None, patterns: List[str] = None) -> List[str]:
        """Find files matching criteria."""
        path = Path(directory)
        if not path.exists():
            return []
        
        files = []
        for file in path.rglob('*'):
            if file.is_file():
                if name and file.name == name:
                    files.append(str(file))
                elif patterns and any(file.name.endswith(p) for p in patterns):
                    files.append(str(file))
        
        return files
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[Dict]:
        """Get file information."""
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            stat = path.stat()
            return {
                "path": str(path),
                "name": path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "extension": path.suffix,
            }
        except Exception as e:
            console.print(f"[red]Failed to get info for {file_path}: {e}[/]")
            return None
    
    @staticmethod
    def create_directory(path: str) -> bool:
        """Create directory (and parents if needed)."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            console.print(f"[red]Failed to create directory {path}: {e}[/]")
            return False
    
    @staticmethod
    def remove_directory(path: str) -> bool:
        """Remove directory and its contents."""
        try:
            shutil.rmtree(path)
            return True
        except Exception as e:
            console.print(f"[red]Failed to remove directory {path}: {e}[/]")
            return False
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """Calculate file hash."""
        import hashlib
        
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            hasher = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            console.print(f"[red]Failed to calculate hash for {file_path}: {e}[/]")
            return None
    
    @staticmethod
    def compare_files(file1: str, file2: str) -> bool:
        """Compare two files for equality."""
        content1 = FileUtils.read_file(file1)
        content2 = FileUtils.read_file(file2)
        
        if content1 is None or content2 is None:
            return False
        
        return content1 == content2

if __name__ == "__main__":
    # Example usage
    utils = FileUtils()
    
    # Test file operations
    test_file = "/tmp/test_file.txt"
    FileUtils.write_file(test_file, "Hello, World!")
    content = FileUtils.read_file(test_file)
    print(f"Read: {content}")
    
    # Test JSON
    test_json = "/tmp/test.json"
    FileUtils.write_json(test_json, {"key": "value"})
    data = FileUtils.read_json(test_json)
    print(f"JSON: {data}")
    
    # Cleanup
    FileUtils.delete_file(test_file)
    FileUtils.delete_file(test_json)
