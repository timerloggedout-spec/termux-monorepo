"""
Search Module for Multi-AI CLI

This module provides comprehensive search capabilities for Mistralai
and other AI services, integrating with:
- Code harvest/extraction results
- GitHub repositories
- Local filesystems
- Remote Termux devices
- AI model responses

Features:
- Full-text search across multiple sources
- Code-aware search with language detection
- Semantic search capabilities
- Integration with harvesters module
- Support for regex and fuzzy matching
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
from abc import ABC, abstractmethod

from core.core import DeepTermWebWrapper, get_wrapper
from harvesters import CodeHarvester, CodeBlock, get_harvester


@dataclass
class SearchResult:
    """Represents a search result"""
    source: str
    path: Optional[str] = None
    line_number: Optional[int] = None
    content: str = ""
    score: float = 0.0
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "source": self.source,
            "path": self.path,
            "line_number": self.line_number,
            "content": self.content,
            "score": self.score,
            "language": self.language,
            "metadata": self.metadata
        }


@dataclass
class SearchQuery:
    """Represents a search query"""
    query: str
    language: Optional[str] = None
    source: Optional[str] = None
    regex: bool = False
    case_sensitive: bool = False
    max_results: int = 100
    min_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "query": self.query,
            "language": self.language,
            "source": self.source,
            "regex": self.regex,
            "case_sensitive": self.case_sensitive,
            "max_results": self.max_results,
            "min_score": self.min_score
        }


class SearchStrategy(ABC):
    """Abstract base class for search strategies"""
    
    @abstractmethod
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Execute the search"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this strategy"""
        pass


class TextSearchStrategy(SearchStrategy):
    """Simple text search strategy"""
    
    def __init__(self, data: List[str], source: str = "text"):
        self.data = data
        self.source = source
    
    def get_name(self) -> str:
        return "text"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        results = []
        query_text = query.query
        
        if not query.case_sensitive:
            query_text = query_text.lower()
        
        for i, item in enumerate(self.data):
            content = item
            if not query.case_sensitive:
                content = content.lower()
            
            if query.regex:
                try:
                    pattern = re.compile(query_text)
                    if pattern.search(content):
                        results.append(SearchResult(
                            source=self.source,
                            path=None,
                            line_number=i + 1,
                            content=item,
                            score=1.0,
                            metadata={"strategy": self.get_name()}
                        ))
                except re.error:
                    continue
            else:
                if query_text in content:
                    results.append(SearchResult(
                        source=self.source,
                        path=None,
                        line_number=i + 1,
                        content=item,
                        score=1.0,
                        metadata={"strategy": self.get_name()}
                    ))
        
        return results[:query.max_results]


class CodeSearchStrategy(SearchStrategy):
    """Search strategy for code blocks"""
    
    def __init__(self, harvester: Optional[CodeHarvester] = None):
        self.harvester = harvester or get_harvester()
    
    def get_name(self) -> str:
        return "code"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        results = []
        
        # Get code blocks from harvester
        code_blocks = self.harvester.get_indexed_blocks()
        
        query_text = query.query
        if not query.case_sensitive:
            query_text = query_text.lower()
        
        for block in code_blocks:
            # Filter by language if specified
            if query.language and block.language != query.language:
                continue
            
            # Filter by source if specified
            if query.source and block.source != query.source:
                continue
            
            content = block.code
            if not query.case_sensitive:
                content = content.lower()
            
            if query.regex:
                try:
                    pattern = re.compile(query_text)
                    if pattern.search(content):
                        results.append(SearchResult(
                            source=block.source,
                            path=block.file_path,
                            line_number=block.line_start,
                            content=block.code,
                            score=1.0,
                            language=block.language,
                            metadata={
                                "strategy": self.get_name(),
                                "harvest_method": block.metadata.get("harvest_method")
                            }
                        ))
                except re.error:
                    continue
            else:
                if query_text in content:
                    results.append(SearchResult(
                        source=block.source,
                        path=block.file_path,
                        line_number=block.line_start,
                        content=block.code,
                        score=1.0,
                        language=block.language,
                        metadata={
                            "strategy": self.get_name(),
                            "harvest_method": block.metadata.get("harvest_method")
                        }
                    ))
        
        return results[:query.max_results]


