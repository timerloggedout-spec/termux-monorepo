#!/bin/bash
# Usage: depgraph.sh deepcli/core.py
if [ -z "$1" ]; then
    echo "Usage: depgraph <file-path>"
    exit 1
fi
python3 ~/workspace/llm_map/graph_query.py --depends-on "$1"
