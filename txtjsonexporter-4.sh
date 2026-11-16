#!/data/data/com.termux/files/usr/bin/bash
# Compact JSON exporter with hashes + metadata

pkg install -y jq coreutils > /dev/null 2>&1

OUTPUT_FILE="project_export_$(date +%Y%m%d_%H%M%S).txt"
EXPORT_DIR="/storage/emulated/0/Download/TermuxExports/_1-proj"
mkdir -p "$EXPORT_DIR"

TEMP_JSON=$(mktemp)
echo '{"structure": [], "files": {}}' > "$TEMP_JSON"

# Capture structure as array of relative paths
find _1-Projects/a -type f | sed 's|^\./||' | jq -R -s -c 'split("\n")[:-1]' \
  | jq '.structure = .' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"

# Add odds_map-n.py if present
if [[ -f "odds_map-n.py" ]]; then
  jq '.structure += ["odds_map-n.py"]' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"
fi

# Function to add file metadata (hash, size, mtime)
add_file() {
  local FILE="$1"
  local REL_PATH="${FILE#./}"
  local HASH=$(sha1sum "$FILE" | awk '{print $1}')
  local SIZE=$(stat -c%s "$FILE")
  local MTIME=$(stat -c%Y "$FILE")
  jq --arg path "$REL_PATH" \
     --arg hash "$HASH" \
     --arg size "$SIZE" \
     --arg mtime "$MTIME" \
     '.files[$path] = {hash:$hash,size:($size|tonumber),mtime:($mtime|tonumber)}' \
     "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"
}

# Process files
find _1-Projects/a -type f \( -name "*.py" -o -name "*.rs" -o -name "*.js" -o -name "*.tsx" -o -name "*.md" \) | while read -r FILE; do
  add_file "$FILE"
done

[[ -f "odds_map-n.py" ]] && add_file "odds_map-n.py"

# Finalize
mv "$TEMP_JSON" "$OUTPUT_FILE"
cp "$OUTPUT_FILE" "$EXPORT_DIR/"
rm "$OUTPUT_FILE"

echo "Compact project export → $EXPORT_DIR/$OUTPUT_FILE"
