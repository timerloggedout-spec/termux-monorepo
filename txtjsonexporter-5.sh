#!/data/data/com.termux/files/usr/bin/bash
# Compact JSON exporter with optional auto-diff

pkg install -y jq coreutils > /dev/null 2>&1

EXPORT_DIR="/storage/emulated/0/Download/TermuxExports/_1-proj"
mkdir -p "$EXPORT_DIR"

MODE="export"
[[ "$1" == "--diff" ]] && MODE="diff"

timestamp=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="project_export_${timestamp}.txt"
TEMP_JSON=$(mktemp)

# Always work from repo root
cd "$HOME" || exit 1

# Build initial JSON with structure array
STRUCTURE=$(find ./_1-Projects/a -type f | sed 's|^\./||')
if [[ -f "./odds_map-n.py" ]]; then
  STRUCTURE="$STRUCTURE"$'\n'"odds_map-n.py"
fi

printf '%s\n' "$STRUCTURE" | jq -R -s -c '{structure: split("\n")[:-1], files:{}}' > "$TEMP_JSON"

# Function to add file metadata
add_file() {
  local FILE="$1"
  local REL_PATH="${FILE#./}"
  local HASH=$(sha1sum "$FILE" | awk '{print $1}')
  local SIZE=$(stat -c%s "$FILE")
  local MTIME=$(stat -c%Y "$FILE")
  jq --arg path "$REL_PATH" \
     --arg hash "$HASH" \
     --argjson size "$SIZE" \
     --argjson mtime "$MTIME" \
     '.files[$path] = {hash:$hash,size:$size,mtime:$mtime}' \
     "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"
}

# Process files
find ./_1-Projects/a -type f \( -name "*.py" -o -name "*.rs" -o -name "*.js" -o -name "*.tsx" -o -name "*.md" -o -name "*.html" -o -name "*.json" \) \
  | while read -r FILE; do
  add_file "$FILE"
done
[[ -f "./odds_map-n.py" ]] && add_file "./odds_map-n.py"

if [[ "$MODE" == "export" ]]; then
  mv "$TEMP_JSON" "$OUTPUT_FILE"
  cp "$OUTPUT_FILE" "$EXPORT_DIR/"
  rm "$OUTPUT_FILE"
  echo "Exported → $EXPORT_DIR/$OUTPUT_FILE"

elif [[ "$MODE" == "diff" ]]; then
  LAST_EXPORT=$(ls -t "$EXPORT_DIR"/project_export_*.txt 2>/dev/null | head -n1)
  if [[ -z "$LAST_EXPORT" ]]; then
    echo "No previous export found in $EXPORT_DIR"
    exit 1
  fi
  echo "Diffing against $LAST_EXPORT"
  jq -s '
    def diff(a;b):
      reduce (a.files|to_entries[]) as $f ({}; .[$f.key] =
        if (b.files[$f.key]|not) then {status:"removed",old:$f.value}
        elif (b.files[$f.key].hash != $f.value.hash) then {status:"changed",old:$f.value,new:b.files[$f.key]}
        else empty end
      ) +
      reduce (b.files|to_entries[]) as $f (.;
        if (a.files[$f.key]|not) then .[$f.key] = {status:"added",new:$f.value} else . end
      );
    diff(.[0];.[1])
  ' "$LAST_EXPORT" "$TEMP_JSON"
  rm "$TEMP_JSON"
fi
