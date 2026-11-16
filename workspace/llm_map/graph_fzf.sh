#!/bin/bash
# Interactive dependency explorer using fzf and existing graph_query.py
MAP_DIR=~/workspace/llm_map
cd "$MAP_DIR"

# List all files that have dependencies (appear in file_graph.json)
python3 -c "
import json
with open('file_graph.json') as f:
    g = json.load(f)
for node in sorted(g.keys()):
    deps = g[node]
    print(f'{node}  (imports {len(deps)})')
" | fzf --preview 'python3 ~/workspace/llm_map/graph_query.py --depends-on {1}' \
       --preview-window=right:70%:wrap \
       --bind 'enter:execute(python3 ~/workspace/llm_map/graph_query.py --depends-on {1} | less)'
