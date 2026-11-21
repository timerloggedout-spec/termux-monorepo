#!/usr/bin/env python3
"""Code Harvester - Unified interface for harvesting code from various sources.

This module provides a unified interface for harvesting code from:
- Files and directories
- Git repositories
- Web URLs
- API endpoints
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Set
from dataclasses import dataclass, field

from .file_harvester import FileHarvester, HarvestedFile
from .repo_harvester import RepositoryHarvester, HarvestedRepository


@dataclass
class HarvestResult:
    """Result of a harvest operation."""
    source: str
    source_type: str
    items: List[Union[HarvestedFile, HarvestedRepository]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "source_type": self.source_type,
            "items": [
                item.to_dict() if hasattr(item, 'to_dict') else item
                for item in self.items
            ],
            "metadata": self.metadata,
        }


class CodeHarvester:
    """Unified code harvester.
    
    This class provides a unified interface for harvesting code from
    various sources with a consistent API.
    """
    
    def __init__(
        self,
        file_harvester: Optional[FileHarvester] = None,
        repo_harvester: Optional[RepositoryHarvester] = None,
        **kwargs
    ):
        """Initialize code harvester.
        
        Args:
            file_harvester: FileHarvester instance
            repo_harvester: RepositoryHarvester instance
        """
        self.file_harvester = file_harvester or FileHarvester(**kwargs)
        self.repo_harvester = repo_harvester or RepositoryHarvester(**kwargs)
        self._web_harvesters = {}
    
    def harvest_files(
        self,
        paths: List[Union[str, Path]],
        **kwargs
    ) -> HarvestResult:
        """Harvest code from files and directories.
        
        Args:
            paths: List of file/directory paths
            
        Returns:
            HarvestResult with harvested files
        """
        files = list(self.file_harvester.harvest(paths, **kwargs))
        
        return HarvestResult(
            source=", ".join(str(p) for p in paths),
            source_type="files",
            items=files,
            metadata={
                "count": len(files),
                "timestamp": time.time(),
            }
        )
    
    def harvest_repository(
        self,
        url: str,
        **kwargs
    ) -> HarvestResult:
        """Harvest code from a Git repository.
        
        Args:
            url: Repository URL
            
        Returns:
            HarvestResult with harvested repository
        """
        repo = self.repo_harvester.harvest_repository(url, **kwargs)
        
        return HarvestResult(
            source=url,
            source_type="repository",
            items=[repo],
            metadata={
                "files_count": len(repo.files),
                "commits_count": len(repo.commits),
                "timestamp": time.time(),
            }
        )
    
    def harvest(
        self,
        source: str,
        source_type: Optional[str] = None,
        **kwargs
    ) -> HarvestResult:
        """Harvest code from a source.
        
        Args:
            source: Source identifier (path, URL, etc.)
            source_type: Type of source (auto-detected if not specified)
            
        Returns:
            HarvestResult with harvested items
        """
        if source_type is None:
            source_type = self._detect_source_type(source)
        
        if source_type == "files":
            return self.harvest_files([source], **kwargs)
        elif source_type == "repository":
            return self.harvest_repository(source, **kwargs)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
    
    def _detect_source_type(self, source: str) -> str:
        """Detect source type from source string."""
        source = source.strip()
        
        # Check for Git URL
        if source.startswith(("http://", "https://", "git@")):
            if source.endswith(".git") or "/" in source:
                return "repository"
        
        # Check for local path
        if os.path.exists(source):
            if os.path.isdir(source):
                return "files"
            elif os.path.isfile(source):
                return "files"
        
        # Default to files
        return "files"
    
    def harvest_batch(
        self,
        sources: List[Union[str, Dict[str, Any]]],
        parallel: bool = False,
        **kwargs
    ) -> List[HarvestResult]:
        """Harvest from multiple sources.
        
        Args:
            sources: List of sources (strings or dicts with source and source_type)
            parallel: Whether to harvest in parallel
            
        Returns:
            List of HarvestResult objects
        """
        results = []
        
        for source in sources:
            if isinstance(source, dict):
                result = self.harvest(
                    source.get("source", ""),
                    source.get("source_type"),
                    **kwargs
                )
            else:
                result = self.harvest(source, **kwargs)
            
            results.append(result)
        
        return results
    
    def to_json(self, result: HarvestResult) -> str:
        """Convert harvest result to JSON."""
        return json.dumps(result.to_dict(), indent=2)
    
    def save(
        self,
        result: HarvestResult,
        output_path: Union[str, Path],
    ):
        """Save harvest result to file."""
        json_str = self.to_json(result)
        Path(output_path).write_text(json_str, encoding="utf-8")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CodeHarvester",
    "HarvestResult",
]
