python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/archwiz.py'
src = p.read_text()

# Fix the AttributeError
src = src.replace(
    "blocks = _json.loads(open(staging).read_text())",
    "blocks = _json.loads(pathlib.Path(staging).read_text())"
)

# Remove the stray print that polluted the status bar
src = src.replace(
    'print("[11] now integrates with staged forensic blocks.")',
    'pass  # staging integration active'
)

p.write_text(src)
print("Fixed.")
PYEOF