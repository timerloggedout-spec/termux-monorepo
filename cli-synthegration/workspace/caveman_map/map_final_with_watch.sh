#!/bin/bash
# map_final_with_watch.sh – map generator + new bloat discovery
EXCLUDE_FILE="bloat_exclusions.lst"
KNOWN_PATTERNS=("node_modules" ".git" ".cache" "__pycache__" "dist" "codex/blobs" "blobs" "browser-data" ".svn" ".hg" ".tox" "vendor" "elm-stuff" ".pytest_cache" ".mypy_cache" ".ruff_cache" ".next" ".nuxt" "target" "build" ".gradle" ".idea" ".vscode")

echo ">>> DISCOVERING NEW BLOAT DIRECTORIES..."
NEW_BLOAT=""
for pattern in "${KNOWN_PATTERNS[@]}"; do
    while IFS= read -r dir; do
        if ! grep -qFx "$dir" "$EXCLUDE_FILE" 2>/dev/null; then
            echo "  NEW: $dir (matches pattern '$pattern')"
            NEW_BLOAT="$NEW_BLOAT$dir\n"
        fi
    done < <(find . -type d -iname "$pattern" -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.cache/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/browser-data/*' 2>/dev/null | sort -u)
done
if [ -z "$NEW_BLOAT" ]; then
    echo "  No new bloat directories found."
else
    echo ">>> NEW BLOAT CANDIDATES FOUND (add to $EXCLUDE_FILE? [y/N])"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo -e "$NEW_BLOAT" >> "$EXCLUDE_FILE"
        sort -u -o "$EXCLUDE_FILE" "$EXCLUDE_FILE"
        echo "  Updated $EXCLUDE_FILE. Re-run to apply exclusions."
        exit 0
    fi
fi

EXCLUDE_ARGS=()
while IFS= read -r line; do
    EXCLUDE_ARGS+=("-not" "-path" "*/$line/*")
done < <(cat "$EXCLUDE_FILE" 2>/dev/null; for p in "${KNOWN_PATTERNS[@]}"; do echo "$p"; done | sort -u)

echo ">>> BLOAT COUNTS"
for dir in node_modules .git .cache __pycache__ dist; do
    cnt=$(find . -type d -name "$dir" -exec sh -c 'find "$1" -type f | wc -l' _ {} \; 2>/dev/null | awk '{s+=$1} END{print s}')
    echo "$dir: $cnt files"
done
blob_cnt=$(find cli-synthegration/codex/blobs -name '*.blob' -type f 2>/dev/null | wc -l)
echo "codex/blobs/*.blob: $blob_cnt files"

echo ">>> FUNCTION SIGNATURES (Python)"
find deepcli deepcli-tui cli-synthegration termux-multi-agent chronos_checkout \
  -name '*.py' \
  "${EXCLUDE_ARGS[@]}" \
  -exec ast-grep -p 'def $_FUNC' --json {} \; 2>/dev/null | jq -r '.[] | "\(.file): \(.lines | split("\n")[0])"'

echo ">>> FUNCTION SIGNATURES (JavaScript/TypeScript)"
find deepseek-cli synthegration-cli \
  -name '*.js' -o -name '*.ts' \
  "${EXCLUDE_ARGS[@]}" \
  -exec ast-grep -p 'async function $_FUNC' --json {} \; 2>/dev/null | jq -r '.[] | "\(.file): \(.lines | split("\n")[0])"'
