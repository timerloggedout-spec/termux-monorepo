#!/usr/bin/env python3
"""File Harvester - Harvest code from files and directories.

This module provides functionality to:
- Recursively scan directories for source files
- Filter files by extension, size, or content
- Extract code with metadata (path, language, size, etc.)
- Handle various file encodings
- Generate file fingerprints for deduplication
"""

import os
import sys
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Set, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing


@dataclass
class HarvestedFile:
    """Represents a harvested file with metadata."""
    path: str
    relative_path: str
    content: str
    encoding: str = "utf-8"
    language: Optional[str] = None
    size: int = 0
    mtime: float = 0.0
    sha256: str = ""
    line_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "relative_path": self.relative_path,
            "content": self.content,
            "encoding": self.encoding,
            "language": self.language,
            "size": self.size,
            "mtime": self.mtime,
            "sha256": self.sha256,
            "line_count": self.line_count,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class FileHarvester:
    """Harvest code from files and directories.
    
    This harvester provides efficient file scanning and code extraction
    with support for filtering, parallel processing, and deduplication.
    """
    
    # Common source file extensions
    SOURCE_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".ps1": "powershell",
        ".lua": "lua",
        ".pl": "perl",
        ".r": "r",
        ".jl": "julia",
        ".f": "fortran",
        ".f90": "fortran",
        ".f95": "fortran",
    }
    
    # Text file extensions
    TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".markdown",
        ".rst",
        ".text",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".csv",
        ".tsv",
        ".xml",
        ".html",
        ".htm",
        ".css",
        ".sql",
    }
    
    # Binary file signatures
    BINARY_SIGNATURES = [
        b"\x00",
        b"\xFF\xD8\xFF",  # JPEG
        b"\x89PNG",  # PNG
        b"GIF8",  # GIF
        b"PK\x03\x04",  # ZIP
        b"\x50K\x03\x04",  # ZIP (alternative)
        b"Rar!",  # RAR
        b"\x1F\x8B",  # GZIP
        b"\xFD\x37\x7A\x58\x5A\x00",  # XZ
        b"\x7FELF",  # ELF binary
        b"\x4D\x5A",  # Windows EXE
        b"\xCA\xFE\xBA\xBE",  # Mach-O binary
    ]
    
    def __init__(
        self,
        base_path: Optional[Union[str, Path]] = None,
        extensions: Optional[Set[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        exclude_dirs: Optional[Set[str]] = None,
        max_size: int = 10 * 1024 * 1024,  # 10MB
        min_size: int = 0,
        max_line_length: int = 10000,
        include_binary: bool = False,
        num_workers: int = 4,
        **kwargs
    ):
        """Initialize file harvester.
        
        Args:
            base_path: Base path to harvest from (default: current directory)
            extensions: File extensions to include (None = all known)
            exclude_patterns: Filename patterns to exclude
            exclude_dirs: Directory names to exclude
            max_size: Maximum file size to harvest (bytes)
            min_size: Minimum file size to harvest (bytes)
            max_line_length: Maximum line length (longer lines truncated)
            include_binary: Whether to include binary files
            num_workers: Number of parallel workers for harvesting
        """
        self.base_path = Path(base_path or ".").resolve()
        self.extensions = extensions or set(self.SOURCE_EXTENSIONS.keys()) | self.TEXT_EXTENSIONS
        self.exclude_patterns = exclude_patterns or []
        self.exclude_dirs = exclude_dirs or {
            ".git",
            ".svn",
            ".hg",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".tox",
            ".nox",
            ".eggs",
            "*egg-info",
            ".venv",
            "venv",
            "env",
            ".env",
            "node_modules",
            "bower_components",
            "dist",
            "build",
            "target",
            "bin",
            "obj",
            ".vs",
            ".vscode",
            ".idea",
            ".settings",
            "logs",
            "log",
            "tmp",
            "temp",
        }
        self.max_size = max_size
        self.min_size = min_size
        self.max_line_length = max_line_length
        self.include_binary = include_binary
        self.num_workers = min(num_workers, os.cpu_count() or 4)
        self._cpu_count = os.cpu_count() or 4
    
    def _should_exclude_dir(self, dir_name: str) -> bool:
        """Check if directory should be excluded."""
        for pattern in self.exclude_dirs:
            if pattern == dir_name:
                return True
            if pattern.startswith("*") and dir_name.endswith(pattern[1:]):
                return True
            if pattern.endswith("*") and dir_name.startswith(pattern[:-1]):
                return True
        return False
    
    def _should_exclude_file(self, filename: str) -> bool:
        """Check if file should be excluded based on patterns."""
        for pattern in self.exclude_patterns:
            if pattern in filename:
                return True
        return False
    
    def _should_harvest_file(self, path: Path) -> bool:
        """Check if a file should be harvested."""
        # Check extension
        if self.extensions:
            suffix = path.suffix.lower()
            if suffix not in self.extensions:
                return False
        
        # Check size
        try:
            size = path.stat().st_size
            if size < self.min_size or size > self.max_size:
                return False
        except OSError:
            return False
        
        # Check exclude patterns
        if self._should_exclude_file(path.name):
            return False
        
        return True
    
    def _is_binary(self, path: Path) -> bool:
        """Check if a file is binary."""
        if self.include_binary:
            return False
        
        try:
            with open(path, "rb") as f:
                # Check for null bytes in first 1024 bytes
                header = f.read(1024)
                if b"\x00" in header:
                    return True
                
                # Check against known binary signatures
                for sig in self.BINARY_SIGNATURES:
                    if header.startswith(sig):
                        return True
                
                # Try to decode as text
                try:
                    header.decode("utf-8")
                    header.decode("latin-1")
                except UnicodeDecodeError:
                    return True
                
                return False
        except Exception:
            return True
    
    def _detect_encoding(self, path: Path) -> str:
        """Detect file encoding."""
        encodings = ["utf-8", "utf-16", "latin-1", "ascii"]
        
        try:
            with open(path, "rb") as f:
                content = f.read(4096)
                
                for enc in encodings:
                    try:
                        content.decode(enc)
                        return enc
                    except UnicodeDecodeError:
                        continue
                
                return "latin-1"  # Fallback
        except Exception:
            return "utf-8"
    
    def _detect_language(self, path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        suffix = path.suffix.lower()
        return self.SOURCE_EXTENSIONS.get(suffix)
    
    def _compute_sha256(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()
    
    def _read_file(self, path: Path) -> Optional[HarvestedFile]:
        """Read and process a single file."""
        try:
            # Check if file should be harvested
            if not self._should_harvest_file(path):
                return None
            
            # Check if binary
            if self._is_binary(path):
                return None
            
            # Detect encoding
            encoding = self._detect_encoding(path)
            
            # Read file content
            with open(path, "r", encoding=encoding, errors="replace") as f:
                content = f.read()
            
            # Truncate long lines
            lines = content.splitlines()
            truncated_lines = []
            for line in lines:
                if len(line) > self.max_line_length:
                    truncated_lines.append(line[:self.max_line_length] + "... [TRUNCATED]")
                else:
                    truncated_lines.append(line)
            content = "\n".join(truncated_lines)
            
            # Get file metadata
            stat = path.stat()
            relative_path = str(path.relative_to(self.base_path))
            
            # Compute hash
            sha256 = self._compute_sha256(content)
            
            return HarvestedFile(
                path=str(path),
                relative_path=relative_path,
                content=content,
                encoding=encoding,
                language=self._detect_language(path),
                size=stat.st_size,
                mtime=stat.st_mtime,
                sha256=sha256,
                line_count=len(lines),
                metadata={
                    "mode": stat.st_mode,
                    "uid": stat.st_uid,
                    "gid": stat.st_gid,
                }
            )
        except Exception as e:
            # Log error but continue
            print(f"Error reading {path}: {e}", file=sys.stderr)
            return None
    
    def _scan_directory(self, path: Path) -> Generator[Path, None, None]:
        """Recursively scan directory for files."""
        if self._should_exclude_dir(path.name):
            return
        
        if path.is_file():
            yield path
        elif path.is_dir():
            for entry in path.iterdir():
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    yield from self._scan_directory(entry)
                elif entry.is_file():
                    yield entry
    
    def harvest(
        self,
        paths: Optional[List[Union[str, Path]]] = None,
        parallel: bool = True,
    ) -> Generator[HarvestedFile, None, None]:
        """Harvest files from specified paths.
        
        Args:
            paths: List of paths to harvest (default: base_path)
            parallel: Whether to use parallel processing
            
        Yields:
            HarvestedFile objects
        """
        if paths is None:
            paths = [self.base_path]
        
        # Collect all files to process
        all_files = []
        for path in paths:
            p = Path(path).resolve()
            if p.is_file():
                if self._should_harvest_file(p):
                    all_files.append(p)
            elif p.is_dir():
                for f in self._scan_directory(p):
                    if self._should_harvest_file(f):
                        all_files.append(f)
        
        # Process files
        if parallel and len(all_files) > 10 and self.num_workers > 1:
            yield from self._harvest_parallel(all_files)
        else:
            yield from self._harvest_sequential(all_files)
    
    def _harvest_sequential(self, files: List[Path]) -> Generator[HarvestedFile, None, None]:
        """Harvest files sequentially."""
        for f in files:
            result = self._read_file(f)
            if result:
                yield result
    
    def _harvest_parallel(self, files: List[Path]) -> Generator[HarvestedFile, None, None]:
        """Harvest files in parallel."""
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._read_file, f): f for f in files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    yield result
    
    def harvest_to_list(
        self,
        paths: Optional[List[Union[str, Path]]] = None,
        parallel: bool = True,
    ) -> List[HarvestedFile]:
        """Harvest files and return as list.
        
        Args:
            paths: List of paths to harvest
            parallel: Whether to use parallel processing
            
        Returns:
            List of HarvestedFile objects
        """
        return list(self.harvest(paths, parallel))
    
    def harvest_to_dict(
        self,
        paths: Optional[List[Union[str, Path]]] = None,
        parallel: bool = True,
    ) -> Dict[str, HarvestedFile]:
        """Harvest files and return as dictionary keyed by relative path.
        
        Args:
            paths: List of paths to harvest
            parallel: Whether to use parallel processing
            
        Returns:
            Dictionary of HarvestedFile objects
        """
        return {f.relative_path: f for f in self.harvest(paths, parallel)}
    
    def harvest_to_json(
        self,
        paths: Optional[List[Union[str, Path]]] = None,
        output_path: Optional[Union[str, Path]] = None,
        parallel: bool = True,
    ) -> str:
        """Harvest files and return as JSON.
        
        Args:
            paths: List of paths to harvest
            output_path: Path to save JSON (optional)
            parallel: Whether to use parallel processing
            
        Returns:
            JSON string
        """
        files = self.harvest_to_list(paths, parallel)
        data = [f.to_dict() for f in files]
        json_str = json.dumps(data, indent=2)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding="utf-8")
        
        return json_str
    
    def count_files(
        self,
        paths: Optional[List[Union[str, Path]]] = None,
    ) -> int:
        """Count files that would be harvested.
        
        Args:
            paths: List of paths to count
            
        Returns:
            Number of files
        """
        if paths is None:
            paths = [self.base_path]
        
        count = 0
        for path in paths:
            p = Path(path).resolve()
            if p.is_file():
                if self._should_harvest_file(p):
                    count += 1
            elif p.is_dir():
                for f in self._scan_directory(p):
                    if self._should_harvest_file(f):
                        count += 1
        return count


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "FileHarvester",
    "HarvestedFile",
]
