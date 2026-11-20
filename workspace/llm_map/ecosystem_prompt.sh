#!/bin/bash
# ecosystem_prompt.sh — custom zsh prompt segment using our versioning system
REFS="$HOME/cli-synthegration/conv_repo/refs.json"
MASTER="$HOME/workspace/llm_map/master_tasks.json"

output=""

# Current branch from refs.json
if [[ -f "$REFS" ]]; then
    branch=$(jq -r '.HEAD // "?"' "$REFS" 2>/dev/null)
    [[ -n "$branch" && "$branch" != "null" ]] && output+="🌿$branch "
fi

# Pending task count from master_tasks.json
if [[ -f "$MASTER" ]]; then
    pending=$(jq -r '[.[] | select(.status=="pending")] | length' "$MASTER" 2>/dev/null)
    last=$(jq -r '[.[] | select(.ref=="PROMOTE")] | last | .title // ""' "$MASTER" 2>/dev/null)
    [[ "$last" != "null" && -n "$last" ]] && output+="✅ "
    [[ "$pending" -gt 0 ]] && output+="⬜$pending "
fi

echo -n "$output"
