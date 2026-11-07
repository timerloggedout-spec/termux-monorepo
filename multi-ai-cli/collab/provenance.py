#!/usr/bin/env python3
"""Provenance Reconciliation - Track and reconcile provenance across integrations.

This module provides:
- Provenance tracking for all operations
- Reconciliation across Colab, AI Studio, ChapitoAI
- GitHub Actions integration
- Termux CLI tracking
- Audit logging
"""

import os
import sys
import json
import time
import hashlib
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class ProvenanceRecord:
    """Represents a provenance record."""
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    operation: str
    source: str
    target: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""
    parent_hashes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Compute hash after initialization."""
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute hash of record."""
        data_str = json.dumps({
            "operation": self.operation,
            "source": self.source,
            "target": self.target,
            "data": self.data,
            "metadata": self.metadata,
            "parent_hashes": self.parent_hashes,
        }, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "timestamp_iso": datetime.fromtimestamp(self.timestamp).isoformat(),
            "operation": self.operation,
            "source": self.source,
            "target": self.target,
            "data": self.data,
            "metadata": self.metadata,
            "hash": self.hash,
            "parent_hashes": self.parent_hashes,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ReconciliationResult:
    """Result of provenance reconciliation."""
    success: bool
    records: List[ProvenanceRecord] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "records": [r.to_dict() for r in self.records],
            "conflicts": self.conflicts,
            "missing": self.missing,
            "duration": self.duration,
            "metadata": self.metadata,
        }


