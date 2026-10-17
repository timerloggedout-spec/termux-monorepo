#!/usr/bin/env python3
"""Semantic Searcher - Semantic similarity search.

This module provides functionality to:
- Search by semantic similarity
- Create and search embeddings
- Find similar code
- Find similar documents
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    _NUMPY_AVAILABLE = False

from bridge.mistralai_bridge import get_mistral_bridge


@dataclass
class SemanticResult:
    """Represents a semantic search result."""
    item: Any
    similarity: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "similarity": self.similarity,
            "metadata": self.metadata,
        }


class SemanticSearcher:
    """Semantic similarity search.
    
    This searcher uses embeddings to find semantically similar items.
    """
    
    def __init__(
        self,
        embedding_model: str = "mistral-embed",
        batch_size: int = 32,
        num_workers: int = 4,
        **kwargs
    ):
        """Initialize semantic searcher.
        
        Args:
            embedding_model: Model to use for embeddings
            batch_size: Batch size for embedding creation
            num_workers: Number of parallel workers
        """
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        self.num_workers = num_workers
        self._bridge = get_mistral_bridge()
        
        # Embedding cache
        self._embedding_cache: Dict[str, List[float]] = {}
        
        # Index
        self._index: Dict[str, List[Tuple[Any, List[float]]]] = {}
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        try:
            embedding = self._bridge.create_embedding(text, model=self.embedding_model)
            self._embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            print(f"Failed to create embedding: {e}", file=sys.stderr)
            return []
    
    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # Check cache
        results = []
        to_embed = []
        
        for text in texts:
            if text in self._embedding_cache:
                results.append(self._embedding_cache[text])
            else:
                to_embed.append(text)
        
        # Create embeddings for uncached texts
        if to_embed:
            try:
                embeddings = self._bridge.create_embeddings(to_embed, model=self.embedding_model)
                for text, embedding in zip(to_embed, embeddings):
                    self._embedding_cache[text] = embedding
                    results.append(embedding)
            except Exception as e:
                print(f"Failed to create embeddings: {e}", file=sys.stderr)
                # Use zeros for failed embeddings
                results.extend([[] for _ in to_embed])
        
        return results
    
    def _cosine_similarity(
        self,
        a: List[float],
        b: List[float],
    ) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine similarity (0 to 1)
        """
        if not a or not b:
            return 0.0
        
        if _NUMPY_AVAILABLE:
            a_array = np.array(a)
            b_array = np.array(b)
            dot_product = np.dot(a_array, b_array)
            norm_a = np.linalg.norm(a_array)
            norm_b = np.linalg.norm(b_array)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
        else:
            # Manual calculation
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
    
    def index(
        self,
        items: List[Any],
        key: Optional[callable] = None,
        key_name: Optional[str] = None,
    ):
        """Index items for semantic search.
        
        Args:
            items: List of items to index
            key: Function to extract text from items
            key_name: Name of attribute to use as text
        """
        # Get text from items
        if key:
            texts = [key(item) for item in items]
        elif key_name:
            texts = [getattr(item, key_name, "") for item in items]
        else:
            texts = [str(item) for item in items]
        
        # Create embeddings
        embeddings = self._create_embeddings(texts)
        
        # Store in index
        for item, embedding in zip(items, embeddings):
            item_id = str(id(item))
            if item_id not in self._index:
                self._index[item_id] = []
            self._index[item_id].append((item, embedding))
    
    def search(
        self,
        query: str,
        items: Optional[List[Any]] = None,
        key: Optional[callable] = None,
        key_name: Optional[str] = None,
        limit: int = 10,
        threshold: float = 0.0,
    ) -> List[SemanticResult]:
        """Search for semantically similar items.
        
        Args:
            query: Search query
            items: List of items to search (overrides indexed items)
            key: Function to extract text from items
            key_name: Name of attribute to use as text
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of SemanticResult objects
        """
        # Create query embedding
        query_embedding = self._create_embedding(query)
        
        if not query_embedding:
            return []
        
        # Get items to search
        if items is not None:
            # Use provided items
            if key:
                texts = [key(item) for item in items]
            elif key_name:
                texts = [getattr(item, key_name, "") for item in items]
            else:
                texts = [str(item) for item in items]
            
            embeddings = self._create_embeddings(texts)
            search_items = list(zip(items, embeddings))
        else:
            # Use indexed items
            search_items = []
            for item_list in self._index.values():
                search_items.extend(item_list)
        
        # Calculate similarities
        results = []
        for item, embedding in search_items:
            if not embedding:
                continue
            
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            if similarity >= threshold:
                results.append(SemanticResult(
                    item=item,
                    similarity=similarity,
                    metadata={
                        "type": type(item).__name__,
                    }
                ))
        
        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)
        
        return results[:limit]
    
    def search_code(
        self,
        query: str,
        code_snippets: List[str],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> List[SemanticResult]:
        """Search for semantically similar code.
        
        Args:
            query: Search query
            code_snippets: List of code snippets to search
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of SemanticResult objects
        """
        return self.search(
            query,
            items=code_snippets,
            limit=limit,
            threshold=threshold,
        )
    
    def search_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        text_key: str = "content",
        limit: int = 10,
        threshold: float = 0.0,
    ) -> List[SemanticResult]:
        """Search for semantically similar documents.
        
        Args:
            query: Search query
            documents: List of documents to search
            text_key: Key containing text in documents
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of SemanticResult objects
        """
        return self.search(
            query,
            items=documents,
            key=lambda x: x.get(text_key, ""),
            limit=limit,
            threshold=threshold,
        )
    
    def find_similar(
        self,
        text: str,
        candidates: List[str],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> List[SemanticResult]:
        """Find similar texts.
        
        Args:
            text: Reference text
            candidates: List of candidate texts
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of SemanticResult objects
        """
        return self.search(
            text,
            items=candidates,
            limit=limit,
            threshold=threshold,
        )
    
    def cluster(
        self,
        items: List[Any],
        key: Optional[callable] = None,
        key_name: Optional[str] = None,
        threshold: float = 0.7,
        max_clusters: int = 10,
    ) -> List[List[Any]]:
        """Cluster items by semantic similarity.
        
        Args:
            items: List of items to cluster
            key: Function to extract text from items
            key_name: Name of attribute to use as text
            threshold: Similarity threshold for clustering
            max_clusters: Maximum number of clusters
            
        Returns:
            List of clusters (lists of items)
        """
        if len(items) <= 1:
            return [items]
        
        # Get texts and embeddings
        if key:
            texts = [key(item) for item in items]
        elif key_name:
            texts = [getattr(item, key_name, "") for item in items]
        else:
            texts = [str(item) for item in items]
        
        embeddings = self._create_embeddings(texts)
        
        # Simple clustering (hierarchical)
        clusters = []
        used = set()
        
        for i, (item, embedding) in enumerate(zip(items, embeddings)):
            if i in used:
                continue
            
            # Find similar items
            cluster = [item]
            used.add(i)
            
            for j, (other_item, other_embedding) in enumerate(zip(items, embeddings)):
                if j in used:
                    continue
                
                similarity = self._cosine_similarity(embedding, other_embedding)
                if similarity >= threshold:
                    cluster.append(other_item)
                    used.add(j)
            
            clusters.append(cluster)
            
            if len(clusters) >= max_clusters:
                break
        
        return clusters
    
    def clear_cache(self):
        """Clear embedding cache."""
        self._embedding_cache.clear()
    
    def clear_index(self):
        """Clear search index."""
        self._index.clear()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SemanticSearcher",
    "SemanticResult",
]
