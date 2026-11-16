# The previous replacement left a stray function definition. Fix it now.
python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/live_view.py'
src = p.read_text()
src = src.replace(
    "def send_message(get_token(), SESSION_ID, text)",
    "send_message(get_token(), SESSION_ID, text)"
)
p.write_text(src)
print("Fixed.")
PYEOF