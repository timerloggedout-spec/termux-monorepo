#!/usr/bin/env python3
"""Conversation DAG versioning – C++ style pointers, content‑addressed dedup."""
import json, hashlib, re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

class MessageRef:
    """Pointer to a message – like C++ reference with integrity hash."""
    __slots__ = ('message_id', 'parent_id', 'role', 'content_hash', 'timestamp')
    
    def __init__(self, msg: Dict[str, Any]):
        self.message_id = msg.get('id', msg.get('message_id', ''))
        self.parent_id = msg.get('parent_message_id')
        self.role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        self.content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        self.timestamp = msg.get('inserted_at', msg.get('timestamp', ''))
    
    def to_ref(self) -> str:
        """Return a git‑style reference: content_hash + pointer."""
        return f"msg:{self.message_id}→{self.content_hash}"

class ConversationDAG:
    """Directed acyclic graph of messages, indexed by hash for O(1) dedup."""
    
    def __init__(self, session_id: str, title: str = ""):
        self.session_id = session_id
        self.title = title
        self.nodes: Dict[str, MessageRef] = {}  # content_hash → ref
        self.edges: Dict[str, List[str]] = {}   # parent_hash → [child_hashes]
        self.id_to_hash: Dict[str, str] = {}    # message_id → content_hash
        self.roots: List[str] = []              # messages with no parent
        self.dup_map: Dict[str, str] = {}       # duplicate_hash → canonical_hash
    
    def add_message(self, msg: Dict[str, Any]) -> Optional[str]:
        """Add a message; return its content_hash or None if duplicate."""
        ref = MessageRef(msg)
        h = ref.content_hash
        # Dedup: if same content already exists, just note the pointer
        if h in self.nodes:
            self.dup_map[ref.message_id] = h
            return None
        self.nodes[h] = ref
        self.id_to_hash[ref.message_id] = h
        # Build edges
        if ref.parent_id and ref.parent_id in self.id_to_hash:
            parent_hash = self.id_to_hash[ref.parent_id]
            self.edges.setdefault(parent_hash, []).append(h)
        elif not ref.parent_id or ref.parent_id not in self.id_to_hash:
            self.roots.append(h)
        return h
    
    def get_version(self) -> str:
        """Composite version hash (like a Merkle root)."""
        payload = json.dumps({
            'session': self.session_id,
            'nodes': sorted(self.nodes.keys()),
            'edges': {k: sorted(v) for k, v in sorted(self.edges.items())},
            'roots': sorted(self.roots)
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
    
    def diff(self, other: 'ConversationDAG') -> Dict[str, List[str]]:
        """Compute diff between two DAGs – returns added, removed, modified."""
        my_hashes = set(self.nodes.keys())
        other_hashes = set(other.nodes.keys())
        return {
            'added': list(other_hashes - my_hashes),
            'removed': list(my_hashes - other_hashes),
            'modified': [h for h in (my_hashes & other_hashes)
                        if self.nodes[h].content_hash != other.nodes[h].content_hash]
        }
    
    def commit(self, repo_dir: Path) -> str:
        """Persist DAG to repo_dir/objects/ and return version hash."""
        objects = repo_dir / 'objects'
        objects.mkdir(parents=True, exist_ok=True)
        version = self.get_version()
        # Store each message as blob
        for h, ref in self.nodes.items():
            (objects / f"{h}.json").write_text(json.dumps({
                'message_id': ref.message_id,
                'parent_id': ref.parent_id,
                'role': ref.role,
                'content_hash': ref.content_hash,
                'timestamp': ref.timestamp
            }))
        # Store DAG index
        index = {
            'session_id': self.session_id,
            'title': self.title,
            'version': version,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'nodes': list(self.nodes.keys()),
            'edges': {k: v for k, v in self.edges.items()},
            'roots': self.roots,
            'id_to_hash': self.id_to_hash,
            'duplicates': self.dup_map
        }
        (repo_dir / 'HEAD.json').write_text(json.dumps(index, indent=2))
        return version
    
    @classmethod
    def load(cls, repo_dir: Path) -> Optional['ConversationDAG']:
        """Load a persisted DAG."""
        head = repo_dir / 'HEAD.json'
        if not head.exists():
            return None
        index = json.loads(head.read_text())
        dag = cls(index['session_id'], index['title'])
        dag.nodes = {}
        dag.edges = index['edges']
        dag.roots = index['roots']
        dag.id_to_hash = index['id_to_hash']
        dag.dup_map = index.get('duplicates', {})
        for h in index['nodes']:
            blob = repo_dir / 'objects' / f'{h}.json'
            if blob.exists():
                ref_data = json.loads(blob.read_text())
                dag.nodes[h] = MessageRef({
                    'id': ref_data['message_id'],
                    'parent_message_id': ref_data['parent_id'],
                    'role': ref_data['role'],
                    'content': '',  # content not stored in blob, only hash
                })
        return dag
    
    def to_graphviz(self) -> str:
        """Export as Graphviz DOT for visualization."""
        lines = ['digraph Conversation {', '  rankdir=LR;', f'  label="{self.title}";']
        for h, ref in self.nodes.items():
            label = f"{ref.role}:{h[:6]}"
            lines.append(f'  "{h}" [label="{label}"];')
        for parent, children in self.edges.items():
            for child in children:
                lines.append(f'  "{parent}" -> "{child}";')
        lines.append('}')
        return '\n'.join(lines)
