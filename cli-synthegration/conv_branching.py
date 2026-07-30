#!/usr/bin/env python3
"""Branching conversation DAG: fork, merge, branch pointer management."""
import sys, json, hashlib, time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

sys.path.insert(0, str(Path.home() / 'cli-synthegration'))
from conv_versioner import ConversationDAG, MessageRef

class BranchRef:
    """Named pointer to a DAG version, like a Git branch."""
    __slots__ = ('name', 'session_id', 'version_hash', 'parent_branch', 'created_at')
    
    def __init__(self, name: str, session_id: str, version_hash: str, parent_branch: str = None):
        self.name = name
        self.session_id = session_id
        self.version_hash = version_hash
        self.parent_branch = parent_branch
        self.created_at = datetime.now(timezone.utc).isoformat()

class ConversationRepo:
    """Git‑style repo for conversation DAGs with branching."""
    
    def __init__(self, repo_path: Path = None):
        self.path = repo_path or Path.home() / 'cli-synthegration' / 'conv_repo'
        self.path.mkdir(parents=True, exist_ok=True)
        self.branches: Dict[str, BranchRef] = {}
        self.current_branch: Optional[str] = None
        self._load_refs()
    
    def _load_refs(self):
        refs_file = self.path / 'refs.json'
        if refs_file.exists():
            data = json.loads(refs_file.read_text())
            for br_data in data.get('branches', []):
                br = BranchRef(
                    br_data['name'], br_data['session_id'],
                    br_data['version_hash'], br_data.get('parent_branch')
                )
                self.branches[br.name] = br
            self.current_branch = data.get('HEAD')
    
    def _save_refs(self):
        refs = {
            'HEAD': self.current_branch,
            'branches': [
                {'name': b.name, 'session_id': b.session_id,
                 'version_hash': b.version_hash, 'parent_branch': b.parent_branch,
                 'created_at': b.created_at}
                for b in self.branches.values()
            ]
        }
        (self.path / 'refs.json').write_text(json.dumps(refs, indent=2))
    
    def create_branch(self, name: str, session_id: str, parent_branch: str = None) -> BranchRef:
        """Fork a new branch from an existing session."""
        dag = ConversationDAG.load(self.path / 'sessions' / session_id)
        if not dag:
            dag = ConversationDAG(session_id, f"Branch: {name}")
        version = dag.get_version()
        dag.commit(self.path / 'sessions' / session_id)
        
        # If parent branch specified, link knowledge
        parent_ref = self.branches.get(parent_branch) if parent_branch else None
        br = BranchRef(name, session_id, version, parent_branch)
        self.branches[name] = br
        self.current_branch = name
        self._save_refs()
        return br
    
    def merge_branches(self, source: str, target: str, merge_strategy: str = "dedup") -> str:
        """Merge two branches. Strategy: 'dedup' (skip duplicates) or 'rebase'."""
        src_br = self.branches.get(source)
        tgt_br = self.branches.get(target)
        if not src_br or not tgt_br:
            raise ValueError(f"Branch not found: {source or target}")
        
        src_dag = ConversationDAG.load(self.path / 'sessions' / src_br.session_id)
        tgt_dag = ConversationDAG.load(self.path / 'sessions' / tgt_br.session_id)
        
        if merge_strategy == "dedup":
            # Copy missing nodes from source to target
            added = 0
            for h, ref in src_dag.nodes.items():
                if h not in tgt_dag.nodes:
                    tgt_dag.nodes[h] = ref
                    if ref.parent_id and ref.parent_id in src_dag.id_to_hash:
                        parent_h = src_dag.id_to_hash[ref.parent_id]
                        tgt_dag.edges.setdefault(parent_h, []).append(h)
                    elif not ref.parent_id:
                        tgt_dag.roots.append(h)
                    added += 1
            tgt_dag.id_to_hash.update(src_dag.id_to_hash)
        elif merge_strategy == "rebase":
            # Replay all source messages onto target
            for h, ref in src_dag.nodes.items():
                tgt_dag.nodes[h] = ref
            tgt_dag.edges.update(src_dag.edges)
            tgt_dag.roots = list(set(tgt_dag.roots + src_dag.roots))
        
        new_version = tgt_dag.get_version()
        tgt_dag.commit(self.path / 'sessions' / tgt_br.session_id)
        tgt_br.version_hash = new_version
        self._save_refs()
        return new_version
    
    def a_b_test(self, base_branch: str, variant_a: str, variant_b: str, 
                 session_a: str, session_b: str) -> Dict:
        """Create an A/B test by forking a base branch into two variants."""
        base = self.branches.get(base_branch)
        if not base:
            raise ValueError(f"Base branch not found: {base_branch}")
        br_a = self.create_branch(variant_a, session_a, base_branch)
        br_b = self.create_branch(variant_b, session_b, base_branch)
        return {
            'base': base.version_hash,
            'variant_a': {'branch': variant_a, 'version': br_a.version_hash},
            'variant_b': {'branch': variant_b, 'version': br_b.version_hash}
        }
    
    def link_knowledge(self, from_branch: str, to_branch: str, link_type: str = "reference"):
        """Create a semantic link between branches (knowledge graph edge)."""
        links_file = self.path / 'knowledge_links.jsonl'
        link = {
            'from': from_branch,
            'to': to_branch,
            'type': link_type,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        with open(links_file, 'a') as f:
            f.write(json.dumps(link) + '\n')
        return link
    
    def list_branches(self):
        """Return all branches with metadata."""
        results = []
        for name, br in self.branches.items():
            dag = ConversationDAG.load(self.path / 'sessions' / br.session_id)
            node_count = len(dag.nodes) if dag else 0
            results.append({
                'name': name,
                'session_id': br.session_id,
                'version': br.version_hash[:12],
                'nodes': node_count,
                'parent': br.parent_branch,
                'created': br.created_at
            })
        return sorted(results, key=lambda x: x['created'], reverse=True)

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path.home() / 'deepcli'))
    from deepcli.core import get_token, fetch_sessions, get_history
    
    repo = ConversationRepo()
    token = get_token()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            for b in repo.list_branches():
                print(f"{b['name']:30s} | {b['version']} | {b['nodes']:3d} nodes | parent: {b['parent']}")
        elif cmd == "fork" and len(sys.argv) > 2:
            name = sys.argv[2]
            parent = sys.argv[3] if len(sys.argv) > 3 else None
            sessions = fetch_sessions(token)
            if sessions:
                sid = sessions[0]['id']
                br = repo.create_branch(name, sid, parent)
                print(f"Created branch '{name}' → {br.version_hash[:12]}")
        elif cmd == "merge" and len(sys.argv) > 3:
            version = repo.merge_branches(sys.argv[2], sys.argv[3])
            print(f"Merged {sys.argv[2]} into {sys.argv[3]} → {version[:12]}")
        elif cmd == "link" and len(sys.argv) > 3:
            repo.link_knowledge(sys.argv[2], sys.argv[3])
            print(f"Linked {sys.argv[2]} ↔ {sys.argv[3]}")
    else:
        # Auto‑create branches from first 5 live sessions
        sessions = fetch_sessions(token)[:5]
        for i, s in enumerate(sessions):
            name = s.get('title', f'branch-{i}')[:30].replace(' ', '-')
            br = repo.create_branch(name, s['id'])
            print(f"Imported: {name} → {br.version_hash[:12]}")
