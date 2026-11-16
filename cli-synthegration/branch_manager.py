#!/usr/bin/env python3
"""Conversation branch & knowledge-link manager."""
import sys, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
REPO = HOME / 'cli-synthegration' / 'repo'
REPO.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, fetch_sessions, get_history
sys.path.insert(0, str(HOME / 'cli-synthegration'))
from conv_versioner import ConversationDAG

def list_branches():
    branches = {}
    for session_dir in REPO.iterdir():
        if session_dir.is_dir() and (session_dir / 'HEAD.json').exists():
            dag = ConversationDAG.load(session_dir)
            if dag:
                branches[session_dir.name] = {
                    'title': dag.title,
                    'version': dag.get_version(),
                    'nodes': len(dag.nodes)
                }
    return branches

def fork_branch(source_name: str, new_name: str):
    """Create an independent copy of a conversation branch."""
    source_dir = REPO / source_name
    if not source_dir.exists():
        # find by partial match
        matches = [d.name for d in REPO.iterdir() if source_name in d.name and (d/'HEAD.json').exists()]
        if matches:
            source_dir = REPO / matches[0]
        else:
            print(f"Source branch not found: {source_name}")
            return
    new_dir = REPO / new_name
    # copy objects and HEAD
    import shutil
    shutil.copytree(source_dir, new_dir)
    head = json.loads((new_dir / 'HEAD.json').read_text())
    head['title'] = new_name
    head['timestamp'] = datetime.now(timezone.utc).isoformat()
    (new_dir / 'HEAD.json').write_text(json.dumps(head, indent=2))
    print(f"Forked {source_dir.name} -> {new_name}")

def merge_branches(source_name: str, target_name: str):
    """Merge source branch into target (union of nodes)."""
    src_dir = resolve_branch_dir(source_name)
    tgt_dir = resolve_branch_dir(target_name)
    if not src_dir or not tgt_dir:
        print("Branch not found")
        return
    src_dag = ConversationDAG.load(src_dir)
    tgt_dag = ConversationDAG.load(tgt_dir)
    diff = tgt_dag.diff(src_dag)
    added = 0
    for h in diff['added']:
        blob = src_dir / 'objects' / f'{h}.json'
        if blob.exists():
            import shutil
            shutil.copy(blob, tgt_dir / 'objects' / f'{h}.json')
            ref_data = json.loads(blob.read_text())
            tgt_dag.nodes[h] = None  # placeholder; real fix would reconstruct
            added += 1
    tgt_dag.commit(tgt_dir)
    print(f"Merged {added} new nodes from {src_dir.name} into {tgt_dir.name}")

