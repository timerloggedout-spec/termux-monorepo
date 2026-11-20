#!/data/data/com.termux/files/usr/bin/bash
set -e

TARGET="tests/deepseek-full-suite.js"

if [ ! -f "$TARGET" ]; then
  echo "❌ Missing: $TARGET"
  exit 1
fi

echo "🔧 Patching Puppeteer waitForTimeout compatibility..."

python3 << 'PYEOF'
from pathlib import Path
import re

path = Path("tests/deepseek-full-suite.js")

text = path.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# Inject portable wait() helper if not already present
# ------------------------------------------------------------------

if "const wait = ms =>" not in text:

    insertion = r"""
const wait = ms =>
  new Promise(resolve =>
    setTimeout(resolve, ms)
  );

"""

    text = re.sub(
        r"(const REPORT_FILE = path\.join\([\s\S]*?\);\n)",
        r"\1\n" + insertion,
        text,
        count=1
    )

# ------------------------------------------------------------------
# Replace deprecated page.waitForTimeout(...)
# ------------------------------------------------------------------

text = re.sub(
    r"await\s+page\.waitForTimeout\((.*?)\);",
    r"await wait(\1);",
    text
)

path.write_text(text, encoding="utf-8")

print("✅ waitForTimeout patched.")
PYEOF

echo ""
echo "🧪 Verifying..."

grep -n "waitForTimeout" "$TARGET" || true

echo ""
echo "✅ Patch complete."
echo ""
echo "Run:"
echo "   node tests/deepseek-full-suite.js"
