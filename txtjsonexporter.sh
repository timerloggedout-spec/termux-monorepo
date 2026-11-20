#!/data/data/com.termux/files/usr/bin/bash

# Install required packages if not already installed
pkg install -y jq tree > /dev/null 2>&1

# Define output file and export directory
OUTPUT_FILE="project_export_$(date +%Y%m%d_%H%M%S).txt"
EXPORT_DIR="$HOME/storage/downloads/Termux_exports"

# Ensure export directory exists (assumes termux-setup-storage has been run)
mkdir -p "$EXPORT_DIR"

# Create temporary JSON file
TEMP_JSON=$(mktemp)

echo '{}' > "$TEMP_JSON"

# Capture directory structure as a multiline string escaped for JSON
STRUCTURE=$(tree . | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')

# Add structure to JSON
jq --arg struct "$STRUCTURE" '.structure = $struct' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"

# Find and add file contents for specified extensions
find . -type f \( -name "*.py" -o -name "*.rs" -o -name "*.js" -o -name "*.tsx" -o -name "*.md" \) | while read -r FILE; do
  # Get relative path (remove leading ./)
  REL_PATH="${FILE#./}"
  # Escape content for JSON (escape quotes and convert newlines to \n)
  CONTENT=$(cat "$FILE" | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
  # Add to JSON
  jq --arg path "$REL_PATH" --arg cont "$CONTENT" '.files[$path] = $cont' "$TEMP_JSON" > temp2 && mv temp2 "$TEMP_JSON"
done

# Move the temp JSON to the output .txt file (it's JSON content in a .txt file for LLM compatibility)
mv "$TEMP_JSON" "$OUTPUT_FILE"

# Copy to export directory
cp "$OUTPUT_FILE" "$EXPORT_DIR/"

# Clean up local copy if desired (comment out if you want to keep it)
rm "$OUTPUT_FILE"

echo "Project exported to $EXPORT_DIR/$OUTPUT_FILE"
