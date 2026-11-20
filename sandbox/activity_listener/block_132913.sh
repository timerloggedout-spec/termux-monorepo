python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/live_view.py'
src = p.read_text()
old = "r'