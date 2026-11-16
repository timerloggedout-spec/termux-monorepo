#!/data/data/com.termux/files/usr/bin/bash
set -e

FILE="tests/deepseek-full-suite.js"

echo "🧠 Injecting runtime stream hooks..."

cp "$FILE" "$FILE.bak.$(date +%s)"

python3 << 'PYEOF'
from pathlib import Path

p = Path("tests/deepseek-full-suite.js")
text = p.read_text()

if "runtime-stream-intelligence" not in text:

    text = text.replace(
        "const fs = require('fs');",
        """const fs = require('fs');
const runtimeIntel = require('./runtime-stream-intelligence');
"""
    )

    marker = "await page.goto("
    idx = text.find(marker)

    if idx != -1:
        insert_after = text.find(";", idx) + 1

        text = (
            text[:insert_after] +
            """

await runtimeIntel.install(page);

""" +
            text[insert_after:]
        )

    text += """

// ============================================
// Runtime stream export
// ============================================

try {

  const runtime = await runtimeIntel.exportRuntime(page);

  console.log("✅ Runtime stream intelligence");

  console.log(JSON.stringify({
    fetches: runtime.fetches.length,
    streams: runtime.streams.length,
    completions: runtime.completions.length,
    uploads: runtime.uploads.length
  }, null, 2));

} catch (e) {

  console.log("❌ Runtime stream intelligence");

  console.log({
    error: e.message
  });

}

"""

p.write_text(text)

print("patched")
PYEOF

echo "✅ Runtime hook patch complete."

