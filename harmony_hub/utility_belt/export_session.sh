#!/bin/bash
# Export a single session to synthegration_exports
SESSION_ID="${1:?Usage: export_session.sh <session_id>}"
echo "📤 Exporting $SESSION_ID..."
python3 "$HOME/cli-synthegration/synthegration_index.py" export "$SESSION_ID" 2>/dev/null && echo "✅ Exported" || echo "❌ Export failed"