class ProvenanceTracker:
    """Track provenance across all integrations.
    
    This tracker provides:
    - Provenance recording
    - Lineage tracking
    - Cross-integration reconciliation
    - Audit trail
    """
    
    def __init__(
        self,
        storage_path: Optional[Union[str, Path]] = None,
        auto_save: bool = True,
        **kwargs
    ):
        """Initialize provenance tracker.
        
        Args:
            storage_path: Path to store provenance records
            auto_save: Whether to auto-save records
        """
        self.storage_path = Path(storage_path or (Path.home() / ".multi-ai-cli" / "provenance"))
        self.auto_save = auto_save
        self._records: Dict[str, ProvenanceRecord] = {}
        self._index: Dict[str, List[str]] = {}
        self._loaded = False
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _ensure_loaded(self):
        """Ensure records are loaded from storage."""
        if not self._loaded:
            self._load_records()
            self._loaded = True
    
    def _load_records(self):
        """Load records from storage."""
        for record_file in self.storage_path.glob("*.json"):
            try:
                with open(record_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    record = ProvenanceRecord(**data)
                    self._records[record.record_id] = record
                    self._index_record(record)
            except Exception as e:
                print(f"Error loading record {record_file}: {e}", file=sys.stderr)
    
    def _index_record(self, record: ProvenanceRecord):
        """Index a record for fast lookup."""
        # Index by operation
        if record.operation not in self._index:
            self._index[record.operation] = []
        self._index[record.operation].append(record.record_id)
        
        # Index by source
        if record.source not in self._index:
            self._index[record.source] = []
        self._index[record.source].append(record.record_id)
        
        # Index by target
        if record.target not in self._index:
            self._index[record.target] = []
        self._index[record.target].append(record.record_id)
        
        # Index by hash
        if record.hash not in self._index:
            self._index[record.hash] = []
        self._index[record.hash].append(record.record_id)
        
        # Index parent hashes
        for parent_hash in record.parent_hashes:
            key = f"parent:{parent_hash}"
            if key not in self._index:
                self._index[key] = []
            self._index[key].append(record.record_id)
    
    def _save_record(self, record: ProvenanceRecord):
        """Save a record to storage."""
        if not self.auto_save:
            return
        
        record_path = self.storage_path / f"{record.record_id}.json"
        record_path.write_text(record.to_json(), encoding="utf-8")
        
        # Set permissions
        if not record_path.is_symlink():
            try:
                record_path.chmod(0o600)
            except Exception:
                pass
    
    def record(
        self,
        operation: str,
        source: str,
        target: str,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_hashes: Optional[List[str]] = None,
    ) -> ProvenanceRecord:
        """Record a provenance event.
        
        Args:
            operation: Operation type
            source: Source identifier
            target: Target identifier
            data: Operation data
            metadata: Additional metadata
            parent_hashes: Parent record hashes
            
        Returns:
            ProvenanceRecord
        """
        self._ensure_loaded()
        
        record = ProvenanceRecord(
            operation=operation,
            source=source,
            target=target,
            data=data or {},
            metadata=metadata or {},
            parent_hashes=parent_hashes or [],
        )
        
        self._records[record.record_id] = record
        self._index_record(record)
        self._save_record(record)
        
        return record
    
    def record_colab_operation(
        self,
        operation: str,
        notebook_id: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ProvenanceRecord:
        """Record a Colab operation.
        
        Args:
            operation: Operation type
            notebook_id: Colab notebook ID
            data: Operation data
            
        Returns:
            ProvenanceRecord
        """
        return self.record(
            operation=f"colab:{operation}",
            source="colab",
            target=notebook_id,
            data=data or {},
            metadata={"integration": "colab", **kwargs},
        )
    
    def record_ai_studio_operation(
        self,
        operation: str,
        model: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ProvenanceRecord:
        """Record an AI Studio operation.
        
        Args:
            operation: Operation type
            model: AI Studio model
            data: Operation data
            
        Returns:
            ProvenanceRecord
        """
        return self.record(
            operation=f"ai_studio:{operation}",
            source="ai_studio",
            target=model,
            data=data or {},
            metadata={"integration": "ai_studio", "model": model, **kwargs},
        )
    
    def record_chapito_operation(
        self,
        operation: str,
        chatbot: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ProvenanceRecord:
        """Record a ChapitoAI operation.
        
        Args:
            operation: Operation type
            chatbot: ChapitoAI chatbot
            data: Operation data
            
        Returns:
            ProvenanceRecord
        """
        return self.record(
            operation=f"chapito:{operation}",
            source="chapito",
            target=chatbot,
            data=data or {},
            metadata={"integration": "chapito", "chatbot": chatbot, **kwargs},
        )
    
    def record_github_actions_operation(
        self,
        operation: str,
        workflow: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ProvenanceRecord:
        """Record a GitHub Actions operation.
        
        Args:
            operation: Operation type
            workflow: Workflow name
            data: Operation data
            
        Returns:
            ProvenanceRecord
        """
        return self.record(
            operation=f"github_actions:{operation}",
            source="github_actions",
            target=workflow,
            data=data or {},
            metadata={"integration": "github_actions", "workflow": workflow, **kwargs},
        )
    
    def record_termux_operation(
        self,
        operation: str,
        command: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ProvenanceRecord:
        """Record a Termux operation.
        
        Args:
            operation: Operation type
            command: Termux command
            data: Operation data
            
        Returns:
            ProvenanceRecord
        """
        return self.record(
            operation=f"termux:{operation}",
            source="termux",
            target=command,
            data=data or {},
            metadata={"integration": "termux", "command": command, **kwargs},
        )
    
    def get_record(self, record_id: str) -> Optional[ProvenanceRecord]:
        """Get a provenance record.
        
        Args:
            record_id: Record ID
            
        Returns:
            ProvenanceRecord or None
        """
        self._ensure_loaded()
        return self._records.get(record_id)
    
    def query_records(
        self,
        operation: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        since: Optional[float] = None,
        until: Optional[float] = None,
        limit: int = 100,
    ) -> List[ProvenanceRecord]:
        """Query provenance records.
        
        Args:
            operation: Filter by operation
            source: Filter by source
            target: Filter by target
            since: Start timestamp
            until: End timestamp
            limit: Maximum number of records
            
        Returns:
            List of matching records
        """
        self._ensure_loaded()
        
        results = []
        
        for record in self._records.values():
            # Apply filters
            if operation and record.operation != operation:
                continue
            if source and record.source != source:
                continue
            if target and record.target != target:
                continue
            if since and record.timestamp < since:
                continue
            if until and record.timestamp > until:
                continue
            
            results.append(record)
            
            if len(results) >= limit:
                break
        
        # Sort by timestamp
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        return results
    
    def get_lineage(self, record_id: str, depth: int = 5) -> List[ProvenanceRecord]:
        """Get lineage for a record.
        
        Args:
            record_id: Record ID
            depth: Maximum depth to traverse
            
        Returns:
            List of ancestor records
        """
        self._ensure_loaded()
        
        record = self.get_record(record_id)
        if not record:
            return []
        
        lineage = [record]
        visited = {record.record_id}
        
        for parent_hash in record.parent_hashes:
            parent_records = self._index.get(f"hash:{parent_hash}", [])
            for parent_id in parent_records:
                if parent_id not in visited:
                    parent = self.get_record(parent_id)
                    if parent:
                        lineage.append(parent)
                        visited.add(parent.record_id)
                        
                        # Recursively get ancestors
                        if depth > 1:
                            ancestors = self.get_lineage(parent.record_id, depth - 1)
                            for ancestor in ancestors:
                                if ancestor.record_id not in visited:
                                    lineage.append(ancestor)
                                    visited.add(ancestor.record_id)
        
        # Sort by timestamp
        lineage.sort(key=lambda x: x.timestamp)
        
        return lineage
    
    def get_children(self, record_id: str, depth: int = 5) -> List[ProvenanceRecord]:
        """Get children for a record.
        
        Args:
            record_id: Record ID
            depth: Maximum depth to traverse
            
        Returns:
            List of child records
        """
        self._ensure_loaded()
        
        record = self.get_record(record_id)
        if not record:
            return []
        
        children = []
        visited = {record.record_id}
        queue = [record]
        
        for _ in range(depth):
            new_queue = []
            for current in queue:
                child_ids = self._index.get(f"parent:{current.hash}", [])
                for child_id in child_ids:
                    if child_id not in visited:
                        child = self.get_record(child_id)
                        if child:
                            children.append(child)
                            visited.add(child.record_id)
                            new_queue.append(child)
            
            if not new_queue:
                break
            queue = new_queue
        
        # Sort by timestamp
        children.sort(key=lambda x: x.timestamp)
        
        return children
    
    def reconcile(
        self,
        sources: Optional[List[str]] = None,
        targets: Optional[List[str]] = None,
        since: Optional[float] = None,
    ) -> ReconciliationResult:
        """Reconcile provenance across sources and targets.
        
        Args:
            sources: List of source identifiers
            targets: List of target identifiers
            since: Start timestamp
            
        Returns:
            ReconciliationResult
        """
        start_time = time.time()
        
        self._ensure_loaded()
        
        # Get all relevant records
        records = []
        for record in self._records.values():
            if since and record.timestamp < since:
                continue
            if sources and record.source not in sources:
                continue
            if targets and record.target not in targets:
                continue
            records.append(record)
        
        # Sort by timestamp
        records.sort(key=lambda x: x.timestamp)
        
        # Check for conflicts
        conflicts = []
        seen_targets = {}
        
        for record in records:
            key = f"{record.source}:{record.target}"
            if key in seen_targets:
                conflicts.append({
                    "type": "duplicate_target",
                    "target": record.target,
                    "source": record.source,
                    "records": [seen_targets[key], record.record_id],
                })
            else:
                seen_targets[key] = record.record_id
        
        # Check for missing dependencies
        missing = []
        all_hashes = {r.hash for r in records}
        
        for record in records:
            for parent_hash in record.parent_hashes:
                if parent_hash not in all_hashes:
                    missing.append(parent_hash)
        
        return ReconciliationResult(
            success=len(conflicts) == 0 and len(missing) == 0,
            records=records,
            conflicts=conflicts,
            missing=list(set(missing)),
            duration=time.time() - start_time,
            metadata={
                "record_count": len(records),
                "conflict_count": len(conflicts),
                "missing_count": len(missing),
            }
        )
    
    def export_records(
        self,
        output_path: Union[str, Path],
        since: Optional[float] = None,
        until: Optional[float] = None,
    ) -> bool:
        """Export provenance records to file.
        
        Args:
            output_path: Output file path
            since: Start timestamp
            until: End timestamp
            
        Returns:
            True if successful
        """
        self._ensure_loaded()
        
        records = self.query_records(since=since, until=until)
        
        data = {
            "export_timestamp": time.time(),
            "export_timestamp_iso": datetime.now().isoformat(),
            "records": [r.to_dict() for r in records],
            "count": len(records),
        }
        
        Path(output_path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        
        return True
    
    def clear(self, before: Optional[float] = None) -> int:
        """Clear provenance records.
        
        Args:
            before: Clear records before this timestamp (None = clear all)
            
        Returns:
            Number of records cleared
        """
        self._ensure_loaded()
        
        cleared = 0
        
        for record_id, record in list(self._records.items()):
            if before and record.timestamp >= before:
                continue
            
            # Remove from index
            self._remove_from_index(record)
            
            # Remove from storage
            record_path = self.storage_path / f"{record_id}.json"
            if record_path.exists():
                record_path.unlink()
            
            # Remove from memory
            del self._records[record_id]
            cleared += 1
        
        return cleared
    
    def _remove_from_index(self, record: ProvenanceRecord):
        """Remove a record from the index."""
        # Remove from operation index
        if record.operation in self._index:
            if record.record_id in self._index[record.operation]:
                self._index[record.operation].remove(record.record_id)
        
        # Remove from source index
        if record.source in self._index:
            if record.record_id in self._index[record.source]:
                self._index[record.source].remove(record.record_id)
        
        # Remove from target index
        if record.target in self._index:
            if record.record_id in self._index[record.target]:
                self._index[record.target].remove(record.record_id)
        
        # Remove from hash index
        if record.hash in self._index:
            if record.record_id in self._index[record.hash]:
                self._index[record.hash].remove(record.record_id)
        
        # Remove from parent hash indices
        for parent_hash in record.parent_hashes:
            key = f"parent:{parent_hash}"
            if key in self._index:
                if record.record_id in self._index[key]:
                    self._index[key].remove(record.record_id)


# =============================================================================
# Global Provenance Tracker
# =============================================================================

_default_tracker: Optional[ProvenanceTracker] = None


def get_provenance_tracker(
    storage_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> ProvenanceTracker:
    """Get the default provenance tracker.
    
    Args:
        storage_path: Storage path
        
    Returns:
        ProvenanceTracker instance
    """
    global _default_tracker
    
    if _default_tracker is None or storage_path or kwargs:
        _default_tracker = ProvenanceTracker(
            storage_path=storage_path,
            **kwargs
        )
    
    return _default_tracker


def record_operation(
    operation: str,
    source: str,
    target: str,
    **kwargs
) -> ProvenanceRecord:
    """Record a provenance operation.
    
    Args:
        operation: Operation type
        source: Source identifier
        target: Target identifier
        
    Returns:
        ProvenanceRecord
    """
    tracker = get_provenance_tracker()
    return tracker.record(operation, source, target, **kwargs)


# =============================================================================
# Decorators for Automatic Provenance Tracking
# =============================================================================

def track_provenance(
    operation: str,
    source: str = "",
    target_param: str = "",
):
    """Decorator to automatically track provenance.
    
    Args:
        operation: Operation type
        source: Source identifier
        target_param: Parameter name containing target
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_provenance_tracker()
            
            # Get target from parameter
            target = ""
            if target_param:
                if target_param in kwargs:
                    target = kwargs[target_param]
                elif len(args) > 0:
                    # Try to get from args based on function signature
                    import inspect
                    sig = inspect.signature(func)
                    params = list(sig.parameters.keys())
                    if target_param in params:
                        idx = params.index(target_param)
                        if idx < len(args):
                            target = args[idx]
            
            # Get parent hashes from context
            parent_hashes = kwargs.get("parent_hashes", [])
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Record provenance
            tracker.record(
                operation=operation,
                source=source,
                target=target or str(result),
                data={"result": str(result)[:1000]},
                parent_hashes=parent_hashes,
            )
            
            return result
        
        return wrapper
    return decorator


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ProvenanceTracker",
    "ProvenanceRecord",
    "ReconciliationResult",
    "get_provenance_tracker",
    "record_operation",
    "track_provenance",
]
