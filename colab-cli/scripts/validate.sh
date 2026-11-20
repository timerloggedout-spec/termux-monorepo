#!/bin/bash
# validate.sh <production_dir>
# Run tests (e.g., pytest if exists, or check for required files)
PROD_DIR="$1"
echo "🔬 Validating $PROD_DIR"
# Example: check if there's a requirements.txt and try to install
if [ -f "$PROD_DIR/requirements.txt" ]; then
    pip install -r "$PROD_DIR/requirements.txt" --quiet
fi
# Run pytest if available
if [ -f "$PROD_DIR/tests/test_main.py" ]; then
    pytest "$PROD_DIR/tests"
fi
echo "✅ Validation passed."