class GitHubSearchStrategy(SearchStrategy):
    """Search strategy for GitHub repositories"""
    
    def __init__(self, repo: str = "timerloggedout-spec/termux-monorepo",
                 branch: str = "master"):
        self.repo = repo
        self.branch = branch
    
    def get_name(self) -> str:
        return "github"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        results = []
        
        try:
            # Use gh CLI to search code
            cmd = [
                "gh", "search", "code", query.query,
                "--repo", self.repo,
                "--json", "path,lineNumber,text"
            ]
            
            if self.branch:
                cmd.extend(["--branch", self.branch])
            
            if query.language:
                cmd.extend(["--language", query.language])
            
            if query.max_results:
                cmd.extend(["--limit", str(query.max_results)])
            
            proc = subprocess.run(cmd, capture_output=True, 
                                timeout=60, text=True)
            
            if proc.returncode == 0:
                try:
                    data = json.loads(proc.stdout)
                    if isinstance(data, list):
                        for item in data:
                            results.append(SearchResult(
                                source=f"github:{self.repo}@{self.branch}",
                                path=item.get("path"),
                                line_number=item.get("lineNumber"),
                                content=item.get("text", ""),
                                score=1.0,
                                metadata={"strategy": self.get_name()}
                            ))
                except json.JSONDecodeError:
                    # Parse as text
                    for line in proc.stdout.strip().split('\n'):
                        if line:
                            results.append(SearchResult(
                                source=f"github:{self.repo}@{self.branch}",
                                content=line,
                                score=1.0,
                                metadata={"strategy": self.get_name()}
                            ))
        
        except Exception as e:
            print(f"Warning: GitHub search failed: {e}", file=sys.stderr)
        
        return results[:query.max_results]