def link_knowledge(from_branch: str, to_branch: str, link_type: str = 'reference-back'):
    """Create a semantic link between two branches."""
    links_file = REPO / 'knowledge_links.jsonl'
    link = {
        'from': from_branch,
        'to': to_branch,
        'type': link_type,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    with open(links_file, 'a') as f:
        f.write(json.dumps(link) + '\n')
    print(f"Linked: {from_branch} --[{link_type}]--> {to_branch}")

def resolve_branch_dir(name: str):
    if (REPO / name).exists():
        return REPO / name
    for d in REPO.iterdir():
        if name in d.name and (d/'HEAD.json').exists():
            return d
    return None


def list_dangling(session_filter=None, max_gap=None):
    """Find asymmetric forks where branches ended at different depths.
    
    An asymmetric fork = a parent message with 2+ children where at least one
    branch stopped short (its leaf is at a shallower depth than the longest branch).
    These are opportunities to review: should the short branch be continued, or
    was the fork resolved by the longer branch?
    
    Args:
        session_filter: only check sessions matching this substring in title
        max_gap: only show branches where depth gap >= max_gap (default: show all)
    """
    import sys
    from datetime import datetime, timezone
    from collections import deque
    
    sys.path.insert(0, str(HOME / 'deepcli'))
    from deepcli.core import get_token, fetch_sessions, get_history
    
    token = get_token()
    sessions = fetch_sessions(token)
    total_forks = 0
    total_dangling = 0
    
    for s in sessions:
        title = s.get('title', '')
        if session_filter and session_filter.lower() not in title.lower():
            continue
        
        try:
            msgs = get_history(token, s['id'])
            if not msgs or len(msgs) < 3:
                continue
        except:
            continue
        
        # Build tree with full chain tracing
        tree = {}
        for m in msgs:
            mid = str(m.get('message_id', m.get('id', '')))
            pid = m.get('parent_id')
            pid = str(pid) if pid is not None else None
            ts_raw = m.get('inserted_at', '')
            if isinstance(ts_raw, (int, float)):
                ts = str(ts_raw)[:10]
            else:
                ts = str(ts_raw)[:10] if ts_raw else ''
            tree[mid] = {
                'pid': pid,
                'role': str(m.get('role', '')),
                'kids': [],
                'ts': ts,
                'depth': 0,
                'content': (str(m.get('content', '')) or '')[:80]
            }
        
        # Link children
        for mid, node in tree.items():
            p = node['pid']
            if p and p in tree:
                tree[p]['kids'].append(mid)
        
        # BFS to set depths
        roots = [mid for mid, node in tree.items() if node['pid'] is None or node['pid'] not in tree]
        for root in roots:
            q = deque([(root, 0)])
            while q:
                nid, d = q.popleft()
                if nid in tree:
                    tree[nid]['depth'] = d
                    for child in tree[nid]['kids']:
                        q.append((child, d + 1))
        
        # Find leaf of each child branch
        def get_leaf(mid):
            node = tree.get(mid)
            if not node or not node['kids']:
                return mid
            return get_leaf(node['kids'][-1])
        
        # Find asymmetric forks
        forks = [(mid, node) for mid, node in tree.items() if len(node['kids']) >= 2]
        for mid, node in forks:
            kids = node['kids']
            leaves = [(k, get_leaf(k)) for k in kids]
            leaf_depths = {k: tree.get(leaf, {}).get('depth', 0) for k, leaf in leaves}
            max_depth = max(leaf_depths.values()) if leaf_depths else 0
            
            if len(set(leaf_depths.values())) <= 1:
                continue  # symmetrical — all branches reached same depth
            
            shorter = [(k, leaf, leaf_depths[k]) for k, leaf in leaves if leaf_depths[k] < max_depth]
            if max_gap and all(max_depth - ld < max_gap for _, _, ld in shorter):
                continue
            
            if total_forks == 0:
                print(f"{'='*70}")
                print(f"  Asymmetric Fork Report — branches that stopped short")
                print(f"{'='*70}\n")
            
            total_forks += 1
            longest_kid = max(leaf_depths, key=leaf_depths.get)
            longest_leaf = dict(leaves).get(longest_kid, '?')
            
            print(f"Session: {title[:60]}")
            print(f"  Fork at message {mid[:12]}... (depth {node['depth']}, {len(kids)} branches)")
            print(f"    Longest: {longest_kid[:12]}... → leaf at depth {max_depth}")
            
            for k, leaf, ld in shorter:
                total_dangling += 1
                leaf_node = tree.get(leaf, {})
                gap = max_depth - ld
                print(f"    Asymmetric: {k[:12]}... → leaf {leaf[:12]}...")
                print(f"      Role: {leaf_node.get('role','?')}, depth: {ld}, gap: {gap}")
                print(f"      Preview: {leaf_node.get('content','')[:80]}")
                print(f"      ↳ To continue: synthegration branch-fork {s['id'][:12]} {leaf[:12]}")
            print()
    
    print(f"Total: {total_forks} asymmetric forks, {total_dangling} shorter branches")
    print(f"Filter: {'all sessions' if not session_filter else session_filter}, gap >= {max_gap or 1}")


def message_map(session_id=None):
    """Print position → message_id mapping for a session."""
    import sys
    sys.path.insert(0, str(HOME / 'deepcli'))
    from deepcli.core import get_token, fetch_sessions, get_history
    
    token = get_token()
    if not session_id:
        sessions = fetch_sessions(token)
        for s in sessions:
            if 'Termux CLI Recon' in s.get('title',''):
                session_id = s['id']
                break
        if not session_id:
            # use first session
            sessions = fetch_sessions(token)
            session_id = sessions[0]['id'] if sessions else None
    
    if not session_id:
        print("No session found")
        return
    
    msgs = get_history(token, session_id)
    print(f"Session: {session_id}")
    print(f"Total messages: {len(msgs)}")
    print(f"{'Pos':<6} {'message_id':<20} {'role':<12} {'preview'}")
    print("-" * 80)
    for pos, m in enumerate(msgs):
        if isinstance(m, int):
            continue  # skip nested int refs
        mid = str(m.get('message_id', ''))[:20]
        role = str(m.get('role', ''))[:12]
        preview = str(m.get('content', ''))[:60].replace('\n', ' ')
        print(f"{pos+1:<6} {mid:<20} {role:<12} {preview}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        branches = list_branches()
        for name, info in sorted(branches.items()):
            print(f"{info['version'][:12]} | {info['title'][:60]} ({info['nodes']} nodes) [{name}]")
    elif cmd == 'fork':
        src = sys.argv[2]
        dst = sys.argv[3] if len(sys.argv) > 3 else f"{src}-fork-{datetime.now().strftime('%Y%m%d%H%M')}"
        fork_branch(src, dst)
    elif cmd == 'merge':
        merge_branches(sys.argv[2], sys.argv[3])
    elif cmd == 'dangling':
        list_dangling()
    elif cmd == 'message-map':
        message_map(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == 'forks':
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('--session', type=str)
        ap.add_argument('--min-gap', type=int, default=1)
        a, _ = ap.parse_known_args()
        list_dangling(session_filter=a.session, max_gap=a.min_gap)
    elif cmd == 'link':
        link_knowledge(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'reference-back')
    else:
        print("Commands: list | fork <src> [dst] | merge <src> <tgt> | link <from> <to> [type]")
