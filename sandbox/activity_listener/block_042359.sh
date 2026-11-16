python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/forensic_toolchain.py'
src = p.read_text()

# Fix the similarity_scan function signature to accept threshold
src = src.replace(
    "def similarity_scan(target_text):",
    "def similarity_scan(target_text, threshold=0.3):"
)

# Fix the CLI to pass threshold
src = src.replace(
    "elif cmd == 'similar' and len(sys.argv) > 2:\n        similarity_scan(' '.join(sys.argv[2:]))",
    "elif cmd == 'similar' and len(sys.argv) > 2:\n        target = ' '.join(sys.argv[2:]).rsplit(' ', 1)\n        if len(target) > 1 and target[-1].replace('.','').isdigit():\n            similarity_scan(target[0], float(target[-1]))\n        else:\n            similarity_scan(' '.join(sys.argv[2:]))"
)

p.write_text(src)
print("similarity_scan now accepts optional threshold argument.")
PYEOF