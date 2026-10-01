#!/usr/bin/env python3
"""Pattern Searcher - Search using regex and string patterns.

This module provides functionality to:
- Search using regular expressions
- Search using glob patterns
- Search using custom patterns
- Replace patterns
- Validate patterns
"""

import os
import sys
import json
import re
import fnmatch
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from tools.search.code_searcher import SearchResult


@dataclass
class PatternSearchResult(SearchResult):
    """Represents a pattern search result."""
    pattern: str
    groups: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "pattern": self.pattern,
            "groups": self.groups,
        })
        return result


class PatternSearcher:
    """Search using patterns.
    
    This searcher provides:
    - Regex search
    - Glob pattern search
    - Custom pattern search
    - Pattern replacement
    - Pattern validation
    """
    
    # Common patterns
    COMMON_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "url": r"https?://[^\s]+",
        "phone": r"\+?[0-9\s\-\(\)]{10,}",
        "date": r"\d{4}-\d{2}-\d{2}",
        "time": r"\d{1,2}:\d{2}(:\d{2})?",
        "uuid": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        "ip": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        "number": r"-?\d+\.?\d*",
    }
    
    # Code patterns
    CODE_PATTERNS = {
        "function": r"def\s+(\w+)\s*\([^)]*\)\s*:",
        "class": r"class\s+(\w+)\s*:",
        "import": r"^(import|from)\s+[^\s]+",
        "comment": r"#\s*(.+)$",
        "string": r'"[^"]*"|\'[^\']*\'',
    }
    
    def __init__(
        self,
        patterns: Optional[Dict[str, str]] = None,
        case_sensitive: bool = False,
        multiline: bool = True,
        dotall: bool = True,
        num_workers: int = 4,
        **kwargs
    ):
        """Initialize pattern searcher.
        
        Args:
            patterns: Custom patterns to use
            case_sensitive: Whether patterns are case-sensitive
            multiline: Whether to use multiline matching
            dotall: Whether . matches newline
            num_workers: Number of parallel workers
        """
        self.patterns = patterns or {}
        self.case_sensitive = case_sensitive
        self.multiline = multiline
        self.dotall = dotall
        self.num_workers = num_workers
        self._compiled_patterns = {}
    
    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """Compile a regex pattern.
        
        Args:
            pattern: Regex pattern string
            
        Returns:
            Compiled regex pattern
        """
        flags = 0
        if not self.case_sensitive:
            flags |= re.IGNORECASE
        if self.multiline:
            flags |= re.MULTILINE
        if self.dotall:
            flags |= re.DOTALL
        
        return re.compile(pattern, flags)
    
    def _get_compiled_pattern(self, pattern: str) -> re.Pattern:
        """Get compiled pattern, compiling if necessary.
        
        Args:
            pattern: Pattern string
            
        Returns:
            Compiled pattern
        """
        if pattern not in self._compiled_patterns:
            self._compiled_patterns[pattern] = self._compile_pattern(pattern)
        return self._compiled_patterns[pattern]
    
    def search(
        self,
        pattern: str,
        text: str,
        group_names: Optional[List[str]] = None,
    ) -> List[PatternSearchResult]:
        """Search for pattern in text.
        
        Args:
            pattern: Pattern to search for
            text: Text to search in
            group_names: Names for capture groups
            
        Returns:
            List of PatternSearchResult objects
        """
        # Check if pattern is a named pattern
        if pattern in self.patterns:
            pattern = self.patterns[pattern]
        elif pattern in self.COMMON_PATTERNS:
            pattern = self.COMMON_PATTERNS[pattern]
        elif pattern in self.CODE_PATTERNS:
            pattern = self.CODE_PATTERNS[pattern]
        
        # Compile pattern
        compiled = self._get_compiled_pattern(pattern)
        
        # Find all matches
        results = []
        for match in compiled.finditer(text):
            groups = {}
            if group_names:
                for i, name in enumerate(group_names):
                    if i < len(match.groups()):
                        groups[name] = match.group(i + 1)
            else:
                for i, group in enumerate(match.groups()):
                    groups[f"group_{i}"] = group
            
            # Count newlines before match to get line number
            line = text[:match.start()].count("\n") + 1
            
            # Get line content
            lines = text.splitlines()
            line_content = lines[line - 1] if line <= len(lines) else ""
            
            # Get context
            start = max(0, line - 3)
            end = min(len(lines), line + 2)
            context = lines[start:end]
            
            results.append(PatternSearchResult(
                file="",
                path="",
                line_number=line,
                line=line_content,
                context=context,
                score=1.0,
                pattern=pattern,
                groups=groups,
                metadata={
                    "start": match.start(),
                    "end": match.end(),
                    "all_groups": match.groups(),
                }
            ))
        
        return results
    
    def search_files(
        self,
        pattern: str,
        paths: List[Union[str, Path]],
        group_names: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[PatternSearchResult]:
        """Search for pattern in files.
        
        Args:
            pattern: Pattern to search for
            paths: List of file paths to search
            group_names: Names for capture groups
            limit: Maximum number of results
            
        Returns:
            List of PatternSearchResult objects
        """
        results = []
        
        for path in paths:
            p = Path(path)
            if p.is_file():
                file_results = self._search_file(p, pattern, group_names)
                results.extend(file_results)
                
                if len(results) >= limit:
                    break
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file():
                        file_results = self._search_file(f, pattern, group_names)
                        results.extend(file_results)
                        
                        if len(results) >= limit:
                            break
        
        return results[:limit]
    
    def _search_file(
        self,
        path: Path,
        pattern: str,
        group_names: Optional[List[str]] = None,
    ) -> List[PatternSearchResult]:
        """Search for pattern in a single file.
        
        Args:
            path: File path
            pattern: Pattern to search for
            group_names: Names for capture groups
            
        Returns:
            List of PatternSearchResult objects
        """
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            
            # Adjust pattern for file search
            file_patterns = []
            if pattern in self.patterns:
                file_patterns.append(self.patterns[pattern])
            elif pattern in self.COMMON_PATTERNS:
                file_patterns.append(self.COMMON_PATTERNS[pattern])
            elif pattern in self.CODE_PATTERNS:
                file_patterns.append(self.CODE_PATTERNS[pattern])
            else:
                file_patterns.append(pattern)
            
            results = []
            for p in file_patterns:
                file_results = self.search(p, content, group_names)
                for r in file_results:
                    r.file = path.name
                    r.path = str(path)
                results.extend(file_results)
            
            return results
        except Exception:
            return []
    
    def glob_search(
        self,
        pattern: str,
        paths: List[Union[str, Path]],
        limit: int = 100,
    ) -> List[Path]:
        """Search using glob pattern.
        
        Args:
            pattern: Glob pattern
            paths: List of paths to search in
            limit: Maximum number of results
            
        Returns:
            List of matching Path objects
        """
        results = []
        
        for path in paths:
            p = Path(path)
            if p.is_dir():
                for match in p.glob(pattern):
                    results.append(match)
                    if len(results) >= limit:
                        break
            elif p.match(pattern):
                results.append(p)
        
        return results[:limit]
    
    def replace(
        self,
        pattern: str,
        replacement: str,
        text: str,
        count: int = 0,
    ) -> Tuple[str, int]:
        """Replace pattern in text.
        
        Args:
            pattern: Pattern to replace
            replacement: Replacement text
            text: Text to modify
            count: Maximum number of replacements (0 = all)
            
        Returns:
            Tuple of (modified text, number of replacements)
        """
        # Check if pattern is a named pattern
        if pattern in self.patterns:
            pattern = self.patterns[pattern]
        elif pattern in self.COMMON_PATTERNS:
            pattern = self.COMMON_PATTERNS[pattern]
        elif pattern in self.CODE_PATTERNS:
            pattern = self.CODE_PATTERNS[pattern]
        
        compiled = self._get_compiled_pattern(pattern)
        
        new_text, replacements = compiled.subn(replacement, text, count=count)
        
        return new_text, replacements
    
    def validate_pattern(self, pattern: str) -> bool:
        """Validate a regex pattern.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            True if pattern is valid
        """
        try:
            self._compile_pattern(pattern)
            return True
        except re.error:
            return False
    
    def search_to_dict(
        self,
        pattern: str,
        text: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search and return results as dictionaries.
        
        Args:
            pattern: Pattern to search for
            text: Text to search in
            **kwargs: Search options
            
        Returns:
            List of result dictionaries
        """
        results = self.search(pattern, text, **kwargs)
        return [r.to_dict() for r in results]
    
    def search_to_json(
        self,
        pattern: str,
        text: str,
        **kwargs
    ) -> str:
        """Search and return results as JSON.
        
        Args:
            pattern: Pattern to search for
            text: Text to search in
            **kwargs: Search options
            
        Returns:
            JSON string
        """
        return json.dumps(self.search_to_dict(pattern, text, **kwargs), indent=2)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "PatternSearcher",
    "PatternSearchResult",
]
