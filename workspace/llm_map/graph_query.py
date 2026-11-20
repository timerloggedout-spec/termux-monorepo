import json, sys
from pathlib import Path
from collections import deque
WS = Path.home()/'workspace/llm_map'
def load(): return json.load(open(WS/'file_graph.json'))
def rev(g):
    r={}
    for s,d in g.items():
        for x in d: r.setdefault(x,[]).append(s)
    return r
cmd = sys.argv[1]
g = load()
if cmd == '--depends-on':
    pattern = sys.argv[2]
    r=rev(g)
    for k in r:
        if pattern in k:  # match any part of path
            for v in r[k]: print(v)
elif cmd == '--imports-of':
    pattern = sys.argv[2]
    for k in g:
        if pattern in k:
            for v in g[k]: print(v)
elif cmd == '--path':
    s=sys.argv[2]; e=sys.argv[3]
    starts=[n for n in g if s in n]
    ends=[n for n in rev(g) if e in n]
    q=deque([(x,[x]) for x in starts])
    vis=set(starts)
    while q:
        cur,p = q.popleft()
        if cur in ends:
            print(' -> '.join(p)); break
        for nb in g.get(cur,[]):
            if nb not in vis:
                vis.add(nb); q.append((nb,p+[nb]))
    else: print('No path')
