#!/bin/bash
# map-query.sh – wrap common index queries
INDEX="$HOME/workspace/llm_map/llm_index_compact.jsonl"
GRAPH="$HOME/workspace/llm_map/file_graph.json"
case "${1:-}" in
  --projects) jq -r '.pj' "$INDEX" | sort | uniq -c | sort -rn ;;
  --ast-coverage)
    total=$(wc -l < "$INDEX")
    hashes=$(jq -r 'select(.ah and .ah != []) | .p' "$INDEX" | wc -l)
    echo "$hashes/$total" ;;
  --dep-of)
    [ -n "$2" ] && jq -r --arg f "$2" '.[$f][]' "$GRAPH" 2>/dev/null || echo "Usage: map-query --dep-of <file>" ;;
  *) echo "Usage: map-query --projects|--ast-coverage|--dep-of <file>" ;;
esac
