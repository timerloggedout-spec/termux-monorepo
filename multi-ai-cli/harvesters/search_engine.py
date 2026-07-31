#!/usr/bin/env python3
"""Search Engine for code and text search across harvested data."""
import os
import json
import re
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from rich.console import Console
import hashlib

console = Console()

@dataclass
class SearchResult:
    """Represents a search result."""
    snippet_hash: str
    content: str
    language: str
    source: str
    file_path: str
    score: float
    line_number: int = 0
    context: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "snippet_hash": self.snippet_hash,
            "content": self.content,
            "language": self.language,
            "source": self.source,
            "file_path": self.file_path,
            "score": self.score,
            "line_number": self.line_number,
            "context": self.context,
            "metadata": self.metadata,
        }

class SearchEngine:
    """Full-text search engine for code and text."""
    
    def __init__(self, index_path: str = None):
        """Initialize the search engine."""
        self.index_path = index_path or os.path.join(
            os.path.expanduser("~/.mistralai-cli"), "search_index"
        )
        os.makedirs(self.index_path, exist_ok=True)
        
        # In-memory index
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)  # term -> set of snippet hashes
        self.snippets: Dict[str, Dict] = {}  # hash -> snippet data
        self.token_counts: Dict[str, int] = defaultdict(int)  # term -> count
    
    def index_snippet(self, snippet: Dict) -> str:
        """Index a code snippet."""
        snippet_hash = snippet.get("hash", "")
        content = snippet.get("content", "")
        
        # Tokenize content
        tokens = self._tokenize(content)
        
        # Update inverted index
        for token in tokens:
            self.inverted_index[token].add(snippet_hash)
            self.token_counts[token] += 1
        
        # Store snippet
        self.snippets[snippet_hash] = snippet
        
        return snippet_hash
    
    def index_snippets(self, snippets: List[Dict]):
        """Index multiple snippets."""
        for snippet in snippets:
            self.index_snippet(snippet)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for indexing."""
        # Remove special characters and split into tokens
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.lower().split()
        
        # Filter out very short tokens
        tokens = [t for t in tokens if len(t) >= 2]
        
        return tokens
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for snippets matching the query."""
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Find snippets containing all query tokens (AND search)
        matching_hashes = None
        for token in query_tokens:
            if token in self.inverted_index:
                if matching_hashes is None:
                    matching_hashes = self.inverted_index[token].copy()
                else:
                    matching_hashes.intersection_update(self.inverted_index[token])
            else:
                matching_hashes = set()
                break
        
        if not matching_hashes:
            return []
        
        # Score and sort results
        results = []
        for snippet_hash in matching_hashes:
            snippet = self.snippets.get(snippet_hash, {})
            score = self._calculate_score(snippet, query_tokens)
            
            result = SearchResult(
                snippet_hash=snippet_hash,
                content=snippet.get("content", ""),
                language=snippet.get("language", "unknown"),
                source=snippet.get("source", "unknown"),
                file_path=snippet.get("file_path", ""),
                score=score,
                metadata=snippet.get("metadata", {}),
            )
            results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def _calculate_score(self, snippet: Dict, query_tokens: List[str]) -> float:
        """Calculate relevance score for a snippet."""
        content = snippet.get("content", "").lower()
        score = 0.0
        
        # Count token matches
        for token in query_tokens:
            count = content.count(token)
            # Weight by inverse document frequency
            idf = 1.0 / (1.0 + self.token_counts.get(token, 1))
            score += count * idf
        
        # Boost by language match if query contains language hint
        language = snippet.get("language", "").lower()
        for token in query_tokens:
            if token == language:
                score *= 1.5
        
        return score
    
    def fuzzy_search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Fuzzy search using substring matching."""
        query_lower = query.lower()
        results = []
        
        for snippet_hash, snippet in self.snippets.items():
            content = snippet.get("content", "").lower()
            if query_lower in content:
                score = content.count(query_lower)
                result = SearchResult(
                    snippet_hash=snippet_hash,
                    content=snippet.get("content", ""),
                    language=snippet.get("language", "unknown"),
                    source=snippet.get("source", "unknown"),
                    file_path=snippet.get("file_path", ""),
                    score=score,
                    metadata=snippet.get("metadata", {}),
                )
                results.append(result)
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]
    
    def search_by_language(self, language: str, query: str = "", limit: int = 10) -> List[SearchResult]:
        """Search snippets by language."""
        results = []
        
        for snippet_hash, snippet in self.snippets.items():
            if snippet.get("language", "").lower() == language.lower():
                if not query or query.lower() in snippet.get("content", "").lower():
                    result = SearchResult(
                        snippet_hash=snippet_hash,
                        content=snippet.get("content", ""),
                        language=snippet.get("language", "unknown"),
                        source=snippet.get("source", "unknown"),
                        file_path=snippet.get("file_path", ""),
                        score=1.0,
                        metadata=snippet.get("metadata", {}),
                    )
                    results.append(result)
        
        return results[:limit]
    
    def search_by_file(self, file_path: str) -> List[SearchResult]:
        """Search snippets from a specific file."""
        results = []
        
        for snippet_hash, snippet in self.snippets.items():
            if snippet.get("file_path", "") == file_path:
                result = SearchResult(
                    snippet_hash=snippet_hash,
                    content=snippet.get("content", ""),
                    language=snippet.get("language", "unknown"),
                    source=snippet.get("source", "unknown"),
                    file_path=file_path,
                    score=1.0,
                    metadata=snippet.get("metadata", {}),
                )
                results.append(result)
        
        return results
    
    def save_index(self, name: str = "default"):
        """Save index to disk."""
        index_file = os.path.join(self.index_path, f"{name}.json")
        data = {
            "inverted_index": {k: list(v) for k, v in self.inverted_index.items()},
            "snippets": self.snippets,
            "token_counts": dict(self.token_counts),
        }
        
        with open(index_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"[green]Index saved to {index_file}[/]")
    
    def load_index(self, name: str = "default"):
        """Load index from disk."""
        index_file = os.path.join(self.index_path, f"{name}.json")
        
        if not os.path.exists(index_file):
            console.print(f"[red]Index file not found: {index_file}[/]")
            return False
        
        with open(index_file) as f:
            data = json.load(f)
        
        self.inverted_index = {k: set(v) for k, v in data.get("inverted_index", {}).items()}
        self.snippets = data.get("snippets", {})
        self.token_counts = defaultdict(int, data.get("token_counts", {}))
        
        console.print(f"[green]Index loaded from {index_file}[/]")
        return True
    
    def clear(self):
        """Clear the index."""
        self.inverted_index.clear()
        self.snippets.clear()
        self.token_counts.clear()
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "total_snippets": len(self.snippets),
            "total_unique_tokens": len(self.inverted_index),
            "total_token_occurrences": sum(self.token_counts.values()),
        }

if __name__ == "__main__":
    # Example usage
    engine = SearchEngine()
    
    # Create some test snippets
    test_snippets = [
        {
            "hash": "abc123",
            "content": "def hello_world():\n    print('Hello, World!')",
            "language": "python",
            "source": "test",
            "file_path": "test.py",
        },
        {
            "hash": "def456",
            "content": "function add(a, b) { return a + b; }",
            "language": "javascript",
            "source": "test",
            "file_path": "test.js",
        },
    ]
    
    # Index snippets
    engine.index_snippets(test_snippets)
    
    # Search
    results = engine.search("hello")
    print(f"Found {len(results)} results")
    for result in results:
        print(f"  - {result.language}: {result.content[:50]}...")
