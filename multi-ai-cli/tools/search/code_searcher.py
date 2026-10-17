#!/usr/bin/env python3
"""Code Searcher - Search code using various methods.

This module provides functionality to:
- Search code by name
- Search code by content
- Search code by pattern
- Search code by type (function, class, variable)
- Search with regular expressions
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

from tools.harvest.file_harvester import FileHarvester, HarvestedFile
from tools.extraction.code_extractor import CodeExtractor
from tools.extraction.ast_extractor import ASTExtractor


@dataclass
class SearchResult:
    """Represents a search result."""
    file: str
    path: str
    line_number: int
    line: str
    context: List[str]
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "path": self.path,
            "line_number": self.line_number,
            "line": self.line,
            "context": self.context,
            "score": self.score,
            "metadata": self.metadata,
        }


@dataclass
class CodeSearchResult(SearchResult):
    """Represents a code search result."""
    code: str
    language: Optional[str] = None
    function: Optional[str] = None
    class_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "code": self.code,
            "language": self.language,
            "function": self.function,
            "class_name": self.class_name,
        })
        return result


class CodeSearcher:
    """Search code using various methods.
    
    This searcher provides:
    - Full-text search
    - Regex search
    - Symbol search (functions, classes, variables)
    - Type-aware search
    - Context-aware search
    """
    
    def __init__(
        self,
        paths: Optional[List[Union[str, Path]]] = None,
        extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        num_workers: int = 4,
        context_lines: int = 3,
        **kwargs
    ):
        """Initialize code searcher.
        
        Args:
            paths: Paths to search in
            extensions: File extensions to search
            exclude_patterns: Patterns to exclude
            num_workers: Number of parallel workers
            context_lines: Number of context lines to include
        """
        self.paths = paths or [Path.cwd()]
        self.extensions = extensions or [".py", ".js", ".ts", ".java", ".go", ".rs"]
        self.exclude_patterns = exclude_patterns or [".git", "__pycache__", "node_modules"]
        self.num_workers = num_workers
        self.context_lines = context_lines
        
        self._harvester = FileHarvester(
            extensions=set(self.extensions),
            exclude_patterns=self.exclude_patterns,
        )
        self._code_extractor = CodeExtractor()
        self._ast_extractor = ASTExtractor()
        
        # Index for faster searching
        self._index: Dict[str, List[HarvestedFile]] = {}
        self._indexed = False
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        for pattern in self.exclude_patterns:
            if pattern in str(path):
                return True
        return False
    
    def _index_files(self):
        """Index files for faster searching."""
        if self._indexed:
            return
        
        self._index = {}
        
        for path in self.paths:
            p = Path(path)
            if p.is_file():
                if not self._should_exclude(p):
                    files = [p]
            elif p.is_dir():
                files = list(p.rglob("*"))
            else:
                continue
            
            for f in files:
                if f.is_file() and not self._should_exclude(f):
                    if f.suffix in self.extensions:
                        try:
                            content = f.read_text(encoding="utf-8", errors="replace")
                            file = HarvestedFile(
                                path=str(f),
                                relative_path=str(f.relative_to(p)),
                                content=content,
                                language=self._code_extractor.LANGUAGE_ALIASES.get(f.suffix.lower()[1:]),
                            )
                            
                            # Index by file path
                            if str(f) not in self._index:
                                self._index[str(f)] = []
                            self._index[str(f)].append(file)
                            
                            # Index by words in content
                            words = set(re.findall(r"\b\w+\b", content.lower()))
                            for word in words:
                                if word not in self._index:
                                    self._index[word] = []
                                self._index[word].append(file)
                        except Exception:
                            continue
        
        self._indexed = True
    
    def search(
        self,
        query: str,
        paths: Optional[List[Union[str, Path]]] = None,
        pattern: bool = False,
        regex: bool = False,
        case_sensitive: bool = False,
        whole_word: bool = True,
        limit: int = 100,
    ) -> List[SearchResult]:
        """Search for query in code.
        
        Args:
            query: Search query
            paths: Paths to search in (overrides default)
            pattern: Whether query is a pattern (glob)
            regex: Whether query is a regex
            case_sensitive: Whether search is case-sensitive
            whole_word: Whether to match whole words only
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        # Build search paths
        search_paths = paths or self.paths
        
        results = []
        
        for path in search_paths:
            p = Path(path)
            if p.is_file():
                file_results = self._search_file(p, query, pattern, regex, case_sensitive, whole_word)
                results.extend(file_results)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file() and not self._should_exclude(f):
                        if f.suffix in self.extensions:
                            file_results = self._search_file(f, query, pattern, regex, case_sensitive, whole_word)
                            results.extend(file_results)
                            
                            if len(results) >= limit:
                                break
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def _search_file(
        self,
        path: Path,
        query: str,
        pattern: bool,
        regex: bool,
        case_sensitive: bool,
        whole_word: bool,
    ) -> List[SearchResult]:
        """Search in a single file.
        
        Args:
            path: File path
            query: Search query
            pattern: Whether query is a pattern
            regex: Whether query is a regex
            case_sensitive: Whether search is case-sensitive
            whole_word: Whether to match whole words only
            
        Returns:
            List of SearchResult objects
        """
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            
            results = []
            
            for i, line in enumerate(lines, 1):
                if self._match_line(line, query, pattern, regex, case_sensitive, whole_word):
                    # Get context
                    start = max(0, i - self.context_lines - 1)
                    end = min(len(lines), i + self.context_lines)
                    context = lines[start:end]
                    
                    results.append(SearchResult(
                        file=path.name,
                        path=str(path),
                        line_number=i,
                        line=line,
                        context=context,
                        score=self._calculate_score(line, query, case_sensitive, whole_word),
                        metadata={
                            "file_size": len(content),
                            "line_count": len(lines),
                        }
                    ))
            
            return results
        except Exception:
            return []
    
    def _match_line(
        self,
        line: str,
        query: str,
        pattern: bool,
        regex: bool,
        case_sensitive: bool,
        whole_word: bool,
    ) -> bool:
        """Check if line matches query.
        
        Args:
            line: Line to check
            query: Search query
            pattern: Whether query is a pattern
            regex: Whether query is a regex
            case_sensitive: Whether search is case-sensitive
            whole_word: Whether to match whole words only
            
        Returns:
            True if line matches
        """
        if not case_sensitive:
            line = line.lower()
            query = query.lower()
        
        if regex:
            try:
                return bool(re.search(query, line))
            except Exception:
                return False
        
        if pattern:
            return fnmatch.fnmatch(line, query)
        
        if whole_word:
            # Match whole words
            words = re.findall(r"\b\w+\b", line)
            return query in words
        
        return query in line
    
    def _calculate_score(
        self,
        line: str,
        query: str,
        case_sensitive: bool,
        whole_word: bool,
    ) -> float:
        """Calculate score for a match.
        
        Args:
            line: Line that matched
            query: Search query
            case_sensitive: Whether search is case-sensitive
            whole_word: Whether to match whole words only
            
        Returns:
            Match score
        """
        if not case_sensitive:
            line = line.lower()
            query = query.lower()
        
        # Count occurrences
        count = line.count(query)
        
        # Higher score for whole word matches
        if whole_word:
            words = re.findall(r"\b\w+\b", line)
            word_count = words.count(query)
            return float(count + word_count * 2)
        
        return float(count)
    
    def search_functions(
        self,
        name: str,
        paths: Optional[List[Union[str, Path]]] = None,
    ) -> List[CodeSearchResult]:
        """Search for function definitions.
        
        Args:
            name: Function name to search for
            paths: Paths to search in
            
        Returns:
            List of CodeSearchResult objects
        """
        results = []
        
        search_paths = paths or self.paths
        
        for path in search_paths:
            p = Path(path)
            if p.is_file():
                file_results = self._search_functions_in_file(p, name)
                results.extend(file_results)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file() and not self._should_exclude(f):
                        if f.suffix in self.extensions:
                            file_results = self._search_functions_in_file(f, name)
                            results.extend(file_results)
        
        return results
    
    def _search_functions_in_file(
        self,
        path: Path,
        name: str,
    ) -> List[CodeSearchResult]:
        """Search for functions in a single file.
        
        Args:
            path: File path
            name: Function name
            
        Returns:
            List of CodeSearchResult objects
        """
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            
            # Use AST extractor
            functions = self._ast_extractor.extract_functions(content, str(path))
            
            results = []
            for func in functions:
                if func.name == name:
                    # Get context lines
                    lines = content.splitlines()
                    start = max(0, func.start_line - self.context_lines - 1)
                    end = min(len(lines), func.end_line + self.context_lines)
                    context = lines[start:end]
                    
                    results.append(CodeSearchResult(
                        file=path.name,
                        path=str(path),
                        line_number=func.start_line,
                        line=func.body.splitlines()[0] if func.body else "",
                        context=context,
                        code=func.body,
                        language=self._code_extractor.LANGUAGE_ALIASES.get(path.suffix.lower()[1:]),
                        function=func.name,
                        score=1.0,
                    ))
            
            return results
        except Exception:
            return []
    
    def search_classes(
        self,
        name: str,
        paths: Optional[List[Union[str, Path]]] = None,
    ) -> List[CodeSearchResult]:
        """Search for class definitions.
        
        Args:
            name: Class name to search for
            paths: Paths to search in
            
        Returns:
            List of CodeSearchResult objects
        """
        results = []
        
        search_paths = paths or self.paths
        
        for path in search_paths:
            p = Path(path)
            if p.is_file():
                file_results = self._search_classes_in_file(p, name)
                results.extend(file_results)
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file() and not self._should_exclude(f):
                        if f.suffix in self.extensions:
                            file_results = self._search_classes_in_file(f, name)
                            results.extend(file_results)
        
        return results
    
    def _search_classes_in_file(
        self,
        path: Path,
        name: str,
    ) -> List[CodeSearchResult]:
        """Search for classes in a single file.
        
        Args:
            path: File path
            name: Class name
            
        Returns:
            List of CodeSearchResult objects
        """
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            
            # Use AST extractor
            classes = self._ast_extractor.extract_classes(content, str(path))
            
            results = []
            for cls in classes:
                if cls.name == name:
                    # Get context lines
                    lines = content.splitlines()
                    start = max(0, cls.start_line - self.context_lines - 1)
                    end = min(len(lines), cls.end_line + self.context_lines)
                    context = lines[start:end]
                    
                    results.append(CodeSearchResult(
                        file=path.name,
                        path=str(path),
                        line_number=cls.start_line,
                        line=content.splitlines()[cls.start_line - 1] if cls.start_line <= len(content.splitlines()) else "",
                        context=context,
                        code=str(cls),
                        language=self._code_extractor.LANGUAGE_ALIASES.get(path.suffix.lower()[1:]),
                        class_name=cls.name,
                        score=1.0,
                    ))
            
            return results
        except Exception:
            return []
    
    def search_code_blocks(
        self,
        language: Optional[str] = None,
        paths: Optional[List[Union[str, Path]]] = None,
        limit: int = 100,
    ) -> List[CodeSearchResult]:
        """Search for code blocks.
        
        Args:
            language: Language to filter by
            paths: Paths to search in
            limit: Maximum number of results
            
        Returns:
            List of CodeSearchResult objects
        """
        results = []
        
        search_paths = paths or self.paths
        
        for path in search_paths:
            p = Path(path)
            if p.is_file():
                file_results = self._search_code_blocks_in_file(p, language)
                results.extend(file_results)
                
                if len(results) >= limit:
                    break
            elif p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file() and not self._should_exclude(f):
                        if f.suffix in self.extensions:
                            file_results = self._search_code_blocks_in_file(f, language)
                            results.extend(file_results)
                            
                            if len(results) >= limit:
                                break
        
        return results[:limit]
    
    def _search_code_blocks_in_file(
        self,
        path: Path,
        language: Optional[str] = None,
    ) -> List[CodeSearchResult]:
        """Search for code blocks in a single file.
        
        Args:
            path: File path
            language: Language to filter by
            
        Returns:
            List of CodeSearchResult objects
        """
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            
            # Extract code blocks
            code_blocks = self._code_extractor.extract(content, str(path))
            
            results = []
            for block in code_blocks:
                if language and block.language != language:
                    continue
                
                # Get line number
                lines = content.splitlines()
                try:
                    line_num = lines.index(block.code.splitlines()[0]) + 1
                except ValueError:
                    line_num = 0
                
                results.append(CodeSearchResult(
                    file=path.name,
                    path=str(path),
                    line_number=line_num,
                    line=block.code.splitlines()[0] if block.code else "",
                    context=[],
                    code=block.code,
                    language=block.language,
                    score=1.0,
                ))
            
            return results
        except Exception:
            return []
    
    def search_to_dict(
        self,
        query: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search and return results as dictionaries.
        
        Args:
            query: Search query
            **kwargs: Search options
            
        Returns:
            List of result dictionaries
        """
        results = self.search(query, **kwargs)
        return [r.to_dict() for r in results]
    
    def search_to_json(
        self,
        query: str,
        **kwargs
    ) -> str:
        """Search and return results as JSON.
        
        Args:
            query: Search query
            **kwargs: Search options
            
        Returns:
            JSON string
        """
        return json.dumps(self.search_to_dict(query, **kwargs), indent=2)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CodeSearcher",
    "SearchResult",
    "CodeSearchResult",
]
