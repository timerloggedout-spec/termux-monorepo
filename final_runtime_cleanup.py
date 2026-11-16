from pathlib import Path
import re

p = Path("tests/deepseek-full-suite.mjs")
s = p.read_text()

# -------------------------------------------------
# Remove duplicate Runtime stream intelligence blocks
# Keep only the FIRST success logger
# -------------------------------------------------

success_blocks = list(re.finditer(
    r'console\.log\("✅ Runtime stream intelligence"\);.*?\n\s*\}\s*, null, 2\)\);\s*',
    s,
    re.S
))

if len(success_blocks) > 1:
    for m in reversed(success_blocks[1:]):
        s = s[:m.start()] + s[m.end():]

# -------------------------------------------------
# Remove duplicate failure logger blocks
# -------------------------------------------------

failure_blocks = list(re.finditer(
    r'console\.log\("❌ Runtime stream intelligence"\);.*?\n\s*\}\);\s*',
    s,
    re.S
))

if len(failure_blocks) > 1:
    for m in reversed(failure_blocks[1:]):
        s = s[:m.start()] + s[m.end():]

# -------------------------------------------------
# Guarantee runtime exists before telemetry logger
# -------------------------------------------------

needle = 'console.log("✅ Runtime stream intelligence");'

replacement = """
runtime = runtime || {
  streams: [],
  fetches: [],
  wsMessages: [],
  domMutations: [],
  lastStream: null
};

console.log("✅ Runtime stream intelligence");
"""

s = s.replace(needle, replacement, 1)

p.write_text(s)

print("✅ Final runtime logger cleanup applied")
