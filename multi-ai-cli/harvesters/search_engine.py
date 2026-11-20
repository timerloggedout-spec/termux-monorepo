#!/usr/bin/env python3
"""Search Engine for code and text search across harvested data.

This uses the CodexIndex from code_harvester for efficient code block search.
"""
import os
import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from rich.console import Console

console = Console()

@dataclass
class SearchResult:
    """Represents a search result."""
    content_hash: str
    content: str
    language: str
    session_id: str
    message_index: int
    block_index: int
    score: float
    timestamp: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "content_hash": self.content_hash,
            "content": self.content,
            "language": self.language,
            "session_id": self.session_id,
            "message_index": self.message_index,
            "block_index": self.block_index,
            "score": self.score,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

class SearchEngine:
    """Full-text search engine for code and text.
    
    This wraps the CodexIndex for efficient code block search,
    and adds additional search capabilities.
    """
    
    def __init__(self, codex_dir: str = None):
        """Initialize the search engine."""
        from .code_harvester import CodexIndex
        from pathlib import Path
        
        if codex_dir:
            self.codex = CodexIndex(Path(codex_dir))
        else:
            self.codex = CodexIndex()
    
    def index_conversation(self, session_id: str, title: str, messages: List[Dict]):
        """Index a conversation for search."""
        self.codex.index_conversation(session_id, title, messages)
    
    def search(self, query: str, language: str = None, limit: int = 10) -> List[SearchResult]:
        """Search for code blocks matching the query.
        
        Args:
            query: Search query
            language: Optional language filter
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        # Use codex search
        codex_results = self.codex.search(query, language)
        
        for idx, result in enumerate(codex_results[:limit]):
            search_result = SearchResult(
                content_hash=result.get("hash", ""),
                content=result.get("code", ""),
                language=result.get("language", "text"),
                session_id=result.get("session_id", ""),
                message_index=result.get("message_index", 0),
                block_index=result.get("block_index", 0),
                score=1.0 - (idx * 0.1),  # Simple scoring based on position
                timestamp=result.get("timestamp", ""),
                metadata={
                    "pointer": result.get("pointer", ""),
                }
            )
            results.append(search_result)
        
        return results
    
    def search_by_language(self, language: str, query: str = "", limit: int = 10) -> List[SearchResult]:
        """Search code blocks by language.
        
        Args:
            language: Language to filter by
            query: Optional additional query filter
            limit: Maximum number of results
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        codex_results = self.codex.search_by_language(language, query)
        
        for idx, result in enumerate(codex_results[:limit]):
            search_result = SearchResult(
                content_hash=result.get("hash", ""),
                content=result.get("code", ""),
                language=language,
                session_id=result.get("session_id", ""),
                message_index=result.get("message_index", 0),
                block_index=result.get("block_index", 0),
                score=1.0 - (idx * 0.1),
                timestamp=result.get("timestamp", ""),
                metadata={
                    "pointer": result.get("pointer", ""),
                }
            )
            results.append(search_result)
        
        return results
    
    def get_by_hash(self, content_hash: str) -> Optional[str]:
        """Get code content by hash.
        
        Args:
            content_hash: The content hash
            
        Returns:
            The code content, or None if not found
        """
        return self.codex.get_code_by_hash(content_hash)
    
    def get_stats(self) -> Dict:
        """Get search engine statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.codex.get_stats()
    
    def get_all_blocks(self) -> List[Dict]:
        """Get all code blocks.
        
        Returns:
            List of all code blocks
        """
        code_blocks = self.codex.get_all_blocks()
        return [block.to_dict() for block in code_blocks]


if __name__ == "__main__":
    # Example usage
    engine = SearchEngine()
    
    # Index some sample data
    sample_messages = [
        {
            "role": "user",
            "content": "Write a Python function",
        },
        {
            "role": "assistant",
            "content": "```python\ndef hello():\n    print('Hello')\n```",
        },
    ]
    
    engine.index_conversation("test_session", "Test", sample_messages)
    
    # Search
    results = engine.search("hello")
    print(f"Found {len(results)} results")
    for result in results:
        print(f"  - {result.language}: {result.content[:50]}...")
