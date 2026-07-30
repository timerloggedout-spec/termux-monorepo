#!/data/data/com.termux/files/usr/bin/bash

# Install required packages if not already installed
pkg install -y jq tree > /dev/null 2>&1

# Define output file and export directory
OUTPUT_FILE="project_export_$(date +%Y%m%d_%H%M%S).txt"
EXPORT_DIR="/storage/emulated/0/Download/TermuxExports/_1-proj"

# Ensure export directory exists (assumes termux-setup-storage has been run)
mkdir -p "$EXPORT_DIR"

# Create temporary JSON file
TEMP_JSON=$(mktemp)

# Initialize JSON object
echo '{"structure": {}, "files": {}}' > "$TEMP_JSON"

# Capture directory structure for _1-Projects
cd _1-Projects || { echo "Error: _1-Projects directory not found"; exit 1; }
STRUCTURE=$(tree . | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
cd ..

# Add _1-Projects structure to JSON
jq --arg struct "$STRUCTURE" '.structure._1_Projects = $struct' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"

# Add odds_map-n.py structure (as a single file)
jq --arg struct "odds_map-n.py" '.structure.odds_map_n_py = $struct' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"

# Add file contents for _1-Projects (specified extensions)
find _1-Projects -type f \( -name "*.py" -o -name "*.rs" -o -name "*.js" -o -name "*.tsx" -o -name "*.md" \) | while read -r FILE; do
  # Get relative path (remove leading _1-Projects/)
  REL_PATH="${FILE#./}"
  # Escape content for JSON
  CONTENT=$(cat "$FILE" | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
  # Add to JSON
  jq --arg path "$REL_PATH" --arg cont "$CONTENT" '.files[$path] = $cont' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"
done

# Add odds_map-n.py file content
if [[ -f "odds_map-n.py" ]]; then
  CONTENT=$(cat "odds_map-n.py" | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
  jq --arg path "odds_map-n.py" --arg cont "$CONTENT" '.files[$path] = $cont' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"
else
  echo "Warning: odds_map-n.py not found"
fi

# Move the temp JSON to the output .txt file
mv "$TEMP_JSON" "$OUTPUT_FILE"

# Copy to export directory
cp "$OUTPUT_FILE" "$EXPORT_DIR/"

# Clean up local copy (comment out to keep local copy)
rm "$OUTPUT_FILE"

echo "Project exported to $EXPORT_DIR/$OUTPUT_FILE"
