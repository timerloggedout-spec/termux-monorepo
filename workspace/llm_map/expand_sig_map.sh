#!/bin/bash
# expand_sig_map.sh – regenerate full_map_output.txt from ALL indexed source files
INDEX="$HOME/workspace/llm_map/llm_index_compact.jsonl"
OUT="$HOME/workspace/llm_map/full_map_output.txt"

> "$OUT"

jq -r '.p' "$INDEX" | grep -E '\.(py|js|ts|sh|mjs|rs)$' | while read -r f; do
    full_path="$HOME/$f"
    [ -f "$full_path" ] || continue
    # Extract signatures – NO line numbers
    grep -E '^\s*(def |class |async function |function )' "$full_path" 2>/dev/null | \
    while read -r sig; do
        echo "${f}:${sig}"
    done
done >> "$OUT"

echo "Signature map updated: $(wc -l < "$OUT") lines"
