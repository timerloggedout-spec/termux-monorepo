#!/usr/bin/env python3
"""Find optimal refocus messages to edit/continue from – the 'loop' prompt."""
import sys, json
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
sys.path.insert(0, str(HOME / 'cli-synthegration'))
sys.path.insert(0, str(HOME / 'deepcli'))
from deepcli.core import get_token, fetch_sessions, get_history
from success_metrics import RefactorELO
from branch_manager import list_dangling

def find_loop_candidates(session_filter=None, top_n=5):
    """Find the best messages to branch from, ranked by ELO + asymmetry gap."""
    elo = RefactorELO()
    token = get_token()
    sessions = fetch_sessions(token)
    candidates = []
    
    for s in sessions:
        title = s.get('title','')
        if session_filter and session_filter.lower() not in title.lower():
            continue
        try:
            msgs = get_history(token, s['id'])
            if not msgs or len(msgs) < 3:
                continue
        except:
            continue
        
        # Build tree, find fork points
        tree = {}
        for m in msgs:
            mid = str(m.get('message_id', m.get('id','')))
            pid = m.get('parent_id')
            pid = str(pid) if pid is not None else None
            tree[mid] = {
                'pid': pid, 'role': str(m.get('role','')),
                'kids': [], 'depth': 0,
                'content': (str(m.get('content','')) or '')[:120],
                'ts': m.get('inserted_at','')
            }
        for mid, node in tree.items():
            p = node['pid']
            if p and p in tree:
                tree[p]['kids'].append(mid)
        
        # BFS for depths
        from collections import deque
        roots = [m for m,n in tree.items() if n['pid'] is None or n['pid'] not in tree]
        for r in roots:
            q = deque([(r,0)])
            while q:
                nid, d = q.popleft()
                if nid in tree:
                    tree[nid]['depth'] = d
                    for c in tree[nid]['kids']:
                        q.append((c, d+1))
        
        # Rank fork points by asymmetry gap
        for mid, node in tree.items():
            kids = node['kids']
            if len(kids) < 2:
                continue
            # Get depths of leaves for each child
            def leaf_depth(kid):
                n = tree.get(kid)
                if not n or not n['kids']:
                    return tree.get(kid,{}).get('depth',0)
                return max(leaf_depth(c) for c in n['kids'])
            depths = {k: leaf_depth(k) for k in kids}
            max_d = max(depths.values())
            min_d = min(depths.values())
            gap = max_d - min_d
            
            # ELO boost for patterns in the message content
            prompt = node.get('content','')
            ph = elo.pattern_hash(prompt, 'investigation')
            elo_rating = elo.ratings.get(ph, 1200)
            
            score = gap * 10 + (elo_rating - 1200) * 0.1
            candidates.append({
                'session_id': s['id'][:12],
                'title': title[:60],
                'message_id': mid,
                'depth': node['depth'],
                'gap': gap,
                'elo': elo_rating,
                'score': score,
                'preview': node.get('content','')[:80]
            })
    
    candidates.sort(key=lambda x: -x['score'])
    return candidates[:top_n]

if __name__ == '__main__':
    candidates = find_loop_candidates()
    print(f"{'Score':<8} {'Gap':<6} {'ELO':<8} {'Session':<14} {'Message ID':<12} {'Preview'}")
    print("-" * 90)
    for c in candidates:
        print(f"{c['score']:<8.1f} {c['gap']:<6} {c['elo']:<8.0f} {c['session_id']:<14} {c['message_id'][:12]:<12} {c['preview'][:50]}")
    print(f"\nGenerated: {datetime.now(timezone.utc).isoformat()}")
    print("Use: synthegration loop --session-id <id> --parent-id <message_id>")