class FileSearchStrategy(SearchStrategy):
    """Search strategy for local files"""
    
    def __init__(self, directory: str = ".", 
                 extensions: Optional[List[str]] = None):
        self.directory = directory
        self.extensions = extensions or [".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".h"]
    
    def get_name(self) -> str:
        return "file"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        results = []
        path_obj = Path(self.directory)
        
        if not path_obj.exists():
            return results
        
        query_text = query.query
        if not query.case_sensitive:
            query_text = query_text.lower()
        
        # Recursively search through files
        for file_path in path_obj.rglob("*"):
            if file_path.is_file():
                # Filter by extension if specified
                if self.extensions:
                    if file_path.suffix not in self.extensions:
                        continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            content = line
                            if not query.case_sensitive:
                                content = content.lower()
                            
                            if query.regex:
                                try:
                                    pattern = re.compile(query_text)
                                    if pattern.search(content):
                                        results.append(SearchResult(
                                            source="file",
                                            path=str(file_path),
                                            line_number=line_num,
                                            content=line.strip(),
                                            score=1.0,
                                            metadata={"strategy": self.get_name()}
                                        ))
                                except re.error:
                                    continue
                            else:
                                if query_text in content:
                                    results.append(SearchResult(
                                        source="file",
                                        path=str(file_path),
                                        line_number=line_num,
                                        content=line.strip(),
                                        score=1.0,
                                        metadata={"strategy": self.get_name()}
                                    ))
                except Exception:
                    continue
        
        return results[:query.max_results]


class TermuxSearchStrategy(SearchStrategy):
    """Search strategy for remote Termux devices"""
    
    def __init__(self, wrapper: Optional[DeepTermWebWrapper] = None):
        self.wrapper = wrapper or get_wrapper()
    
    def get_name(self) -> str:
        return "termux"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        results = []
        
        try:
            # Execute remote grep command
            # Note: This requires the bridge to be initialized
            if not hasattr(self.wrapper, 'bridge') or not self.wrapper.bridge:
                return results
            
            # Build grep command
            grep_cmd = "grep"
            if not query.case_sensitive:
                grep_cmd = "grep -i"
            if query.regex:
                grep_cmd += " -E"
            
            command = f"{grep_cmd} '{query.query}' /data/data/com.termux/files/home/*"
            
            output = self.wrapper.execute_shell_command(command)
            
            # Parse output
            for line in output.strip().split('\n'):
                if line:
                    # Parse grep output format: filename:line_number:content
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        file_path = parts[0]
                        try:
                            line_num = int(parts[1])
                        except ValueError:
                            line_num = None
                        content = parts[2] if len(parts) > 2 else ""
                        
                        results.append(SearchResult(
                            source="termux",
                            path=file_path,
                            line_number=line_num,
                            content=content,
                            score=1.0,
                            metadata={"strategy": self.get_name()}
                        ))
                    else:
                        results.append(SearchResult(
                            source="termux",
                            content=line,
                            score=1.0,
                            metadata={"strategy": self.get_name()}
                        ))
        
        except Exception as e:
            print(f"Warning: Termux search failed: {e}", file=sys.stderr)
        
        return results[:query.max_results]


class CompositeSearchStrategy(SearchStrategy):
    """Composite search strategy that combines multiple strategies"""
    
    def __init__(self):
        self.strategies: List[SearchStrategy] = []
    
    def add_strategy(self, strategy: SearchStrategy):
        """Add a search strategy"""
        self.strategies.append(strategy)
    
    def get_name(self) -> str:
        return "composite"
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        all_results = []
        
        for strategy in self.strategies:
            try:
                results = strategy.search(query)
                all_results.extend(results)
            except Exception as e:
                print(f"Warning: Strategy {strategy.get_name()} failed: {e}", 
                      file=sys.stderr)
        
        # Deduplicate results
        seen = set()
        unique_results = []
        for result in all_results:
            # Create a unique key based on content and source
            key = f"{result.source}:{result.path}:{result.line_number}:{result.content[:100]}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Sort by score (descending)
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        return unique_results[:query.max_results]


class SearchEngine:
    """
    Main search engine class
    
    Provides comprehensive search capabilities across multiple sources
    with support for different search strategies and query types.
    """
    
    def __init__(self):
        self.strategies: Dict[str, SearchStrategy] = {}
        self._composite = CompositeSearchStrategy()
        
        # Initialize default strategies
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """Initialize default search strategies"""
        # Code search
        code_strategy = CodeSearchStrategy()
        self.register_strategy("code", code_strategy)
        self._composite.add_strategy(code_strategy)
        
        # GitHub search
        github_strategy = GitHubSearchStrategy()
        self.register_strategy("github", github_strategy)
        self._composite.add_strategy(github_strategy)
        
        # File search
        file_strategy = FileSearchStrategy()
        self.register_strategy("file", file_strategy)
        self._composite.add_strategy(file_strategy)
        
        # Termux search
        try:
            termux_strategy = TermuxSearchStrategy()
            self.register_strategy("termux", termux_strategy)
            self._composite.add_strategy(termux_strategy)
        except Exception:
            pass
    
    def register_strategy(self, name: str, strategy: SearchStrategy):
        """Register a search strategy"""
        self.strategies[name] = strategy
    
    def get_strategy(self, name: str) -> Optional[SearchStrategy]:
        """Get a registered strategy"""
        return self.strategies.get(name)
    
    def search(self, query: Union[str, SearchQuery], 
               strategy: Optional[str] = None) -> List[SearchResult]:
        """
        Execute a search
        
        Args:
            query: Search query (string or SearchQuery object)
            strategy: Optional strategy name to use (defaults to composite)
        
        Returns:
            List of SearchResult objects
        """
        if isinstance(query, str):
            query = SearchQuery(query=query)
        
        if strategy:
            strat = self.get_strategy(strategy)
            if strat:
                return strat.search(query)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")
        
        return self._composite.search(query)
    
    def code_search(self, query: Union[str, SearchQuery]) -> List[SearchResult]:
        """Search code specifically"""
        if isinstance(query, str):
            query = SearchQuery(query=query)
        return self.search(query, strategy="code")
    
    def github_search(self, query: Union[str, SearchQuery], 
                      repo: Optional[str] = None) -> List[SearchResult]:
        """Search GitHub specifically"""
        if isinstance(query, str):
            query = SearchQuery(query=query)
        
        if repo:
            # Create a new GitHub strategy for the specific repo
            strategy = GitHubSearchStrategy(repo=repo)
            return strategy.search(query)
        
        return self.search(query, strategy="github")
    
    def file_search(self, query: Union[str, SearchQuery], 
                    directory: Optional[str] = None) -> List[SearchResult]:
        """Search files specifically"""
        if isinstance(query, str):
            query = SearchQuery(query=query)
        
        if directory:
            strategy = FileSearchStrategy(directory=directory)
            return strategy.search(query)
        
        return self.search(query, strategy="file")
    
    def advanced_search(self, query: str, 
                        filters: Dict[str, Any] = None) -> List[SearchResult]:
        """
        Execute an advanced search with filters
        
        Args:
            query: Search query string
            filters: Dictionary of filters (language, source, etc.)
        
        Returns:
            List of SearchResult objects
        """
        search_query = SearchQuery(
            query=query,
            language=filters.get("language") if filters else None,
            source=filters.get("source") if filters else None,
            regex=filters.get("regex", False) if filters else False,
            case_sensitive=filters.get("case_sensitive", False) if filters else False,
            max_results=filters.get("max_results", 100) if filters else 100
        )
        
        return self.search(search_query)


# Global search engine instance
_search_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    """Get or create the global SearchEngine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine


def reset_search_engine():
    """Reset the global search engine instance"""
    global _search_engine
    _search_engine = None


if __name__ == "__main__":
    # Example usage
    engine = get_search_engine()
    
    # Simple search
    results = engine.search("def hello")
    print(f"Found {len(results)} results for 'def hello'")
    for result in results[:5]:
        print(f"  - {result.source}: {result.path}:{result.line_number}")
        print(f"    {result.content[:100]}...")
    
    # Code search
    code_results = engine.code_search("print")
    print(f"\nFound {len(code_results)} code results for 'print'")
    for result in code_results[:3]:
        print(f"  - {result.language}: {result.content[:80]}...")
    
    # Advanced search
    advanced_results = engine.advanced_search(
        "class.*Backend",
        filters={"language": "python", "max_results": 10}
    )
    print(f"\nFound {len(advanced_results)} Python class results")
    for result in advanced_results[:3]:
        print(f"  - {result.path}: {result.content[:80]}...")
