#!/usr/bin/env bash
INDEX="/data/data/com.termux/files/home/central_index.jsonl"
WHITELIST="$HOME/.monorepo/whitelist.txt"

if [[ ! -f "$INDEX" ]]; then
    echo "Caveman index not found at $INDEX. Skipping."
    exit 0
fi

# Extract all directory names from paths that are not marked bloat
python3 -c "
import json
import os

seen = set()
with open('$INDEX') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('bloat', False):
                continue
            path = data.get('path', '')
            if path:
                # take the top-level directory (first component)
                parts = path.split('/')
                if parts:
                    top = parts[0]
                    if top and top not in seen:
                        seen.add(top)
                        print(top)
        except:
            pass
" | sort -u > "$WHITELIST.tmp"

# Merge with existing whitelist (if any)
if [[ -f "$WHITELIST" ]]; then
    cat "$WHITELIST" "$WHITELIST.tmp" | sort -u > "$WHITELIST.merged"
    mv "$WHITELIST.merged" "$WHITELIST"
else
    mv "$WHITELIST.tmp" "$WHITELIST"
fi

echo "Whitelist generated from Caveman index: $(wc -l < $WHITELIST) entries"
