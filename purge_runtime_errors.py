from pathlib import Path
import re

p = Path("tests/deepseek-full-suite.mjs")
s = p.read_text()

# Remove stale completions/uploads references
s = s.replace(
    "runtime?.completions.length",
    "(runtime?.completions || []).length"
)

s = s.replace(
    "runtime?.uploads.length",
    "(runtime?.uploads || []).length"
)

# Replace unsafe runtime.streams access
s = s.replace(
    "runtime.streams",
    "(runtime?.streams || [])"
)

s = s.replace(
    "runtime.fetches",
    "(runtime?.fetches || [])"
)

# Remove duplicate failing logger blocks
pattern = re.compile(
    r'console\.log\("❌ Runtime stream intelligence"\);.*?console\.log\(\{\s*error:\s*e\.message\s*\}\);\s*',
    re.S
)

matches = pattern.findall(s)

if len(matches) > 1:
    s = s.replace(matches[-1], '')

p.write_text(s)

print("✅ Purged stale runtime references")
