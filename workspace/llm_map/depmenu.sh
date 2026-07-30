#!/bin/bash
# Browse all files with dependencies, pick one, see its tree.
MAP_DIR=~/workspace/llm_map
cd "$MAP_DIR"
echo "Fetching files with dependencies..."
# Gather file list from file_graph.json
mapfile -t files < <(python3 -c "
import json
with open('file_graph.json') as f:
    g = json.load(f)
for node in sorted(g.keys()):
    print(node)
")
PS3="Pick a file (number): "
select f in "${files[@]}"; do
    if [[ -n "$f" ]]; then
        echo "Dependencies of $f:"
        python3 ~/workspace/llm_map/graph_query.py --depends-on "$f"
        break
    fi
done
