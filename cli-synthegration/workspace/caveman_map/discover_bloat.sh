#!/bin/bash
# discover_bloat.sh – find potential bloat directories and show counts
EXCLUDE_FILE="bloat_exclusions.lst"
PATTERNS=(
    "node_modules" ".git" ".cache" "__pycache__" "dist"
    ".pytest_cache" ".mypy_cache" ".ruff_cache" ".tox" ".next" ".nuxt"
    "target" "build" ".gradle" ".idea" ".vscode" "vendor" "elm-stuff"
    ".svn" ".hg" "blobs" "codex/blobs" "browser-data" ".blob" "logs" "tmp"
)
RESULT="$(mktemp)"
for pat in "${PATTERNS[@]}"; do
    while IFS= read -r dir; do
        grep -qFx "$dir" "$EXCLUDE_FILE" 2>/dev/null && continue
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        total_size=$(du -sb "$dir" 2>/dev/null | awk '{print $1}')
        echo "$dir|$file_count files|$total_size bytes" >> "$RESULT"
    done < <(find . -type d -name "$pat" -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.cache/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/browser-data/*' 2>/dev/null | sort -u)
done

if [ ! -s "$RESULT" ]; then
    echo "No new bloat directories found."
    exit 0
fi

echo "=== CANDIDATES ==="
awk -F'|' '{printf "[%3d] %s\n\t%s\n\t%s\n", NR, $1, $2, $3}' "$RESULT"
echo "Enter numbers to add (or 'all'/'none'):"
read -r selection

if [[ "$selection" == "none" ]]; then
    echo "Nothing added."
elif [[ "$selection" == "all" ]]; then
    awk -F'|' '{print $1}' "$RESULT" >> "$EXCLUDE_FILE"
    sort -u -o "$EXCLUDE_FILE" "$EXCLUDE_FILE"
    echo "All candidates added."
else
    for num in $selection; do
        dir=$(awk -F'|' -v n="$num" 'NR==n{print $1}' "$RESULT")
        [ -n "$dir" ] && echo "$dir" >> "$EXCLUDE_FILE" && echo "Added $dir"
    done
    sort -u -o "$EXCLUDE_FILE" "$EXCLUDE_FILE"
fi
rm "$RESULT"
echo "Updated $EXCLUDE_FILE. Run map generator to apply."
